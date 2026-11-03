"""Best-effort, independently bounded failure evidence for Robot tests."""

from __future__ import annotations

import json
import re
import threading
import uuid
import subprocess
from pathlib import Path
from typing import Any, cast

from robot.libraries.BuiltIn import BuiltIn

from libraries.evidence_scope import resolve_private_evidence_dir
from libraries.android_adb import resolve_adb_executable

_SENSITIVE_ATTRIBUTE = re.compile(
    r'(?i)(text|content-desc|hint|value|password)="[^"]*"'
)


def _appium() -> Any:
    return cast(Any, BuiltIn().get_library_instance("AppiumLibrary"))


def _redact_source(source: str) -> str:
    return _SENSITIVE_ATTRIBUTE.sub(lambda match: f'{match.group(1)}="[REDACTED]"', source)


def _bounded_artifact_call(
    label: str,
    target: Path,
    callback: Any,
    timeout: float,
) -> str:
    """Run one bounded capture without allowing a timed-out worker to publish late."""
    pending = target.with_name(f".{target.name}.{uuid.uuid4().hex}.pending")
    gate = threading.Lock()
    state: dict[str, Any] = {"publish_allowed": True, "status": None}

    def invoke() -> None:
        try:
            callback(pending)
        except Exception:  # pragma: no cover - Appium/device dependent
            try:
                pending.unlink(missing_ok=True)
            except OSError:
                pass
            with gate:
                state["status"] = "EVIDENCE_CAPTURE_FAILED"
            return

        with gate:
            if not state["publish_allowed"]:
                try:
                    pending.unlink(missing_ok=True)
                except OSError:
                    pass
                state["status"] = "EVIDENCE_CAPTURE_TIMEOUT"
                return
            try:
                pending.replace(target)
                state["status"] = "PASS"
            except OSError:
                try:
                    pending.unlink(missing_ok=True)
                except OSError:
                    pass
                state["status"] = "EVIDENCE_CAPTURE_FAILED"

    worker = threading.Thread(target=invoke, name=f"evidence-{label}", daemon=True)
    worker.start()
    worker.join(float(timeout))
    if worker.is_alive():
        with gate:
            if state["status"] == "PASS":
                return "PASS"
            state["publish_allowed"] = False
        return "EVIDENCE_CAPTURE_TIMEOUT"
    with gate:
        return str(state["status"] or "EVIDENCE_CAPTURE_FAILED")


def _capture_status(screenshot: str, page_source: str) -> str:
    statuses = (screenshot, page_source)
    if statuses == ("PASS", "PASS"):
        return "COMPLETE"
    if "PASS" in statuses:
        return "PARTIAL"
    if "EVIDENCE_CAPTURE_TIMEOUT" in statuses or "EVIDENCE_CAPTURE_NOT_ATTEMPTED" in statuses:
        return "TIMEOUT"
    return "FAILED"


def capture_etb_failure_evidence(
    output_dir: str, stem: str = "etb_failure", timeout: float = 3.0
) -> str:
    """Capture screenshot and page source without changing the business failure."""
    evidence_dir = Path(resolve_private_evidence_dir(output_dir))
    try:
        application = _appium()._current_application()
    except Exception:  # pragma: no cover - Appium/session dependent
        screenshot = "EVIDENCE_CAPTURE_FAILED"
        source = "EVIDENCE_CAPTURE_FAILED"
    else:
        screenshot = _bounded_artifact_call(
            "screenshot",
            evidence_dir / f"{stem}.png",
            lambda pending: application.save_screenshot(str(pending)),
            timeout,
        )
        # Do not start a second driver request while a timed-out screenshot
        # worker may still be alive.  One in-flight Appium request is the
        # maximum this evidence path permits.
        if screenshot == "EVIDENCE_CAPTURE_TIMEOUT":
            source = "EVIDENCE_CAPTURE_NOT_ATTEMPTED"
        else:
            source = _bounded_artifact_call(
                "source",
                evidence_dir / f"{stem}.xml",
                lambda pending: pending.write_text(
                    _redact_source(str(application.page_source)), encoding="utf-8"
                ),
                timeout,
            )
    capture_status = _capture_status(screenshot, source)
    result = {
        "schema": "etb-evidence/v2",
        "artifact_classification": "PRIVATE_LOCAL",
        "operation_status": "COMPLETED",
        "capture_status": capture_status,
        "artifacts": {
            "screenshot": screenshot,
            "page_source": source,
        },
    }
    (evidence_dir / f"{stem}.json").write_text(
        json.dumps(result, sort_keys=True) + "\n", encoding="utf-8"
    )
    if capture_status != "COMPLETE":
        BuiltIn().log(f"ETB_EVIDENCE_CAPTURE_STATUS={capture_status}", level="WARN")
    return result


def capture_etb_device_terminal_evidence(
    output_dir: str, stem: str, serial: str
) -> str:
    """Capture foreground state when the app's hierarchy is no longer available."""
    evidence_dir = Path(resolve_private_evidence_dir(output_dir))
    try:
        result = subprocess.run(
            [resolve_adb_executable(), "-s", serial, "shell", "dumpsys", "window", "displays"],
            capture_output=True,
            text=True,
            timeout=10,
            check=False,
        )
        output = result.stdout or result.stderr or ""
        marker = "mCurrentFocus="
        foreground = next(
            (line.strip() for line in output.splitlines() if marker in line),
            "",
        )
        status = "PASS" if result.returncode == 0 and foreground else "FAILED"
    except (OSError, subprocess.TimeoutExpired):
        foreground = ""
        status = "FAILED"
    (evidence_dir / f"{stem}.foreground.txt").write_text(f"{foreground}\n", encoding="utf-8")
    payload = {
        "schema": "etb-evidence/v2",
        "artifact_classification": "PRIVATE_LOCAL",
        "operation_status": "COMPLETED",
        "capture_status": "COMPLETE" if status == "PASS" else "FAILED",
        "artifacts": {"foreground": status},
    }
    (evidence_dir / f"{stem}.json").write_text(
        json.dumps(payload, sort_keys=True) + "\n", encoding="utf-8"
    )
    return payload["capture_status"]
