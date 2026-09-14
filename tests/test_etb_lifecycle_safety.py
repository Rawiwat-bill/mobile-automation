from __future__ import annotations

import json
import os
import subprocess
import sys
import tempfile
import time
import unittest
from pathlib import Path
from unittest.mock import patch

from libraries import adb_device, failure_evidence

ROOT = Path(__file__).resolve().parents[1]


def _read(relative: str) -> str:
    return (ROOT / relative).read_text(encoding="utf-8")


def _keyword_block(text: str, name: str) -> str:
    lines = text.splitlines()
    try:
        start = lines.index(name)
    except ValueError as exc:
        raise AssertionError(f"keyword not found: {name}") from exc
    block = [lines[start]]
    for line in lines[start + 1 :]:
        if line and not line[0].isspace() and not line.startswith("#"):
            break
        block.append(line)
    return "\n".join(block)


class _FakeBuiltIn:
    def log(self, *_args, **_kwargs) -> None:
        return None


class _FakeApplication:
    def __init__(
        self,
        label: str,
        *,
        screenshot_delay: float = 0.0,
        source_delay: float = 0.0,
    ) -> None:
        self.label = label
        self.screenshot_delay = screenshot_delay
        self.source_delay = source_delay

    def save_screenshot(self, path: str) -> bool:
        time.sleep(self.screenshot_delay)
        Path(path).write_text(f"SCREENSHOT:{self.label}\n", encoding="utf-8")
        return True

    @property
    def page_source(self) -> str:
        time.sleep(self.source_delay)
        return (
            "<hierarchy>"
            f'<node resource-id="{self.label}" text="sensitive" />'
            "</hierarchy>"
        )


class _SequencedAppium:
    def __init__(self, applications: list[_FakeApplication]) -> None:
        self.applications = applications
        self.calls = 0

    def _current_application(self) -> _FakeApplication:
        index = min(self.calls, len(self.applications) - 1)
        self.calls += 1
        return self.applications[index]


