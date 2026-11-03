"""Robot result-file privacy and opt-in dispatch tests. Synthetic input only."""
from __future__ import annotations
import io
from pathlib import Path
import sys
import tempfile
import unittest
from robot import run
from robot.api import get_resource_model
ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT))
from libraries.robot_output_sanitizer import RobotOutputSanitizer

def body(name):
 path=ROOT/'resources/pages/onboarding/profile_dob.resource'
 model=get_resource_model(str(path))
 node=next(k for s in model.sections for k in getattr(s,'body',[]) if k.__class__.__name__=='Keyword' and k.name==name)
 return ''.join(path.read_text().splitlines(keepends=True)[node.lineno-1:node.end_lineno])

class DOBRobotContractTests(unittest.TestCase):
 def test_dob_logs_are_masked_and_logging_scope_restored_after_error(self):
  text='''*** Test Cases ***
DOB Detail Success
    Input Date Of Birth    09-11-2000
    Log    POST_DOB_DIAGNOSTICS_VISIBLE
    Log    09 Nov 2000
    Log    9/11/2000

DOB Detail Failure
    Run Keyword And Expect Error    DOB_COMMITTED_VALUE_MISMATCH*    Verify DOB Field Value    09    11    2000
    Log    POST_FAILURE_DIAGNOSTICS_VISIBLE

*** Keywords ***
Input Date Of Birth
    [Arguments]    ${value}
    Log    ${value}
    Log    Element text is '09 Nov 2000'
    Log    Element text is '9 November 2000'
    Verify Nested DOB    ${value}

Verify Nested DOB
    [Arguments]    ${value}
    Log    ${value}

Verify DOB Field Value
    [Arguments]    ${day}    ${month}    ${year}
    Log    09/11/2000
    Fail    DOB_COMMITTED_VALUE_MISMATCH actual=09 Nov 2000
'''
  with tempfile.TemporaryDirectory(dir=ROOT/'.runtime',prefix='dob-private-test-') as tmp:
   p=Path(tmp); (p/'case.robot').write_text(text)
   rc=run(str(p/'case.robot'),outputdir=str(p),log='log.html',report='NONE',console='none',listener=RobotOutputSanitizer(),stdout=io.StringIO(),stderr=io.StringIO())
   self.assertEqual(rc,0)
   xml=(p/'output.xml').read_text()
   for sensitive in ('09-11-2000','09 Nov 2000','9 November 2000','09/11/2000','9/11/2000'):
    self.assertNotIn(sensitive,xml)
   self.assertIn('POST_DOB_DIAGNOSTICS_VISIBLE',xml)
   self.assertIn('POST_FAILURE_DIAGNOSTICS_VISIBLE',xml)
   self.assertIn('DOB_COMMITTED_VALUE_MISMATCH',xml)
 def test_real_resource_dispatches_candidate_only_when_opted_in(self):
  text='''*** Settings ***
Library    Collections

*** Variables ***
${PROFILE_DOB_CONTAINER}    OPEN
${PROFILE_DOB_YEAR_PICKER}    YEAR
${PROFILE_DOB_MONTH_PICKER}    MONTH
${PROFILE_DOB_DAY_PICKER}    DAY
${PROFILE_DOB_CONFIRM_BUTTON}    DONE
${PROFILE_DOB_INPUT}    FIELD
${PROFILE_TITLE_TEXT}    TITLE

*** Test Cases ***
Candidate Opt In Uses Exact Controller
    Set Test Variable    ${ETB_DOB_STRATEGY}    STABLE_V1
    Input Date Of Birth    09-11-2000
    Should Be Equal    ${ETB_DOB_LAST_METRICS}[status]    PASS

Legacy Remains Default
    Run Keyword And Expect Error    LEGACY_PATH_REACHED    Input Date Of Birth    09-11-2000

Unknown Strategy Fails Closed
    Set Test Variable    ${ETB_DOB_STRATEGY}    WRONG
    Run Keyword And Expect Error    DOB_STRATEGY_UNSUPPORTED    Input Date Of Birth    09-11-2000

*** Keywords ***
Select ETB DOB Exact
    [Arguments]    ${expected}    @{locators}
    Should Be Equal    ${expected}    09-11-2000
    Length Should Be    ${locators}    7
    Should Be Equal    ${locators}[0]    OPEN
    ${metrics}=    Create Dictionary    status=PASS    exact_match=${True}
    RETURN    ${metrics}

Observe Profile DOB Boundary
    [Arguments]    ${point}
    Fail    LEGACY_PATH_REACHED

'''+body('Input Date Of Birth')
  with tempfile.TemporaryDirectory(dir=ROOT/'.runtime',prefix='dob-dispatch-test-') as tmp:
   p=Path(tmp); (p/'case.robot').write_text(text)
   rc=run(str(p/'case.robot'),outputdir=str(p),log='NONE',report='NONE',console='none',stdout=io.StringIO(),stderr=io.StringIO())
   self.assertEqual(rc,0)

if __name__=='__main__': unittest.main(verbosity=2)
