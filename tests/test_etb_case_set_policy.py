from __future__ import annotations

import importlib.util
import json
import re
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
MANIFEST_PATH = ROOT / "configs" / "etb_case_set.json"
RUNTIME_PATH = ROOT / "tools" / "runner" / "etb_runtime.py"
SUITE_PATH = ROOT / "tests" / "android" / "etb" / "etb_regression.robot"
CONTRACT_PATH = ROOT / "testdata" / "onboarding" / "etb_cases.yaml"


def load_runtime():
    spec = importlib.util.spec_from_file_location("etb_runtime_case_set_test", RUNTIME_PATH)
    if spec is None or spec.loader is None:
        raise AssertionError("ETB_RUNTIME_IMPORT_FAILED")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def suite_case_ids() -> list[str]:
    ids: list[str] = []
    in_tests = False
    for line in SUITE_PATH.read_text(encoding="utf-8").splitlines():
        if line.strip() == "*** Test Cases ***":
            in_tests = True
            continue
        if in_tests and line.startswith("*** "):
            break
        if in_tests and line and not line[0].isspace():
            match = re.match(r"^(TC-ETB-\d{3})(?:\s|$)", line.strip())
            if match:
                ids.append(match.group(1))
    return ids


def contract_case_ids() -> list[str]:
    return re.findall(
        r"^\s+tc_id:\s*(TC-ETB-\d{3})\s*$",
        CONTRACT_PATH.read_text(encoding="utf-8"),
        flags=re.MULTILINE,
    )


class ETBCaseSetPolicyTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.manifest = json.loads(MANIFEST_PATH.read_text(encoding="utf-8"))
        cls.runtime = load_runtime()

    def test_manifest_suite_and_case_contract_have_same_ordered_ids(self) -> None:
        expected = self.manifest["canonical_case_ids"]
        self.assertEqual(self.manifest["schema"], "bbl-etb-case-set/v1")
        self.assertEqual(suite_case_ids(), expected)
        self.assertEqual(contract_case_ids(), expected)
        self.assertEqual(len(expected), len(set(expected)))

    def test_full_suite_runner_uses_manifest_not_magic_number(self) -> None:
        selection = (ROOT / "tools/runner/etb_selection.sh").read_text(encoding="utf-8")
        self.assertIn("validate-case-set", selection)
        self.assertIn("configs/etb_case_set.json", selection)
        self.assertNotIn('selected_count" != "13"', selection)
        self.assertNotIn("expected 13", selection)

    def test_release_override_is_validated_and_forwarded_to_robot(self) -> None:
        configuration = (ROOT / "tools/runner/etb_configuration.sh").read_text(encoding="utf-8")
        self.assertIn("ETB_PRODUCT_RELEASE", configuration)
        self.assertIn("MMP_LOT2_V2|POST_MMP_1", configuration)
        self.assertIn('robot_variable_args+=(--variable "ETB_PRODUCT_RELEASE:${ETB_PRODUCT_RELEASE}")', configuration)

    def test_validate_case_set_accepts_exact_set_and_order(self) -> None:
        expected = list(self.manifest["canonical_case_ids"])
        self.assertEqual(self.runtime.validate_case_set(str(MANIFEST_PATH), expected), 0)

    def test_validate_case_set_rejects_missing_extra_duplicate_and_order_change(self) -> None:
        expected = list(self.manifest["canonical_case_ids"])
        cases = {
            "missing": expected[:-1],
            "extra": [*expected, "TC-ETB-999"],
            "duplicate": [*expected[:-1], expected[-2]],
            "order": [expected[1], expected[0], *expected[2:]],
        }
        for label, selected in cases.items():
            with self.subTest(label=label):
                self.assertEqual(
                    self.runtime.validate_case_set(str(MANIFEST_PATH), selected),
                    3,
                )

    def test_tc004_is_independent_in_full_suite(self) -> None:
        policy = self.manifest["execution_policies"]
        self.assertEqual(policy["full_suite"], "CONTINUE_INDEPENDENT_CASES")
        self.assertEqual(policy["tc004"], "INDEPENDENT_PREPARATION_AND_ASSERTIONS")
        keywords = (ROOT / "resources/keywords/etb/etb_regression_keywords.resource").read_text(encoding="utf-8")
        suite = SUITE_PATH.read_text(encoding="utf-8")
        self.assertNotIn("Require TC003 Control Home For TC004", keywords)
        self.assertNotIn("TC003_CONTROL_HOME_NOT_PROVEN", keywords)
        self.assertLess(
            suite.index("TC-ETB-003 Positive Product Selection Variant"),
            suite.index("TC-ETB-004 Positive Product Selection Existing Accounts"),
        )

    def test_case_manifest_is_safe_non_runtime_metadata(self) -> None:
        text = MANIFEST_PATH.read_text(encoding="utf-8").lower()
        for forbidden in (
            "citizen_id",
            "mobile_number",
            "date_of_birth",
            "laser_code",
            "otp",
            "password",
            "account_number",
        ):
            self.assertNotIn(forbidden, text)


if __name__ == "__main__":
    unittest.main(verbosity=2)
