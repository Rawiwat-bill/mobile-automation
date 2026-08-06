from __future__ import annotations

import hashlib
import tempfile
import unittest
from pathlib import Path

import yaml

from tools.generate_flow_knowledge import FLOW_CONFIG, generate


class FlowKnowledgeGeneratorTest(unittest.TestCase):
    def test_generates_required_contract_outputs_for_all_flows(self) -> None:
        with tempfile.TemporaryDirectory(prefix="flow-knowledge-test-") as directory:
            output_root = Path(directory) / "knowledge" / "flows"
            generated = generate(list(FLOW_CONFIG), output_root)

            self.assertEqual(len(generated), 9)
            required = {
                "flow_id",
                "business_purpose",
                "expected_sequence",
                "optional_branches",
                "decision_points",
                "success_marker",
                "cleanup_contract",
                "canonical_components_used",
                "synchronization_date",
                "source_visio",
                "generation_timestamp",
            }
            for flow in FLOW_CONFIG:
                contract_path = output_root / flow / "flow.yaml"
                contract = yaml.safe_load(contract_path.read_text(encoding="utf-8"))
                self.assertTrue(required.issubset(contract))
                self.assertTrue((output_root / flow / "flow.md").is_file())
                self.assertTrue((output_root / flow / "diagram.mmd").is_file())
                self.assertIn("flowchart TD", (output_root / flow / "diagram.mmd").read_text(encoding="utf-8"))

    def test_repeated_generation_is_byte_identical(self) -> None:
        with tempfile.TemporaryDirectory(prefix="flow-knowledge-test-") as directory:
            first_root = Path(directory) / "first" / "knowledge" / "flows"
            second_root = Path(directory) / "second" / "knowledge" / "flows"
            generate(list(FLOW_CONFIG), first_root)
            generate(list(FLOW_CONFIG), second_root)

            for flow in FLOW_CONFIG:
                for filename in ("flow.yaml", "flow.md", "diagram.mmd"):
                    first = (first_root / flow / filename).read_bytes()
                    second = (second_root / flow / filename).read_bytes()
                    self.assertEqual(hashlib.sha256(first).digest(), hashlib.sha256(second).digest(), f"{flow}/{filename}")


if __name__ == "__main__":
    unittest.main()
