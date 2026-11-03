"""Error-validation profiles must survive setup and teardown unchanged."""

import os
from pathlib import Path
import tempfile
import unittest
from unittest.mock import patch

from libraries import cis_preparation


class ErrorCisLifecycleTests(unittest.TestCase):
    def test_all_error_cases_make_zero_mutations_in_both_phases(self):
        with tempfile.TemporaryDirectory() as output, patch.dict(
            os.environ, {"ETB_ENVIRONMENT": "DEV", "CIS_MODE": "AUTOMATION"}, clear=True
        ), patch.object(cis_preparation, "_resolve_citizen_id") as identity, patch.object(
            cis_preparation, "_clear_once"
        ) as clear:
            for number in range(5, 14):
                for function, phase in (
                    (cis_preparation.prepare_cis_state, "PRE_TEST"),
                    (cis_preparation.cleanup_cis_state, "POST_TEST"),
                ):
                    with self.subTest(number=number, phase=phase):
                        result = function("unused.yaml", f"etb_tc_{number:03d}", output)
                        self.assertEqual(result["phase"], phase)
                        self.assertEqual(result["cis_mode"], "ERROR_VALIDATION")
                        self.assertEqual(result["cis_clear"], "NOT_APPLICABLE")
                        self.assertEqual(result["cis_state_ready"], "PRESERVED_NOT_VERIFIED")
                        self.assertEqual(result["operation_count"], 0)
                        self.assertEqual(result["transport_category"], "NOT_ATTEMPTED")
            identity.assert_not_called()
            clear.assert_not_called()

    def test_e2e_cases_keep_existing_clear_lifecycle(self):
        with patch.dict(os.environ, {"ETB_ENVIRONMENT": "DEV"}, clear=True), patch.object(
            cis_preparation, "_clear_state", return_value={"sentinel": True}
        ) as clear:
            for number in range(1, 5):
                for function, phase in (
                    (cis_preparation.prepare_cis_state, "PRE_TEST"),
                    (cis_preparation.cleanup_cis_state, "POST_TEST"),
                ):
                    key = f"etb_tc_{number:03d}"
                    with self.subTest(number=number, phase=phase):
                        self.assertEqual(function("profiles.yaml", key, "output"), {"sentinel": True})
                        clear.assert_called_with("profiles.yaml", key, "output", phase)
            self.assertEqual(clear.call_count, 8)

    def test_robot_accepts_only_explicit_zero_operation_preservation(self):
        from robot import run

        resource = Path(__file__).resolve().parents[1] / "resources/keywords/etb/etb_regression_keywords.resource"
        with tempfile.TemporaryDirectory() as output, patch.dict(
            os.environ, {"ETB_ENVIRONMENT": "DEV", "CIS_MODE": "AUTOMATION"}, clear=True
        ):
            suite = Path(output) / "policy.robot"
            suite.write_text(f"""*** Settings ***
Resource    {resource}
*** Test Cases ***
Preservation Policy
    ${{result}}=    Create Dictionary    cis_mode=ERROR_VALIDATION    cis_clear=NOT_APPLICABLE    cis_state_ready=PRESERVED_NOT_VERIFIED    operation_count=${{0}}
    Assert CIS Preparation Ready    ${{result}}
    Assert CIS Cleanup Policy    ${{result}}
    Set To Dictionary    ${{result}}    operation_count=${{1}}
    Run Keyword And Expect Error    *    Assert CIS Preparation Ready    ${{result}}
    Run Keyword And Expect Error    *    Assert CIS Cleanup Policy    ${{result}}
    Set To Dictionary    ${{result}}    operation_count=${{0}}    cis_clear=PASS
    Run Keyword And Expect Error    *    Assert CIS Preparation Ready    ${{result}}
    Run Keyword And Expect Error    *    Assert CIS Cleanup Policy    ${{result}}
    Set To Dictionary    ${{result}}    cis_clear=NOT_APPLICABLE    cis_state_ready=YES
    Run Keyword And Expect Error    *    Assert CIS Preparation Ready    ${{result}}
""", encoding="utf-8")
            self.assertEqual(run(str(suite), outputdir=output, console="none"), 0)


if __name__ == "__main__":
    unittest.main()
