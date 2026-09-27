from __future__ import annotations

import hashlib
import io
import subprocess
import tempfile
import unittest
from pathlib import Path
from unittest.mock import Mock, patch

from robot import run
from robot.api import ExecutionResult

from libraries import adb_device

ROOT=Path(__file__).resolve().parents[1]
_TERMS_STATE = {}


def configure_terms(*states):
    _TERMS_STATE.clear()
    _TERMS_STATE.update(states=list(states), source_calls=0, back_count=0, navigation_count=0)


def mock_get_source():
    _TERMS_STATE["source_calls"] += 1
    if not _TERMS_STATE["states"]:
        raise AssertionError("TERMS_MOCK_SOURCE_EXHAUSTED")
    state = _TERMS_STATE["states"].pop(0)
    if state == "ERROR":
        raise AssertionError("SYNTHETIC_APPIUM_SOURCE_ERROR")
    if state == "BLANK":
        return '<hierarchy><android.webkit.WebView/><android.widget.Button text="Accept"/></hierarchy>'
    if state == "LOADED":
        return '<hierarchy><android.webkit.WebView><android.widget.TextView text="Definitions"/></android.webkit.WebView><android.widget.Button text="Accept"/></hierarchy>'
    raise AssertionError("TERMS_MOCK_UNKNOWN_STATE")


def mock_terms_back():
    _TERMS_STATE["back_count"] += 1


def mock_terms_navigation():
    _TERMS_STATE["navigation_count"] += 1


def assert_terms_calls(source_calls, back_count, navigation_count):
    actual = (
        _TERMS_STATE["source_calls"],
        _TERMS_STATE["back_count"],
        _TERMS_STATE["navigation_count"],
    )
    expected = tuple(map(int, (source_calls, back_count, navigation_count)))
    if actual != expected:
        raise AssertionError(f"TERMS_MOCK_CALLS expected={expected} actual={actual}")


def _terms_behavior_suite():
    return '''*** Settings ***
Resource    {page}
Resource    {common}
Library    {library}    WITH NAME    TermsMock

*** Variables ***
${{TERMS_CONTENT_READY_POLL_INTERVAL}}    0s

*** Test Cases ***
Content Loaded Before Bottom Is Ready
    Configure Terms    LOADED
    Wait Until Terms Content Is Ready
    Assert Terms Calls    1    0    0

Slow Content Load Is Bounded
    Configure Terms    BLANK    LOADED
    Wait Until Terms Content Is Ready
    Assert Terms Calls    2    0    0

Blank Content Fails Closed
    Configure Terms    BLANK    BLANK    BLANK
    Run Keyword And Expect Error    *TERMS_CONTENT_NOT_RENDERED*    Wait Until Terms Content Is Ready
    Assert Terms Calls    3    0    0

Recovery Stops After First Success
    Configure Terms    BLANK    BLANK    BLANK    LOADED
    Ensure Terms Content Ready With Interim Navigation Retries
    Assert Terms Calls    4    1    1

Appium Source Error Fails Without Navigation
    Configure Terms    ERROR
    Run Keyword And Expect Error    *TERMS_SOURCE_READ_FAILED*    Ensure Terms Content Ready With Interim Navigation Retries
    Assert Terms Calls    1    0    0

*** Keywords ***
Get Source
    ${{source}}=    TermsMock.Mock Get Source
    RETURN    ${{source}}

Tap Terms Back Button For Recovery
    TermsMock.Mock Terms Back

Wait Until Landing Screen Is Displayed
    No Operation

Advance Landing To Terms Destination
    [Arguments]    ${{recovery_mode}}=${{FALSE}}
    TermsMock.Mock Terms Navigation

Sleep
    [Arguments]    ${{duration}}
    No Operation
'''.format(
        page=ROOT / "resources/pages/common_onboarding/terms_and_conditions_page.resource",
        common=ROOT / "resources/keywords/common_onboarding.resource",
        library=Path(__file__).resolve(),
    )


