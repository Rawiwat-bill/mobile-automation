"""Canonical contract and routing tests. No local profiles, Appium or backend."""
from __future__ import annotations
import io,json,tempfile,unittest
from pathlib import Path
import yaml
from robot import run
from robot.api import ExecutionResult,get_resource_model
from tools.verify_etb_profile_source import digits,numeric_identity,SourceTraceError
ROOT=Path(__file__).resolve().parents[1]
def body(rel,name):
    p=ROOT/rel;text=p.read_text();model=get_resource_model(str(p))
    node=next(n for s in model.sections for n in getattr(s,'body',[]) if n.__class__.__name__=='Keyword' and n.name==name)
    return ''.join(text.splitlines(keepends=True)[node.lineno-1:node.end_lineno])
class SourceRepresentationTests(unittest.TestCase):
    def test_leading_zero_survives_presentation_normalization(self):self.assertEqual(digits('000-111 2222'),'0001112222')
    def test_no_guessing_missing_zero(self):self.assertNotEqual(digits('00111'),digits('111'))
    def test_invalid_letters_are_not_silently_discarded(self):
        for value in ('001ABC111','[MASKED_PHONE]',None,111):
            with self.subTest(value_type=type(value).__name__),self.assertRaises(SourceTraceError):digits(value)
    def test_fixed_width_numeric_display_only(self):
        self.assertEqual(numeric_identity('111','00000'),'00111');self.assertEqual(numeric_identity('111','General'),'111')
    def test_fraction_or_negative_identity_is_rejected(self):
        for v in ('111.5','-111','NaN','Infinity'):
            with self.subTest(v=v),self.assertRaises(SourceTraceError):numeric_identity(v,'0')
class CanonicalContractTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):cls.contract=yaml.safe_load((ROOT/'testdata/onboarding/etb_cases.yaml').read_text());cls.cases=cls.contract['cases']
    def test_all_aliases_bound_to_canonical_rows(self):
        self.assertEqual(len(self.cases),13)
        for i in range(1,14):
            c=self.cases[f'etb_tc_{i:03d}'];self.assertEqual(c['tc_id'],f'TC-ETB-{i:03d}');self.assertEqual(c['source_row'],i+3)
    def test_confirmed_pdpa_policies_and_cleanup_are_preserved(self):
        self.assertEqual(self.cases['etb_tc_001']['pdpa_policy'],'MUST_SKIP')
        self.assertFalse(self.cases['etb_tc_001']['pdpa_reset_required'])
        c=self.cases['etb_tc_002'];self.assertEqual(c['pdpa_policy'],'REQUIRED');self.assertEqual(c['execution_lifecycle']['cleanup']['pdpa_clear'],'BEST_EFFORT')
    def test_unresolved_pdpa_is_not_invented(self):
        for alias in ('etb_tc_003','etb_tc_004'):self.assertEqual(self.cases[alias]['pdpa_policy'],'UNRESOLVED')
    def test_product_policies_and_case_independence(self):
        self.assertEqual(self.cases['etb_tc_003']['product_selection_policy'],'MUST_SKIP')
        for alias in ('etb_tc_001','etb_tc_002','etb_tc_004'):self.assertEqual(self.cases[alias]['product_selection_policy'],'REQUIRED')
        self.assertEqual(self.cases['etb_tc_004']['expected_product_categories'],['Saving','e-Saving'])
        text=(ROOT/'tests/android/etb/etb_regression.robot').read_text();self.assertIn('Run ETB Positive Case    etb_tc_004',text)
    def test_exact_negative_codes_and_subtypes(self):
        expected={5:'RGI-079',6:'RGI-076',7:'RGI-012',8:'RGI-014',9:'RGI-014',10:'RGI-014',11:'RGI-014',12:'RGI-013',13:'RGI-016'}
        for i,code in expected.items():self.assertEqual(self.cases[f'etb_tc_{i:03d}']['expected_error_code'],code)
        for i,tag in ((8,'3A'),(9,'3V'),(10,'3U'),(11,'3B')):self.assertIn(tag,self.cases[f'etb_tc_{i:03d}']['tags'])
    def test_release_specific_optional_preset(self):
        p=self.contract['pre_setting_requirements'];self.assertFalse(p['settings_required'])
        self.assertEqual(p['by_release']['MMP_LOT2_V2']['passkey_section'],'MUST_NOT_DISPLAY')
        self.assertEqual(p['by_release']['POST_MMP_1']['passkey_section'],'MUST_DISPLAY')
        self.assertEqual(p['by_release']['POST_MMP_1']['add_email_option'],'MUST_DISPLAY')
    def test_all_positive_cases_retain_3c_assertions(self):
        suite=(ROOT/'tests/android/etb/etb_regression.robot').read_text()
        for i in (1,3,4):self.assertIn(f'Run ETB Positive Case    etb_tc_{i:03d}    assert_3c=${{True}}',suite)
        source=body('resources/keywords/etb/etb_regression_keywords.resource','Run ETB TC002 PDPA Case');self.assertIn('Assert TC001 Introduction And Control 3C',source)
