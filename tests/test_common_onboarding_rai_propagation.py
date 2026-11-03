"""Ensure an observed RAI popup is preserved by the shared onboarding caller."""
from __future__ import annotations

import io
import tempfile
import unittest
from pathlib import Path

from robot import run
from robot.api import ExecutionResult, get_resource_model

ROOT = Path(__file__).resolve().parents[1]
RESOURCE = ROOT / "resources/keywords/common_onboarding.resource"


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


class CommonOnboardingRaiTests(unittest.TestCase):
    def test_rai_code_is_not_collapsed_into_generic_navigation_failure(self) -> None:
        body = keyword_body(RESOURCE, "Run Common Onboarding")
        with tempfile.TemporaryDirectory(prefix="etb-common-rai-") as temp:
            root = Path(temp)
            resource = root / "common_rai.resource"
            resource.write_text(
                """*** Settings ***
Library    String

*** Variables ***
${FLOW_STATE_AJI_001}    AJI-001
${FLOW_STATE_NEXT}    NEXT
${FLOW_STATE_GOD_013}    GOD-013
${FLOW_STATE_RGI_104}    RGI-104
${FLOW_STATE_PROFILE_LEFT_OR_NEXT}    PROFILE_LEFT_OR_NEXT

*** Keywords ***
"""
                + body
                + """
Dismiss Optional App Update Prompt If Visible
    No Operation
Wait Until Landing Screen Is Displayed
    No Operation
Switch Landing Language To English
    No Operation
Advance Landing To Terms Destination
    No Operation
Ensure Terms Content Ready With Interim Navigation Retries
    No Operation
Scroll Down Terms And Conditions
    No Operation
Accept Terms And Conditions
    RETURN    NEXT
Wait Until Profile Screen Is Displayed
    No Operation
Input Citizen ID
    [Arguments]    ${value}
    No Operation
Input Date Of Birth
    [Arguments]    ${value}
    No Operation
profile_screen_page.Input Date Of Birth
    [Arguments]    ${value}
    No Operation
Input Mobile Number
    [Arguments]    ${value}
    No Operation
Verify Current Profile Fields Before Next
    [Arguments]    ${cid}    ${dob}    ${mobile}
    No Operation
Tap Profile Next
    RETURN    RAI-033
""",
                encoding="utf-8",
            )
            suite = root / "common_rai.robot"
            suite.write_text(
                """*** Settings ***
Resource    common_rai.resource

*** Test Cases ***
RAI remains an observed route
    ${result}=    Run Common Onboarding    CID    DOB    MOBILE
    Should Be Equal As Strings    ${result}    RAI-033
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
