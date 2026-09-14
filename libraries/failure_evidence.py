"""Best-effort, independently bounded failure evidence for Robot tests."""

from __future__ import annotations

import json
import re
import threading
import uuid
from pathlib import Path
from typing import Any, cast

from robot.libraries.BuiltIn import BuiltIn

from libraries.evidence_scope import resolve_private_evidence_dir

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
        source = _bounded_artifact_call(
            "source",
            evidence_dir / f"{stem}.xml",
            lambda pending: pending.write_text(
                _redact_source(str(application.page_source)), encoding="utf-8"
            ),
            timeout,
        )
    result = {
        "artifact_classification": "PRIVATE_LOCAL",
        "screenshot": screenshot,
        "page_source": source,
    }
    (evidence_dir / f"{stem}.json").write_text(
        json.dumps(result, sort_keys=True) + "\n", encoding="utf-8"
    )
    if "EVIDENCE_CAPTURE_TIMEOUT" in (screenshot, source):
        BuiltIn().log("EVIDENCE_CAPTURE_TIMEOUT", level="WARN")
    return "PASS"
