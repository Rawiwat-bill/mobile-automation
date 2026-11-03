import io
import tempfile
import unittest
from pathlib import Path

from robot import run
from robot.api import ExecutionResult, get_resource_model


ROOT = Path(__file__).resolve().parents[1]
CONFIRM_PIN = ROOT / "resources/pages/onboarding/confirm_pin_page.resource"
LOCATORS = ROOT / "locators/android/onboarding/confirm_pin_locators.resource"


def keyword_body(path: Path, name: str) -> str:
    text = path.read_text(encoding="utf-8")
    model = get_resource_model(str(path))
    keyword = next(
        node
        for section in model.sections
        for node in getattr(section, "body", [])
        if node.__class__.__name__ == "Keyword" and node.name == name
    )
    return "".join(text.splitlines(keepends=True)[keyword.lineno - 1 : keyword.end_lineno])


class ConfirmPinStaleRetryTests(unittest.TestCase):
    def test_stale_after_screen_transition_is_not_reclicked(self) -> None:
        with tempfile.TemporaryDirectory(prefix="bbl-confirm-pin-stale-") as directory:
            root = Path(directory)
            resource = root / "confirm_pin.resource"
            resource.write_text(
                "*** Settings ***\nLibrary    Collections\nResource    "
                + str(LOCATORS)
                + "\n\n*** Keywords ***\n"
                + keyword_body(CONFIRM_PIN, "Confirm PIN Screen Is Active")
                + keyword_body(CONFIRM_PIN, "Confirm PIN Screen Markers Should Be Visible")
                + keyword_body(CONFIRM_PIN, "Enter Confirm PIN Using Custom Keypad"),
                encoding="utf-8",
            )
            suite = root / "stale_retry.robot"
            suite.write_text(
                """*** Settings ***
Resource    confirm_pin.resource

*** Test Cases ***
Relocate First Stale Element
    Set Test Variable    ${CLICK_CALLS}    ${0}
    Set Test Variable    ${ACTIVE}    ${True}
    Run Keyword And Expect Error    *CONFIRM_PIN_SCREEN_NOT_ACTIVE*    Enter Confirm PIN Using Custom Keypad    111111
    Should Be Equal As Integers    ${CLICK_CALLS}    1

*** Keywords ***
Get WebElement
    [Arguments]    ${locator}
    RETURN    ${locator}

Click Element
    [Arguments]    ${element}
    ${calls}=    Evaluate    $CLICK_CALLS + 1
    Set Test Variable    ${CLICK_CALLS}    ${calls}
    IF    ${calls} == 1
        Set Test Variable    ${ACTIVE}    ${False}
        Fail    StaleElementReferenceException: synthetic first click
    END

Capture Confirm PIN Failure Evidence
    No Operation

Element Should Be Visible Now
    [Arguments]    ${locator}
    IF    not ${ACTIVE}
        Fail    CONFIRM_PIN_SCREEN_NOT_ACTIVE
    END
    IF    'security-error-container' in '${locator}'
        Fail    synthetic error marker absent
    END
""",
                encoding="utf-8",
            )
            stdout = io.StringIO()
            code = run(
                str(suite),
                outputdir=directory,
                log="NONE",
                report="NONE",
                console="none",
                stdout=stdout,
            )
            result = ExecutionResult(str(root / "output.xml"))
            self.assertEqual(result.suite.tests[0].status, "PASS", result.suite.tests[0].message)
            self.assertEqual(code, 0, stdout.getvalue())


if __name__ == "__main__":
    unittest.main(verbosity=2)
