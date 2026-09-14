from pathlib import Path
import unittest

ROOT = Path(__file__).resolve().parents[1]
TEXT = (ROOT / "resources/app/app_keywords.resource").read_text(encoding="utf-8")
START = TEXT.index("Allow Android Permission If Visible\n")
END = TEXT.index("\nPermission Transition Should Be Complete\n", START)
BLOCK = TEXT[START:END]


class MobileReviewTask7Contracts(unittest.TestCase):
    def test_permission_statuses_are_used_as_booleans(self):
        self.assertIn("IF    not ${click_status}", BLOCK)
        self.assertIn("IF    not ${retry_status}", BLOCK)
        self.assertNotIn("'${click_status}' != 'PASS'", BLOCK)
        self.assertNotIn("'${retry_status}' != 'PASS'", BLOCK)
        self.assertNotIn("== 'PASS'", BLOCK)

    def test_retry_requires_failed_click_and_incomplete_transition(self):
        click_fail = BLOCK.index("IF    not ${click_status}")
        transition_check = BLOCK.index("${already_transitioned}=", click_fail)
        incomplete = BLOCK.index("IF    not ${already_transitioned}", transition_check)
        reacquire = BLOCK.index("PERMISSION_CLICK_REACQUIRE=TRUE", incomplete)
        retry = BLOCK.index("${retry_status}=", reacquire)
        self.assertLess(click_fail, transition_check)
        self.assertLess(transition_check, incomplete)
        self.assertLess(incomplete, reacquire)
        self.assertLess(reacquire, retry)

    def test_final_transition_is_verified_independently_of_click_return(self):
        final_wait = "Wait Until Keyword Succeeds    10s    500ms    Permission Transition Should Be Complete"
        self.assertIn(final_wait, BLOCK)
        self.assertGreater(BLOCK.index(final_wait), BLOCK.index("${retry_status}="))
        self.assertIn("Activate Application    ${APP_PACKAGE}", BLOCK)


if __name__ == "__main__":
    unittest.main(verbosity=2)
