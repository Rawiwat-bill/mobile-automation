"""Sanitized Product Selection evidence extraction for bounded discovery."""
from __future__ import annotations

import json
import re
import xml.etree.ElementTree as ET
from pathlib import Path
from typing import Any

from libraries.evidence_scope import resolve_private_evidence_dir

_ACCOUNT_PATTERN = re.compile(r"\b\d{8,}\b")


def _mask(value: str) -> str:
    return _ACCOUNT_PATTERN.sub("[MASKED_ACCOUNT]", value)


def _visible(node: ET.Element) -> bool:
    return node.get("visible-to-user", "true").lower() == "true"


def _safe_attributes(node: ET.Element, product_index: int | None = None) -> dict[str, str]:
    attrs = {key: _mask(value) for key, value in node.attrib.items()}
    rid = node.get("resource-id", "")
    if "flatListCardsTextProductName_" in rid:
        attrs["text"] = f"[PRODUCT_NAME_{product_index if product_index is not None else 'UNKNOWN'}]"
        if "content-desc" in attrs:
            attrs["content-desc"] = attrs["text"]
    return attrs


def _index_from_id(resource_id: str) -> str:
    match = re.search(r"_(\d+)$", resource_id)
    return match.group(1) if match else "UNKNOWN"


def capture_product_selection_evidence(source: str, activity_output: str, output_dir: str) -> str:
    root = ET.fromstring(source)
    evidence_dir = Path(resolve_private_evidence_dir(output_dir))

    rows: list[dict[str, Any]] = []
    checkboxes: list[dict[str, Any]] = []
    confirm: list[dict[str, Any]] = []
    empty_alerts: list[dict[str, Any]] = []
    product_ids: list[str] = []

    for node in root.iter():
        rid = node.get("resource-id", "")
        if not _visible(node):
            continue
        if "flatListCardsTouchableOpacity_" in rid:
            index = _index_from_id(rid)
            product_ids.append(rid)
            rows.append({"resource_id": rid, "index": index, "attributes": _safe_attributes(node)})
        elif "flatListCardsCheckBox_" in rid:
            checkboxes.append({"resource_id": rid, "index": _index_from_id(rid), "attributes": _safe_attributes(node)})
        elif rid == "screenProductSelection_buttonConfirm":
            confirm.append(_safe_attributes(node))
        elif "alert" in rid.lower() or "validation" in rid.lower():
            empty_alerts.append({"resource_id": rid, "attributes": _safe_attributes(node)})

    names = []
    for node in root.iter():
        rid = node.get("resource-id", "")
        if "flatListCardsTextProductName_" in rid and _visible(node):
            names.append({
                "resource_id": rid,
                "index": _index_from_id(rid),
                "sanitized_name": f"[PRODUCT_NAME_{_index_from_id(rid)}]",
                "attributes": _safe_attributes(node, int(_index_from_id(rid)) if _index_from_id(rid).isdigit() else None),
            })

    safe_xml_root = ET.fromstring(source)
    for node in safe_xml_root.iter():
        rid = node.get("resource-id", "")
        index = int(_index_from_id(rid)) if _index_from_id(rid).isdigit() else None
        safe_attributes = _safe_attributes(node, index)
        node.attrib.clear()
        node.attrib.update(safe_attributes)
    safe_xml = ET.tostring(safe_xml_root, encoding="unicode")
    (evidence_dir / "product_selection_appium_sanitized.xml").write_text(safe_xml + "\n", encoding="utf-8")

    activity_lines = []
    for line in activity_output.splitlines():
        if "mResumedActivity" in line or "mFocusedApp" in line or "com.bangkokbank.blue.sit" in line:
            activity_lines.append(_mask(line))
    (evidence_dir / "foreground_activity.txt").write_text("\n".join(activity_lines) + "\n", encoding="utf-8")

    result = {
        "artifact_classification": "PRIVATE_LOCAL",
        "classification": {
            "product_selection_root": "RUNTIME_PROVEN",
            "dynamic_row_structure": "RUNTIME_PROVEN" if rows else "NAMING_ONLY",
            "selected_state_semantics": "RUNTIME_PROVEN" if checkboxes else "NAMING_ONLY",
            "eligible_product": "RUNTIME_PROVEN" if rows else "NAMING_ONLY",
            "inactive_state": "RUNTIME_PROVEN" if any(item["attributes"].get("enabled") == "false" for item in rows + checkboxes) else "NOT_PROVEN",
            "confirm_cta": "RUNTIME_PROVEN" if confirm else "NAMING_ONLY",
            "navigation_destination": "NOT_PROVEN",
        },
        "root_marker": "screenProductSelection_textTitle" if "screenProductSelection_textTitle" in source else "NOT_FOUND",
        "visible_product_row_resource_ids": sorted(set(product_ids)),
        "product_names": names,
        "checkboxes": checkboxes,
        "confirm": confirm,
        "empty_selection_alerts": empty_alerts,
        "confirm_pressed": False,
        "navigation_probed": False,
    }
    (evidence_dir / "product_selection_runtime.json").write_text(json.dumps(result, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    return json.dumps({
        "row_count": len(rows),
        "checkbox_count": len(checkboxes),
        "confirm_present": bool(confirm),
        "empty_selection_alert_count": len(empty_alerts),
        "confirm_pressed": False,
    }, sort_keys=True)


def capture_product_selection_snapshot(
    source: str,
    snapshot_name: str,
    output_dir: str,
    package: str = "",
    activity: str = "",
) -> str:
    """Write a focused, sanitized snapshot of Product Selection markers.

    This is intentionally discovery-only: it records marker presence and the
    requested state attributes without retaining product text or customer data.
    """
    root = ET.fromstring(source)
    target_ids = {
        "screenProductSelection_textTitle",
        "screenProductSelection_textDescription",
        "screenProductSelection_buttonConfirm",
    }
    target_prefixes = (
        "screenProductSelection_flatListCardsTouchableOpacity_",
        "screenProductSelection_flatListCardsCheckBox_",
    )
    snapshots: list[dict[str, Any]] = []
    for node in root.iter():
        rid = node.get("resource-id", "")
        if rid not in target_ids and not rid.startswith(target_prefixes):
            continue
        snapshots.append({
            "resource_id": rid,
            "attributes": {
                key: _mask(node.get(key, ""))
                for key in ("visible-to-user", "enabled", "clickable", "checked", "selected")
                if key in node.attrib
            },
        })

    result = {
        "artifact_classification": "PRIVATE_LOCAL",
        "snapshot": snapshot_name,
        "package": _mask(package),
        "activity": _mask(activity),
        "markers": snapshots,
        "presence": {
            "title": any(item["resource_id"] == "screenProductSelection_textTitle" for item in snapshots),
            "description": any(item["resource_id"] == "screenProductSelection_textDescription" for item in snapshots),
            "rows": any(item["resource_id"].startswith("screenProductSelection_flatListCardsTouchableOpacity_") for item in snapshots),
            "checkboxes": any(item["resource_id"].startswith("screenProductSelection_flatListCardsCheckBox_") for item in snapshots),
            "confirm": any(item["resource_id"] == "screenProductSelection_buttonConfirm" for item in snapshots),
        },
    }
    evidence_dir = Path(resolve_private_evidence_dir(output_dir))
    (evidence_dir / f"{snapshot_name}.json").write_text(json.dumps(result, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    focused = ET.Element("hierarchy")
    for item in snapshots:
        node = ET.SubElement(focused, "node")
        node.set("resource-id", item["resource_id"])
        node.attrib.update(item["attributes"])
    (evidence_dir / f"{snapshot_name}.xml").write_text(ET.tostring(focused, encoding="unicode") + "\n", encoding="utf-8")
    return json.dumps(result["presence"], sort_keys=True)


def capture_tc004_post_first_pin_probe(
    source: str,
    native_source: str,
    snapshot_name: str,
    output_dir: str,
    package: str = "",
    activity: str = "",
    timestamp: str = "",
) -> str:
    """Capture sanitized state evidence immediately after first-PIN entry."""
    evidence_dir = Path(resolve_private_evidence_dir(output_dir))

    def classify(value: str) -> str:
        if "screenPinInput_headerText" in value and (
            "Re-enter PIN to confirm" in value or "re-enter PIN to confirm" in value
        ):
            return "CONFIRM_PIN"
        if "screenReEnterPinInput_keyPad" in value:
            return "CONFIRM_PIN"
        if "You're all set!" in value or "You’re all set!" in value or "Let's go" in value or "Let’s go" in value:
            return "COMPLETION_SUCCESS"
        if "screenProductSelection_textTitle" in value or "screenProductSelection_textDescription" in value:
            return "PRODUCT_SELECTION"
        if "AJI-001" in value or "RGI-" in value:
            return "EXACT_ERROR"
        if "screenPinInput" in value or "loading" in value.lower() or "ImageView" in value:
            return "LOADING_OR_INTERMEDIATE"
        return "UNKNOWN"

    def sanitize(value: str) -> str:
        return _mask(value)

    (evidence_dir / f"{snapshot_name}_appium_page_source.xml").write_text(
        sanitize(source) + "\n", encoding="utf-8"
    )
    (evidence_dir / f"{snapshot_name}_native_ui_hierarchy.xml").write_text(
        sanitize(native_source) + "\n", encoding="utf-8"
    )
    result = {
        "artifact_classification": "PRIVATE_LOCAL",
        "timestamp": timestamp,
        "package": _mask(package),
        "activity": _mask(activity),
        "classification": classify(source + native_source),
        "markers": {
            "confirm_pin": "screenReEnterPinInput_keyPad" in source or "Re-enter PIN to confirm" in source,
            "completion_success": any(marker in source for marker in ("You're all set!", "You’re all set!", "Let's go", "Let’s go")),
            "product_selection": "screenProductSelection_textTitle" in source or "screenProductSelection_textDescription" in source,
            "exact_error": "AJI-001" in source or "RGI-" in source,
        },
    }
    (evidence_dir / f"{snapshot_name}.json").write_text(json.dumps(result, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    return result["classification"]
