"""Offline contract for ETB Product Selection completion state (F11).

The test executes the exact current ``Complete ETB Onboarding`` keyword body
extracted from production source. All UI, device, backend, profile, evidence
and reporting boundaries are synthetic Robot stubs.
"""
import hashlib
import io
import tempfile
import unittest
from pathlib import Path

from robot import run
from robot.api import ExecutionResult, get_resource_model

ROOT = Path(__file__).resolve().parents[1]
ETB = ROOT / "resources/keywords/etb/etb_keywords.resource"


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


TESTS = r'''*** Variables ***
${CHECK_DOPA_FILL_LASER_CODE_BUTTON_NEXT}    synthetic-dopa-next
${INTRO_FACE_SCAN_NEXT_BUTTON}               synthetic-face-next
${LABEL_ETB_FINISHED}                        synthetic-finished
${BUTTON_LETGO}                              synthetic-lets-go
${NCBD_LOADING_TIMEOUT}                      1s

*** Test Cases ***
Selection Before Registration Success Is Remembered
    Configure    PRODUCT_SELECTION    REGISTRATION_SUCCESS
    ${actual}=    Complete ETB Onboarding    OMITTED    OMITTED    OMITTED    OMITTED    OMITTED    OMITTED
    Should Be True    ${actual}
    Should Be Equal As Integers    ${PRODUCT_SELECTION_CALLS}    1
    List Should Contain Value    ${CHECKPOINTS}    PRODUCT_SELECTION_VISIBLE

Confirm Then Product Selection Remains Supported
    Configure    CONFIRM_PIN    PRODUCT_SELECTION
    ${actual}=    Complete ETB Onboarding    OMITTED    OMITTED    OMITTED    OMITTED    OMITTED    OMITTED
    Should Be True    ${actual}
    Should Be Equal As Integers    ${PIN_CALLS}    2
    Should Be Equal As Integers    ${PRODUCT_SELECTION_CALLS}    1

Required Immediate Success Still Means Selection Was Skipped
    Configure    COMPLETION_SUCCESS    REGISTRATION_SUCCESS
    Run Keyword And Expect Error    PRODUCT_SELECTION_REQUIRED_BUT_SKIPPED    Complete ETB Onboarding    OMITTED    OMITTED    OMITTED    OMITTED    OMITTED    OMITTED
    Should Be Equal As Integers    ${PRODUCT_SELECTION_CALLS}    0

Optional Immediate Success Is Allowed
    Configure    COMPLETION_SUCCESS    REGISTRATION_SUCCESS
    ${actual}=    Complete ETB Onboarding    OMITTED    OMITTED    OMITTED    OMITTED    OMITTED    OMITTED    product_selection_policy=OPTIONAL
    Should Be True    ${actual}
    Should Be Equal As Integers    ${PRODUCT_SELECTION_CALLS}    0

Unexpected Selection With Optional Policy Fails Contract
    Configure    PRODUCT_SELECTION    REGISTRATION_SUCCESS
    Run Keyword And Expect Error    PRODUCT_SELECTION_CONTRACT_VIOLATION    Complete ETB Onboarding    OMITTED    OMITTED    OMITTED    OMITTED    OMITTED    OMITTED    product_selection_policy=OPTIONAL

*** Keywords ***
Configure
    [Arguments]    ${post_first_state}    ${destination}
    Set Test Variable    ${POST_FIRST_STATE}    ${post_first_state}
    Set Test Variable    ${DESTINATION}    ${destination}
    Set Test Variable    ${PRODUCT_SELECTION_CALLS}    ${0}
    Set Test Variable    ${PIN_CALLS}    ${0}
    ${points}=    Create List
    Set Test Variable    ${CHECKPOINTS}    ${points}

Common Onboarding Flow
    [Arguments]    ${citizen_id}    ${date_of_birth}    ${mobile_number}
    RETURN    NEXT

Wait Until Check DOPA Fill Laser Code Is Displayed
    No Operation

Input Laser Code
    [Arguments]    ${laser_code}
    No Operation

Wait Until Element Is Visible
    [Arguments]    ${locator}    ${timeout}=NONE
    No Operation

Click Element
    [Arguments]    ${locator}
    No Operation

Wait Until Mobile OTP Screen Is Displayed
    No Operation

Input OTP
    [Arguments]    ${otp}
    No Operation

Handle Post OTP Transition
    RETURN    NONE

Wait Until Intro Face Screen Is Displayed
    No Operation

Allow Android Permission If Visible
    No Operation

Wait Until Setup Pin Screen Is Displayed
    No Operation

Set Up PIN
    [Arguments]    ${pin}    ${re_pin}=${FALSE}
    ${calls}=    Evaluate    $PIN_CALLS + 1
    Set Test Variable    ${PIN_CALLS}    ${calls}

Probe Post First PIN State
    RETURN    ${POST_FIRST_STATE}

ETB Post PIN Destination Should Be Displayed
    RETURN    ${DESTINATION}

Complete Product Selection
    ${calls}=    Evaluate    $PRODUCT_SELECTION_CALLS + 1
    Set Test Variable    ${PRODUCT_SELECTION_CALLS}    ${calls}

Mark Health Checkpoint
    [Arguments]    ${stage}
    Append To List    ${CHECKPOINTS}    ${stage}

Set Health Check Blocker
    [Arguments]    ${code}    ${message}    ${directory}
    No Operation
'''


class ETBProductSelectionStateTests(unittest.TestCase):
    def test_exact_production_product_selection_state_contract(self):
        print("SHA256 " + str(ETB.relative_to(ROOT)) + " " + hashlib.sha256(ETB.read_bytes()).hexdigest())
        with tempfile.TemporaryDirectory(prefix="bbl-product-selection-state-") as directory:
            root = Path(directory)
            resource = root / "production_product_state.resource"
            resource.write_text(
                "*** Keywords ***\n" + keyword_body(ETB, "Complete ETB Onboarding"),
                encoding="utf-8",
            )
            suite = root / "product_state.robot"
            suite.write_text(
                "*** Settings ***\nLibrary    Collections\nResource    production_product_state.resource\n\n"
                + TESTS,
                encoding="utf-8",
            )
            stdout = io.StringIO()
            stderr = io.StringIO()
            code = run(
                str(suite),
                outputdir=directory,
                log="NONE",
                report="NONE",
                console="none",
                stdout=stdout,
                stderr=stderr,
            )
            result = ExecutionResult(str(root / "output.xml"))
            self.assertEqual(len(result.suite.tests), 5)
            print("PRODUCT_SELECTION_STATE_CASES=5")
            for case in result.suite.tests:
                print(case.name + "=" + case.status)
            if code != 0:
                print(stdout.getvalue())
                print(stderr.getvalue())
            self.assertEqual(code, 0, "PRODUCT_SELECTION_STATE_CONTRACT_FAILED")


if __name__ == "__main__":
    unittest.main(verbosity=2)
