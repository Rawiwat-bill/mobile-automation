"""Behavioral contract for sequential Android permission prompts.

Runs the production Robot permission keyword against an in-process synthetic
Permission Controller. No device, network, customer data, or banking logs are used.
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


def configure_permission_sequence(sequence, combined_locator, generic_locator, foreground_locator):
    prompts = [] if str(sequence).upper() == "NONE" else str(sequence).upper().split(",")
    _STATE.clear()
    _STATE.update(
        prompts=prompts,
        combined=combined_locator,
        generic=generic_locator,
        foreground=foreground_locator,
        clicks=[],
        activations=0,
    )


def _current():
    return _STATE["prompts"][0] if _STATE["prompts"] else "NONE"


def mock_visible(locator):
    current = _current()
    if locator == _STATE["combined"]:
        if current == "NONE":
            raise AssertionError("PERMISSION_MOCK_NOT_VISIBLE")
        return
    if locator == _STATE["generic"]:
        if current not in {"GENERIC", "GENERIC_STUCK"}:
            raise AssertionError("PERMISSION_MOCK_NOT_VISIBLE")
        return
    if locator == _STATE["foreground"]:
        if current != "FOREGROUND":
            raise AssertionError("PERMISSION_MOCK_NOT_VISIBLE")
        return
    raise AssertionError("PERMISSION_MOCK_UNEXPECTED_LOCATOR")


def mock_click(locator):
    current = _current()
    expected = {
        "GENERIC": _STATE["generic"],
        "GENERIC_STUCK": _STATE["generic"],
        "FOREGROUND": _STATE["foreground"],
    }.get(current)
    if expected is None or locator != expected:
        raise AssertionError("PERMISSION_MOCK_WRONG_CLICK")
    _STATE["clicks"].append(current)
    if current != "GENERIC_STUCK":
        _STATE["prompts"].pop(0)


def mock_activity():
    if _current() == "NONE":
        return "com.bangkokbank.blue.MainActivity"
    return "com.android.permissioncontroller.permission.ui.GrantPermissionsActivity"


def mock_source():
    current = _current()
    if current in {"GENERIC", "GENERIC_STUCK"}:
        return (
            '<hierarchy><node package="com.google.android.permissioncontroller" '
            'resource-id="com.android.permissioncontroller:id/permission_allow_button" />'
            '</hierarchy>'
        )
    if current == "FOREGROUND":
        return (
            '<hierarchy><node package="com.google.android.permissioncontroller" '
            'resource-id="com.android.permissioncontroller:id/'
            'permission_allow_foreground_only_button" /></hierarchy>'
        )
    return '<hierarchy><node package="com.bangkokbank.blue.dev" resource-id="termsAndConditions" /></hierarchy>'


def mock_activate(package):
    if package != "com.bangkokbank.blue.dev":
        raise AssertionError("PERMISSION_MOCK_WRONG_PACKAGE")
    _STATE["activations"] += 1


def assert_permission_contract(expected_clicks, expected_activations, expected_remaining):
    expected = [] if str(expected_clicks).upper() == "NONE" else str(expected_clicks).upper().split(",")
    if _STATE["clicks"] != expected:
        raise AssertionError(
            f"PERMISSION_MOCK_CLICK_MISMATCH expected={expected} actual={_STATE['clicks']}"
        )
    if _STATE["activations"] != int(expected_activations):
        raise AssertionError("PERMISSION_MOCK_ACTIVATION_MISMATCH")
    if len(_STATE["prompts"]) != int(expected_remaining):
        raise AssertionError("PERMISSION_MOCK_REMAINING_PROMPT_MISMATCH")


def _suite_text():
    template = """*** Settings ***
Resource    __RESOURCE__
Library    __LIBRARY__    WITH NAME    PermMock

*** Variables ***
${APP_PACKAGE}    com.bangkokbank.blue.dev

