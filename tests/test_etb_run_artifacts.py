from __future__ import annotations

import importlib.util
import json
import tempfile
import unittest
import xml.etree.ElementTree as ET
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
RUNTIME_PATH = ROOT / "tools" / "runner" / "etb_runtime.py"


def load_runtime():
    spec = importlib.util.spec_from_file_location("etb_runtime_r3_test", RUNTIME_PATH)
    if spec is None or spec.loader is None:
        raise AssertionError("ETB_RUNTIME_IMPORT_FAILED")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def write_output_xml(path: Path) -> None:
    root = ET.Element("robot")
    suite = ET.SubElement(root, "suite", name="ETB")

    passed = ET.SubElement(suite, "test", name="TC-ETB-001 Positive Registration Success")
    keyword = ET.SubElement(passed, "kw", name="cleanup")
    ET.SubElement(keyword, "msg").text = "APPIUM_SESSION_CLOSE=PASS"
    ET.SubElement(passed, "status", status="PASS").text = ""

    blocked = ET.SubElement(suite, "test", name="TC-ETB-002 Positive Registration With PDPA Clause 6")
    ET.SubElement(blocked, "msg").text = "APPIUM_SESSION_CLOSE=NOT_REQUIRED"
    ET.SubElement(blocked, "status", status="FAIL").text = (
        "BLOCKED_BY_ENVIRONMENT_BACKEND_AJI_001: service unavailable"
    )

    skipped = ET.SubElement(suite, "test", name="TC-ETB-003 Positive Product Selection Variant")
    ET.SubElement(skipped, "kw", name="policy")
    ET.SubElement(skipped, "status", status="SKIP").text = "TC003_CONTROL_HOME_NOT_PROVEN"

    ET.ElementTree(root).write(path, encoding="unicode")


