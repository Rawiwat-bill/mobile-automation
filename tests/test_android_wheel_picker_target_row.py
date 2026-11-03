"""Regression checks for the production wheel target-row branch."""
from __future__ import annotations

import io
import tempfile
import unittest
from pathlib import Path

from robot import run
from robot.api import ExecutionResult, get_resource_model


ROOT = Path(__file__).resolve().parents[1]
WHEEL = ROOT / "resources/keywords/android_wheel_picker.resource"


def keyword_body(path: Path, name: str) -> str:
    text = path.read_text(encoding="utf-8")
    model = get_resource_model(str(path))
    node = next(
        node
        for section in model.sections
        for node in getattr(section, "body", [])
        if node.__class__.__name__ == "Keyword" and node.name == name
    )
    return "".join(text.splitlines(keepends=True)[node.lineno - 1 : node.end_lineno])


class WheelTargetRowTests(unittest.TestCase):
    def test_visible_distance_two_row_is_used_and_out_of_bounds_is_rejected(self) -> None:
        body = keyword_body(WHEEL, "Select Android Wheel Picker Value")
        with tempfile.TemporaryDirectory(prefix="etb-wheel-target-row-") as temp:
            root = Path(temp)
            resource = root / "wheel.resource"
            resource.write_text(
                """*** Settings ***
Library    Collections

*** Variables ***
${ANDROID_WHEEL_TIMEOUT}    1s
${DOB_PICKER_MAX_SECONDS}    5
${DOB_PICKER_NO_PROGRESS_LIMIT}    2
${DOB_COARSE_END_RATIO}    0.30
${DOB_COARSE_START_RATIO}    0.70
${DOB_DRAG_DURATION}    1
&{MONTH_INDEXES}    January=1    February=2    March=3    April=4    May=5    June=6    July=7    August=8    September=9    October=10    November=11    December=12

*** Keywords ***
"""
                + body
                + """
Read Android Wheel Picker Value
    [Arguments]    ${locator}
    RETURN    ${CURRENT}

Android Wheel Picker Value Should Be
    [Arguments]    ${locator}    ${target}    ${kind}
    ${current}=    Read Android Wheel Picker Value    ${locator}
    IF    '${kind}' == 'month'
        Should Be Equal As Strings    ${current}    ${target}
    ELSE
        Should Be Equal As Integers    ${current}    ${target}
    END

Android Wheel Picker Value Should Change From
    [Arguments]    ${locator}    ${previous}    ${kind}
    ${current}=    Read Android Wheel Picker Value    ${locator}
    Should Not Be Equal As Strings    ${current}    ${previous}
    RETURN    ${current}

Record DOB Picker Attempt
    [Arguments]    @{ignored}
    No Operation

Record DOB Failure
    [Arguments]    @{ignored}
    No Operation

Wait Until Element Is Visible
    [Arguments]    ${locator}    ${timeout}
    IF    '${locator}' == 'TARGET_ROW' and ${ROW_ABSENT}
        Fail    SYNTHETIC_ROW_ABSENT
    END
    No Operation

Get WebElements
    [Arguments]    ${locator}
    IF    '${locator}' == 'TARGET_ROW' and ${ROW_AMBIGUOUS}
        ${items}=    Create List    first    second
        RETURN    ${items}
    END
    ${items}=    Create List    one
    RETURN    ${items}

Get Element Rect
    [Arguments]    ${locator}
    IF    '${locator}' == 'TARGET_ROW'
        ${y}=    Set Variable If    ${ROW_OUTSIDE}    800    1300
        ${target}=    Evaluate    {'x': 700, 'y': int($y), 'width': 300, 'height': 100}
        RETURN    ${target}
    END
    RETURN    ${PICKER_RECT}

Tap
    [Arguments]    ${point}
    ${count}=    Evaluate    int($TAPS) + 1
    Set Test Variable    ${TAPS}    ${count}
    Set Test Variable    ${CURRENT}    2000

Execute Adb Shell
    [Arguments]    @{ignored}
    Fail    SYNTHETIC_SWIPE_PATH

Reset State
    Set Test Variable    ${CURRENT}    2002
    ${zero}=    Evaluate    0
    Set Test Variable    ${TAPS}    ${zero}
    Set Test Variable    ${ROW_OUTSIDE}    ${False}
    Set Test Variable    ${ROW_ABSENT}    ${False}
    Set Test Variable    ${ROW_AMBIGUOUS}    ${False}
    ${picker}=    Evaluate    {'x': 700, 'y': 1000, 'width': 300, 'height': 800}
    ${target}=    Evaluate    {'x': 700, 'y': 1300, 'width': 300, 'height': 100}
    Set Test Variable    ${PICKER_RECT}    ${picker}
    Set Test Variable    ${TARGET_RECT}    ${target}
""",
                encoding="utf-8",
            )
            suite = root / "wheel.robot"
            suite.write_text(
                """*** Settings ***
Resource    wheel.resource
Test Setup    Reset State

*** Test Cases ***
Distance Two Visible Row Is Tapped
    Select Android Wheel Picker Value    WHEEL    2000    number    TARGET_ROW
    Should Be Equal As Integers    ${TAPS}    1

Out Of Bounds Row Falls Back Without Tapping
    Set Test Variable    ${ROW_OUTSIDE}    ${True}
    Run Keyword And Expect Error    SYNTHETIC_SWIPE_PATH    Select Android Wheel Picker Value    WHEEL    2000    number    TARGET_ROW
    Should Be Equal As Integers    ${TAPS}    0

Absent Row Falls Back Without Tapping
    Set Test Variable    ${ROW_ABSENT}    ${True}
    Run Keyword And Expect Error    SYNTHETIC_SWIPE_PATH    Select Android Wheel Picker Value    WHEEL    2000    number    TARGET_ROW
    Should Be Equal As Integers    ${TAPS}    0

Ambiguous Row Falls Back Without Tapping
    Set Test Variable    ${ROW_AMBIGUOUS}    ${True}
    Run Keyword And Expect Error    SYNTHETIC_SWIPE_PATH    Select Android Wheel Picker Value    WHEEL    2000    number    TARGET_ROW
    Should Be Equal As Integers    ${TAPS}    0
""",
                encoding="utf-8",
            )
            exit_code = run(
                str(suite),
                outputdir=temp,
                log="NONE",
                report="NONE",
                console="none",
                stdout=io.StringIO(),
                stderr=io.StringIO(),
            )
            result = ExecutionResult(str(root / "output.xml"))
            self.assertEqual(exit_code, 0, [test.message for test in result.suite.tests])


if __name__ == "__main__":
    unittest.main(verbosity=2)
