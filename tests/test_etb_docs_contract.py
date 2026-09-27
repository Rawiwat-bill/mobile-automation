from pathlib import Path
import json
import unittest


ROOT = Path(__file__).resolve().parents[1]
README = (ROOT / "README.md").read_text(encoding="utf-8")
OVERVIEW = (ROOT / "AUTOMATION_OVERVIEW.md").read_text(encoding="utf-8")
AGENTS = (ROOT / "AGENTS.md").read_text(encoding="utf-8")
PROJECT_WIKI = (ROOT / "docs/PROJECT_WIKI.md").read_text(encoding="utf-8")
TRACEABILITY_MATRIX = (ROOT / "docs/standards/ETB_TRACEABILITY_MATRIX.md").read_text(encoding="utf-8")
BASELINE_AUDIT = (ROOT / "docs/standards/ETB_STANDARD_BASELINE_AUDIT.md").read_text(encoding="utf-8")
FULL_TRACEABILITY = json.loads((ROOT / "configs/etb_traceability_full.json").read_text(encoding="utf-8"))
PACKAGE = json.loads((ROOT / "package.json").read_text(encoding="utf-8"))
ENV_PREP = (ROOT / "tools/env_prep.py").read_text(encoding="utf-8")
APPIUM_LAUNCHER = (ROOT / "tools/appium_server.py").read_text(encoding="utf-8")


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

    def test_legacy_health_check_is_not_documented_as_active(self):
        for text in (README, OVERVIEW):
            self.assertNotIn("./health-check", text)
            self.assertNotIn("run_health_check.sh", text)
            self.assertNotIn("onboarding_health_check.robot", text)

    def test_appium_entrypoints_are_loopback_and_least_privilege(self):
        default = PACKAGE["scripts"]["appium"]
        self.assertEqual(default, "python3 -I tools/appium_server.py")

        inspector = PACKAGE["scripts"]["appium:inspector"]
        self.assertEqual(inspector, "python3 -I tools/appium_server.py --inspector")

        self.assertIn('"--address"', APPIUM_LAUNCHER)
        self.assertIn('"127.0.0.1"', APPIUM_LAUNCHER)
        self.assertIn('"--allow-insecure=uiautomator2:adb_shell"', APPIUM_LAUNCHER)
        self.assertIn('argv.extend(["--use-plugins=inspector", "--allow-cors"])', APPIUM_LAUNCHER)
        self.assertNotIn("--relaxed-security", APPIUM_LAUNCHER)

        self.assertIn('APPIUM_BIND = "127.0.0.1"', ENV_PREP)
        self.assertIn('APPIUM_ALLOW_INSECURE = "uiautomator2:adb_shell"', ENV_PREP)
        self.assertIn('f"--allow-insecure={APPIUM_ALLOW_INSECURE}"', ENV_PREP)
        self.assertNotIn("--relaxed-security", ENV_PREP)

    def test_overview_documents_least_privilege_appium(self):
        self.assertIn("--allow-insecure=uiautomator2:adb_shell", OVERVIEW)
        self.assertIn("pnpm appium:inspector", OVERVIEW)
        self.assertNotIn("--address 127.0.0.1 --relaxed-security", OVERVIEW)

    def test_overview_documents_immutable_run_result_artifacts(self):
        for expected in (
            "reports/run-etb/<ETB_RUN_ID>/",
            "run_manifest.json",
            "run_result.json",
            "latest.json",
            "business_outcome",
            "evidence",
        ):
            self.assertIn(expected, OVERVIEW)


    def test_readme_and_project_wiki_use_managed_least_privilege_appium(self):
        for text in (README, PROJECT_WIKI):
            self.assertIn("pnpm appium", text)
            self.assertIn("--allow-insecure=uiautomator2:adb_shell", text)
            self.assertNotIn("appium --address 127.0.0.1 --relaxed-security", text)

    def test_full_traceability_docs_are_linked_and_do_not_claim_runtime_percentage(self):
        for text in (README, PROJECT_WIKI):
            self.assertIn("ETB_TRACEABILITY_MATRIX.md", text)
            self.assertIn("etb_traceability_full.json", text)
        self.assertEqual(FULL_TRACEABILITY["scope"], [f"TC-ETB-{index:03d}" for index in range(1, 14)])
        self.assertFalse(FULL_TRACEABILITY["coverage_policy"]["runtime_coverage_percentage_allowed"])
        self.assertIn("Static traceability scope is 13/13 cases.", TRACEABILITY_MATRIX)
        self.assertIn("Do not publish a runtime pass percentage", TRACEABILITY_MATRIX)


    def test_baseline_audit_reflects_current_completed_standard_work(self):
        for obsolete in (
            "## 4. Result-semantics gap",
            "## 5. Result-trust gap",
            "## 6. Traceability gap",
            "## 7. Evidence policy gap",
            "immutable snapshot hash is still pending",
        ):
            self.assertNotIn(obsolete, BASELINE_AUDIT)
        for current in (
            "## 4. Result-semantics status",
            "## 5. Result-trust status",
            "## 6. Traceability status",
            "## 7. Evidence policy status",
            "configs/etb_traceability_full.json",
            "docs/standards/ETB_TRACEABILITY_MATRIX.md",
        ):
            self.assertIn(current, BASELINE_AUDIT)


if __name__ == "__main__":
    unittest.main(verbosity=2)
