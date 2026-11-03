"""Best-effort, sanitized visual timeline evidence for ETB runtime research."""
from __future__ import annotations

import json
import re
import xml.etree.ElementTree as ET
from datetime import datetime
from pathlib import Path
from typing import Any, cast

from PIL import Image, ImageDraw
from robot.libraries.BuiltIn import BuiltIn

from libraries.evidence_scope import resolve_private_evidence_dir

_PRODUCT_ROW_PREFIXES = (
    "screenProductSelection_flatListCardsTouchableOpacity_",
    "screenProductSelection_flatListCardsCheckBox_",
)
_SENSITIVE_ATTRIBUTE = re.compile(r'(?i)(text|content-desc|hint|value|password)="[^"]*"')
_SCREENSHOT_NAMES = {
    "PS0_PRODUCT_SELECTION_VISIBLE": "01_product_selection.png",
    "PS2_SELECTION_STATE": "02_selection_state.png",
    "PS3_SELECTION_ACTION": "03_after_selection.png",
    "PS5_CONFIRM_CLICK_END": "04_after_confirm.png",
    "SUCCESS0_VISIBLE": "05_registration_success.png",
    "PRESET0_VISIBLE": "06_preset.png",
    "PRESET_ACTION_END": "06_after_preset_action.png",
    "3C0_INTRO_VISIBLE": "07_3c_intro.png",
    "CONTROL0_VISIBLE": "08_control_home.png",
}


def _now() -> str:
    return datetime.now().astimezone().strftime("%Y-%m-%dT%H:%M:%S.%f")


def _appium() -> Any:
    return cast(Any, BuiltIn().get_library_instance("AppiumLibrary"))


def _source() -> str:
    return _appium()._current_application().page_source


def _activity() -> str:
    return str(_appium().get_activity())


def _package() -> str:
    return str(_appium()._current_application().current_package)


def _product_metrics(source: str) -> dict[str, Any]:
    root = ET.fromstring(source)
    rows = []
    checkboxes = []
    for node in root.iter():
        rid = node.get("resource-id", "")
        if not any(rid.startswith(prefix) for prefix in _PRODUCT_ROW_PREFIXES):
            continue
        item = {
            "resource_id": rid,
            "enabled": node.get("enabled", ""),
            "checked": node.get("checked", ""),
            "selected": node.get("selected", ""),
        }
        if "CheckBox" in rid:
            checkboxes.append(item)
        else:
            rows.append(item)
    # Product type classification is intentionally marker-only. Values/text are never persisted.
    lower = source.lower()
    return {
        "row_count": len(rows),
        "eligible_count": sum(item["enabled"] == "true" for item in rows),
        "selected_count": sum(item["checked"] == "true" or item["selected"] == "true" for item in checkboxes),
        "checkbox_state": [
            {"resource_id": item["resource_id"], "checked": item["checked"], "selected": item["selected"]}
            for item in checkboxes
        ],
        "saving_present": "saving" in lower,
        "e_saving_present": "e-saving" in lower or "esaving" in lower,
    }


def _marker_summary(source: str, state: str) -> dict[str, Any]:
    markers = {
        "product_selection_title": "screenProductSelection_textTitle" in source,
        "product_selection_description": "screenProductSelection_textDescription" in source,
        "product_selection_confirm": "screenProductSelection_buttonConfirm" in source,
        "registration_success": any(value in source for value in ("You're all set!", "You’re all set!", "Let's go", "Let’s go")),
        "preset_title": "screenPresetSettingProfile_titleText" in source,
        "preset_description": "screenPresetSettingProfile_textCompleteDescription" in source,
        "preset_button": "screenPresetSettingProfile_buttonLetsGo" in source,
        "intro_3c": "screen3CIntroduction_buttonGotIt" in source,
        "control_transfer": "control_body_quickMenu_buttonTransfer" in source,
        "control_profile": "control_header_headerNavbar_buttonUserProfile-touchable" in source,
    }
    result: dict[str, Any] = {"recognized_state": state, "markers": markers}
    if state == "PRODUCT_SELECTION":
        result["product_selection"] = _product_metrics(source)
    return result


def _mask_product_rows(image_path: Path, source: str) -> None:
    root = ET.fromstring(source)
    image = Image.open(image_path).convert("RGB")
    draw = ImageDraw.Draw(image)
    width, height = image.size
    for node in root.iter():
        rid = node.get("resource-id", "")
        if not any(rid.startswith(prefix) for prefix in _PRODUCT_ROW_PREFIXES):
            continue
        match = re.search(r"\[(\d+),(\d+)\]\[(\d+),(\d+)\]", node.get("bounds", ""))
        if match:
            x1, y1, x2, y2 = (max(0, int(value)) for value in match.groups())
            draw.rectangle((min(x1, width), min(y1, height), min(x2, width), min(y2, height)), fill="white")
    image.save(image_path)


def record_visual_timeline_event(
    event_name: str,
    state: str,
    output_dir: str,
    action: str = "",
    screenshot: bool = True,
) -> str:
    """Record one event; all failures are converted to a non-fatal status."""
    try:
        source = _source()
        timestamp = _now()
        evidence_dir = Path(resolve_private_evidence_dir(output_dir))
        event: dict[str, Any] = {
            "artifact_classification": "PRIVATE_LOCAL",
            "timestamp": timestamp,
            "event": event_name,
            "package": _package(),
            "activity": _activity(),
            "recognized_state": state,
            "action": action,
            "markers": _marker_summary(source, state),
        }
        screenshot_path = _SCREENSHOT_NAMES.get(event_name)
        if screenshot and screenshot_path:
            target = evidence_dir / screenshot_path
            _appium()._current_application().save_screenshot(str(target))
            if state == "PRODUCT_SELECTION":
                _mask_product_rows(target, source)
            event["screenshot"] = screenshot_path
        timeline_path = evidence_dir / "timeline.json"
        events = []
        if timeline_path.exists():
            events = json.loads(timeline_path.read_text(encoding="utf-8"))
        previous_state = events[-1].get("new_state") if events else None
        event["previous_state"] = previous_state
        event["new_state"] = state
        events.append(event)
        timeline_path.write_text(json.dumps(events, indent=2, sort_keys=True) + "\n", encoding="utf-8")
        (evidence_dir / "timeline.txt").write_text(
            "\n".join(
                f"{item['timestamp']} {item['event']} state={item['recognized_state']} action={item['action']}"
                for item in events
            )
            + "\n",
            encoding="utf-8",
        )
        return "PASS"
    except Exception as error:  # pragma: no cover - exercised through Robot/Appium
        return f"IGNORED:{type(error).__name__}"


def record_post_success_visual_state(output_dir: str) -> str:
    """Record the first recognized state after the existing Success continuation."""
    try:
        source = _source()
        if all(
            marker in source
            for marker in (
                "screenPresetSettingProfile_titleText",
                "screenPresetSettingProfile_textCompleteDescription",
                "screenPresetSettingProfile_buttonLetsGo",
            )
        ):
            return record_visual_timeline_event("PRESET0_VISIBLE", "PRESET", output_dir)
        return "IGNORED:POST_SUCCESS_STATE_NOT_PRESET"
    except Exception as error:  # pragma: no cover - exercised through Robot/Appium
        return f"IGNORED:{type(error).__name__}"
