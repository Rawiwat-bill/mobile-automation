"""Protect the Profile handoff from a stale/false-positive element lookup."""
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


class ProfileScreenDestinationContractTests(unittest.TestCase):
    def test_profile_requires_source_marker_after_element_visibility(self) -> None:
        body = keyword_body(RESOURCE, "Wait Until Profile Screen Is Displayed")
        with tempfile.TemporaryDirectory(prefix="etb-profile-screen-") as temp:
            root = Path(temp)
            resource = root / "profile_screen.resource"
            resource.write_text(
                """*** Settings ***
Library    String

*** Variables ***
${PROFILE_TITLE_TEXT}    PROFILE_TITLE
${PROFILE_CITIZEN_ID_INPUT}    CID_INPUT
${PROFILE_TIMEOUT}    1s
${SOURCE}    ${EMPTY}

*** Keywords ***
"""
                + body
                + """
Wait Until Element Is Visible
    [Arguments]    ${locator}    ${timeout}
    No Operation

Get Source
    RETURN    ${SOURCE}
""",
                encoding="utf-8",
            )
            suite = root / "profile_screen.robot"
            suite.write_text(
                """*** Settings ***
Resource    profile_screen.resource

*** Test Cases ***
Profile source marker present
    Set Test Variable    ${SOURCE}    <node resource-id="cid-container" displayed="true"/><node resource-id="screenProfile_buttonNext" displayed="true"/>
    Wait Until Profile Screen Is Displayed

Terms source cannot satisfy Profile
    Set Test Variable    ${SOURCE}    <node resource-id="termsAndConditions" displayed="true"/>
    Run Keyword And Expect Error    *PROFILE_SCREEN_SOURCE_MARKER_MISSING*    Wait Until Profile Screen Is Displayed
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
