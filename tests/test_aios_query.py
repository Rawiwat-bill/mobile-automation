import json
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

from tools import aios_query as query_engine
from tools.aios_query_schema import validate_response
from tools.hermes_query_gate import query_before_action


class AiosQueryTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.root = Path(self.temp.name)
        mission_dir = self.root / ".runtime" / "aios" / "missions"
        mission_dir.mkdir(parents=True)
        (mission_dir / "etb-runtime-baseline.yaml").write_text(
            """mission_id: etb-runtime-baseline
status: BLOCKED
current_gate: RUNTIME_VERIFY_PASS
last_result:
  classification: ENVIRONMENT_BACKEND_BLOCKER
  blocker_code: AJI-001
  deepest_screen: Beyond Terms
  last_successful_keyword: Terms acceptance transition completed
blockers:
  - code: AJI-001
    classification: ENVIRONMENT_BACKEND_BLOCKER
    lifecycle: ACTIVE
    message: Service is not available now. Please try again later.
  - code: TERMS_ACCEPT_TRANSITION_NOT_COMPLETED
    lifecycle: RESOLVED
    resolution: Terms transition completed in later evidence.
  - code: TERMS_ACCEPT_LOCATOR
    lifecycle: SUPERSEDED
    resolution: Later runtime superseded the locator checkpoint.
""",
            encoding="utf-8",
        )
        report_dir = self.root / "reports" / "investigation" / "terms_history"
        report_dir.mkdir(parents=True)
        (report_dir / "REPORT.md").write_text(
            """# Terms history

The Terms transition investigation was already performed. The approved pattern uses
ADB-first interaction and the Tell us about you marker.
""",
            encoding="utf-8",
        )

    def tearDown(self):
        self.temp.cleanup()

    def test_current_active_blocker_uses_canonical_mission_state(self):
        result = query_engine.query(
            "etb-runtime-baseline", "What is the current active blocker?", root=self.root
        )
        self.assertEqual(result["repository_answer_exists"], True)
        self.assertEqual(result["confidence"], "HIGH")
        self.assertIn("AJI-001", result["existing_answer"])
        self.assertEqual(set(result), {"repository_answer_exists", "confidence", "answer_source", "existing_answer"})

    def test_lifecycle_queries_separate_resolved_and_superseded(self):
        resolved = query_engine.query("etb-runtime-baseline", "Which blockers are resolved?", root=self.root)
        superseded = query_engine.query("etb-runtime-baseline", "Which findings are superseded?", root=self.root)
        self.assertIn("TERMS_ACCEPT_TRANSITION_NOT_COMPLETED", resolved["existing_answer"])
        self.assertIn("TERMS_ACCEPT_LOCATOR", superseded["existing_answer"])

    def test_repository_answer_prevents_new_investigation(self):
        result = query_engine.query(
            "etb-runtime-baseline", "Has this Terms transition investigation already been performed?", root=self.root
        )
        self.assertTrue(result["repository_answer_exists"])
        self.assertIn("reports/investigation/terms_history/REPORT.md", result["answer_source"])

    def test_missing_question_returns_exact_gap_shape(self):
        result = query_engine.query(
            "etb-runtime-baseline", "What is the quantum telemetry payload checksum for the next run?", root=self.root
        )
        self.assertFalse(result["repository_answer_exists"])
        self.assertIn(result["knowledge_gap"], {"PARTIAL", "UNKNOWN", "REQUIRES_RUNTIME"})
        self.assertEqual(set(result), {"repository_answer_exists", "knowledge_gap", "missing_evidence_required"})

    def test_snapshot_is_success_case_and_contains_codex_context(self):
        result = query_engine.snapshot("etb-runtime-baseline", root=self.root)
        self.assertTrue(result["repository_answer_exists"])
        snapshot = json.loads(result["existing_answer"])
        self.assertEqual(snapshot["active_blocker"], ["AJI-001"])
        self.assertIn("Beyond Terms", snapshot["deepest_verified_screen"])

    def test_cache_is_reused_and_invalidated_by_source_hash(self):
        first = query_engine.query("etb-runtime-baseline", "What is the current active blocker?", root=self.root)
        cache_files = list((self.root / ".runtime" / "aios" / "intelligence").glob("*.json"))
        self.assertEqual(len(cache_files), 1)
        with patch.object(query_engine, "_uncached_query", side_effect=AssertionError("cache was not used")):
            second = query_engine.query("etb-runtime-baseline", "What is the current active blocker?", root=self.root)
        self.assertEqual(first, second)
        mission = self.root / ".runtime" / "aios" / "missions" / "etb-runtime-baseline.yaml"
        mission.write_text(mission.read_text(encoding="utf-8") + "\n# changed\n", encoding="utf-8")
        with patch.object(query_engine, "_uncached_query", wraps=query_engine._uncached_query) as uncached:
            query_engine.query("etb-runtime-baseline", "What is the current active blocker?", root=self.root)
            uncached.assert_called_once()

    def test_schema_rejects_extra_fields(self):
        with self.assertRaises(ValueError):
            validate_response(
                {
                    "repository_answer_exists": True,
                    "confidence": "HIGH",
                    "answer_source": ["source"],
                    "existing_answer": "answer",
                    "recommended_next_action": "forbidden",
                }
            )

    def test_engine_has_no_execution_subprocess_import(self):
        source = Path(query_engine.__file__).read_text(encoding="utf-8")
        self.assertNotIn("import subprocess", source)
        self.assertNotIn("os.system", source)
        self.assertNotIn("subprocess.", source)

    def test_hermes_pre_action_boundary_preserves_exact_query_contract(self):
        result = query_before_action(
            "etb-runtime-baseline",
            "What is the current active blocker?",
            "runtime_attempt",
            root=self.root,
        )
        self.assertEqual(set(result), {"repository_answer_exists", "confidence", "answer_source", "existing_answer"})
        self.assertIn("AJI-001", result["existing_answer"])

    def test_hermes_pre_action_boundary_does_not_accept_unknown_action(self):
        with self.assertRaisesRegex(ValueError, "ACTION_KIND"):
            query_before_action("etb-runtime-baseline", "question", "IMPLEMENT", root=self.root)


if __name__ == "__main__":
    unittest.main()
