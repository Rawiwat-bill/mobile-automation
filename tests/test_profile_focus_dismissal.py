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


class ProfileFocusDismissalTests(unittest.TestCase):
    def test_focus_dismissal_never_hides_an_already_hidden_keyboard(self) -> None:
        body = keyword_body(RESOURCE, "Tap Profile Focus Dismissal Target")
        self.assertLess(body.index("Tap    ${tap_point}"), body.index("Is Keyboard Shown"))
        self.assertIn("IF    '${keyboard_status}' == 'PASS' and ${keyboard_shown}", body)

        with tempfile.TemporaryDirectory(prefix="bbl-profile-focus-") as directory:
            root = Path(directory)
            resource = root / "profile_focus.resource"
            resource.write_text(
                """*** Settings ***
Library    Collections

*** Variables ***
${PROFILE_TITLE_TEXT}    PROFILE_TITLE

*** Keywords ***
"""
                + body
                + """
Wait Until Element Is Visible
    [Arguments]    ${locator}    ${timeout}
    IF    not ${PROFILE_VISIBLE}
        Fail    PROFILE_NOT_VISIBLE
    END

Get Element Rect
    [Arguments]    ${locator}
    &{rect}=    Create Dictionary    x=10    y=20    width=100    height=40
    RETURN    ${rect}

Tap
    [Arguments]    ${point}
    ${calls}=    Evaluate    ${TAP_CALLS} + 1
    Set Test Variable    ${TAP_CALLS}    ${calls}

Is Keyboard Shown
    RETURN    ${KEYBOARD_SHOWN}

Hide Keyboard
    ${calls}=    Evaluate    ${HIDE_CALLS} + 1
    Set Test Variable    ${HIDE_CALLS}    ${calls}
    IF    not ${KEYBOARD_SHOWN}
        Set Test Variable    ${PROFILE_VISIBLE}    ${False}
        Fail    SYNTHETIC_BACK_NAVIGATION
    END
    Set Test Variable    ${KEYBOARD_SHOWN}    ${False}

Element Should Be Visible Now
    [Arguments]    ${locator}
    IF    not ${PROFILE_VISIBLE}
        Fail    PROFILE_NOT_VISIBLE
    END
""",
                encoding="utf-8",
            )
            suite = root / "profile_focus.robot"
            suite.write_text(
                """*** Settings ***
Resource    profile_focus.resource

*** Test Cases ***
Already hidden keyboard never triggers hide
    Set Test Variable    ${PROFILE_VISIBLE}    ${True}
    Set Test Variable    ${KEYBOARD_SHOWN}    ${False}
    Set Test Variable    ${HIDE_CALLS}    ${0}
    Set Test Variable    ${TAP_CALLS}    ${0}
    Tap Profile Focus Dismissal Target    0
    Should Be Equal As Integers    ${HIDE_CALLS}    0
    Should Be Equal As Integers    ${TAP_CALLS}    1
    Should Be True    ${PROFILE_VISIBLE}

Shown keyboard is hidden once after safe profile tap
    Set Test Variable    ${PROFILE_VISIBLE}    ${True}
    Set Test Variable    ${KEYBOARD_SHOWN}    ${True}
    Set Test Variable    ${HIDE_CALLS}    ${0}
    Set Test Variable    ${TAP_CALLS}    ${0}
    Tap Profile Focus Dismissal Target    0
    Should Be Equal As Integers    ${HIDE_CALLS}    1
    Should Be Equal As Integers    ${TAP_CALLS}    1
    Should Be True    ${PROFILE_VISIBLE}
    Should Not Be True    ${KEYBOARD_SHOWN}

Missing profile still fails closed
    Set Test Variable    ${PROFILE_VISIBLE}    ${False}
    Set Test Variable    ${KEYBOARD_SHOWN}    ${False}
    Set Test Variable    ${HIDE_CALLS}    ${0}
    Set Test Variable    ${TAP_CALLS}    ${0}
    Run Keyword And Expect Error    *PROFILE_DISAPPEARED_BEFORE_FOCUS_DISMISSAL*    Tap Profile Focus Dismissal Target    0
    Should Be Equal As Integers    ${HIDE_CALLS}    0
""",
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
            self.assertEqual(
                code,
                0,
                "\n".join(test.message for test in result.suite.tests)
                + stdout.getvalue()
                + stderr.getvalue(),
            )


if __name__ == "__main__":
    unittest.main(verbosity=2)