class ConsentScrollStateTests(unittest.TestCase):
    def test_terms_behavioral_regressions(self):
        with tempfile.TemporaryDirectory(prefix="bbl-terms-contract-") as directory:
            suite = Path(directory) / "terms.robot"
            suite.write_text(_terms_behavior_suite(), encoding="utf-8")
            stdout, stderr = io.StringIO(), io.StringIO()
            code = run(
                str(suite),
                outputdir=directory,
                log="NONE",
                report="NONE",
                console="none",
                stdout=stdout,
                stderr=stderr,
            )
            result = ExecutionResult(str(Path(directory) / "output.xml"))
            self.assertEqual(len(result.suite.tests), 5)
            self.assertEqual(code, 0, str(result.suite.statistics))

    def test_screenshot_hash_uses_canonical_adb_and_binary_screencap(self):
        payload=b"synthetic-png-bytes"
        completed=subprocess.CompletedProcess([], 0, stdout=payload, stderr=b'')
        with patch.object(adb_device, "resolve_adb_executable", return_value="/synthetic/adb"), patch.object(adb_device.subprocess, "run", return_value=completed) as run:
            result=adb_device.get_android_screenshot_hash("emulator-5556")
        self.assertEqual(result, hashlib.sha256(payload).hexdigest()[:16])
        args,kwargs=run.call_args
        self.assertEqual(args[0], ["/synthetic/adb","-s","emulator-5556","exec-out","screencap","-p"])
        self.assertTrue(kwargs["capture_output"])
        self.assertEqual(kwargs["timeout"], 10)

    def test_screenshot_hash_failure_is_sanitized(self):
        completed=subprocess.CompletedProcess([], 1, stdout=b'', stderr=b'sensitive-detail')
        with patch.object(adb_device, "resolve_adb_executable", return_value="/synthetic/adb"), patch.object(adb_device.subprocess, "run", return_value=completed):
            with self.assertRaisesRegex(AssertionError, '^ADB_SCREENSHOT_HASH_FAILED$'):
                adb_device.get_android_screenshot_hash("emulator-5556")

    def test_consent_scroll_uses_visual_progress_not_appium_source_hash_for_stall(self):
        source=(ROOT/"resources/keywords/scroll_keywords.resource").read_text(encoding="utf-8")
        block=source.split("Scroll Down Consent Terms With Big Fling",1)[1]
        self.assertIn("Get Android Screenshot Hash    ${DEVICE_UDID}", block)
        self.assertIn("${visual_progress_observed}=    Set Variable    ${TRUE}", block)
        self.assertIn("bottom_state=VISUAL_NO_CHANGE_AFTER_PROGRESS", block)
        self.assertIn("Fail    CONSENT_SCROLL_STALLED", block)
        self.assertNotIn("hashlib.sha256($source.encode())", block)
        self.assertLess(block.index("${visual_progress_observed}=    Set Variable    ${TRUE}"), block.index("bottom_state=VISUAL_NO_CHANGE_AFTER_PROGRESS"))

    def test_terms_content_readiness_requires_hydrated_agreement_content(self):
        terms=(ROOT/"resources/pages/common_onboarding/terms_and_conditions_page.resource").read_text(encoding="utf-8")
        block=terms.split("Terms Content Should Be Ready",1)[1].split("\nWait Until Terms Content Is Ready\n",1)[0]
        wait_block=terms.split("Wait Until Terms Content Is Ready",1)[1].split("\nTap Terms Back Button For Recovery\n",1)[0]
        self.assertIn("Run Keyword And Ignore Error    Get Source", block)
        self.assertIn("Terms Content Loaded From Source", block)
        self.assertIn("TERMS_SOURCE_READ_FAILED", block)
        self.assertIn("TERMS_CONTENT_NOT_RENDERED", block)
        self.assertNotIn("I have read and understood", block)
        self.assertNotIn("${CONSENT_THAI_ACKNOWLEDGEMENT_MARKER}", block)
        self.assertIn("${TERMS_CONTENT_READY_MAX_READS}             3", terms)
        self.assertIn("${TERMS_CONTENT_READY_RANGE_END}             4", terms)
        self.assertIn("Sleep    ${TERMS_CONTENT_READY_POLL_INTERVAL}", wait_block)
        self.assertIn("Terms Content Should Be Ready", wait_block)
        self.assertIn("IF    '${error}' == 'TERMS_SOURCE_READ_FAILED'", wait_block)
        self.assertIn("Tap Terms Back Button For Recovery", terms)
        self.assertIn("${TERMS_CONTENT_RECOVERY_MAX_ATTEMPTS}    10", terms)
        self.assertIn("${TERMS_CONTENT_RECOVERY_RANGE_END}       11", terms)
        self.assertIn("${TERMS_CONTENT_RECOVERY_LANDING_PAUSE}   2s", terms)

    def test_adb_terms_readiness_requires_content_and_accept(self):
        english='<node text="I have read and understood"/><node text="Accept"/>'
        thai='<node text="ข้าพเจ้าได้อ่านและทำความเข้าใจกับข้อตกลงการใช้บริการ"/><node content-desc="ยอมรับ"/>'
        blank='<node text="Terms and Conditions"/><node text="Accept"/>'
        with patch.object(adb_device, "_dump_source", side_effect=[english, thai, blank]):
            self.assertTrue(adb_device.terms_content_ready_via_adb("emulator-5556"))
            self.assertTrue(adb_device.terms_content_ready_via_adb("emulator-5556"))
            self.assertFalse(adb_device.terms_content_ready_via_adb("emulator-5556"))

    def test_consent_scroll_uses_bounded_appium_acknowledgement_reads(self):
        source=(ROOT/"resources/keywords/scroll_keywords.resource").read_text(encoding="utf-8")
        block=source.split("Scroll Down Consent Terms With Big Fling",1)[1]
        self.assertEqual(block.count("${source}=    Get Source"), 2)
        self.assertEqual(block.count("Should Contain Any    ${source}"), 2)
        self.assertNotIn("Consent Acknowledgement Present Via Adb", block)

    def test_common_onboarding_uses_bounded_interim_terms_retries_before_scroll(self):
        common=(ROOT/"resources/keywords/common_onboarding.resource").read_text(encoding="utf-8")
        landing=(ROOT/"resources/pages/common_onboarding/landing_screen_page.resource").read_text(encoding="utf-8")
        self.assertLess(
            common.index("    Ensure Terms Content Ready With Interim Navigation Retries"),
            common.index("    Scroll Down Terms And Conditions"),
        )
        self.assertEqual(common.count("Resolve Optional App Update Or Destination"), 1)
        advance=common.rsplit("\nAdvance Landing To Terms Destination\n",1)[1].split(
            "\nEnsure Terms Content Ready With Interim Navigation Retries\n",1
        )[0]
        self.assertIn("[Arguments]    ${recovery_mode}=${FALSE}", advance)
        self.assertEqual(advance.count("Resolve Optional App Update Or Destination"), 1)
        self.assertEqual(advance.count("Wait For Landing Destination"), 1)
        self.assertIn("IF    ${recovery_mode}", advance)
        self.assertIn("Tap Landing Ready Button For Destination Race", advance)
        self.assertIn("ELSE\n        Tap Landing Ready Button", advance)
        self.assertIn("LANDING_READY_REAPPEARED_AFTER_PERMISSION=TRUE", advance)
        self.assertLess(
            advance.index("Allow Android Permission If Visible"),
            advance.index("LANDING_READY_REAPPEARED_AFTER_PERMISSION=TRUE"),
        )
        self.assertLess(
            advance.index("LANDING_READY_REAPPEARED_AFTER_PERMISSION=TRUE"),
            advance.index("Resolve Optional App Update Or Destination"),
        )

        recovery=common.rsplit("\nEnsure Terms Content Ready With Interim Navigation Retries\n",1)[1]
        self.assertIn("FOR    ${attempt}    IN RANGE    1    ${TERMS_CONTENT_RECOVERY_RANGE_END}", recovery)
        self.assertNotIn("${TERMS_CONTENT_RECOVERY_MAX_ATTEMPTS + 1}", recovery)
        self.assertEqual(recovery.count("Tap Terms Back Button For Recovery"), 1)
        self.assertEqual(recovery.count("Run Keyword And Ignore Error    Wait Until Terms Content Is Ready"), 2)
        self.assertEqual(recovery.count("IF    '${error}' != 'TERMS_CONTENT_NOT_RENDERED'"), 2)
        self.assertIn("Sleep    ${TERMS_CONTENT_RECOVERY_LANDING_PAUSE}", recovery)
        self.assertLess(
            recovery.index("Sleep    ${TERMS_CONTENT_RECOVERY_LANDING_PAUSE}"),
            recovery.index("Advance Landing To Terms Destination    recovery_mode=${TRUE}"),
        )
        self.assertIn("Advance Landing To Terms Destination    recovery_mode=${TRUE}", recovery)
        self.assertIn("TERMS_CONTENT_READY=RECOVERED attempt=${attempt}", recovery)
        self.assertIn("TERMS_CONTENT_NOT_RENDERED_AFTER_${TERMS_CONTENT_RECOVERY_MAX_ATTEMPTS}_RECOVERY_ATTEMPTS", recovery)
        self.assertNotIn("Resolve Optional App Update Or Destination", recovery)
        self.assertLess(
            recovery.index("Tap Terms Back Button For Recovery"),
            recovery.index("Advance Landing To Terms Destination"),
        )

        recovery_tap=landing.rsplit("\nTap Landing Ready Button For Destination Race\n",1)[1].split(
            "\nLanding Ready Should Replace Skip\n",1
        )[0]
        self.assertIn("Get Fresh Landing Element Rect    ${LANDING_READY_BUTTON}", recovery_tap)
        self.assertIn("LANDING_RECOVERY_READY_ALREADY_GONE=TRUE", recovery_tap)
        self.assertIn("recovery=DESTINATION_RACE", recovery_tap)
        self.assertNotIn("Click Element    ${LANDING_READY_BUTTON}", recovery_tap)
        self.assertNotIn("Landing Action Should Be Gone", recovery_tap)


if __name__=="__main__":
    unittest.main(verbosity=2)
