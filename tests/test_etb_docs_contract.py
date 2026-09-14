from pathlib import Path
import unittest


ROOT = Path(__file__).resolve().parents[1]
README = (ROOT / "README.md").read_text(encoding="utf-8")
OVERVIEW = (ROOT / "AUTOMATION_OVERVIEW.md").read_text(encoding="utf-8")
AGENTS = (ROOT / "AGENTS.md").read_text(encoding="utf-8")


class ETBDocumentationContractTests(unittest.TestCase):
    def test_readme_documents_current_etb_environments_and_canonical_apks(self):
        for expected in (
            "ETB_ENVIRONMENT=DEV",
            "ETB_ENVIRONMENT=SIT",
            "DEV_MOCK",
            "apps/android/app-dev.apk",
            "apps/android/app-sit-mmplot2.apk",
        ):
            self.assertIn(expected, README)
        self.assertNotIn("Android + DEV เท่านั้น", README)
        self.assertNotIn("apps/android/app.apk", README)

    def test_readme_documents_targeting_dryrun_and_profile_override(self):
        for expected in (
            "DEVICE_UDID",
            "--dry-run",
            "ETB_CASE_PROFILES",
            "requirements-mobile.lock.txt",
            "F17_CLEAN_CHECKOUT_PROOF=PASS",
            "independent clean-machine fresh-install proof ยังไม่ได้รัน",
        ):
            self.assertIn(expected, README)
        self.assertNotIn("Runner ปัจจุบันยังไม่ forward device serial", README)
        self.assertNotIn("การ export path อื่นยังไม่สามารถเปลี่ยน path ที่ suite โหลดได้", README)

    def test_overview_support_matrix_matches_current_runner(self):
        for expected in (
            "Android DEV",
            "Android SIT",
            "DEV_MOCK",
            "apps/android/app-dev.apk",
            "apps/android/app-sit-mmplot2.apk",
            "ETB_CASE_PROFILES",
            "requirements-mobile.lock.txt",
            "ETB_RUN_ID",
        ):
            self.assertIn(expected, OVERVIEW)
        self.assertNotIn("| SIT/UAT | Not configured |", OVERVIEW)
        self.assertNotIn("App package/activity และ environment configuration ยังผูกกับ DEV", OVERVIEW)

    def test_agents_validation_path_uses_current_ntb_suite(self):
        self.assertIn("tests/android/ntb/ntb_flow.robot", AGENTS)
        self.assertNotIn("tests/android/onboarding/ntb_onboarding.robot", AGENTS)


if __name__ == "__main__":
    unittest.main(verbosity=2)
