from pathlib import Path
import unittest

ROOT = Path(__file__).resolve().parents[1]


def read(path: str) -> str:
    return (ROOT / path).read_text(encoding="utf-8")


class MobileReviewTask3Contracts(unittest.TestCase):
    def test_common_flow_returns_explicit_terminal_outcome(self):
        text = read("resources/keywords/onboarding_common.resource")
        common = text[text.index("Complete Common Onboarding\n"):text.index("Complete Stage 1 Onboarding\n")]
        self.assertIn("RETURN    PDPA_ACCEPT_NO_TRANSITION", common)
        self.assertIn("RETURN    COMMON_ONBOARDING_COMPLETED", common)
        self.assertNotIn("\n        RETURN\n", common)

    def test_ntb_and_health_callers_must_assert_common_outcome(self):
        ntb = read("tests/android/ntb/ntb_flow.robot")
        health = read("tests/android/onboarding/onboarding_health_check.robot")
        for text in (ntb, health):
            self.assertIn("${common_result}=    Complete Common Onboarding", text)
            self.assertIn("Should Be Equal As Strings    ${common_result}    COMMON_ONBOARDING_COMPLETED", text)

    def test_stage1_stops_when_common_flow_is_blocked(self):
        text = read("resources/keywords/onboarding_common.resource")
        stage1 = text[text.index("Complete Stage 1 Onboarding\n"):text.index("Detect Post PIN Terminal State\n")]
        self.assertIn("${common_result}=    Complete Common Onboarding", stage1)
        self.assertIn("Should Be Equal As Strings    ${common_result}    COMMON_ONBOARDING_COMPLETED", stage1)

    def test_post_pin_success_markers_are_specific_and_error_wins(self):
        text = read("resources/keywords/onboarding_common.resource")
        self.assertNotIn("@{SUCCESS_MARKERS}    success    complete    saved    welcome    congratulations", text)
        self.assertIn("you're all set!", text.lower())
        detector = text[text.index("Detect Post PIN Terminal State\n"):text.index("Accept Terms And Conditions\n")]
        self.assertLess(detector.index("IF    ${has_error}"), detector.index("ELSE IF    ${has_success}"))

    def test_counterexamples_cannot_match_success_markers(self):
        markers = ["you're all set!", "you’re all set!", "let's go", "let’s go"]
        for counterexample in ("registration unsuccessful", "process not completed"):
            self.assertFalse(any(marker in counterexample for marker in markers))


if __name__ == "__main__":
    unittest.main(verbosity=2)
