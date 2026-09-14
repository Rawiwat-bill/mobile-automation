"""Read-only, allowlisted inspection of the existing TC001 DOPA boundary.

Never starts Robot, Appium, ADB or backend work; never prints raw XML, messages,
input values, screenshots or local profiles. Run after TC001 has completed.
Ignore leftover evidence files older than the current testcase start.
"""
import hashlib
import json
import re
import xml.etree.ElementTree as ET
from datetime import datetime
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
RUN = ROOT / 'reports/run-etb/TC-ETB-001'
NAMES = {
    'Reset ETB Regression Application', 'Tap Landing Ready Button',
    'Wait Until Terms And Conditions Screen Is Displayed', 'Scroll Down Terms And Conditions',
    'Accept Terms And Conditions', 'Wait Until Tell Us About You Screen Is Displayed',
    'Common Onboarding Flow', 'Tap Profile Next', 'Tap Profile Next Button',
    'Observe Profile Next Transition', 'Complete ETB Onboarding',
    'Wait Until Check DOPA Fill Laser Code Is Displayed', 'Input Laser Code',
    'Assert CIS Cleanup Policy', 'Normalize ETB Regression Application',
}


def read_bounded(path):
    if path.is_symlink() or not path.resolve().is_relative_to(ROOT) or path.stat().st_size > 20000000:
        raise ValueError('EVIDENCE_PATH_NOT_SAFE')
    return path.read_bytes()


def status(node):
    result = node.find('status')
    return {k: result.get(k) for k in ('status', 'start', 'elapsed')} if result is not None else {}


def inspect():
    path = RUN / 'output.xml'
    data = read_bounded(path)
    root = ET.fromstring(data)
    tests = list(root.iter('test'))
    if len(tests) != 1 or not tests[0].get('name', '').startswith('TC-ETB-001 '):
        raise ValueError('EXPECTED_EXACTLY_TC001')
    test = tests[0]
    started = datetime.fromisoformat(status(test)['start']).timestamp()
    final_text = test.findtext('status', '')
    result = {
        'source': str(path.relative_to(ROOT)),
        'sha256': hashlib.sha256(data).hexdigest(),
        'generated': root.get('generated'), 'test_count': 1,
        'test_status': status(test),
        'terminal_codes': sorted(set(re.findall(r'\b(?:AJI|GOD|RGI|COO|FSI)-[0-9]{3}\b', final_text))),
        'reported_pre_dopa_aji_blocker': 'BLOCKED_BY_ENVIRONMENT_BACKEND_AJI_001' in final_text,
        'reported_dopa_locator_timeout': 'screenPersonalInformation_navBarTitleList' in final_text,
        'reported_terms_webview_timeout': 'xpath=//android.webkit.WebView' in final_text,
        'keyword_statuses': [], 'returned_markers': [], 'completed_checkpoints': [],
    }
    marker_pattern = re.compile(r'\$\{(?:transition_result|profile_result|common_result)\} = (AJI-001|GOD-013|RGI-104|NEXT|None|PROFILE_LEFT_OR_NEXT_STATE_VISIBLE)')
    for kw in test.iter('kw'):
        if kw.get('name') in NAMES:
            result['keyword_statuses'].append({'keyword': kw.get('name'), **status(kw)})
            for message in kw.findall('msg'):
                match = marker_pattern.fullmatch(message.text or '')
                if match:
                    result['returned_markers'].append({'keyword': kw.get('name'), 'value': match.group(1), 'time': message.get('time')})
        if kw.get('name') == 'Mark Health Checkpoint' and status(kw).get('status') == 'PASS':
            stage = kw.findtext('arg', '')
            if re.fullmatch(r'[A-Z][A-Z0-9_]{1,80}', stage):
                result['completed_checkpoints'].append(stage)
    summary = RUN / 'profile_exit_evidence/private_local/marker_summary.txt'
    result['profile_summary_fresh'] = summary.is_file() and summary.stat().st_mtime >= started
    if result['profile_summary_fresh']:
        for line in read_bounded(summary).decode('utf-8').splitlines():
            if re.fullmatch(r'destination_marker=(AJI-001|GOD-013|RGI-104|PROFILE_LEFT_OR_NEXT_STATE_VISIBLE)', line):
                result['profile_destination'] = line.split('=', 1)[1]
    xml = RUN / 'private_local/etb_tc_001_result.xml'
    result['terminal_ui_fresh'] = xml.is_file() and xml.stat().st_mtime >= started
    if result['terminal_ui_fresh']:
        ui = ET.fromstring(read_bounded(xml))
        ids = []
        for node in ui.iter():
            rid = node.get('resource-id', '')
            if re.fullmatch(r'(?:screen[A-Za-z0-9_.-]*|security-error-container|text-input-flat)', rid) and not re.search(r'\d{8,}', rid):
                ids.append(rid)
        result['terminal_resource_ids'] = sorted(set(ids))[:50]
        result['terminal_edittext_count'] = sum(n.tag == 'android.widget.EditText' for n in ui.iter())
        result['terminal_webview_count'] = sum(n.tag == 'android.webkit.WebView' for n in ui.iter())
    report = ROOT / 'reports/investigation/dopa_boundary/post_mmp_9c15241b.md'
    if report.is_file():
        result['investigation_report_sha256'] = hashlib.sha256(read_bounded(report)).hexdigest()
    print(json.dumps(result, indent=2, sort_keys=True))


if __name__ == '__main__':
    try:
        inspect()
    except (OSError, ValueError, ET.ParseError, KeyError) as error:
        print('DOPA_EVIDENCE_INSPECTION_FAILED=' + type(error).__name__)
        raise SystemExit(2) from None
