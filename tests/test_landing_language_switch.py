"""Behavioral regression for DEV landing-language selection.

Exercises the production Robot keyword with a synthetic Appium/ADB boundary.
No device, backend, profile data, or banking logs are accessed.
"""
from __future__ import annotations

import io
import tempfile
import unittest
from pathlib import Path

from robot import run
from robot.api import ExecutionResult

ROOT = Path(__file__).resolve().parents[1]
_STATE = {}


def configure_language(language, switch_locator, skip_locator):
    _STATE.clear()
    _STATE.update(
        language=str(language).upper(),
        switch_locator=switch_locator,
        skip_locator=skip_locator,
        taps=0,
    )


def mock_visible(locator):
    if locator not in {_STATE["switch_locator"], _STATE["skip_locator"]}:
        raise AssertionError("LANGUAGE_MOCK_UNEXPECTED_LOCATOR")


def mock_attribute(locator, attribute):
    if attribute != "content-desc":
        raise AssertionError("LANGUAGE_MOCK_UNEXPECTED_ATTRIBUTE")
    if locator == _STATE["switch_locator"]:
        return "accessibility.language_switch_accessibility_label"
    if locator == _STATE["skip_locator"]:
        return "Skip" if _STATE["language"] == "ENGLISH" else "ข้าม"
    raise AssertionError("LANGUAGE_MOCK_UNEXPECTED_LOCATOR")


def mock_rect(locator):
    if locator != _STATE["switch_locator"]:
        raise AssertionError("LANGUAGE_MOCK_UNEXPECTED_RECT")
    return {"x": 862, "y": 148, "width": 159, "height": 87}


def mock_adb(*args):
    if len(args) != 4 or args[:2] != ("input", "tap"):
        raise AssertionError("LANGUAGE_MOCK_UNEXPECTED_ADB_COMMAND")
    rect = mock_rect(_STATE["switch_locator"])
    expected = (
        int(rect["x"] + rect["width"] / 2),
        int(rect["y"] + rect["height"] / 2),
    )
    if tuple(map(int, args[2:])) != expected:
        raise AssertionError("LANGUAGE_MOCK_WRONG_TAP_BOUNDS")
    _STATE["taps"] += 1
    _STATE["language"] = "THAI" if _STATE["language"] == "ENGLISH" else "ENGLISH"


def assert_language_contract(expected_language, expected_taps):
    if _STATE["language"] != str(expected_language).upper():
        raise AssertionError("LANGUAGE_MOCK_WRONG_STATE")
    if _STATE["taps"] != int(expected_taps):
        raise AssertionError("LANGUAGE_MOCK_WRONG_TAP_COUNT")


def _suite_text():
    return """*** Settings ***
Resource    __RESOURCE__
Library    __LIBRARY__    WITH NAME    LangMock

*** Variables ***
${APP_PACKAGE}    com.bangkokbank.blue.dev

*** Test Cases ***
Already English Must Not Toggle
    Configure Language    ENGLISH    ${LANDING_LANGUAGE_SWITCH}    ${LANDING_SKIP_BUTTON}
    Switch Landing Language To English
    Assert Language Contract    ENGLISH    0

Thai Must Toggle Exactly Once To English
    Configure Language    THAI    ${LANDING_LANGUAGE_SWITCH}    ${LANDING_SKIP_BUTTON}
    Switch Landing Language To English
    Assert Language Contract    ENGLISH    1

*** Keywords ***
Element Should Be Visible
    [Arguments]    ${locator}
    LangMock.Mock Visible    ${locator}

Wait Until Element Is Visible
    [Arguments]    ${locator}    ${timeout}
    LangMock.Mock Visible    ${locator}

Get Element Attribute
    [Arguments]    ${locator}    ${attribute}
    ${value}=    LangMock.Mock Attribute    ${locator}    ${attribute}
    RETURN    ${value}

Get Element Rect
    [Arguments]    ${locator}
    ${rect}=    LangMock.Mock Rect    ${locator}
    RETURN    ${rect}

Execute Adb Shell
    [Arguments]    @{args}
    LangMock.Mock Adb    @{args}

Wait Until Keyword Succeeds
    [Arguments]    ${timeout}    ${interval}    ${keyword}    @{args}
    Should Be Equal    ${timeout}    10s
    Should Be Equal    ${interval}    500ms
    BuiltIn.Wait Until Keyword Succeeds    2x    0s    ${keyword}    @{args}
""".replace(
        "__RESOURCE__",
        str(ROOT / "resources/pages/common_onboarding/landing_screen_page.resource"),
    ).replace(
        "__LIBRARY__",
        str(Path(__file__).resolve()),
    )


class LandingLanguageSwitchTests(unittest.TestCase):
    def _run_suite(self, dryrun=False):
        with tempfile.TemporaryDirectory(prefix="bbl-landing-language-") as directory:
            suite = Path(directory) / "landing_language.robot"
            suite.write_text(_suite_text(), encoding="utf-8")
            stdout, stderr = io.StringIO(), io.StringIO()
            code = run(
                str(suite), outputdir=directory, log="NONE", report="NONE",
                console="none", stdout=stdout, stderr=stderr, dryrun=dryrun,
            )
            result = ExecutionResult(str(Path(directory) / "output.xml"))
            self.assertEqual(len(result.suite.tests), 2)
            for case in result.suite.tests:
                print("LANDING_LANGUAGE_" + case.name.upper().replace(" ", "_") + "=" + case.status)
            self.assertEqual(code, 0, "Synthetic landing-language contract failed: " + str(result.suite.statistics))

    def test_landing_language_behavior(self):
        self._run_suite()

    def test_landing_language_dryrun(self):
        self._run_suite(dryrun=True)


if __name__ == "__main__":
    unittest.main(verbosity=2)
