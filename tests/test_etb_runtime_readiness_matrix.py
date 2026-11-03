from __future__ import annotations

import json
import re
import unittest
from pathlib import Path

import yaml

ROOT = Path(__file__).resolve().parents[1]
SUITE = ROOT / "tests/android/etb/etb_regression.robot"
CASE_SET = ROOT / "configs/etb_case_set.json"
PROFILE = ROOT / "testdata/onboarding/etb_cases.yaml"


def suite_cases() -> list[tuple[str, set[str]]]:
    rows: list[tuple[str, set[str]]] = []
    current: str | None = None
    in_cases = False
    for raw in SUITE.read_text(encoding="utf-8").splitlines():
        stripped = raw.strip()
        if stripped == "*** Test Cases ***":
            in_cases = True
            continue
        if in_cases and stripped.startswith("*** "):
            break
        if in_cases and raw and not raw[0].isspace() and stripped:
            match = re.match(r"^(TC-ETB-\d{3})\b", stripped)
            if match:
                current = match.group(1)
                rows.append((current, set()))
            continue
        if in_cases and current and stripped.startswith("[Tags]"):
            rows[-1][1].update(stripped.split()[1:])
    return rows


class EtbRuntimeReadinessMatrixTests(unittest.TestCase):
    def test_suite_and_canonical_manifest_are_exactly_001_through_013(self):
        expected = [f"TC-ETB-{index:03d}" for index in range(1, 14)]
        manifest = json.loads(CASE_SET.read_text(encoding="utf-8"))
        self.assertEqual(manifest["canonical_case_ids"], expected)
        self.assertEqual([case_id for case_id, _ in suite_cases()], expected)

    def test_smoke_scope_is_exactly_tc001_and_tc005(self):
        smoke = [case_id for case_id, tags in suite_cases() if "smoke" in tags]
        self.assertEqual(smoke, ["TC-ETB-001", "TC-ETB-005"])

    def test_all_case_contracts_are_enabled_and_approved_to_attempt_runtime(self):
        payload = yaml.safe_load(PROFILE.read_text(encoding="utf-8"))
        cases = payload["cases"]
        self.assertEqual(len(cases), 13)
        for index in range(1, 14):
            key = f"etb_tc_{index:03d}"
            case = cases[key]
            with self.subTest(case=key):
                self.assertTrue(case["enabled"])
                self.assertEqual(case["execution_status"], "APPROVED_TO_PROCEED")
                self.assertEqual(case["readiness"], "READY_TO_ATTEMPT_RUNTIME")
                self.assertEqual(case["runtime_status"], "RUNTIME_EVIDENCE_REQUIRED")

    def test_exception_expected_error_codes_remain_canonical(self):
        payload = yaml.safe_load(PROFILE.read_text(encoding="utf-8"))
        cases = payload["cases"]
        expected = {
            "etb_tc_005": "RGI-079",
            "etb_tc_006": "RGI-076",
            "etb_tc_007": "RGI-012",
            "etb_tc_008": "RGI-014",
            "etb_tc_009": "RGI-014",
            "etb_tc_010": "RGI-014",
            "etb_tc_011": "RGI-014",
            "etb_tc_012": "RGI-013",
            "etb_tc_013": "RGI-016",
        }
        for key, code in expected.items():
            with self.subTest(case=key):
                self.assertEqual(cases[key]["expected_error_code"], code)

    def test_tc003_product_skip_and_tc004_independent_execution_policy(self):
        payload = yaml.safe_load(PROFILE.read_text(encoding="utf-8"))
        tc003 = payload["cases"]["etb_tc_003"]
        self.assertTrue(tc003["clarification_required"])
        self.assertEqual(tc003["product_selection_policy"], "MUST_SKIP")

        manifest = json.loads(CASE_SET.read_text(encoding="utf-8"))
        self.assertEqual(manifest["execution_policies"]["tc004"], "INDEPENDENT_PREPARATION_AND_ASSERTIONS")


if __name__ == "__main__":
    unittest.main(verbosity=2)
