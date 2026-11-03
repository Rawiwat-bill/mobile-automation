from pathlib import Path
import unittest


ROOT = Path(__file__).resolve().parents[1]


class ThreeCPromptContractTests(unittest.TestCase):
    def test_mobile_phone_risk_prompt_uses_scoped_maybe_later_locator(self):
        locators = (ROOT / "locators/android/etb/three_c_locators.resource").read_text()
        page = (ROOT / "resources/pages/etb/three_c_page.resource").read_text()

        self.assertIn('THREE_C_RISK_MAYBE_LATER', locators)
        self.assertIn('@text="Maybe later"', locators)
        self.assertIn('Dismiss Mobile Phone Risk Prompt If Present', page)
        self.assertIn('Click Element    ${THREE_C_RISK_MAYBE_LATER}', page)


if __name__ == "__main__":
    unittest.main()
