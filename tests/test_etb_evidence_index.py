from __future__ import annotations

import json
import tempfile
import unittest
from pathlib import Path

import libraries.evidence_index as evidence_index


class ETBEvidenceIndexTests(unittest.TestCase):
    def _write_json(self, path: Path, payload: object) -> None:
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(json.dumps(payload) + "\n", encoding="utf-8")

    def test_index_maps_run_case_stage_and_discovers_unregistered_existing_evidence(self) -> None:
        with tempfile.TemporaryDirectory(prefix="bbl-evidence-index-") as temp:
            root = Path(temp)
            previous_root = evidence_index._PROJECT_ROOT
            evidence_index._PROJECT_ROOT = root
            try:
                output = root / "reports" / "run-etb" / "RUN-INDEX"
                output.mkdir(parents=True)

                self._write_json(
                    output / "run_manifest.json",
                    {
                        "schema": "bbl-etb-run-manifest/v1",
                        "artifact_classification": "SHAREABLE_SANITIZED",
                        "run_id": "RUN-INDEX",
                        "selection": {"case_ids": ["TC-ETB-001", "TC-ETB-003"]},
                    },
                )
                self._write_json(
                    output / "run_result.json",
                    {
                        "schema": "bbl-etb-run-result/v1",
                        "artifact_classification": "SHAREABLE_SANITIZED",
                        "run_id": "RUN-INDEX",
                        "run_status": "FAIL",
                        "result_trust": "UNTRUSTED",
                        "cases": [
                            {
                                "case_id": "TC-ETB-001",
                                "execution_status": "EXECUTED",
                                "business_outcome": "FAIL",
                                "failure_origin": "AUTOMATION",
                                "result_trust": "TRUSTED",
                                "blocker": {"type": None, "code": None},
                            },
                            {
                                "case_id": "TC-ETB-003",
                                "execution_status": "EXECUTED",
                                "business_outcome": "FAIL",
                                "failure_origin": "UNKNOWN",
                                "result_trust": "DEGRADED",
                                "blocker": {"type": None, "code": None},
                            },
                        ],
                    },
                )
                for name in ("output.xml", "log.html", "report.html"):
                    (output / name).write_text("private robot artifact\n", encoding="utf-8")

                case1 = output / "evidence" / "RUN-INDEX" / "TC-ETB-001" / "private_local"
                case1.mkdir(parents=True)
                self._write_json(
                    case1 / "timeline.json",
                    [
                        {
                            "event": "CONFIRM_PIN_VISIBLE",
                            "recognized_state": "CONFIRM_PIN",
                            "screenshot": "confirm_pin.png",
                        },
                        {
                            "event": "MISSING_CHECKPOINT",
                            "recognized_state": "UNKNOWN",
                            "screenshot": "missing_checkpoint.png",
                        },
                    ],
                )
                (case1 / "confirm_pin.png").write_bytes(b"png")
                self._write_json(
                    case1 / "confirm_pin_failure.json",
                    {
                        "schema": "etb-evidence/v2",
                        "artifact_classification": "PRIVATE_LOCAL",
                        "capture_status": "COMPLETE",
                        "operation_status": "COMPLETED",
                        "artifacts": {
                            "screenshot": "PASS",
                            "page_source": "PASS",
                        },
                    },
                )
                (case1 / "confirm_pin_failure.png").write_bytes(b"png")
                (case1 / "confirm_pin_failure.xml").write_text(
                    '<node text="[REDACTED]" />\n', encoding="utf-8"
                )

                case3 = output / "evidence" / "RUN-INDEX" / "TC-ETB-003" / "private_local"
                case3.mkdir(parents=True)
                (case3 / "tc003_physical_screenshot.png").write_bytes(b"png")
                (case3 / "orphan.bin").write_bytes(b"binary")
                self._write_json(
                    case3 / "safe_metadata.json",
                    {
                        "artifact_classification": "PRIVATE_LOCAL",
                        "never_copy_this_secret": "9999999999999",
                    },
                )

                target = evidence_index.build_evidence_index(output, "RUN-INDEX")
                payload = json.loads(target.read_text(encoding="utf-8"))
                serialized = target.read_text(encoding="utf-8")

                self.assertEqual(payload["schema"], "bbl-etb-evidence-index/v1")
                self.assertEqual(payload["run_id"], "RUN-INDEX")
                self.assertEqual(payload["run_status"], "FAIL")
                self.assertEqual(
                    {item["role"]: item["presence"] for item in payload["robot_artifacts"]},
                    {
                        "ROBOT_OUTPUT": "PRESENT",
                        "ROBOT_LOG": "PRESENT",
                        "ROBOT_REPORT": "PRESENT",
                    },
                )
                self.assertTrue(
                    all(item["classification"] == "PRIVATE_LOCAL" for item in payload["robot_artifacts"])
                )

                by_case = {item["case_id"]: item for item in payload["cases"]}
                self.assertEqual(set(by_case), {"TC-ETB-001", "TC-ETB-003"})
                self.assertEqual(
                    by_case["TC-ETB-001"]["status"]["failure_origin"],
                    "AUTOMATION",
                )

                case1_refs = {
                    artifact["ref"]
                    for checkpoint in by_case["TC-ETB-001"]["checkpoints"]
                    for artifact in checkpoint["artifacts"]
                }
                self.assertIn(
                    "reports/run-etb/RUN-INDEX/evidence/RUN-INDEX/TC-ETB-001/private_local/confirm_pin.png",
                    case1_refs,
                )
                self.assertIn(
                    "reports/run-etb/RUN-INDEX/evidence/RUN-INDEX/TC-ETB-001/private_local/confirm_pin_failure.xml",
                    case1_refs,
                )
                self.assertEqual(
                    by_case["TC-ETB-001"]["discovery"]["missing_expected"],
                    [
                        {
                            "stage": "MISSING_CHECKPOINT",
                            "role": "SCREENSHOT",
                            "ref": "reports/run-etb/RUN-INDEX/evidence/RUN-INDEX/TC-ETB-001/private_local/missing_checkpoint.png",
                        }
                    ],
                )

                case3_refs = {
                    artifact["ref"]
                    for checkpoint in by_case["TC-ETB-003"]["checkpoints"]
                    for artifact in checkpoint["artifacts"]
                }
                self.assertIn(
                    "reports/run-etb/RUN-INDEX/evidence/RUN-INDEX/TC-ETB-003/private_local/tc003_physical_screenshot.png",
                    case3_refs,
                    "physical screenshot must be discovered even without producer metadata",
                )
                self.assertEqual(
                    by_case["TC-ETB-003"]["discovery"]["existing_unindexed"],
                    [
                        {
                            "ref": "reports/run-etb/RUN-INDEX/evidence/RUN-INDEX/TC-ETB-003/private_local/orphan.bin",
                            "reason": "UNSUPPORTED_OR_UNMAPPED_ARTIFACT",
                        }
                    ],
                )
                self.assertNotIn("9999999999999", serialized)
                self.assertNotIn("never_copy_this_secret", serialized)
            finally:
                evidence_index._PROJECT_ROOT = previous_root

    def test_missing_robot_artifacts_are_explicit_not_confused_with_unindexed_files(self) -> None:
        with tempfile.TemporaryDirectory(prefix="bbl-evidence-index-missing-") as temp:
            root = Path(temp)
            previous_root = evidence_index._PROJECT_ROOT
            evidence_index._PROJECT_ROOT = root
            try:
                output = root / "reports" / "run-etb" / "RUN-MISSING"
                output.mkdir(parents=True)
                self._write_json(
                    output / "run_manifest.json",
                    {
                        "schema": "bbl-etb-run-manifest/v1",
                        "artifact_classification": "SHAREABLE_SANITIZED",
                        "run_id": "RUN-MISSING",
                        "selection": {"case_ids": ["TC-ETB-004"]},
                    },
                )
                self._write_json(
                    output / "run_result.json",
                    {
                        "schema": "bbl-etb-run-result/v1",
                        "artifact_classification": "SHAREABLE_SANITIZED",
                        "run_id": "RUN-MISSING",
                        "run_status": "RESULT_UNAVAILABLE",
                        "result_trust": "NOT_ASSESSABLE",
                        "cases": [],
                    },
                )

                payload = json.loads(
                    evidence_index.build_evidence_index(output, "RUN-MISSING").read_text(
                        encoding="utf-8"
                    )
                )
                missing_roles = {
                    item["role"] for item in payload["discovery"]["missing_expected"]
                }
                self.assertEqual(
                    missing_roles,
                    {"ROBOT_OUTPUT", "ROBOT_LOG", "ROBOT_REPORT"},
                )
                case = payload["cases"][0]
                self.assertEqual(case["case_id"], "TC-ETB-004")
                self.assertEqual(case["discovery"]["case_evidence_root_presence"], "MISSING")
                self.assertEqual(case["discovery"]["existing_unindexed"], [])
            finally:
                evidence_index._PROJECT_ROOT = previous_root


if __name__ == "__main__":
    unittest.main(verbosity=2)
