"""Read existing F05 evidence only; never run Robot, ADB, or network calls."""
from pathlib import Path
import ast
import hashlib
import json
import re
import xml.etree.ElementTree as ET

ROOT = Path(__file__).resolve().parents[1]
PATH = ROOT / 'reports/run-etb/TC-ETB-001/output.xml'

def stamp(value):
    return value if re.fullmatch(r'[0-9T:.+Z -]{1,40}', value or '') else None

def status(node):
    item = node.find('status')
    return None if item is None else {
        'status': item.get('status') if item.get('status') in {'PASS', 'FAIL', 'NOT RUN', 'SKIP'} else 'UNKNOWN',
        'start': stamp(item.get('start') or item.get('starttime')),
        'elapsed': stamp(item.get('elapsed')),
    }

def identity(text):
    if '${LANDING_SKIP_BUTTON}' in text or 'screenLanding_skipButton' in text:
        return 'SKIP'
    if '${LANDING_READY_BUTTON}' in text or 'screenLanding_buttonReady' in text:
        return 'READY'
    return 'UNKNOWN'

def selected_messages(node):
    result = []
    allowed = [
        r'LANDING_ACTION_TAPPED=ADB_FRESH_BOUNDS action=(?:SKIP|READY)',
        r'\$\{(?:action_name)\} = (?:SKIP|READY)',
        r'\$\{(?:is_skip_visible|is_ready_visible|skip_visible)\} = (?:True|False)',
    ]
    for msg in node.iter('msg'):
        text = (msg.text or '').strip()
        if any(re.fullmatch(pattern, text) for pattern in allowed):
            result.append({'time': stamp(msg.get('time') or msg.get('timestamp')), 'value': text})
    return result

def main():
    if PATH.is_symlink() or not PATH.is_file() or PATH.stat().st_size > 40 * 1024 * 1024:
        raise ValueError('EVIDENCE_INPUT_NOT_BOUNDED_REGULAR_FILE')
    raw = PATH.read_bytes()
    if b'<!DOCTYPE' in raw or b'<!ENTITY' in raw:
        raise ValueError('UNEXPECTED_XML_DECLARATION')
    root = ET.fromstring(raw)
    tests = [t for t in root.iter('test') if re.match(r'^TC-ETB-001(?:\b|_)', t.get('name', ''))]
    out = {'source': 'reports/run-etb/TC-ETB-001/output.xml', 'sha256': hashlib.sha256(raw).hexdigest(),
           'generated': stamp(root.get('generated')), 'matching_tests': len(tests), 'taps': []}
    for test in tests:
        out['test_status'] = status(test)
        known_names = set()
        for source in (ROOT / 'resources').rglob('*.resource'):
            if source.is_symlink() or source.stat().st_size > 200000:
                continue
            in_keywords = False
            for line in source.read_text(encoding='utf-8').splitlines():
                if line.startswith('*** '):
                    in_keywords = line.strip() == '*** Keywords ***'
                elif in_keywords and re.fullmatch(r'[A-Za-z][A-Za-z0-9 ]{1,100}', line):
                    known_names.add(line)
        business = [k for k in test.findall('kw') if k.get('type') not in ('SETUP', 'TEARDOWN')]
        observed = []
        for body in business:
            for kw in body.iter('kw'):
                current = status(kw)
                if kw.get('name') in known_names and current and current['status'] in ('PASS', 'FAIL'):
                    observed.append({'keyword': kw.get('name'), **current})
        out['business_keywords'] = observed[-35:]
        out['failed_business_keywords'] = [k for k in observed if k['status'] == 'FAIL'][:12]
        status_text = test.findtext('status', '')
        out['personal_information_title_missing'] = 'screenPersonalInformation_navBarTitleList' in status_text and 'did not match any elements after 40 seconds' in status_text
        out['failure_codes'] = sorted(set(re.findall(r'\b(?:RGI|GOD|COO|FSI|AJI)-[0-9]{3}\b', status_text)))
        out['known_failure_present'] = any(
            'LANDING_ACTION_DID_NOT_TRANSITION' in (item.text or '')
            for item in test.iter('status') if item.get('status') == 'FAIL'
        )
        out['health_checkpoints'] = [
            {'stage': arg.text, **status(kw)}
            for kw in test.iter('kw')
            if kw.get('name') == 'Mark Health Checkpoint' and status(kw) and status(kw)['status'] == 'PASS'
            for arg in kw.findall('arg') if re.fullmatch(r'[A-Z][A-Z_]{2,63}', arg.text or '')
        ][-15:]
        out['landing_and_terms_keywords'] = [
            item for item in observed
            if any(part in item['keyword'] for part in ('Landing', 'Terms', 'Tell Us', 'Common Onboarding'))
        ][:30]
        taps = [k for k in test.iter('kw') if k.get('name') == 'Tap Landing Ready Button']
        for tap in taps[:4]:
            entry = {'status': status(tap), 'messages': selected_messages(tap), 'rects': [], 'post_checks': []}
            for kw in tap.iter('kw'):
                if kw.get('name') == 'Get Element Rect':
                    rect = {'action': identity(' '.join(a.text or '' for a in kw.findall('arg'))), 'status': status(kw)}
                    for msg in kw.findall('msg'):
                        match = re.fullmatch(r'\$\{action_rect\} = (\{[^\n]{1,180}\})', (msg.text or '').strip())
                        if match:
                            value = ast.literal_eval(match.group(1))
                            if isinstance(value, dict) and set(value) == {'x', 'y', 'width', 'height'} and all(isinstance(v, (int, float)) and abs(v) < 10000 for v in value.values()):
                                rect['bounds'] = value
                    entry['rects'].append(rect)
                if kw.get('name') == 'Landing Action Should Be Gone':
                    checks = []
                    for child in kw.iter('kw'):
                        if child.get('name') == 'Element Should Be Visible':
                            checks.append({'action': identity(' '.join(a.text or '' for a in child.findall('arg'))), 'status': status(child)})
                    entry['post_checks'].append({'status': status(kw), 'messages': selected_messages(kw), 'visibility': checks})
            entry['post_check_count'] = len(entry['post_checks'])
            entry['post_checks'] = entry['post_checks'][:2] + entry['post_checks'][-2:] if len(entry['post_checks']) > 4 else entry['post_checks']
            entry['messages'] = entry['messages'][:8] + entry['messages'][-4:] if len(entry['messages']) > 12 else entry['messages']
            out['taps'].append(entry)
    out['knowledge_files'] = {folder: sorted(p.name for p in (ROOT / folder).glob('*.md') if p.is_file())[:40] for folder in ('knowledge/playbooks', 'knowledge/patterns')}
    print(json.dumps(out, indent=2, ensure_ascii=True))

if __name__ == '__main__':
    try:
        main()
    except Exception as exc:
        print('EVIDENCE_EXTRACTION_FAILED=' + type(exc).__name__)
        raise SystemExit(1)
