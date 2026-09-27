from __future__ import annotations

import io
import tempfile
import unittest
from pathlib import Path

from robot import run
from robot.api import ExecutionResult, get_resource_model


ROOT = Path(__file__).resolve().parents[1]
OBSERVABILITY = ROOT / "resources/diagnostics/etb_observability.resource"
CONFIRM_PIN = ROOT / "resources/pages/onboarding/confirm_pin_page.resource"
PDPA = ROOT / "resources/pages/onboarding/pdpa_consent_page.resource"
DOPA = ROOT / "resources/pages/onboarding/dopa_information_page.resource"
TERMS = ROOT / "resources/pages/common_onboarding/terms_and_conditions_page.resource"
PROFILE = ROOT / "resources/diagnostics/profile_observability.resource"


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


class ETBEvidenceCaptureConsolidationTests(unittest.TestCase):
    def assert_shared_capture_only(self, path: Path, keyword: str) -> None:
        body = keyword_body(path, keyword)
        self.assertIn("Record ETB Evidence Capture", body)
        self.assertNotIn("Capture Page Screenshot", body)
        self.assertNotIn("Create File", body)

    def test_checkpoint_and_failure_capture_paths_use_shared_adapter(self) -> None:
        for path in (CONFIRM_PIN, PDPA, DOPA, TERMS):
            with self.subTest(resource=path.name):
                self.assertIn(
                    "diagnostics/etb_observability.resource",
                    path.read_text(encoding="utf-8"),
                )

        self.assert_shared_capture_only(CONFIRM_PIN, "Capture Confirm PIN Failure Evidence")
        self.assert_shared_capture_only(PDPA, "Capture PDPA Blocker Evidence")
        self.assert_shared_capture_only(PDPA, "Capture After PDPA Evidence")
        self.assert_shared_capture_only(DOPA, "Capture DOPA Title Dropdown Evidence")
        self.assert_shared_capture_only(TERMS, "Capture Terms Transition Evidence")

        profile_text = PROFILE.read_text(encoding="utf-8")
        self.assertIn("Resource         etb_observability.resource", profile_text)
        self.assert_shared_capture_only(PROFILE, "Capture Profile Handoff Snapshot Evidence")
        self.assertNotIn("${OUTPUT DIR}/profile_exit_evidence", profile_text)
        self.assertIn(
            "Persist Profile Exit Point    ${point_name}    ${OUTPUT DIR}",
            keyword_body(PROFILE, "Record Profile Exit Evidence Point"),
        )
        self.assertIn(
            "Persist Profile Exit Evidence Summary    ${OUTPUT DIR}",
            keyword_body(PROFILE, "Record Profile Exit Evidence Summary"),
        )

    def test_shared_adapter_capture_failure_does_not_mask_original_failure(self) -> None:
        with tempfile.TemporaryDirectory(prefix="bbl-evidence-adapter-") as directory:
            root = Path(directory)
            resource = root / "adapter.resource"
            resource.write_text(
                "*** Keywords ***\n"
                + keyword_body(OBSERVABILITY, "Record ETB Evidence Capture")
                + "\nCapture ETB Failure Evidence\n"
                + "    [Arguments]    ${output_dir}    ${stem}\n"
                + "    Fail    SYNTHETIC_EVIDENCE_CAPTURE_FAILURE\n",
                encoding="utf-8",
            )
            suite = root / "original_failure.robot"
            suite.write_text(
                """*** Settings ***
Resource    adapter.resource

*** Test Cases ***
Original Failure Remains Terminal
    ${status}    ${message}=    Run Keyword And Ignore Error    Operation With Original Failure
    Should Be Equal    ${status}    FAIL
    Should Be Equal    ${message}    ORIGINAL_AUTOMATION_FAILURE

*** Keywords ***
Operation With Original Failure
    Record ETB Evidence Capture    ${OUTPUT DIR}    confirm_pin_failure
    Fail    ORIGINAL_AUTOMATION_FAILURE
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
