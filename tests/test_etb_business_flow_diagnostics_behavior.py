from __future__ import annotations

import io
import tempfile
import unittest
from pathlib import Path

from robot import run
from robot.api import ExecutionResult, get_resource_model

ROOT = Path(__file__).resolve().parents[1]
LANDING = ROOT / "resources/pages/common_onboarding/landing_screen_page.resource"
TERMS = ROOT / "resources/pages/common_onboarding/terms_and_conditions_page.resource"
DOPA = ROOT / "resources/pages/etb/check_dopa_fill_laser_code_page.resource"
PROFILE_FIELDS = ROOT / "resources/pages/onboarding/profile_fields.resource"


def keyword_body(path: Path, name: str) -> str:
    text = path.read_text(encoding="utf-8")
    model = get_resource_model(str(path))
    nodes = [
        node
        for section in model.sections
        for node in getattr(section, "body", [])
        if node.__class__.__name__ == "Keyword" and node.name == name
    ]
    if len(nodes) != 1:
        raise AssertionError("PRODUCTION_KEYWORD_NOT_UNIQUE: " + name)
    node = nodes[0]
    return "".join(text.splitlines(keepends=True)[node.lineno - 1 : node.end_lineno]).rstrip() + "\n"


class ETBBusinessFlowDiagnosticBehaviorTests(unittest.TestCase):
    def test_classifiers_execute_against_synthetic_sources(self) -> None:
        production = "\n".join([
            keyword_body(LANDING, "Classify Landing Gub Code"),
            keyword_body(TERMS, "Classify Terms Non Transition State"),
            keyword_body(DOPA, "Classify Post Laser Failure State"),
            keyword_body(PROFILE_FIELDS, "Classify Profile State Before Next"),
        ])
        suite_text = r'''*** Settings ***
Library    String
Resource    production.resource

*** Variables ***
${SOURCE}    ${EMPTY}
${TERMS_VISIBLE}    ${False}

*** Test Cases ***
Landing Exact Code
    Set Test Variable    ${SOURCE}    <node text="AJI-001"/>
    ${actual}=    Classify Landing Gub Code
    Should Be Equal    ${actual}    AJI-001

Landing Unknown
    Set Test Variable    ${SOURCE}    <node resource-id="screenLanding_Full-Screen_Gub_CTAButton0"/>
    ${actual}=    Classify Landing Gub Code
    Should Be Equal    ${actual}    UNKNOWN

Terms Still Visible
    Set Test Variable    ${SOURCE}    <node resource-id="termsAndConditions"/>
    Set Test Variable    ${TERMS_VISIBLE}    ${True}
    ${actual}=    Classify Terms Non Transition State
    Should Be Equal    ${actual}    TERMS_STILL_VISIBLE

Terms Exact Error Code
    Set Test Variable    ${SOURCE}    <node text="RGI-106"/>
    Set Test Variable    ${TERMS_VISIBLE}    ${False}
    ${actual}=    Classify Terms Non Transition State
    Should Be Equal    ${actual}    RGI-106

Terms Dopa Visible
    Set Test Variable    ${SOURCE}    <node resource-id="screenPersonalInformation_navBarTitleList"/>
    Set Test Variable    ${TERMS_VISIBLE}    ${False}
    ${actual}=    Classify Terms Non Transition State
    Should Be Equal    ${actual}    DOPA_VISIBLE

Terms Profile Visible
    Set Test Variable    ${SOURCE}    <node resource-id="screenProfile_buttonNext"/>
    Set Test Variable    ${TERMS_VISIBLE}    ${False}
    ${actual}=    Classify Terms Non Transition State
    Should Be Equal    ${actual}    PROFILE_VISIBLE

Terms Unknown
    Set Test Variable    ${SOURCE}    <node resource-id="unexpected"/>
    Set Test Variable    ${TERMS_VISIBLE}    ${False}
    ${actual}=    Classify Terms Non Transition State
    Should Be Equal    ${actual}    UNKNOWN_DESTINATION

Post Laser Exact Code
    Set Test Variable    ${SOURCE}    <node text="RGI-016"/>
    ${actual}=    Classify Post Laser Failure State    RGI-016
    Should Be Equal    ${actual}    RGI-016

Post Laser Dopa Still Visible
    Set Test Variable    ${SOURCE}    <node resource-id="screenPersonalInformation_navBarTitleList"/><node resource-id="text-input-flat"/>
    ${actual}=    Classify Post Laser Failure State    RGI-016
    Should Be Equal    ${actual}    DOPA_STILL_VISIBLE

Post Laser Unknown
    Set Test Variable    ${SOURCE}    <node resource-id="unexpected"/>
    ${actual}=    Classify Post Laser Failure State    RGI-016
    Should Be Equal    ${actual}    UNKNOWN_DESTINATION

Profile Exact Error Code
    Set Test Variable    ${SOURCE}    <node text="RAI-033"/>
    ${actual}=    Classify Profile State Before Next
    Should Be Equal    ${actual}    RAI-033

Profile Security WebView
    Set Test Variable    ${SOURCE}    <node resource-id="security-error-container"/><android.webkit.WebView/>
    ${actual}=    Classify Profile State Before Next
    Should Be Equal    ${actual}    SECURITY_WEBVIEW

Profile Dopa Visible
    Set Test Variable    ${SOURCE}    <node resource-id="screenPersonalInformation_navBarTitleList"/>
    ${actual}=    Classify Profile State Before Next
    Should Be Equal    ${actual}    DOPA_VISIBLE

Profile Unknown
    Set Test Variable    ${SOURCE}    <node resource-id="unexpected"/>
    ${actual}=    Classify Profile State Before Next
    Should Be Equal    ${actual}    UNKNOWN_DESTINATION

*** Keywords ***
Get Source
    RETURN    ${SOURCE}

Terms Destination Visible From Source
    [Arguments]    ${source}
    RETURN    ${TERMS_VISIBLE}
'''
        with tempfile.TemporaryDirectory(prefix="etb-business-diagnostics-") as directory:
            root = Path(directory)
            (root / "production.resource").write_text("*** Keywords ***\n" + production, encoding="utf-8")
            suite = root / "diagnostics.robot"
            suite.write_text(suite_text, encoding="utf-8")
            stdout, stderr = io.StringIO(), io.StringIO()
            code = run(
                str(suite), outputdir=directory, log="NONE", report="NONE",
                console="none", stdout=stdout, stderr=stderr,
            )
            result = ExecutionResult(str(root / "output.xml"))
            self.assertEqual(len(result.suite.tests), 14)
            if code != 0:
                print(stdout.getvalue())
                print(stderr.getvalue())
                for test in result.suite.tests:
                    print(test.name, test.status, test.message)
            self.assertEqual(code, 0, "BUSINESS_FLOW_DIAGNOSTIC_BEHAVIOR_FAILED")


if __name__ == "__main__":
    unittest.main(verbosity=2)