class ETBLifecycleSafetyTests(unittest.TestCase):
    def test_timed_out_workers_never_publish_late_final_artifacts(self) -> None:
        with tempfile.TemporaryDirectory(prefix="etb-late-write-") as temp:
            app = _FakeApplication(
                "SESSION-TIMEOUT", screenshot_delay=0.08, source_delay=0.08
            )
            appium = _SequencedAppium([app])
            env = {"ETB_RUN_ID": "RUN-TIMEOUT", "ETB_CASE_ID": "TC-ETB-001"}
            with patch.dict(os.environ, env, clear=False), patch.object(
                failure_evidence, "_appium", return_value=appium
            ), patch.object(failure_evidence, "BuiltIn", return_value=_FakeBuiltIn()):
                result = failure_evidence.capture_etb_failure_evidence(
                    temp, "late", timeout=0.01
                )

            self.assertEqual(result, "PASS")
            evidence_dir = (
                Path(temp)
                / "evidence"
                / "RUN-TIMEOUT"
                / "TC-ETB-001"
                / "private_local"
            )
            metadata = json.loads((evidence_dir / "late.json").read_text(encoding="utf-8"))
            self.assertEqual(metadata["screenshot"], "EVIDENCE_CAPTURE_TIMEOUT")
            self.assertEqual(metadata["page_source"], "EVIDENCE_CAPTURE_TIMEOUT")

            time.sleep(0.18)
            self.assertFalse(
                (evidence_dir / "late.png").exists(),
                "timed-out screenshot worker published a final artifact after return",
            )
            self.assertFalse(
                (evidence_dir / "late.xml").exists(),
                "timed-out source worker published a final artifact after return",
            )
            self.assertEqual(
                list(evidence_dir.glob(".*.pending")),
                [],
                "timed-out evidence worker left pending artifacts behind",
            )

    def test_evidence_capture_pins_one_appium_session_before_workers(self) -> None:
        with tempfile.TemporaryDirectory(prefix="etb-session-pin-") as temp:
            first = _FakeApplication("SESSION-A")
            second = _FakeApplication("SESSION-B")
            appium = _SequencedAppium([first, second])
            env = {"ETB_RUN_ID": "RUN-PIN", "ETB_CASE_ID": "TC-ETB-001"}
            with patch.dict(os.environ, env, clear=False), patch.object(
                failure_evidence, "_appium", return_value=appium
            ), patch.object(failure_evidence, "BuiltIn", return_value=_FakeBuiltIn()):
                failure_evidence.capture_etb_failure_evidence(
                    temp, "pin", timeout=0.2
                )

            evidence_dir = (
                Path(temp) / "evidence" / "RUN-PIN" / "TC-ETB-001" / "private_local"
            )
            source = (evidence_dir / "pin.xml").read_text(encoding="utf-8")
            self.assertIn("SESSION-A", source)
            self.assertNotIn("SESSION-B", source)
            self.assertEqual(
                appium.calls,
                1,
                "evidence capture must resolve the current Appium session once per bundle",
            )

    def test_etb_regression_session_owner_is_per_test_setup_and_teardown(self) -> None:
        suite = _read("tests/android/etb/etb_regression.robot")
        keywords = _read("resources/keywords/etb/etb_regression_keywords.resource")

        self.assertIn("Suite Setup      Prepare ETB Regression Suite", suite)
        self.assertIn("Suite Teardown   No Operation", suite)
        self.assertIn("Test Setup       Reset ETB Regression Application", suite)
        self.assertIn("Test Teardown    Finalize ETB Regression Test", suite)

        prepare = _keyword_block(keywords, "Prepare ETB Regression Suite")
        reset = _keyword_block(keywords, "Reset ETB Regression Application")

        self.assertNotIn("Open Mobile Application", prepare)
        self.assertNotIn("Close Application", prepare)
        self.assertIn("Open Mobile Application", reset)

    def test_robot_runs_test_teardown_after_test_setup_failure(self) -> None:
        with tempfile.TemporaryDirectory(prefix="etb-setup-failure-") as temp:
            temp_path = Path(temp)
            marker = temp_path / "lifecycle.marker"
            suite = temp_path / "setup_failure.robot"
            output_dir = temp_path / "robot-output"
            suite.write_text(
                """*** Settings ***
Library          OperatingSystem
Test Setup       Setup Opens Then Fails
Test Teardown    Teardown Marker

*** Test Cases ***
Setup Failure Still Tears Down
    Append To File    ${MARKER}    BODY_RAN|

*** Keywords ***
Setup Opens Then Fails
    Append To File    ${MARKER}    SETUP_STARTED|
    Fail    SETUP_FAILED

Teardown Marker
    Append To File    ${MARKER}    TEARDOWN_RAN|
""",
                encoding="utf-8",
            )
            completed = subprocess.run(
                [
                    sys.executable,
                    "-m",
                    "robot",
                    "--console",
                    "none",
                    "--outputdir",
                    str(output_dir),
                    "--variable",
                    f"MARKER:{marker}",
                    str(suite),
                ],
                cwd=ROOT,
                capture_output=True,
                text=True,
                timeout=20,
                check=False,
            )

            self.assertNotEqual(
                completed.returncode,
                0,
                "synthetic setup failure must remain a Robot failure",
            )
            self.assertEqual(
                marker.read_text(encoding="utf-8"),
                "SETUP_STARTED|TEARDOWN_RAN|",
                "Robot must run Test Teardown after Test Setup fails, without running the body",
            )

    def test_etb_teardown_always_purges_and_remains_fail_closed(self) -> None:
        suite = _read("tests/android/etb/etb_regression.robot")
        lifecycle = _read("resources/keywords/etb/etb_session_lifecycle.resource")
        finalize = _keyword_block(lifecycle, "Finalize ETB Regression Test")

        self.assertIn("Test Teardown    Finalize ETB Regression Test", suite)
        self.assertIn("Force Stop Android Application", finalize)
        self.assertIn(
            "Run Keyword And Ignore Error    Close Application",
            finalize,
        )
        self.assertIn(
            "Run Keyword And Return Status    Close All Applications",
            finalize,
        )
        self.assertIn("SESSION_CLOSE_FAILED", finalize)
        self.assertLess(
            finalize.index("Close All Applications"),
            finalize.rindex("Fail    SESSION_CLOSE_FAILED"),
            "cache purge must occur before reporting a genuine close failure",
        )

    def test_finalize_treats_no_open_app_as_no_session_not_close_failure(self) -> None:
        lifecycle = _read("resources/keywords/etb/etb_session_lifecycle.resource")
        finalize = _keyword_block(lifecycle, "Finalize ETB Regression Test")

        self.assertIn("No application is open", finalize)
        self.assertIn("APPIUM_SESSION_CLOSE=NOT_REQUIRED", finalize)
        self.assertIn("APPIUM_SESSION_CLOSE=PASS", finalize)
        self.assertIn("${close_failed}=    Set Variable    ${TRUE}", finalize)

    def test_startup_observer_uses_evidence_scope_resolver_contract(self) -> None:
        source = _read("libraries/adb_device.py")
        self.assertIn("evidence_dir = Path(", source)
        self.assertIn(
            "resolve_private_evidence_dir(output_dir, case_id=_current_case_id())",
            source,
        )
        self.assertNotIn("create=True", source)

    def test_startup_error_marker_is_safe_specific_and_persisted(self) -> None:
        self.assertEqual(
            adb_device._classify_startup_error_marker('<node text="AJI-001"/>'),
            "AJI-001",
        )
        self.assertEqual(
            adb_device._classify_startup_error_marker('<node text="RGI-104"/>'),
            "RGI-104",
        )
        self.assertEqual(
            adb_device._classify_startup_error_marker(
                '<node text="Please try again later"/>'
            ),
            "GENERIC_SERVICE_ERROR",
        )
        self.assertEqual(
            adb_device._classify_startup_error_marker('<node text="Close app"/>'),
            "GENERIC_CLOSE_APP_ERROR",
        )
        self.assertEqual(
            adb_device._classify_startup_error_marker(
                '<node text="The app requires newer operating system"/>'
            ),
            "UNSUPPORTED_OS",
        )
        self.assertEqual(
            adb_device._classify_startup_error_marker('<node text="customer-secret"/>'),
            "",
        )

        source = _read("libraries/adb_device.py")
        self.assertIn('"startup_error_marker": error_marker', source)
        self.assertIn("marker={error_marker or 'NONE'}", source)


if __name__ == "__main__":
    unittest.main(verbosity=2)
