from __future__ import annotations

import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def read(relative: str) -> str:
    return (ROOT / relative).read_text(encoding="utf-8")


class EtbArtifactSecurityContractTests(unittest.TestCase):
    def test_robot_debug_screenshot_is_private_local(self):
        text = read("resources/app/app_keywords.resource")
        block = text[text.index("Debug Screenshot"):text.index("Debug Log")]
        self.assertIn("evidence_scope.py", text)
        self.assertIn("Resolve Private Evidence Dir    ${OUTPUT DIR}", block)
        self.assertIn("Capture Page Screenshot    ${evidence_dir}/debug_screenshot.png", block)
        self.assertNotIn("${OUTPUT DIR}/private_local", block)

    def test_mobile_otp_raw_screenshots_and_sources_are_private_local(self):
        page = read("resources/pages/etb/mobile_otp_page.resource")
        diagnostics = read("resources/diagnostics/mobile_otp_observability.resource")

        self.assertIn("mobile_otp_observability.resource", page)
        self.assertNotIn("evidence_scope.py", page)
        self.assertNotIn("Resolve Private Evidence Dir", page)
        self.assertNotIn("Capture Page Screenshot", page)
        self.assertNotIn("Create File", page)

        self.assertIn("evidence_scope.py", diagnostics)
        self.assertIn("Resolve Private Evidence Dir    ${output_dir}", diagnostics)
        self.assertIn(
            "Capture Page Screenshot    ${evidence_dir}/android_resolver_unexpected.png",
            diagnostics,
        )
        self.assertIn(
            "Create File    ${evidence_dir}/android_resolver_unexpected.xml",
            diagnostics,
        )
        self.assertIn("[REDACTED]", diagnostics)
        self.assertNotIn("${OUTPUT DIR}/private_local/", diagnostics)

    def test_python_evidence_writers_use_private_local_and_classification(self):
        scoped = (
            "libraries/failure_evidence.py",
            "libraries/visual_timeline.py",
            "libraries/product_selection_evidence.py",
            "libraries/adb_device.py",
        )
        for relative in scoped:
            with self.subTest(relative=relative):
                text = read(relative)
                self.assertIn("evidence_scope", text)
                self.assertIn("resolve_private_evidence_dir", text)
                self.assertIn("PRIVATE_LOCAL", text)

        preflight = read("tools/real_device_preflight.py")
        self.assertIn("private_local", preflight)
        self.assertIn("PRIVATE_LOCAL", preflight)

    def test_profile_exit_evidence_is_private_and_redacts_sensitive_attributes(self):
        text = read("libraries/profile_exit_evidence.py")
        self.assertIn("evidence_scope", text)
        self.assertIn("resolve_private_evidence_dir", text)
        self.assertIn("[REDACTED]", text)
        self.assertIn("artifact_classification=PRIVATE_LOCAL", text)

    def test_failure_and_product_xml_paths_are_sanitized(self):
        failure = read("libraries/failure_evidence.py")
        product = read("libraries/product_selection_evidence.py")
        self.assertIn("_redact_source", failure)
        self.assertIn("[REDACTED]", failure)
        self.assertIn("product_selection_appium_sanitized.xml", product)
        self.assertIn("_mask", product)


if __name__ == "__main__":
    unittest.main(verbosity=2)
