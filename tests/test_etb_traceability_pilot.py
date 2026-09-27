from __future__ import annotations

import hashlib
import json
import re
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
MAPPING_PATH = ROOT / "configs/etb_traceability_pilot.json"
FULL_MAPPING_PATH = ROOT / "configs/etb_traceability_full.json"
CASE_CONTRACT_PATH = ROOT / "testdata/onboarding/etb_cases.yaml"
SUITE_PATH = ROOT / "tests/android/etb/etb_regression.robot"
ACCEPTANCE_SNAPSHOT_PATH = ROOT / "docs/standards/BBL_ETB_ACCEPTANCE_SNAPSHOT_2026-09-27.md"


def case_block(text: str, key: str, next_key: str | None = None) -> str:
    start_token = f"  {key}:\n"
    start = text.index(start_token)
    if next_key is None:
        end = text.index("\npolicy:\n", start)
    else:
        end = text.index(f"  {next_key}:\n", start)
    return text[start:end]


def scalar(block: str, name: str) -> str:
    match = re.search(rf"^    {re.escape(name)}:\s*([^\n]+)$", block, re.MULTILINE)
    if match is None:
        raise AssertionError(f"missing case field: {name}")
    return match.group(1).strip().strip("'").strip('"')


def int_scalar(block: str, name: str) -> int:
    return int(scalar(block, name))


def inline_list(block: str, name: str) -> list[str]:
    raw = scalar(block, name)
    if raw == "[]":
        return []
    if not (raw.startswith("[") and raw.endswith("]")):
        raise AssertionError(f"{name} is not an inline list: {raw}")
    inner = raw[1:-1].strip()
    return [item.strip().strip("'").strip('"') for item in inner.split(",") if item.strip()]


class ETBTraceabilityPilotTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.mapping = json.loads(MAPPING_PATH.read_text(encoding="utf-8"))
        cls.case_contract_text = CASE_CONTRACT_PATH.read_text(encoding="utf-8")
        cls.blocks = {
            "etb_tc_001": case_block(cls.case_contract_text, "etb_tc_001", "etb_tc_002"),
            "etb_tc_002": case_block(cls.case_contract_text, "etb_tc_002", "etb_tc_003"),
            "etb_tc_003": case_block(cls.case_contract_text, "etb_tc_003", "etb_tc_004"),
            "etb_tc_004": case_block(cls.case_contract_text, "etb_tc_004", "etb_tc_005"),
        }

    def test_schema_scope_and_runtime_boundary(self) -> None:
        self.assertEqual(self.mapping["schema"], "bbl-etb-traceability/v1")
        self.assertEqual(
            self.mapping["scope"],
            ["TC-ETB-001", "TC-ETB-002", "TC-ETB-004"],
        )
        self.assertFalse(self.mapping["pilot_decision"]["product_coverage_percentage_allowed"])
        for item in self.mapping["mappings"]:
            with self.subTest(case_id=item["case_id"]):
                self.assertEqual(item["runtime_validation"], "RUNTIME_EVIDENCE_REQUIRED")
                self.assertFalse(item["coverage_eligible"])
                self.assertNotIn(item["runtime_validation"], {"PASS", "PASSED"})

    def test_ado_live_binding_and_supporting_evidence_are_bounded(self) -> None:
        authority = self.mapping["authority_model"]["ado_work_items"]
        self.assertIn(
            "REQUIREMENT_AUTHORITY_ONLY_WHEN_EXACT_STORY_AC_MAPPING_IS_RECORDED",
            authority,
        )

        binding = self.mapping["ado_binding"]
        self.assertEqual(binding["status"], "LIVE_READ_ONLY_VERIFIED")
        self.assertEqual(binding["provider"], "azure-devops")
        self.assertEqual(binding["effects"], ["READ", "NETWORK"])
        self.assertFalse(binding["write_back_allowed"])
        self.assertEqual(binding["organization"]["name"], "BBLConsumer")
        self.assertEqual(binding["project"]["name"], "ncbd")
        self.assertEqual(binding["team"]["name"], "Board OPO Build")
        self.assertEqual(binding["board"]["name"], "Stories")
        self.assertEqual(
            binding["scope"],
            {
                "field": "System.AreaPath",
                "values": [
                    {
                        "value": r"ncbd\NCBD Build\OPO Build",
                        "includeChildren": False,
                    }
                ],
            },
        )
        self.assertNotIn("credential", json.dumps(binding).lower())
        self.assertNotIn("token", json.dumps(binding).lower())

        evidence = self.mapping["ado_supporting_evidence"]
        self.assertEqual(
            {item["work_item_id"] for item in evidence},
            {108938, 110544},
        )
        allowed_cases = set(self.mapping["scope"])
        for item in evidence:
            with self.subTest(work_item_id=item["work_item_id"]):
                self.assertFalse(item["case_semantics_authority"])
                self.assertFalse(item["acceptance_criteria_present"])
                self.assertEqual(
                    item["workbook_bridge"],
                    "QA_TestCase_OPO_ETB Registration_MMP.xlsx",
                )
                self.assertTrue(set(item["supports_case_ids"]).issubset(allowed_cases))

    def test_tc003_conflict_is_explicitly_excluded(self) -> None:
        excluded = {item["case_id"]: item for item in self.mapping["excluded_cases"]}
        self.assertIn("TC-ETB-003", excluded)
        self.assertEqual(
            excluded["TC-ETB-003"]["status"],
            "EXCLUDED_UNRESOLVED_REQUIREMENT_CONFLICT",
        )
        self.assertIn("clarification_required:\n    - ", self.blocks["etb_tc_003"])
        self.assertFalse(excluded["TC-ETB-003"]["coverage_eligible"])

    def test_workbook_provenance_matches_committed_case_contract(self) -> None:
        source = self.mapping["requirement_source"]
        self.assertIn(f"  file: {source['upstream_file']}", self.case_contract_text)
        self.assertIn(f"  sheet: {source['upstream_sheet']}", self.case_contract_text)
        self.assertFalse(source["upstream_opened_in_r2"])

        expected = {
            "TC-ETB-001": ("etb_tc_001", 4),
            "TC-ETB-002": ("etb_tc_002", 5),
            "TC-ETB-004": ("etb_tc_004", 7),
        }
        by_case = {item["case_id"]: item for item in self.mapping["mappings"]}
        for case_id, (key, row) in expected.items():
            with self.subTest(case_id=case_id):
                self.assertEqual(by_case[case_id]["requirement_provenance"]["source_row"], row)
                self.assertEqual(int_scalar(self.blocks[key], "source_row"), row)

    def test_case_policies_match_current_contract(self) -> None:
        by_case = {item["case_id"]: item for item in self.mapping["mappings"]}
        expectations = {
            "TC-ETB-001": ("etb_tc_001", "MUST_SKIP", []),
            "TC-ETB-002": ("etb_tc_002", "REQUIRED", []),
            "TC-ETB-004": ("etb_tc_004", "UNRESOLVED", ["Saving", "e-Saving"]),
        }
        for case_id, (key, pdpa_policy, categories) in expectations.items():
            with self.subTest(case_id=case_id):
                block = self.blocks[key]
                mapped_policy = by_case[case_id]["automation"]["policy"]
                self.assertEqual(scalar(block, "pdpa_policy"), pdpa_policy)
                self.assertEqual(mapped_policy["pdpa_policy"], pdpa_policy)
                self.assertEqual(inline_list(block, "expected_product_categories"), categories)
                self.assertEqual(mapped_policy.get("expected_product_categories", []), categories)

    def test_figma_evidence_never_claims_case_semantics_authority(self) -> None:
        allowed_support = {
            "PDPA_CLAUSE_6_STRUCTURAL_PRESENCE_ONLY",
            "POST_REGISTRATION_3C_DESIGN_CONTEXT_ONLY",
            "PRODUCT_SELECTION_IMPORT_STRUCTURAL_PRESENCE_ONLY",
        }
        for item in self.mapping["mappings"]:
            for evidence in item["design_evidence"]:
                with self.subTest(case_id=item["case_id"], source=evidence["source_id"]):
                    self.assertFalse(evidence["case_semantics_authority"])
                    self.assertIn(evidence["supports"], allowed_support)
                    self.assertTrue(evidence["node_ids"])
                    self.assertTrue(evidence["source_id"].startswith("SRC-OPO-FIGMA-"))

    def test_assertion_references_are_present_in_current_source(self) -> None:
        for item in self.mapping["mappings"]:
            for ref in item["automation"]["assertion_refs"]:
                with self.subTest(case_id=item["case_id"], path=ref["path"], marker=ref["marker"]):
                    path = ROOT / ref["path"]
                    self.assertTrue(path.is_file(), f"missing assertion source: {path}")
                    source = path.read_text(encoding="utf-8")
                    self.assertIn(ref["keyword"], source)
                    self.assertIn(ref["marker"], source)

    def test_expected_case_specific_assertion_markers_exist(self) -> None:
        source = (ROOT / "resources/keywords/etb/etb_keywords.resource").read_text(encoding="utf-8")
        self.assertIn("PDPA_MUST_SKIP_BUT_DISPLAYED", source)
        self.assertIn("PDPA_REQUIRED_BUT_SKIPPED", source)

        product = (ROOT / "libraries/product_selection_contract.py").read_text(encoding="utf-8")
        self.assertIn("PRODUCT_SELECTION_EXPECTED_CATEGORIES_MISSING", product)

    def test_wiki_binding_is_immutable_and_matches_exact_design_sources(self) -> None:
        binding = self.mapping["wiki_binding"]
        self.assertEqual(binding["snapshot_status"], "VERIFIED_IMMUTABLE_BINDING")
        self.assertEqual(
            binding["clean_checkout_policy"],
            "LOCAL_ONLY_NOT_REQUIRED_FOR_CLEAN_CHECKOUT",
        )
        manifest_path = ROOT / binding["snapshot_manifest"]
        self.assertTrue(manifest_path.is_file())

        manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
        self.assertEqual(manifest["schema"], "bbl-etb-wiki-snapshot/v1")

        expected_pairs = {
            (evidence["source_id"], evidence["wiki_path"])
            for item in self.mapping["mappings"]
            for evidence in item["design_evidence"]
        }
        manifest_pairs = {
            (item["source_id"], item["path"])
            for item in manifest["sources"]
        }
        self.assertEqual(manifest_pairs, expected_pairs)

        for item in manifest["sources"]:
            with self.subTest(source_id=item["source_id"]):
                path = ROOT / item["path"]
                # The source pages are private local evidence and must not enter
                # the delivery commit. Verify their hash when available.
                if not path.is_file():
                    continue
                self.assertEqual(
                    hashlib.sha256(path.read_bytes()).hexdigest(),
                    item["sha256"],
                )

        canonical = json.dumps(
            manifest["sources"],
            sort_keys=True,
            separators=(",", ":"),
        ).encode("utf-8")
        snapshot_hash = hashlib.sha256(canonical).hexdigest()
        self.assertEqual(snapshot_hash, manifest["snapshot_hash"])
        self.assertEqual(snapshot_hash, binding["immutable_snapshot_hash"])



class ETBFullTraceabilityTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.mapping = json.loads(FULL_MAPPING_PATH.read_text(encoding="utf-8"))
        cls.case_contract_text = CASE_CONTRACT_PATH.read_text(encoding="utf-8")
        cls.suite_text = SUITE_PATH.read_text(encoding="utf-8")
        cls.acceptance_snapshot = ACCEPTANCE_SNAPSHOT_PATH.read_text(encoding="utf-8")

    def test_full_scope_is_exactly_tc001_through_tc013(self) -> None:
        expected = [f"TC-ETB-{index:03d}" for index in range(1, 14)]
        self.assertEqual(self.mapping["schema"], "bbl-etb-traceability/v2")
        self.assertEqual(self.mapping["scope"], expected)
        self.assertEqual([item["case_id"] for item in self.mapping["mappings"]], expected)
        self.assertEqual(self.mapping["coverage_policy"]["static_scope_denominator"], 13)
        self.assertEqual(self.mapping["coverage_policy"]["static_scope_mapped"], 13)
        self.assertFalse(self.mapping["coverage_policy"]["runtime_coverage_percentage_allowed"])

    def test_requirement_rows_and_suite_tests_are_bound_for_every_case(self) -> None:
        for index, item in enumerate(self.mapping["mappings"], start=1):
            case_id = f"TC-ETB-{index:03d}"
            key = f"etb_tc_{index:03d}"
            next_key = f"etb_tc_{index + 1:03d}" if index < 13 else None
            block = case_block(self.case_contract_text, key, next_key)
            with self.subTest(case_id=case_id):
                self.assertEqual(item["case_id"], case_id)
                self.assertEqual(item["requirement"]["source_row"], index + 3)
                self.assertEqual(int_scalar(block, "source_row"), index + 3)
                self.assertIn(item["automation"]["test_name"], self.suite_text)
                assertion_path = ROOT / item["automation"]["assertion_path"]
                self.assertTrue(assertion_path.is_file())
                assertion_source = assertion_path.read_text(encoding="utf-8")
                self.assertIn(item["automation"]["assertion_keyword"], assertion_source)

    def test_expected_error_codes_and_terminal_states_match_case_contract(self) -> None:
        for index, item in enumerate(self.mapping["mappings"], start=1):
            key = f"etb_tc_{index:03d}"
            next_key = f"etb_tc_{index + 1:03d}" if index < 13 else None
            block = case_block(self.case_contract_text, key, next_key)
            expected_error = scalar(block, "expected_error_code")
            if expected_error == "null":
                expected_error = None
            with self.subTest(case_id=item["case_id"]):
                self.assertEqual(item["automation"]["expected_error_code"], expected_error)
                self.assertEqual(item["automation"]["terminal_state"], scalar(block, "terminal_state"))

    def test_runtime_bindings_are_separate_from_static_traceability(self) -> None:
        trusted = 0
        for item in self.mapping["mappings"]:
            runtime = item["runtime"]
            with self.subTest(case_id=item["case_id"]):
                self.assertTrue(item["coverage"]["static_traceability"])
                self.assertNotIn(runtime["status"], {"PASS", "PASSED"})
                self.assertEqual(
                    runtime.get("acceptance_source", self.mapping["acceptance_snapshot"]),
                    self.mapping["acceptance_snapshot"],
                )
                local_evidence = runtime.get("local_evidence_index")
                if local_evidence is not None:
                    self.assertTrue(local_evidence.startswith("reports/run-etb/"))
                    self.assertEqual(
                        runtime["evidence_retention"],
                        "LOCAL_ONLY_NOT_REQUIRED_FOR_CLEAN_CHECKOUT",
                    )
                    self.assertIn(runtime["run_id"], self.acceptance_snapshot)
                if runtime["status"] == "TRUSTED_PASS":
                    trusted += 1
                    self.assertTrue(item["coverage"]["runtime_acceptance"])
                    self.assertIn(item["case_id"], self.acceptance_snapshot)
                    self.assertIn("TRUSTED PASS", self.acceptance_snapshot)
                else:
                    self.assertFalse(item["coverage"]["runtime_acceptance"])
        self.assertEqual(trusted, self.mapping["coverage_policy"]["runtime_pass_count"])
        self.assertEqual(
            self.mapping["runtime_binding_policy"]["committed_source"],
            self.mapping["acceptance_snapshot"],
        )

    def test_known_exceptions_remain_explicit(self) -> None:
        exceptions = {item["case_id"]: item for item in self.mapping["exceptions"]}
        self.assertEqual(exceptions["TC-ETB-003"]["type"], "REQUIREMENT_CONFLICT")
        self.assertEqual(exceptions["TC-ETB-013"]["type"], "TEST_DATA_BACKEND_BRANCH")
        tc003 = case_block(self.case_contract_text, "etb_tc_003", "etb_tc_004")
        self.assertIn("clarification_required:\n    - ", tc003)


if __name__ == "__main__":
    unittest.main(verbosity=2)
