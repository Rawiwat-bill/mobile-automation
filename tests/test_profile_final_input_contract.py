"""Protect the final visible profile-field read before Profile Next."""
from __future__ import annotations

import io
import tempfile
import unittest
from pathlib import Path

from robot import run
from robot.api import ExecutionResult, get_resource_model

ROOT = Path(__file__).resolve().parents[1]
RESOURCE = ROOT / "resources/pages/onboarding/profile_fields.resource"


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


class ProfileFinalInputContractTests(unittest.TestCase):
    def test_final_visible_values_are_read_after_blur(self) -> None:
        body = "\n".join(
            keyword_body(RESOURCE, name)
            for name in (
                "Normalize Digits",
                "Verify Field Value",
                "Read Current Profile Field Value",
                "Verify Current Profile Fields Before Next",
            )
        )
        with tempfile.TemporaryDirectory(prefix="etb-profile-final-input-") as temp:
            root = Path(temp)
            resource = root / "profile_final_input.resource"
            resource.write_text(
                """*** Settings ***
Library    AppiumLibrary
Library    String

*** Variables ***
${PROFILE_TIMEOUT}    1s
${PROFILE_CITIZEN_ID_INPUT}    CID
${PROFILE_MOBILE_NUMBER_INPUT}    MOBILE
${PROFILE_DOB_INPUT}    DOB
${PROFILE_TITLE_TEXT}    PROFILE_TITLE

*** Keywords ***
Wait Until Profile Screen Is Displayed
    No Operation

Wait Until Profile Fields Are Blurred
    No Operation

Wait Until Element Is Visible
    [Arguments]    ${locator}    ${timeout}
    No Operation

Get Text
    [Arguments]    ${locator}
    IF    '${locator}' == 'CID'
        RETURN    3100000000001
    ELSE IF    '${locator}' == 'MOBILE'
        RETURN    ${EMPTY}
    END
    RETURN    09/11/1996

Get Element Attribute
    [Arguments]    ${locator}    ${attribute}
    IF    '${locator}' == 'MOBILE' and '${attribute}' == 'value'
        RETURN    098-973-7491
    END
    RETURN    false

Verify DOB Field Value
    [Arguments]    ${day}    ${month}    ${year}
    Should Be Equal As Strings    ${day}    09
    Should Be Equal As Strings    ${month}    11
    Should Be Equal As Strings    ${year}    1996

"""
                + body,
                encoding="utf-8",
            )
            suite = root / "profile_final_input.robot"
            suite.write_text(
                """*** Settings ***
Resource    profile_final_input.resource

*** Test Cases ***
Final values use visible text and value fallback
    Verify Current Profile Fields Before Next    3100000000001    09-11-1996    098-973-7491

Mismatched final mobile is rejected
    Run Keyword And Expect Error    *Mobile value mismatch*    Verify Current Profile Fields Before Next    3100000000001    09-11-1996    000-000-0000
""",
                encoding="utf-8",
            )
            code = run(
                str(suite),
                outputdir=temp,
                log="NONE",
                report="NONE",
                console="none",
                stdout=io.StringIO(),
                stderr=io.StringIO(),
            )
            result = ExecutionResult(str(root / "output.xml"))
            self.assertEqual(code, 0, [test.message for test in result.suite.tests])


if __name__ == "__main__":
    unittest.main(verbosity=2)
