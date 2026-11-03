"""Focused route classification checks for the shared Profile handoff."""
from __future__ import annotations

import io
import tempfile
import unittest
from pathlib import Path

from robot import run
from robot.api import ExecutionResult, get_resource_model

ROOT = Path(__file__).resolve().parents[1]
PROFILE_TRANSITION = ROOT / "resources/pages/onboarding/profile_transition.resource"


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


class ProfileTransitionRouteTests(unittest.TestCase):
    def test_visible_terminal_routes_are_returned_and_hidden_dopa_is_rejected(self) -> None:
        body = keyword_body(PROFILE_TRANSITION, "Read Visible Profile Error Codes") + keyword_body(
            PROFILE_TRANSITION, "Observe Profile Next Transition"
        )
        with tempfile.TemporaryDirectory(prefix="etb-profile-routes-") as temp:
            root = Path(temp)
            resource = root / "profile_routes.resource"
            resource.write_text(
                """*** Settings ***
Library    String
Library    Collections

*** Variables ***
${FLOW_STATE_GOD_013}    GOD-013
${FLOW_STATE_AJI_001}    AJI-001
${FLOW_STATE_RGI_104}    RGI-104
${FLOW_STATE_PROFILE_LEFT_OR_NEXT}    PROFILE_LEFT_OR_NEXT_STATE_VISIBLE
${PROFILE_TITLE_TEXT}    PROFILE_TITLE
${RGI_POPUP_CONTAINER}    POPUP
${RGI_POPUP_CODE_ELEMENTS}    POPUP_CODE
${FULL_SCREEN_RGI_CONTAINER}    FULL_SCREEN
${FAKE_SOURCE}    <hierarchy/>
${FAKE_TEXT}    ${EMPTY}
${VISIBLE}    ${EMPTY}
${ELEMENTS}    ${EMPTY}
${VISIBLE_ELEMENTS}    ${EMPTY}
${FAIL_GET_TEXT}    ${false}

*** Keywords ***
"""
                + body
                + """
Get Source
    RETURN    ${FAKE_SOURCE}

Get Text
    [Arguments]    ${locator}
    IF    ${FAIL_GET_TEXT}
        Fail    stale RGI-079 attribute lookup
    END
    RETURN    ${FAKE_TEXT}

Get WebElements
    [Arguments]    ${locator}
    RETURN    ${ELEMENTS}

Get Element Attribute
    [Arguments]    ${element}    ${attribute}
    IF    '${element}' == 'FAILED'
        Fail    stale RGI-079 attribute lookup
    END
    RETURN    ${FAKE_TEXT}

Element Should Be Visible
    [Arguments]    ${locator}
    List Should Contain Value    ${VISIBLE_ELEMENTS}    ${locator}

Element Should Be Visible Now
    [Arguments]    ${locator}
    List Should Contain Value    ${VISIBLE_ELEMENTS}    ${locator}

Profile Title Is Not Visible
    No Operation
""",
                encoding="utf-8",
            )
            suite = root / "profile_routes.robot"
            suite.write_text(
                """*** Settings ***
Resource    profile_routes.resource

*** Test Cases ***
Popup Route Returns Exact Code
    Set Test Variable    ${VISIBLE}    POPUP
    Set Test Variable    ${FAKE_TEXT}    RGI-079
    ${elements}=    Create List    POPUP_CODE
    ${visible}=    Create List    POPUP    POPUP_CODE
    Set Test Variable    ${ELEMENTS}    ${elements}
    Set Test Variable    ${VISIBLE_ELEMENTS}    ${visible}
    ${state}=    Observe Profile Next Transition    before
    Should Be Equal    ${state}    RGI-079

Hidden Popup Candidate Is Ignored
    Set Test Variable    ${VISIBLE}    POPUP
    Set Test Variable    ${FAKE_TEXT}    RGI-079
    ${elements}=    Create List    HIDDEN    VISIBLE
    ${visible}=    Create List    POPUP    VISIBLE
    Set Test Variable    ${ELEMENTS}    ${elements}
    Set Test Variable    ${VISIBLE_ELEMENTS}    ${visible}
    ${state}=    Observe Profile Next Transition    before
    Should Be Equal    ${state}    RGI-079

Failed Popup Attribute Does Not Become Code
    Set Test Variable    ${VISIBLE}    POPUP
    Set Test Variable    ${FAIL_GET_TEXT}    ${true}
    ${elements}=    Create List    FAILED
    ${visible}=    Create List    POPUP    FAILED
    Set Test Variable    ${ELEMENTS}    ${elements}
    Set Test Variable    ${VISIBLE_ELEMENTS}    ${visible}
    Run Keyword And Expect Error    PROFILE_POPUP_CODE_UNPROVEN    Observe Profile Next Transition    before

Full Screen Route Returns Exact Code
    Set Test Variable    ${VISIBLE}    FULL_SCREEN
    Set Test Variable    ${FAKE_TEXT}    RGI-012
    Set Test Variable    ${FAKE_SOURCE}    <node resource-id="security-error-container" text="RGI-012"/>
    ${elements}=    Create List    FULL_CODE
    ${visible}=    Create List    FULL_SCREEN    FULL_CODE
    Set Test Variable    ${ELEMENTS}    ${elements}
    Set Test Variable    ${VISIBLE_ELEMENTS}    ${visible}
    ${state}=    Observe Profile Next Transition    before
    Should Be Equal    ${state}    RGI-012

Observed RAI Popup Code Is Preserved
    Set Test Variable    ${VISIBLE}    POPUP
    Set Test Variable    ${FAKE_TEXT}    RAI-033
    ${elements}=    Create List    POPUP_CODE
    ${visible}=    Create List    POPUP    POPUP_CODE
    Set Test Variable    ${ELEMENTS}    ${elements}
    Set Test Variable    ${VISIBLE_ELEMENTS}    ${visible}
    ${state}=    Observe Profile Next Transition    before
    Should Be Equal    ${state}    RAI-033

Hidden DOPA Does Not Prove Destination
    Set Test Variable    ${VISIBLE}    PROFILE_TITLE
    ${visible}=    Create List    PROFILE_TITLE
    Set Test Variable    ${VISIBLE_ELEMENTS}    ${visible}
    Set Test Variable    ${FAKE_SOURCE}    <node resource-id="screenPersonalInformation_navBarTitleList" displayed="false"/>
    Run Keyword And Expect Error    PROFILE_NEXT_DESTINATION_UNPROVEN_PROFILE_STILL_VISIBLE    Observe Profile Next Transition    before

Visible DOPA Proves Destination
    Set Test Variable    ${VISIBLE}    xpath=//*[@resource-id="screenPersonalInformation_navBarTitleList"]
    Set Test Variable    ${VISIBLE}    FULL_SCREEN|xpath=//*[@resource-id="screenPersonalInformation_navBarTitleList"]
    ${visible}=    Create List    FULL_SCREEN    xpath=//*[@resource-id="screenPersonalInformation_navBarTitleList"]
    Set Test Variable    ${VISIBLE_ELEMENTS}    ${visible}
    Set Test Variable    ${FAKE_SOURCE}    <node resource-id="security-error-container" displayed="true"/><node resource-id="screenPersonalInformation_navBarTitleList" displayed="true"/>
    ${state}=    Observe Profile Next Transition    before
    Should Be Equal    ${state}    PROFILE_LEFT_OR_NEXT_STATE_VISIBLE

Hidden Error Does Not Override Visible DOPA
    Set Test Variable    ${VISIBLE}    FULL_SCREEN|xpath=//*[@resource-id="screenPersonalInformation_navBarTitleList"]
    ${visible}=    Create List    FULL_SCREEN    xpath=//*[@resource-id="screenPersonalInformation_navBarTitleList"]
    Set Test Variable    ${VISIBLE_ELEMENTS}    ${visible}
    Set Test Variable    ${FAKE_SOURCE}    <node text="GOD-013" displayed="false"/><node resource-id="screenPersonalInformation_navBarTitleList" displayed="true"/>
    ${state}=    Observe Profile Next Transition    before
    Should Be Equal    ${state}    PROFILE_LEFT_OR_NEXT_STATE_VISIBLE
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
