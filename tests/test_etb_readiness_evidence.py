from __future__ import annotations

import json
import os
import re
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

ROOT = Path(__file__).resolve().parents[1]
LIBRARY_PATH = ROOT / "libraries" / "etb_readiness_evidence.py"
ETB_RESOURCE = ROOT / "resources" / "keywords" / "etb" / "etb_keywords.resource"
ETB_OBSERVABILITY_RESOURCE = ROOT / "resources" / "diagnostics" / "etb_observability.resource"


class ETBReadinessEvidenceContractTests(unittest.TestCase):
    def _load_library(self):
        self.assertTrue(LIBRARY_PATH.exists(), "ETB_READINESS_LIBRARY_MISSING")
        import importlib.util
        import sys

        spec = importlib.util.spec_from_file_location("etb_readiness_evidence", LIBRARY_PATH)
        self.assertIsNotNone(spec)
        self.assertIsNotNone(spec.loader)
        module = importlib.util.module_from_spec(spec)
        sys.modules[spec.name] = module
        spec.loader.exec_module(module)
        return module

    def test_aji_summary_is_run_case_scoped_and_allowlisted(self):
        module = self._load_library()
        with tempfile.TemporaryDirectory(prefix="bbl-readiness-") as temp:
            root = Path(temp)
            scoped = root / "evidence" / "RUN-001" / "TC-ETB-001"
            scoped.mkdir(parents=True)
            (scoped / "cis_pre_test_result.json").write_text(
                json.dumps(
                    {
                        "cis_clear": "PASS",
                        "cis_state_ready": "YES",
                        "profile_reusable": "YES",
                        "phase": "PRE_TEST",
                        "operation_count": 1,
                        "http_status": 404,
                        "business_result_code": "NOT_FOUND",
                    }
                ),
                encoding="utf-8",
            )
            env = {
                "ETB_RUN_ID": "RUN-001",
                "ETB_CASE_ID": "TC-ETB-001",
                "ETB_ENVIRONMENT": "DEV",
            }
            with patch.dict(os.environ, env, clear=False):
                result_path = Path(
                    module.persist_etb_readiness_summary(
                        str(root),
                        blocker_code="AJI-001",
                        profile_handoff="PASS",
                        dopa_reached=False,
                    )
                )
            self.assertEqual(result_path, scoped / "etb_readiness_summary.json")
            payload = json.loads(result_path.read_text(encoding="utf-8"))
            self.assertEqual(payload["schema"], "etb-readiness/v1")
            self.assertEqual(payload["artifact_classification"], "SHAREABLE_SANITIZED")
            self.assertEqual(payload["run_id"], "RUN-001")
            self.assertEqual(payload["case_id"], "TC-ETB-001")
            self.assertEqual(payload["environment"], "DEV")
            self.assertEqual(payload["build_identity"], "UNPROVEN")
            self.assertEqual(payload["cis_pre_test"], "READY")
            self.assertEqual(payload["profile_handoff"], "PASS")
            self.assertEqual(payload["blocker_code"], "AJI-001")
            self.assertEqual(payload["dopa_reached"], "NO")
            self.assertEqual(payload["backend_health"], "UNPROVEN")
            self.assertEqual(
                payload["resume_condition"],
                "CONFIRM_BACKEND_HEALTH_THEN_RUN_ONE_FOCUSED_TC001",
            )
            self.assertEqual(
                set(payload),
                {
                    "schema",
                    "artifact_classification",
                    "run_id",
                    "case_id",
                    "environment",
                    "build_identity",
                    "cis_pre_test",
                    "profile_handoff",
                    "blocker_code",
                    "dopa_reached",
                    "backend_health",
                    "resume_condition",
                },
            )

    def test_missing_cis_metadata_is_unproven_not_assumed_ready(self):
        module = self._load_library()
        with tempfile.TemporaryDirectory(prefix="bbl-readiness-") as temp:
            with patch.dict(
                os.environ,
                {
                    "ETB_RUN_ID": "RUN-002",
                    "ETB_CASE_ID": "TC-ETB-002",
                    "ETB_ENVIRONMENT": "DEV",
                },
                clear=False,
            ):
                path = Path(
                    module.persist_etb_readiness_summary(
                        temp,
                        blocker_code="AJI-001",
                        profile_handoff="PASS",
                        dopa_reached=False,
                    )
                )
            payload = json.loads(path.read_text(encoding="utf-8"))
            self.assertEqual(payload["cis_pre_test"], "UNPROVEN")
            self.assertEqual(payload["backend_health"], "UNPROVEN")

    def test_summary_never_contains_sensitive_identity_fields_or_raw_values(self):
        module = self._load_library()
        with tempfile.TemporaryDirectory(prefix="bbl-readiness-") as temp:
            with patch.dict(
                os.environ,
                {
                    "ETB_RUN_ID": "RUN-003",
                    "ETB_CASE_ID": "TC-ETB-003",
                    "ETB_ENVIRONMENT": "DEV",
                    "ETB_BUILD_IDENTITY": "build-170",
                },
                clear=False,
            ):
                path = Path(
                    module.persist_etb_readiness_summary(
                        temp,
                        blocker_code="AJI-001",
                        profile_handoff="PASS",
                        dopa_reached=False,
                    )
                )
            text = path.read_text(encoding="utf-8")
            for forbidden in (
                "citizen_id",
                "mobile_number",
                "date_of_birth",
                "laser_code",
                "otp",
                "pin",
                "page_source",
                "raw_xml",
            ):
                self.assertNotIn(forbidden, text.lower())
            self.assertIsNone(re.search(r"\b\d{13}\b", text))
            self.assertIsNone(re.search(r"\b\d{10}\b", text))

    def test_production_aji_branch_persists_summary_before_failure(self):
        source = ETB_RESOURCE.read_text(encoding="utf-8")
        observability = ETB_OBSERVABILITY_RESOURCE.read_text(encoding="utf-8")

        self.assertIn(
            "Resource            ../../diagnostics/etb_observability.resource",
            source,
        )
        self.assertIn("Library          ../../libraries/etb_readiness_evidence.py", observability)

        adapter_marker = "Record ETB Readiness Blocker"
        adapter_start = observability.index(adapter_marker)
        adapter_end = observability.index("\n\n", adapter_start)
        adapter = observability[adapter_start:adapter_end]
        self.assertIn("Persist ETB Readiness Summary", adapter)
        self.assertIn("profile_handoff=PASS", adapter)
        self.assertIn("dopa_reached=${dopa_reached}", adapter)

        marker = "IF    '${common_result}' == '${FLOW_STATE_AJI_001}'"
        start = source.index(marker)
        end = source.index("    END", start)
        branch = source[start:end]
        self.assertIn(
            "Record ETB Readiness Blocker    ${OUTPUT DIR}    ${FLOW_STATE_AJI_001}    ${FALSE}",
            branch,
        )
        self.assertLess(
            branch.index("Record ETB Readiness Blocker"),
            branch.index("Fail    BLOCKED_BY_ENVIRONMENT_BACKEND_AJI_001"),
        )


if __name__ == "__main__":
    unittest.main(verbosity=2)
