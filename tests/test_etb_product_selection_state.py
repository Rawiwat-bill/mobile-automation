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

from libraries.product_selection_contract import validate_product_categories

ROOT = Path(__file__).resolve().parents[1]
ETB = ROOT / "resources/keywords/etb/etb_keywords.resource"
FLOW_STATES = ROOT / "resources/contracts/flow_states.resource"


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
    Configure    ${FLOW_STATE_PRODUCT_SELECTION}    ${FLOW_STATE_REGISTRATION_SUCCESS}
    ${actual}=    Complete ETB Onboarding    OMITTED    OMITTED    OMITTED    OMITTED    OMITTED    OMITTED    confirm_pin_policy=OPTIONAL
    Should Be True    ${actual}
    Should Be Equal As Integers    ${PRODUCT_SELECTION_CALLS}    1

Confirm Then Product Selection Remains Supported
    Configure    ${FLOW_STATE_CONFIRM_PIN}    ${FLOW_STATE_PRODUCT_SELECTION}
    ${actual}=    Complete ETB Onboarding    OMITTED    OMITTED    OMITTED    OMITTED    OMITTED    OMITTED
    Should Be True    ${actual}
    Should Be Equal As Integers    ${PIN_CALLS}    2
    Should Be Equal As Integers    ${PRODUCT_SELECTION_CALLS}    1

Required Immediate Success Still Means Selection Was Skipped
    Configure    ${FLOW_STATE_COMPLETION_SUCCESS}    ${FLOW_STATE_REGISTRATION_SUCCESS}
    Run Keyword And Expect Error    PRODUCT_SELECTION_REQUIRED_BUT_SKIPPED    Complete ETB Onboarding    OMITTED    OMITTED    OMITTED    OMITTED    OMITTED    OMITTED    confirm_pin_policy=OPTIONAL
    Should Be Equal As Integers    ${PRODUCT_SELECTION_CALLS}    0

Optional Immediate Success Is Allowed
    Configure    ${FLOW_STATE_COMPLETION_SUCCESS}    ${FLOW_STATE_REGISTRATION_SUCCESS}
    ${actual}=    Complete ETB Onboarding    OMITTED    OMITTED    OMITTED    OMITTED    OMITTED    OMITTED    product_selection_policy=OPTIONAL    confirm_pin_policy=OPTIONAL
    Should Be True    ${actual}
    Should Be Equal As Integers    ${PRODUCT_SELECTION_CALLS}    0

Unexpected Selection With Optional Policy Fails Contract
    Configure    PRODUCT_SELECTION    REGISTRATION_SUCCESS
    Run Keyword And Expect Error    PRODUCT_SELECTION_CONTRACT_VIOLATION    Complete ETB Onboarding    OMITTED    OMITTED    OMITTED    OMITTED    OMITTED    OMITTED    product_selection_policy=OPTIONAL    confirm_pin_policy=OPTIONAL

Required PDPA Cannot Be Skipped
    Configure    ${FLOW_STATE_COMPLETION_SUCCESS}    ${FLOW_STATE_REGISTRATION_SUCCESS}    ${FLOW_STATE_INTRO_FACE_SCAN}
    Run Keyword And Expect Error    PDPA_REQUIRED_BUT_SKIPPED    Complete ETB Onboarding    OMITTED    OMITTED    OMITTED    OMITTED    OMITTED    OMITTED    product_selection_policy=OPTIONAL    pdpa_policy=REQUIRED    confirm_pin_policy=OPTIONAL

Must Skip PDPA Rejects Unexpected Display
    Configure    ${FLOW_STATE_COMPLETION_SUCCESS}    ${FLOW_STATE_REGISTRATION_SUCCESS}    ${FLOW_STATE_CHECK_PDPA_CLAUSE_NO_6}
    Run Keyword And Expect Error    PDPA_MUST_SKIP_BUT_DISPLAYED    Complete ETB Onboarding    OMITTED    OMITTED    OMITTED    OMITTED    OMITTED    OMITTED    product_selection_policy=OPTIONAL    pdpa_policy=MUST_SKIP    confirm_pin_policy=OPTIONAL

Required PDPA Accepts Expected Display
    Configure    ${FLOW_STATE_COMPLETION_SUCCESS}    ${FLOW_STATE_REGISTRATION_SUCCESS}    ${FLOW_STATE_CHECK_PDPA_CLAUSE_NO_6}
    ${actual}=    Complete ETB Onboarding    OMITTED    OMITTED    OMITTED    OMITTED    OMITTED    OMITTED    product_selection_policy=OPTIONAL    pdpa_policy=REQUIRED    confirm_pin_policy=OPTIONAL
    Should Be True    ${actual}
    Should Be Equal As Integers    ${PDPA_ACCEPT_CALLS}    1