*** Test Cases ***
Generic Then Foreground Are Handled Sequentially
    Configure Permission Sequence
    ...    GENERIC,FOREGROUND
    ...    ${ANDROID_PERMISSION_ALLOW_BUTTON}
    ...    ${ANDROID_PERMISSION_ALLOW_GENERIC_BUTTON}
    ...    ${ANDROID_PERMISSION_ALLOW_FOREGROUND_BUTTON}
    Allow Android Permission If Visible
    Assert Permission Contract    GENERIC,FOREGROUND    1    0

Single Foreground Prompt Is Handled
    Configure Permission Sequence
    ...    FOREGROUND
    ...    ${ANDROID_PERMISSION_ALLOW_BUTTON}
    ...    ${ANDROID_PERMISSION_ALLOW_GENERIC_BUTTON}
    ...    ${ANDROID_PERMISSION_ALLOW_FOREGROUND_BUTTON}
    Allow Android Permission If Visible
    Assert Permission Contract    FOREGROUND    1    0

No Prompt Is A No Op
    Configure Permission Sequence
    ...    NONE
    ...    ${ANDROID_PERMISSION_ALLOW_BUTTON}
    ...    ${ANDROID_PERMISSION_ALLOW_GENERIC_BUTTON}
    ...    ${ANDROID_PERMISSION_ALLOW_FOREGROUND_BUTTON}
    Allow Android Permission If Visible
    Assert Permission Contract    NONE    0    0

Stuck Prompt Fails Without Blind Reclick
    Configure Permission Sequence
    ...    GENERIC_STUCK
    ...    ${ANDROID_PERMISSION_ALLOW_BUTTON}
    ...    ${ANDROID_PERMISSION_ALLOW_GENERIC_BUTTON}
    ...    ${ANDROID_PERMISSION_ALLOW_FOREGROUND_BUTTON}
    Run Keyword And Expect Error
    ...    *PERMISSION_PROMPT_DID_NOT_ADVANCE*
    ...    Allow Android Permission If Visible
    Assert Permission Contract    GENERIC_STUCK    0    1

*** Keywords ***
Element Should Be Visible
    [Arguments]    ${locator}
    PermMock.Mock Visible    ${locator}

Wait Until Element Is Visible
    [Arguments]    ${locator}    ${timeout}
    PermMock.Mock Visible    ${locator}

Click Element
    [Arguments]    ${locator}
    PermMock.Mock Click    ${locator}

Get Activity
    ${value}=    PermMock.Mock Activity
    RETURN    ${value}

Get Source
    ${value}=    PermMock.Mock Source
    RETURN    ${value}

Activate Application
    [Arguments]    ${package}
    PermMock.Mock Activate    ${package}

Wait Until Keyword Succeeds
    [Arguments]    ${timeout}    ${interval}    ${keyword}    @{{args}}
    BuiltIn.Wait Until Keyword Succeeds    2x    0s    ${keyword}    @{{args}}
"""
    return template.replace(
        "__RESOURCE__",
        str(ROOT / "resources/app/app_keywords.resource"),
    ).replace(
        "__LIBRARY__",
        str(Path(__file__).resolve()),
    )


class PermissionSequenceTests(unittest.TestCase):
    def _run_suite(self, dryrun=False):
        with tempfile.TemporaryDirectory(prefix="bbl-permission-sequence-") as directory:
            suite = Path(directory) / "permission_sequence.robot"
            suite.write_text(_suite_text(), encoding="utf-8")
            stdout, stderr = io.StringIO(), io.StringIO()
            code = run(
                str(suite),
                outputdir=directory,
                log="NONE",
                report="NONE",
                console="none",
                stdout=stdout,
                stderr=stderr,
                dryrun=dryrun,
            )
            result = ExecutionResult(str(Path(directory) / "output.xml"))
            self.assertEqual(len(result.suite.tests), 4)
            for case in result.suite.tests:
                print("PERMISSION_SEQUENCE_" + case.name.upper().replace(" ", "_") + "=" + case.status)
            self.assertEqual(
                code,
                0,
                "Synthetic permission sequence contract failed: " + str(result.suite.statistics),
            )

    def test_permission_sequence_behavior(self):
        self._run_suite()

    def test_permission_sequence_dryrun(self):
        self._run_suite(dryrun=True)


if __name__ == "__main__":
    unittest.main(verbosity=2)