class ETBRunArtifactsTests(unittest.TestCase):
    def setUp(self) -> None:
        self.runtime = load_runtime()

    def init_run(self, base: Path, run_id: str) -> Path:
        output = base / run_id
        args = [
            str(output),
            str(base),
            run_id,
            "DEV",
            "DIAGNOSTIC_CONTROL",
            "test",
            "TC-ETB-001",
            "feature/etb-regression-pack",
            "48c09a1cd975695c05da09b770c78cb502c38450",
            "57",
            "62",
            "7",
            "stagedfingerprint",
            "worktreefingerprint",
            "build-001",
            "POST_MMP_1",
            "emulator-5556",
            "TC-ETB-001",
        ]
        self.assertEqual(self.runtime.initialize_run_artifacts(args), 0)
        return output

    def test_run_ids_create_distinct_roots_and_latest_pointer_moves_only(self) -> None:
        with tempfile.TemporaryDirectory(prefix="bbl-r3-run-root-") as temp:
            base = Path(temp) / "reports" / "run-etb"
            first = self.init_run(base, "RUN-001")
            second = self.init_run(base, "RUN-002")

            self.assertTrue((first / "run_manifest.json").is_file())
            self.assertTrue((second / "run_manifest.json").is_file())
            self.assertNotEqual(first, second)

            latest = json.loads((base / "latest.json").read_text(encoding="utf-8"))
            self.assertEqual(latest["run_id"], "RUN-002")
            self.assertTrue((first / "run_manifest.json").is_file())

    def test_manifest_separates_code_runtime_selection_and_knowledge_binding(self) -> None:
        with tempfile.TemporaryDirectory(prefix="bbl-r3-manifest-") as temp:
            base = Path(temp) / "run-etb"
            output = self.init_run(base, "RUN-MANIFEST")
            manifest = json.loads((output / "run_manifest.json").read_text(encoding="utf-8"))

            self.assertEqual(manifest["schema"], "bbl-etb-run-manifest/v1")
            self.assertEqual(manifest["run_id"], "RUN-MANIFEST")
            self.assertEqual(manifest["selection"]["case_ids"], ["TC-ETB-001"])
            self.assertEqual(manifest["runtime"]["environment"], "DEV")
            self.assertEqual(manifest["runtime"]["product_release"], "POST_MMP_1")
            self.assertEqual(manifest["runtime"]["device_udid"], "emulator-5556")
            self.assertEqual(manifest["code"]["branch"], "feature/etb-regression-pack")
            self.assertEqual(manifest["code"]["head"], "48c09a1cd975695c05da09b770c78cb502c38450")
            self.assertTrue(manifest["code"]["dirty"])
            self.assertIn("traceability_sha256", manifest["knowledge_binding"])
            self.assertIn("wiki_snapshot_status", manifest["knowledge_binding"])

    def test_finalize_separates_business_blocker_cleanup_and_evidence(self) -> None:
        with tempfile.TemporaryDirectory(prefix="bbl-r3-result-") as temp:
            base = Path(temp) / "run-etb"
            output = self.init_run(base, "RUN-RESULT")
            write_output_xml(output / "output.xml")

            evidence_001 = output / "evidence" / "RUN-RESULT" / "TC-ETB-001"
            private_001 = evidence_001 / "private_local"
            private_001.mkdir(parents=True)
            (evidence_001 / "cis_post_test_result.json").write_text(
                json.dumps({"cis_clear": "PASS"}) + "\n",
                encoding="utf-8",
            )
            (private_001 / "capture.json").write_text(
                json.dumps(
                    {
                        "schema": "etb-evidence/v2",
                        "capture_status": "COMPLETE",
                        "operation_status": "COMPLETED",
                    }
                )
                + "\n",
                encoding="utf-8",
            )

            private_002 = output / "evidence" / "RUN-RESULT" / "TC-ETB-002" / "private_local"
            private_002.mkdir(parents=True)
            (private_002 / "capture.json").write_text(
                json.dumps(
                    {
                        "schema": "etb-evidence/v2",
                        "capture_status": "TIMEOUT",
                        "operation_status": "COMPLETED",
                    }
                )
                + "\n",
                encoding="utf-8",
            )

            self.assertEqual(self.runtime.finalize_run_artifacts(str(output), "RUN-RESULT"), 0)
            result = json.loads((output / "run_result.json").read_text(encoding="utf-8"))

            self.assertEqual(result["schema"], "bbl-etb-run-result/v1")
            self.assertEqual(result["run_status"], "BLOCKED")
            self.assertEqual(result["result_trust"], "UNTRUSTED")
            by_case = {item["case_id"]: item for item in result["cases"]}

            self.assertEqual(by_case["TC-ETB-001"]["business_outcome"], "PASS")
            self.assertIsNone(by_case["TC-ETB-001"]["failure_origin"])
            self.assertEqual(by_case["TC-ETB-001"]["result_trust"], "TRUSTED")
            self.assertEqual(by_case["TC-ETB-001"]["cleanup"]["cis"]["status"], "PASS")
            self.assertEqual(by_case["TC-ETB-001"]["cleanup"]["appium_session"], "PASS")
            self.assertEqual(by_case["TC-ETB-001"]["evidence"]["status"], "COMPLETE")

            self.assertEqual(by_case["TC-ETB-002"]["business_outcome"], "BLOCKED")
            self.assertEqual(by_case["TC-ETB-002"]["failure_origin"], "ENVIRONMENT")
            self.assertEqual(by_case["TC-ETB-002"]["result_trust"], "UNTRUSTED")
            self.assertEqual(by_case["TC-ETB-002"]["blocker"]["type"], "ENVIRONMENT")
            self.assertEqual(by_case["TC-ETB-002"]["blocker"]["code"], "AJI-001")
            self.assertEqual(by_case["TC-ETB-002"]["evidence"]["status"], "INCOMPLETE")
            self.assertEqual(by_case["TC-ETB-002"]["cleanup"]["appium_session"], "NOT_REQUIRED")

            self.assertEqual(by_case["TC-ETB-003"]["business_outcome"], "SKIPPED")
            self.assertEqual(by_case["TC-ETB-003"]["execution_status"], "EXECUTED")
            self.assertEqual(by_case["TC-ETB-003"]["failure_origin"], "EXECUTION_POLICY")
            self.assertEqual(by_case["TC-ETB-003"]["result_trust"], "TRUSTED")
            self.assertEqual(
                by_case["TC-ETB-003"]["blocker"]["code"],
                "TC003_CONTROL_HOME_NOT_PROVEN",
            )

    def test_missing_robot_output_is_explicit_result_unavailable(self) -> None:
        with tempfile.TemporaryDirectory(prefix="bbl-r3-missing-output-") as temp:
            base = Path(temp) / "run-etb"
            output = self.init_run(base, "RUN-MISSING")
            self.assertEqual(self.runtime.finalize_run_artifacts(str(output), "RUN-MISSING"), 4)
            result = json.loads((output / "run_result.json").read_text(encoding="utf-8"))
            self.assertEqual(result["run_status"], "RESULT_UNAVAILABLE")
            self.assertEqual(result["result_trust"], "NOT_ASSESSABLE")
            self.assertEqual(result["cases"], [])

    def test_pass_requires_complete_evidence_and_proven_cleanup_for_trust(self) -> None:
        cleanup = {
            "cis": {"status": "PASS"},
            "pdpa": "NOT_APPLICABLE",
            "appium_session": "PASS",
        }
        self.assertEqual(
            self.runtime._case_result_trust(
                "PASS",
                {"type": None, "code": None},
                None,
                cleanup,
                {"status": "COMPLETE"},
            ),
            "TRUSTED",
        )
        self.assertEqual(
            self.runtime._case_result_trust(
                "PASS",
                {"type": None, "code": None},
                None,
                cleanup,
                {"status": "INCOMPLETE"},
            ),
            "UNTRUSTED",
        )

    def test_failure_with_failed_cleanup_is_not_trusted(self) -> None:
        self.assertEqual(
            self.runtime._case_result_trust(
                "FAIL",
                {"type": "AUTOMATION", "code": "SESSION_CLOSE_FAILED"},
                "AUTOMATION",
                {
                    "cis": {"status": "FAIL"},
                    "pdpa": "FAIL",
                    "appium_session": "FAIL",
                },
                {"status": "COMPLETE"},
            ),
            "UNTRUSTED",
        )

    def test_pdpa_best_effort_states_are_preserved(self) -> None:
        self.assertEqual(
            self.runtime._pdpa_cleanup(
                ["CASE_SPECIFIC_PDPA_CLEANUP=ATTEMPTED status=CLEAR_REQUEST_SUBMITTED semantic_verifiable=False"]
            ),
            "ATTEMPTED_UNVERIFIED",
        )
        self.assertEqual(
            self.runtime._pdpa_cleanup(
                ["CASE_SPECIFIC_PDPA_CLEANUP=BEST_EFFORT_WARNING status=FAIL"]
            ),
            "BEST_EFFORT_WARNING",
        )
        cleanup = {
            "cis": {"status": "PASS"},
            "pdpa": "ATTEMPTED_VERIFIED",
            "appium_session": "PASS",
        }
        for outcome in ("PASS", "BLOCKED"):
            self.assertEqual(
                self.runtime._case_result_trust(
                    outcome,
                    {"type": "ENVIRONMENT", "code": "GOD-005"},
                    "ENVIRONMENT",
                    cleanup,
                    {"status": "COMPLETE"},
                ),
                "TRUSTED",
            )

    def test_fatal_suite_tail_is_not_business_failure(self) -> None:
        test = ET.Element("test", name="TC-ETB-013 Mule Warning")
        ET.SubElement(test, "status", status="FAIL").text = "Test execution stopped due to a fatal error."
        self.assertEqual(self.runtime._execution_status(test, "Test execution stopped due to a fatal error."), "UNEXECUTED")
        self.assertEqual(
            self.runtime._case_result_trust(
                "NOT_RUN",
                {"type": "EXECUTION", "code": "NOT_STARTED"},
                "EXECUTION",
                {"cis": {"status": "UNPROVEN"}, "pdpa": "UNPROVEN", "appium_session": "UNPROVEN"},
                {"status": "NOT_REQUESTED"},
            ),
            "NOT_ASSESSABLE",
        )

    def test_failure_origin_is_conservative_and_does_not_invent_product_failure(self) -> None:
        self.assertEqual(
            self.runtime._failure_origin("FAIL", "unexpected business assertion"),
            "UNKNOWN",
        )
        self.assertEqual(
            self.runtime._failure_origin("FAIL", "SESSION_CLOSE_FAILED"),
            "AUTOMATION",
        )
        self.assertEqual(
            self.runtime._failure_origin(
                "FAIL",
                "Evaluating expression \"$picker_rect['y']\" failed: TypeError: unsupported operand type(s) for +: 'int' and 'str'.",
            ),
            "AUTOMATION",
        )
        self.assertEqual(
            self.runtime._failure_origin("BLOCKED", "BLOCKED_BY_ENVIRONMENT_BACKEND_AJI_001"),
            "ENVIRONMENT",
        )
        self.assertEqual(
            self.runtime._failure_origin("FAIL", "TERMS_CONTENT_NOT_RENDERED"),
            "UNKNOWN",
        )
        self.assertEqual(
            self.runtime._failure_origin(
                "FAIL",
                "TERMS_CONTENT_NOT_RENDERED_AFTER_5_RECOVERY_ATTEMPTS",
            ),
            "APPLICATION",
        )

    def test_failure_origin_uses_terminal_keyword_not_recovered_messages(self) -> None:
        root = ET.Element("test", name="TC-ETB-002")
        recovered = ET.SubElement(root, "kw", name="handled retry")
        ET.SubElement(recovered, "msg").text = (
            "Evaluating expression failed: TypeError: stale intermediate value"
        )
        ET.SubElement(recovered, "status", status="PASS").text = "PASS"
        terminal = ET.SubElement(root, "kw", name="final assertion")
        ET.SubElement(terminal, "msg").text = "PROFILE_POPUP_CODE_UNPROVEN"
        ET.SubElement(terminal, "status", status="FAIL").text = "FAIL"
        self.assertEqual(
            self.runtime._failure_origin(
                "FAIL",
                "Evaluating expression failed: TypeError: stale intermediate value\nPROFILE_POPUP_CODE_UNPROVEN",
                self.runtime._terminal_failure_text(root),
            ),
            "UNKNOWN",
        )

    def test_failure_origin_accepts_terminal_evaluate_failure(self) -> None:
        root = ET.Element("test", name="TC-ETB-002")
        terminal = ET.SubElement(root, "kw", name="DOB picker")
        ET.SubElement(terminal, "msg").text = (
            "Evaluating expression \"$picker_rect['y']\" failed: "
            "TypeError: unsupported operand type(s)"
        )
        ET.SubElement(terminal, "status", status="FAIL").text = "FAIL"
        self.assertEqual(
            self.runtime._failure_origin(
                "FAIL",
                self.runtime._terminal_failure_text(root),
                self.runtime._terminal_failure_text(root),
            ),
            "AUTOMATION",
        )

    def test_primary_body_failure_wins_over_unhandled_teardown_message(self) -> None:
        root = ET.Element("test", name="TC-ETB-002")
        body = ET.SubElement(root, "kw", name="body")
        ET.SubElement(body, "status", status="FAIL").text = "PROFILE_POPUP_CODE_UNPROVEN"
        teardown = ET.SubElement(root, "kw", name="teardown", type="teardown")
        ET.SubElement(teardown, "msg").text = "Evaluating expression failed: TypeError: teardown"
        ET.SubElement(teardown, "status", status="FAIL").text = "teardown failed"
        terminal = self.runtime._terminal_failure_text(root)
        self.assertEqual(terminal, "PROFILE_POPUP_CODE_UNPROVEN")
        self.assertEqual(self.runtime._failure_origin("FAIL", terminal, terminal), "UNKNOWN")

    def test_exhausted_terms_recovery_is_explicit_trusted_application_failure(self) -> None:
        marker = "TERMS_CONTENT_NOT_RENDERED_AFTER_5_RECOVERY_ATTEMPTS"
        outcome, blocker = self.runtime._business_outcome(
            "FAIL",
            f"Keyword failed after bounded hydration recovery: {marker}",
        )
        self.assertEqual(outcome, "FAIL")
        self.assertEqual(blocker, {"type": "APPLICATION", "code": marker})
        origin = self.runtime._failure_origin(outcome, marker)
        self.assertEqual(origin, "APPLICATION")
        self.assertEqual(
            self.runtime._case_result_trust(
                outcome,
                blocker,
                origin,
                {
                    "cis": {"status": "PASS"},
                    "pdpa": "NOT_APPLICABLE",
                    "appium_session": "PASS",
                },
                {"status": "COMPLETE"},
            ),
            "TRUSTED",
        )

    def test_negative_error_assertions_do_not_invent_environment_blocker(self) -> None:
        outcome, blocker = self.runtime._business_outcome(
            "FAIL",
            "page source does not contain 'AJI-001'; ETB_POST_PIN_DESTINATION_NOT_VISIBLE",
        )
        self.assertEqual(outcome, "FAIL")
        self.assertEqual(blocker, {"type": None, "code": None})

    def test_explicit_post_pin_god_005_is_environment_blocker(self) -> None:
        marker = "BLOCKED_BY_ENVIRONMENT_BACKEND_GOD_005: service unavailable after PIN."
        outcome, blocker = self.runtime._business_outcome("FAIL", marker)
        self.assertEqual(outcome, "BLOCKED")
        self.assertEqual(blocker, {"type": "ENVIRONMENT", "code": "GOD-005"})

    def test_explicit_pre_dopa_rai_033_keeps_root_cause_unknown(self) -> None:
        marker = "PROFILE_RESPONSE_UNEXPECTED_RAI_033: observed before DOPA."
        outcome, blocker = self.runtime._business_outcome("FAIL", marker)
        self.assertEqual(outcome, "FAIL")
        self.assertEqual(blocker, {"type": "OBSERVED_RESPONSE", "code": "RAI-033"})
        origin = self.runtime._failure_origin(outcome, marker, marker)
        self.assertEqual(origin, "UNKNOWN")

    def test_landing_full_screen_gub_is_explicit_application_failure(self) -> None:
        marker = "LANDING_FULL_SCREEN_GUB_AFTER_ACTION"
        outcome, blocker = self.runtime._business_outcome("FAIL", marker)
        self.assertEqual(outcome, "FAIL")
        self.assertEqual(blocker, {"type": "APPLICATION", "code": marker})
        origin = self.runtime._failure_origin(outcome, marker, marker)
        self.assertEqual(origin, "APPLICATION")


    def test_runner_sources_use_run_id_root_and_result_finalization(self) -> None:
        run = (ROOT / "run").read_text(encoding="utf-8")
        config = (ROOT / "tools/runner/etb_configuration.sh").read_text(encoding="utf-8")
        selection = (ROOT / "tools/runner/etb_selection.sh").read_text(encoding="utf-8")
        execution = (ROOT / "tools/runner/etb_execution.sh").read_text(encoding="utf-8")

        self.assertIn('ETB_OUTPUT_BASE="$ETB_OUTPUT"', run)
        self.assertIn('ETB_OUTPUT="$ETB_OUTPUT_BASE/$ETB_RUN_ID"', config)
        self.assertIn("init-run", config)
        self.assertNotIn('ETB_OUTPUT="$ETB_OUTPUT/$selector_value"', selection)
        self.assertIn("finalize-run", execution)
        self.assertIn('return "$robot_exit"', execution)


if __name__ == "__main__":
    unittest.main(verbosity=2)