*** Keywords ***
Configure
    [Arguments]    ${post_first_state}    ${destination}    ${post_otp_screen}=NONE
    Set Test Variable    ${POST_FIRST_STATE}    ${post_first_state}
    Set Test Variable    ${DESTINATION}    ${destination}
    Set Test Variable    ${POST_OTP_SCREEN}    ${post_otp_screen}
    Set Test Variable    ${PRODUCT_SELECTION_CALLS}    ${0}
    Set Test Variable    ${PIN_CALLS}    ${0}
    Set Test Variable    ${PDPA_ACCEPT_CALLS}    ${0}

Common Onboarding Flow
    [Arguments]    ${citizen_id}    ${date_of_birth}    ${mobile_number}
    RETURN    ${FLOW_STATE_NEXT}

Wait Until Check DOPA Fill Laser Code Is Displayed
    No Operation

Input Laser Code
    [Arguments]    ${laser_code}
    No Operation

Tap Check DOPA Next
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
    RETURN    ${POST_OTP_SCREEN}

Wait Until Check PDPA Clause No6 Is Displayed
    No Operation

Scroll Down PDPA Clause No6
    No Operation

Accept PDPA Clause No6
    ${calls}=    Evaluate    $PDPA_ACCEPT_CALLS + 1
    Set Test Variable    ${PDPA_ACCEPT_CALLS}    ${calls}

Wait Until Intro Face Screen Is Displayed
    No Operation

Continue From Intro Face Scan
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

Probe Stable Post First PIN State
    RETURN    ${POST_FIRST_STATE}

ETB Post PIN Destination Should Be Displayed
    RETURN    ${DESTINATION}

Complete Product Selection
    [Arguments]    ${expected_product_categories}=${NONE}
    ${calls}=    Evaluate    $PRODUCT_SELECTION_CALLS + 1
    Set Test Variable    ${PRODUCT_SELECTION_CALLS}    ${calls}

Wait Until Registration Success Is Displayed
    No Operation

Tap Registration Success Continue
    No Operation

Assert ETB Release Pre-SET
    No Operation

Record ETB Readiness Blocker
    [Arguments]    ${output_dir}    ${blocker_code}    ${dopa_reached}
    No Operation

Record ETB Registration Success Visible
    [Arguments]    ${output_dir}
    No Operation

Record ETB Registration Continue Start
    [Arguments]    ${output_dir}
    No Operation

Record ETB Registration Continue End
    [Arguments]    ${output_dir}
    No Operation

Record ETB Post Success State
    [Arguments]    ${output_dir}
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
                "*** Settings ***\nLibrary    Collections\nResource    " + str(FLOW_STATES) + "\nResource    production_product_state.resource\n\n"
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
            self.assertEqual(len(result.suite.tests), 8)
            print("ETB_CASE_ASSERTION_CASES=8")
            for case in result.suite.tests:
                print(case.name + "=" + case.status)
            if code != 0:
                print(stdout.getvalue())
                print(stderr.getvalue())
            self.assertEqual(code, 0, "PRODUCT_SELECTION_STATE_CONTRACT_FAILED")

    def test_tc004_expected_product_categories_are_distinct(self):
        self.assertTrue(
            validate_product_categories(
                ["Saving Account", "e-Saving Account"],
                ["Saving", "e-Saving"],
            )
        )
        for actual, missing in (
            (["Saving Account"], "e-Saving"),
            (["e-Saving Account"], "Saving"),
            (["Credit Card"], "Saving,e-Saving"),
        ):
            with self.subTest(actual=actual):
                with self.assertRaisesRegex(
                    AssertionError,
                    "PRODUCT_SELECTION_EXPECTED_CATEGORIES_MISSING=" + missing,
                ):
                    validate_product_categories(actual, ["Saving", "e-Saving"])

    def test_production_flow_forwards_expected_categories(self):
        text = ETB.read_text(encoding="utf-8")
        self.assertIn("${expected_product_categories}=${NONE}", text)
        self.assertGreaterEqual(
            text.count("Complete Product Selection    ${expected_product_categories}"),
            2,
        )

    def test_product_selection_page_wires_category_assertion(self):
        page = (ROOT / "resources/pages/etb/product_selection_page.resource").read_text(encoding="utf-8")
        locators = (ROOT / "locators/android/etb/product_selection_locators.resource").read_text(encoding="utf-8")
        self.assertIn("Assert Expected Product Categories Are Displayed", page)
        self.assertIn("Validate Product Categories", page)
        self.assertIn("${PRODUCT_SELECTION_PRODUCT_NAMES}", page)
        self.assertIn("screenProductSelection_flatListCardsTextProductName_", locators)


if __name__ == "__main__":
    unittest.main(verbosity=2)
