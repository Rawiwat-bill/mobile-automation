from __future__ import annotations

import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


class ETBBusinessFlowDiagnosticsTests(unittest.TestCase):
    def test_landing_full_screen_gub_preserves_fail_closed_contract_with_exact_code(self):
        source = (ROOT / 'resources/pages/common_onboarding/landing_screen_page.resource').read_text(encoding='utf-8')
        self.assertIn('Classify Landing Gub Code', source)
        self.assertIn('(?:RGI|GOD|AJI|RAI)-[0-9]{3}', source)
        self.assertIn('LANDING_FULL_SCREEN_GUB_AFTER_ACTION code=${gub_code}', source)

    def test_terms_stuck_state_is_diagnostic_not_success(self):
        source = (ROOT / 'resources/pages/common_onboarding/terms_and_conditions_page.resource').read_text(encoding='utf-8')
        self.assertIn('Classify Terms Non Transition State', source)
        self.assertIn('RETURN    TERMS_STILL_VISIBLE', source)
        self.assertIn('RETURN    DOPA_VISIBLE', source)
        self.assertIn('RETURN    PROFILE_VISIBLE', source)
        self.assertIn('TERMS_TRANSITION_NOT_OBSERVED observed=${transition}', source)
        self.assertNotIn("RETURN    ${FLOW_STATE_NEXT}\n    END\n\n    Capture Terms Transition Evidence\n    Fail    TERMS_TRANSITION_NOT_OBSERVED\n", source)

    def test_required_product_selection_stays_strict_and_records_observed_state(self):
        source = (ROOT / 'resources/keywords/etb/etb_keywords.resource').read_text(encoding='utf-8')
        self.assertGreaterEqual(source.count('PRODUCT_SELECTION_REQUIRED_BUT_SKIPPED observed='), 2)
        self.assertIn('post_pin_required_selection_skipped', source)
        self.assertIn('post_pin_destination_required_selection_skipped', source)
        self.assertIn('ETB_POST_FIRST_PIN_STATE=${post_pin_state}', source)
        self.assertIn('ETB_POST_PIN_DESTINATION=${destination}', source)

    def test_tc013_uses_bounded_expected_rgi_probe_and_fail_fast_classifier(self):
        flow = (ROOT / 'resources/keywords/etb/etb_regression_keywords.resource').read_text(encoding='utf-8')
        dopa = (ROOT / 'resources/pages/etb/check_dopa_fill_laser_code_page.resource').read_text(encoding='utf-8')
        self.assertIn('Wait Until Element Is Visible    ${expected_rgi_locator}    10s', flow)
        self.assertIn('Classify Post Laser Failure State', flow)
        self.assertIn('EXPECTED_RGI_AFTER_LASER_NOT_TRIGGERED', flow)
        self.assertIn('EXPECTED_RGI_AFTER_LASER_WRONG_CODE', flow)
        self.assertIn('EXPECTED_RGI_AFTER_LASER_DESTINATION_UNPROVEN', flow)
        self.assertIn('RETURN    DOPA_STILL_VISIBLE', dopa)
        self.assertIn('(?:RGI|GOD|AJI|RAI)-[0-9]{3}', dopa)

    def test_business_requirements_were_not_relaxed(self):
        contract = (ROOT / 'testdata/onboarding/etb_cases.yaml').read_text(encoding='utf-8')
        self.assertIn('expected_error_code: RGI-016', contract)
        for key in ('etb_tc_001:', 'etb_tc_002:', 'etb_tc_004:'):
            block = contract.split(key, 1)[1].split('\n  etb_tc_', 1)[0]
            self.assertIn('product_selection_policy: REQUIRED', block)


if __name__ == '__main__':
    unittest.main(verbosity=2)
