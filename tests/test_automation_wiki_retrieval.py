from __future__ import annotations

import json
import unittest
from pathlib import Path

ROOT=Path(__file__).resolve().parents[1]
BENCHMARK=ROOT/"configs/automation_wiki_retrieval_benchmark.json"


class AutomationWikiRetrievalBenchmarkTests(unittest.TestCase):
    def test_benchmark_pages_answer_required_questions(self):
        payload=json.loads(BENCHMARK.read_text(encoding="utf-8"))
        self.assertEqual(payload["schema"], "bbl-automation-wiki-retrieval-benchmark/v1")
        self.assertEqual(
            payload["clean_checkout_policy"],
            "LOCAL_ONLY_NOT_REQUIRED_FOR_CLEAN_CHECKOUT",
        )
        questions=payload["questions"]
        self.assertGreaterEqual(len(questions), 7)
        ids=set()
        for question in questions:
            with self.subTest(question=question["id"]):
                self.assertNotIn(question["id"], ids)
                ids.add(question["id"])
                page=ROOT/question["page"]
                if not page.is_file():
                    continue
                content=page.read_text(encoding="utf-8")
                for marker in question["must_contain"]:
                    self.assertIn(marker, content)

    def test_runtime_and_product_authority_are_not_collapsed(self):
        trace_path=ROOT/"local/obsidian-bbl/wiki/automation/traceability.md"
        index_path=ROOT/"local/obsidian-bbl/wiki/automation/index.md"
        if not trace_path.is_file() or not index_path.is_file():
            return
        trace=trace_path.read_text(encoding="utf-8")
        index=index_path.read_text(encoding="utf-8")
        self.assertIn("No authority plane silently overwrites another.", trace)
        self.assertIn("Automation/runtime evidence MUST NOT silently override approved business behavior.", index)


if __name__=="__main__":
    unittest.main(verbosity=2)
