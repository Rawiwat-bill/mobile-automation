from __future__ import annotations

import io
import tempfile
import unittest
from pathlib import Path

from robot import run
from robot.api import ExecutionResult, get_resource_model

ROOT = Path(__file__).resolve().parents[1]
COMMON = ROOT / "resources" / "keywords" / "common_onboarding.resource"
PAGE = ROOT / "resources" / "pages" / "common_onboarding" / "app_update_prompt_page.resource"
LOCATORS = ROOT / "locators" / "android" / "common_onboarding" / "app_update_prompt_locators.resource"


def keyword_body(name: str) -> str:
    model = get_resource_model(str(PAGE))
    node = next(
        node
        for section in model.sections
        for node in getattr(section, "body", [])
        if node.__class__.__name__ == "Keyword" and node.name == name
    )
    return "".join(PAGE.read_text(encoding="utf-8").splitlines(keepends=True)[node.lineno - 1 : node.end_lineno])


class AppUpdatePromptContractTests(unittest.TestCase):
    def test_rgi109_is_scoped_to_maybe_later(self):
        locators = LOCATORS.read_text(encoding="utf-8")
        self.assertIn('contains(@text,"RGI-109")', locators)
        self.assertIn('contains(@text,"RGI-107")', locators)
        self.assertIn('@text="Maybe later"', locators)
        self.assertIn('@text="Update app"', locators)

        page = PAGE.read_text(encoding="utf-8")
        self.assertIn("Dismiss Optional App Update Prompt If Visible", page)
        self.assertIn("Wait Until Element Is Visible    ${APP_UPDATE_RGI109_CODE}", page)
        self.assertIn("${APP_UPDATE_RGI107_CODE}", page)
        self.assertIn("Click Element    ${APP_UPDATE_MAYBE_LATER_BUTTON}", page)
        self.assertNotIn("Click Element    ${APP_UPDATE_UPDATE_APP_BUTTON}", page)
        self.assertIn("APP_UPDATE_PROMPT_RGI109_DID_NOT_CLOSE", page)

    def test_post_permission_flow_races_destination_and_delayed_rgi109(self):
        source = COMMON.read_text(encoding="utf-8")
        first_dismiss = source.index("Dismiss Optional App Update Prompt If Visible")
        landing = source.index("Wait Until Landing Screen Is Displayed")
        permissions = source.index("Allow Android Permission If Visible")
        resolver = source.index("Resolve Optional App Update Or Destination")
        terms = source.index("Wait For Landing Destination")

        self.assertEqual(source.count("Dismiss Optional App Update Prompt If Visible"), 1)
        self.assertEqual(source.count("Resolve Optional App Update Or Destination"), 1)
        self.assertLess(first_dismiss, landing)
        self.assertLess(permissions, resolver)
        self.assertLess(resolver, terms)
        self.assertIn("${TERMS_AND_CONDITIONS_WEBVIEW}", source)
        self.assertIn("${NCBD_LOADING_TIMEOUT}", source)

    def test_race_is_event_driven_and_never_dismisses_unknown_popup(self):
        page = PAGE.read_text(encoding="utf-8")
        self.assertIn("App Update Destination Or Blocker Should Be Visible", page)
        self.assertIn("${APP_UPDATE_RGI109_CODE}", page)
        self.assertIn("${LANDING_POPUP_GUB_CONTAINER}", page)
        self.assertIn("${LANDING_OFFLINE_MESSAGE}", page)
        self.assertIn("${LANDING_FULL_SCREEN_GUB_CTA}", page)
        self.assertIn("RETURN    BLOCKER_READY", page)
        self.assertIn("RETURN    UPDATE_DISMISSED", page)
        self.assertNotIn("Sleep", page)

        popup_index = page.index("${LANDING_POPUP_GUB_CONTAINER}")
        reacquire_index = page.index(
            "Wait Until Element Is Visible\n        ...    ${APP_UPDATE_RGI109_CODE}"
        )
        dismiss_index = page.index("Dismiss Optional App Update Prompt If Visible", page.index("Resolve Optional"))
        self.assertLess(popup_index, reacquire_index)
        self.assertLess(reacquire_index, dismiss_index)

    def test_update_prompt_page_is_wired_as_common_resource(self):
        source = COMMON.read_text(encoding="utf-8")
        self.assertIn(
            "Resource         ../pages/common_onboarding/app_update_prompt_page.resource",
            source,
        )

    def test_mandatory_update_is_checked_before_destination(self):
        page = PAGE.read_text(encoding="utf-8")
        start = page.index("Resolve Optional App Update Or Destination")
        end = page.index("\nApp Update Destination Or Blocker Should Be Visible", start)
        resolve = page[start:end]
        self.assertLess(resolve.index("${APP_UPDATE_RGI107_CODE}"), resolve.index("RETURN    DESTINATION_READY"))

    def test_update_detector_distinguishes_visible_hidden_optional_and_ambiguous_states(self):
        body = keyword_body("App Update Destination Or Blocker Should Be Visible")
        resolve = keyword_body("Resolve Optional App Update Or Destination")
        with tempfile.TemporaryDirectory(prefix="etb-update-states-") as temp:
            root = Path(temp)
            resource = root / "update_states.resource"
            resource.write_text(
                """*** Settings ***\nLibrary    Collections\n\n*** Variables ***\n${APP_UPDATE_RGI109_CODE}    RGI109\n${APP_UPDATE_RGI107_CODE}    RGI107\n${APP_UPDATE_MAYBE_LATER_BUTTON}    MAYBE\n${APP_UPDATE_UPDATE_APP_BUTTON}    UPDATE\n${LANDING_OFFLINE_MESSAGE}    OFFLINE\n${LANDING_POPUP_GUB_CONTAINER}    POPUP\n${LANDING_FULL_SCREEN_GUB_CTA}    FULL\n${APP_UPDATE_PROMPT_PROBE_TIMEOUT}    0s\n${APP_UPDATE_PROMPT_ACTION_TIMEOUT}    0s\n${APP_UPDATE_PROMPT_TRANSITION_TIMEOUT}    0s\n\n*** Keywords ***\n"""
                + body
                + resolve
                + """\nElement Should Be Visible Now\n    [Arguments]    ${locator}\n    List Should Contain Value    ${VISIBLE}    ${locator}\n\nDismiss Optional App Update Prompt If Visible\n    Fail    OPTIONAL_DISMISS_NOT_EXPECTED\n""",
                encoding="utf-8",
            )
            suite = root / "update_states.robot"
            suite.write_text(
                """*** Settings ***\nResource    update_states.resource\n\n*** Test Cases ***\nVisible Mandatory\n    ${visible}=    Create List    RGI107\n    Set Test Variable    ${VISIBLE}    ${visible}\n    App Update Destination Or Blocker Should Be Visible    DEST\n\nHidden Mandatory Is Not Evidence\n    ${visible}=    Create List\n    Set Test Variable    ${VISIBLE}    ${visible}\n    Run Keyword And Expect Error    *should be true*    App Update Destination Or Blocker Should Be Visible    DEST\n\nVisible Optional\n    ${visible}=    Create List    RGI109\n    Set Test Variable    ${VISIBLE}    ${visible}\n    App Update Destination Or Blocker Should Be Visible    DEST\n\nMandatory Wins Over Destination\n    ${visible}=    Create List    RGI107    DEST\n    Set Test Variable    ${VISIBLE}    ${visible}\n    Run Keyword And Expect Error    APP_UPDATE_REQUIRED_RGI_107    Resolve Optional App Update Or Destination    DEST    0s\n""",
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
