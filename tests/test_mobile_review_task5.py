from pathlib import Path
import unittest
from types import SimpleNamespace

from libraries.robot_output_sanitizer import RobotOutputSanitizer

ROOT = Path(__file__).resolve().parents[1]


def read(path: str) -> str:
    return (ROOT / path).read_text(encoding="utf-8")


class MobileReviewTask5Contracts(unittest.TestCase):
    def test_primary_mobile_entrypoints_load_output_sanitizer(self):
        for path in (
            "tests/android/etb/etb_regression.robot",
            "tests/android/ntb/ntb_flow.robot",
            "tests/android/onboarding/stage1_onboarding.robot",
            "tests/android/onboarding/onboarding_health_check.robot",
        ):
            with self.subTest(path=path):
                self.assertIn("robot_output_sanitizer.py", read(path))

    def test_health_raw_screenshot_and_source_are_private_local(self):
        text = read("tests/android/onboarding/onboarding_health_check.robot")
        block = text[text.index("Capture After ID Card Photo Evidence\n"):text.index("*** Test Cases ***", text.index("Capture After ID Card Photo Evidence\n"))]
        self.assertIn("${evidence_dir}=    Set Variable    ${OUTPUT_DIR}/private_local/after_id_card_photo", block)
        self.assertIn("Capture Page Screenshot    ${evidence_dir}/screenshot.png", block)
        self.assertIn("Create File    ${evidence_dir}/page_source.xml", block)
        self.assertNotIn("reports/investigation/after_id_card_photo", block)

    def test_terms_raw_evidence_is_private_local(self):
        text = read("resources/pages/common_onboarding/terms_and_conditions_page.resource")
        block = text[text.rindex("Capture Terms Transition Evidence\n"):]
        self.assertIn("Resolve Private Evidence Dir    ${OUTPUT DIR}", block)
        self.assertIn("${evidence_dir}=    Set Variable    ${private_evidence_dir}/terms_transition_", block)
        self.assertIn("Capture Page Screenshot    ${evidence_dir}/screen.png", block)
        self.assertIn("Create File    ${evidence_dir}/page_source.xml", block)
        self.assertNotIn("${OUTPUT DIR}/private_local/terms_transition_", block)

    def test_synthetic_profile_values_are_removed_from_robot_messages_and_args(self):
        sanitizer = RobotOutputSanitizer()
        secret_cid = "1111111111119"
        secret_mobile = "0812345678"
        result = SimpleNamespace(name="Input Citizen ID", args=[secret_cid], doc="")
        sanitizer.start_keyword(None, result)
        self.assertNotIn(secret_cid, str(result.args))
        message = SimpleNamespace(message=f"citizen_id={secret_cid} mobile_number={secret_mobile}")
        sanitizer.log_message(message)
        self.assertNotIn(secret_cid, message.message)
        self.assertNotIn(secret_mobile, message.message)
        self.assertIn("[REDACTED_PROFILE_VALUE]", message.message)

    def test_raw_image_capture_is_only_under_private_evidence_keywords(self):
        health = read("tests/android/onboarding/onboarding_health_check.robot")
        terms = read("resources/pages/common_onboarding/terms_and_conditions_page.resource")
        self.assertIn("${OUTPUT_DIR}/private_local/after_id_card_photo", health)
        self.assertIn("Capture Page Screenshot    ${evidence_dir}/screenshot.png", health)
        self.assertIn("Resolve Private Evidence Dir    ${OUTPUT DIR}", terms)
        self.assertIn("${private_evidence_dir}/terms_transition_", terms)
        self.assertIn("Capture Page Screenshot    ${evidence_dir}/screen.png", terms)


if __name__ == "__main__":
    unittest.main(verbosity=2)
