import re
from datetime import datetime
from pathlib import Path
from typing import Any, cast

from robot.libraries.BuiltIn import BuiltIn

from libraries.evidence_scope import resolve_private_evidence_dir


_SENSITIVE_ATTRIBUTE = re.compile(r'(?i)(text|content-desc|hint|value|password)="[^"]*"')
_POINT_MARKERS: dict[str, dict[str, bool]] = {}


def persist_profile_exit_point(point_name: str, evidence_dir: str) -> None:
    appium_library = cast(Any, BuiltIn().get_library_instance("AppiumLibrary"))
    source = appium_library._current_application().page_source
    _POINT_MARKERS[point_name] = {
        "profile": any(
            marker in source
            for marker in (
                "screenProfile_textInputDob-container",
                "screenProfile_textInputMobileNumber-container",
                "screenProfile_buttonNext",
            )
        ),
        "rgi013": "RGI-013" in source,
        "rgi014": "RGI-014" in source,
    }
    sanitized = _SENSITIVE_ATTRIBUTE.sub(
        lambda match: match.group(1) + '="[REDACTED]"', source
    )
    root = Path(resolve_private_evidence_dir(evidence_dir))
    (root / f"{point_name}.xml").write_text(sanitized, encoding="utf-8")


def persist_profile_exit_evidence_summary(
    evidence_dir: str, transition_result: str, package: str, activity: str
) -> None:
    root = Path(resolve_private_evidence_dir(evidence_dir))
    sources = {
        point: (root / f"{point}.xml").read_text(encoding="utf-8")
        for point in (
            "P0_before_profile_next",
            "P1_after_profile_next",
            "P2_first_recognized_destination",
        )
    }
    timestamp = datetime.now().astimezone().isoformat(timespec="seconds")
    lines = [
        "artifact_classification=PRIVATE_LOCAL",
        f"timestamp={timestamp}",
        f"package={package}",
        f"activity={activity}",
    ]
    for point in sources:
        present = _POINT_MARKERS.get(point, {}).get(
            "profile",
            any(
                marker in sources[point]
                for marker in (
                    "screenProfile_textInputDob-container",
                    "screenProfile_textInputMobileNumber-container",
                    "screenProfile_buttonNext",
                )
            ),
        )
        lines.append(f"{point}_Profile_markers_present={present}")
    p2 = sources["P2_first_recognized_destination"]
    p2_markers = _POINT_MARKERS.get("P2_first_recognized_destination", {})
    lines.extend(
        [
            f"destination_marker={transition_result}",
            f"expected_RGI-013_present={p2_markers.get('rgi013', 'RGI-013' in p2)}",
            f"expected_RGI-014_present={p2_markers.get('rgi014', 'RGI-014' in p2)}",
        ]
    )
    (root / "marker_summary.txt").write_text("\n".join(lines), encoding="utf-8")
