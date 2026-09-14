from __future__ import annotations

import json
import xml.etree.ElementTree as ET
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
BASE = ROOT / "reports" / "run-etb" / "TC-ETB-001" / "evidence"


def structural_markers(xml_path: Path) -> tuple[list[str], list[str], list[str]]:
    root = ET.parse(xml_path).getroot()
    packages: list[str] = []
    resource_ids: list[str] = []
    classes: list[str] = []
    for node in root.iter():
        package = node.attrib.get("package", "")
        resource_id = node.attrib.get("resource-id", "")
        class_name = node.attrib.get("class", "")
        if package and package not in packages:
            packages.append(package)
        if resource_id and resource_id not in resource_ids:
            resource_ids.append(resource_id)
        if class_name and class_name not in classes:
            classes.append(class_name)
    return packages, resource_ids, classes


summaries = list(BASE.glob("*/TC-ETB-001/private_local/device/real_startup_summary.json"))
if not summaries:
    raise SystemExit("LATEST_TC001_STARTUP_EVIDENCE=NOT_FOUND")

summary_path = max(summaries, key=lambda path: path.stat().st_mtime_ns)
run_id = summary_path.parts[summary_path.parts.index("evidence") + 1]
summary = json.loads(summary_path.read_text(encoding="utf-8"))
xml_path = summary_path.with_name("real_startup_landing.xml")

print(f"LATEST_RUN_ID={run_id}")
print(f"SUMMARY_PATH={summary_path.relative_to(ROOT)}")
print(f"TERMINAL_STATE={summary.get('terminal_state', '')}")
print(f"STARTUP_ERROR_MARKER={summary.get('startup_error_marker', '')}")
print(f"LAUNCH_RESULT={summary.get('launch_result', '')}")
print(f"APP_PID_BEFORE_ATTACH={'PRESENT' if summary.get('app_pid_before_attach') else 'EMPTY'}")
print("TIMELINE=" + json.dumps(summary.get("timeline", []), separators=(",", ":"), sort_keys=True))

if not xml_path.is_file():
    raise SystemExit("SANITIZED_XML=NOT_FOUND")

packages, resource_ids, classes = structural_markers(xml_path)
print("XML_PACKAGES=" + ",".join(packages[:20]))
print("XML_RESOURCE_IDS=" + ",".join(resource_ids[:40]))
print("XML_CLASSES=" + ",".join(classes[:20]))
print("CRASH_HINT_IDS=" + ",".join(
    value for value in resource_ids if any(token in value.lower() for token in ("aerr", "crash", "close", "wait", "error"))
))

private_dir = BASE / run_id / "TC-ETB-001" / "private_local"
failure_jsons: list[Path] = []
for candidate in private_dir.rglob("*.json"):
    try:
        payload = json.loads(candidate.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError):
        continue
    if (
        payload.get("artifact_classification") == "PRIVATE_LOCAL"
        and "screenshot" in payload
        and "page_source" in payload
    ):
        failure_jsons.append(candidate)

if not failure_jsons:
    print("FAILURE_EVIDENCE=NOT_FOUND")
    raise SystemExit(0)

failure_json = max(failure_jsons, key=lambda path: path.stat().st_mtime_ns)
failure_status = json.loads(failure_json.read_text(encoding="utf-8"))
failure_xml = failure_json.with_suffix(".xml")
print(f"FAILURE_EVIDENCE_JSON={failure_json.relative_to(ROOT)}")
print(f"FAILURE_SCREENSHOT_STATUS={failure_status.get('screenshot', '')}")
print(f"FAILURE_PAGE_SOURCE_STATUS={failure_status.get('page_source', '')}")
if not failure_xml.is_file():
    print("FAILURE_XML=NOT_FOUND")
    raise SystemExit(0)

failure_packages, failure_resource_ids, failure_classes = structural_markers(failure_xml)
print(f"FAILURE_XML={failure_xml.relative_to(ROOT)}")
print("FAILURE_PACKAGES=" + ",".join(failure_packages[:20]))
print("FAILURE_RESOURCE_IDS=" + ",".join(failure_resource_ids[:80]))
print("FAILURE_CLASSES=" + ",".join(failure_classes[:30]))
print("FAILURE_WEBVIEW_PRESENT=" + ("YES" if "android.webkit.WebView" in failure_classes else "NO"))
print("FAILURE_CRASH_HINT_IDS=" + ",".join(
    value for value in failure_resource_ids
    if any(token in value.lower() for token in ("aerr", "crash", "close", "wait", "error"))
))