class LaserBoundaryTests(unittest.TestCase):
    def test_laser_value_verification_reacquires_after_react_native_rerender(self):
        page=(ROOT/'resources/pages/etb/check_dopa_fill_laser_code_page.resource').read_text()
        self.assertIn('Laser Code Field Should Match Fresh',page)
        self.assertIn('Wait Until Keyword Succeeds    5x    300ms',page)
        self.assertIn('Get Text    ${field_locator}',page)

    def test_exact_production_laser_stage_routing(self):
        resource=body('resources/keywords/etb/etb_regression_keywords.resource','Run ETB Expected RGI After Laser Code')
        suite=r'''*** Settings ***
Library    Collections
Resource    production.resource
*** Variables ***
${ETB_CASE_CONTRACT}    CONTRACT
${ETB_CASE_PROFILES}    PROFILES
${FLOW_STATE_NEXT}    NEXT
${CHECK_DOPA_FILL_LASER_CODE_BUTTON_NEXT}    SYNTHETIC_NEXT
${NCBD_LOADING_TIMEOUT}    1s
${DEVICE_UDID}    SYNTHETIC_DEVICE
*** Test Cases ***
RGI016 At Profile Cannot Pass After Laser Case
    Configure    RGI-016
    Run Keyword And Expect Error    *EXPECTED_RGI_AFTER_LASER_PROFILE_STAGE_MISMATCH*    Run ETB Expected RGI After Laser Code    etb_tc_013    Synthetic Handler
    Should Be Equal As Integers    ${LASER_NEXT_CALLS}    0
    Should Be Equal As Integers    ${HANDLER_CALLS}    0
    Should Be Equal As Integers    ${CLEANUP_CALLS}    1
Unrelated Profile Error Cannot Enter Laser
    Configure    RAI-033
    Run Keyword And Expect Error    *EXPECTED_RGI_AFTER_LASER_PROFILE_STAGE_MISMATCH*    Run ETB Expected RGI After Laser Code    etb_tc_013    Synthetic Handler
    Should Be Equal As Integers    ${LASER_NEXT_CALLS}    0
    Should Be Equal As Integers    ${CLEANUP_CALLS}    1
Normal Route Submits Laser Once Before Error Handler
    Configure    NEXT
    Run ETB Expected RGI After Laser Code    etb_tc_013    Synthetic Handler
    Should Be Equal As Integers    ${LASER_NEXT_CALLS}    1
    Should Be Equal As Integers    ${HANDLER_CALLS}    1
    Should Be Equal As Integers    ${CLEANUP_CALLS}    1
*** Keywords ***
Configure
    [Arguments]    ${result}
    Set Test Variable    ${RESULT}    ${result}
    Set Test Variable    ${LASER_NEXT_CALLS}    ${0}
    Set Test Variable    ${HANDLER_CALLS}    ${0}
    Set Test Variable    ${CLEANUP_CALLS}    ${0}
config_loader.Load YAML
    [Arguments]    ${path}
    IF    $path == 'CONTRACT'
        ${value}=    Evaluate    {'cases': {'etb_tc_013': {'expected_error_code': 'RGI-016'}}}
    ELSE
        ${value}=    Evaluate    {'cases': {'etb_tc_013': {'profile': {'date_of_birth': '01/01/2000', 'citizen_id': 'SYNTHETIC', 'mobile_number': 'SYNTHETIC', 'laser_code': 'SYNTHETIC'}}}}
    END
    RETURN    ${value}
Replace String
    [Arguments]    ${value}    ${a}    ${b}
    RETURN    ${value}
Prepare CIS State
    [Arguments]    @{args}
    ${r}=    Create Dictionary    cis_clear=PASS
    RETURN    ${r}
Assert CIS Preparation Ready
    [Arguments]    ${r}
    Should Be Equal    ${r}[cis_clear]    PASS
Common Onboarding Flow
    [Arguments]    @{args}
    RETURN    ${RESULT}
Wait Until Check DOPA Fill Laser Code Is Displayed
    No Operation
Input Laser Code
    [Arguments]    ${value}
    No Operation
Wait Until Element Is Visible
    [Arguments]    @{args}
    No Operation
Click Element
    [Arguments]    ${locator}
    ${n}=    Evaluate    $LASER_NEXT_CALLS + 1
    Set Test Variable    ${LASER_NEXT_CALLS}    ${n}
Record ETB Evidence Capture
    [Arguments]    @{args}
    No Operation
Synthetic Handler
    [Arguments]    ${code}    @{args}
    Should Be Equal    ${code}    RGI-016
    Should Be Equal As Integers    ${LASER_NEXT_CALLS}    1
    ${n}=    Evaluate    $HANDLER_CALLS + 1
    Set Test Variable    ${HANDLER_CALLS}    ${n}
Record ETB Device Terminal Evidence
    [Arguments]    @{args}
    No Operation
Cleanup CIS State
    [Arguments]    @{args}
    ${n}=    Evaluate    $CLEANUP_CALLS + 1
    Set Test Variable    ${CLEANUP_CALLS}    ${n}
    ${r}=    Create Dictionary    cis_clear=PASS
    RETURN    ${r}
Assert CIS Cleanup Policy
    [Arguments]    ${r}
    Should Be Equal    ${r}[cis_clear]    PASS
'''
        with tempfile.TemporaryDirectory() as temp:
            p=Path(temp);(p/'production.resource').write_text('*** Keywords ***\n'+resource);(p/'suite.robot').write_text(suite)
            rc=run(str(p/'suite.robot'),outputdir=temp,console='none',log='NONE',report='NONE',stdout=io.StringIO(),stderr=io.StringIO())
            results=ExecutionResult(str(p/'output.xml'))
            self.assertEqual(rc,0,[t.message for t in results.suite.tests]);self.assertEqual(len(results.suite.tests),3)
if __name__=='__main__':unittest.main(verbosity=2)
