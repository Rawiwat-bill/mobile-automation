"""Offline regression for lost Profile results and false-positive ETB handoffs.

Execute exact current keyword bodies extracted from production resources.
Every UI, backend, profile input and reporting dependency is a synthetic stub;
the first DOPA call raises a sentinel before any input or downstream operation.
"""
import hashlib
import io
import tempfile
import unittest
from pathlib import Path

from robot import run
from robot.api import ExecutionResult, get_resource_model

ROOT = Path(__file__).resolve().parents[1]
PROFILE = ROOT / 'resources/pages/onboarding/profile_screen_page.resource'
COMMON = ROOT / 'resources/keywords/common_onboarding/common_onboarding_keyword.resource'
ETB = ROOT / 'resources/keywords/etb/etb_keywords.resource'


def keyword_body(path, name):
    text = path.read_text(encoding='utf-8')
    model = get_resource_model(str(path))
    nodes = [node for section in model.sections for node in getattr(section, 'body', [])
             if node.__class__.__name__ == 'Keyword' and node.name == name]
    if len(nodes) != 1:
        raise AssertionError('PRODUCTION_KEYWORD_NOT_UNIQUE: ' + name)
    node = nodes[0]
    return ''.join(text.splitlines(keepends=True)[node.lineno - 1:node.end_lineno]).rstrip() + '\n'


TESTS = '''*** Test Cases ***
Wrapper Preserves AJI Result
    Configure    AJI-001
    ${actual}=    Tap Profile Next
    Should Be Equal    ${actual}    AJI-001

Wrapper Preserves GOD Result
    Configure    GOD-013
    ${actual}=    Tap Profile Next
    Should Be Equal    ${actual}    GOD-013

Wrapper Preserves RGI Result
    Configure    RGI-104
    ${actual}=    Tap Profile Next
    Should Be Equal    ${actual}    RGI-104

Wrapper Preserves Normal Transition
    Configure    PROFILE_LEFT_OR_NEXT_STATE_VISIBLE
    ${actual}=    Tap Profile Next
    Should Be Equal    ${actual}    PROFILE_LEFT_OR_NEXT_STATE_VISIBLE

Common Propagates AJI Without Completion
    Configure    AJI-001
    ${actual}=    Common Onboarding Flow    OMITTED    OMITTED    OMITTED
    Should Be Equal    ${actual}    AJI-001
    List Should Not Contain Value    ${CHECKPOINTS}    TELL_US_ABOUT_YOU_COMPLETED
    Should Be Equal As Integers    ${DOPA_CALLS}    0

Positive AJI Fails Before DOPA
    Configure    AJI-001
    Run Keyword And Expect Error    BLOCKED_BY_ENVIRONMENT_BACKEND_AJI_001:*    Complete ETB Onboarding    OMITTED    OMITTED    OMITTED    OMITTED    OMITTED    OMITTED
    Should Be Equal    ${BLOCKER_CODE}    AJI-001
    List Should Contain Value    ${CHECKPOINTS}    ETB_ENVIRONMENT_BACKEND_HANDOFF
    List Should Not Contain Value    ${CHECKPOINTS}    TELL_US_ABOUT_YOU_COMPLETED
    Should Be Equal As Integers    ${DOPA_CALLS}    0

Positive GOD Fails Before DOPA
    Configure    GOD-013
    Run Keyword And Expect Error    BLOCKED_BY_ENVIRONMENT_BACKEND_GOD_013:*    Complete ETB Onboarding    OMITTED    OMITTED    OMITTED    OMITTED    OMITTED    OMITTED
    Should Be Equal    ${BLOCKER_CODE}    ENVIRONMENT_BACKEND_GOD_013
    Should Be Equal As Integers    ${DOPA_CALLS}    0

Positive RGI Does Not Enter DOPA
    Configure    RGI-104
    Run Keyword And Expect Error    *ETB_COMMON_ONBOARDING_DID_NOT_REACH_DOPA*    Complete ETB Onboarding    OMITTED    OMITTED    OMITTED    OMITTED    OMITTED    OMITTED
    Should Be Equal As Integers    ${DOPA_CALLS}    0

Normal Transition Reaches DOPA Once
    Configure    PROFILE_LEFT_OR_NEXT_STATE_VISIBLE
    Run Keyword And Expect Error    DOPA_BOUNDARY_REACHED    Complete ETB Onboarding    OMITTED    OMITTED    OMITTED    OMITTED    OMITTED    OMITTED
    List Should Contain Value    ${CHECKPOINTS}    TELL_US_ABOUT_YOU_COMPLETED
    Should Be Equal As Integers    ${DOPA_CALLS}    1

Terms AJI Fails Before Profile And DOPA
    Configure    PROFILE_LEFT_OR_NEXT_STATE_VISIBLE    AJI-001
    Run Keyword And Expect Error    BLOCKED_BY_ENVIRONMENT_BACKEND_AJI_001:*    Complete ETB Onboarding    OMITTED    OMITTED    OMITTED    OMITTED    OMITTED    OMITTED
    Should Be Equal As Integers    ${PROFILE_CALLS}    0
    Should Be Equal As Integers    ${DOPA_CALLS}    0

*** Keywords ***
Configure
    [Arguments]    ${result}    ${terms}=NEXT
    Set Test Variable    ${PROFILE_RESULT}    ${result}
    Set Test Variable    ${TERMS_RESULT}    ${terms}
    ${points}=    Create List
    Set Test Variable    ${CHECKPOINTS}    ${points}
    Set Test Variable    ${DOPA_CALLS}    ${0}
    Set Test Variable    ${PROFILE_CALLS}    ${0}
    Set Test Variable    ${BLOCKER_CODE}    ${EMPTY}

Tap Profile Next Button
    ${calls}=    Evaluate    $PROFILE_CALLS + 1
    Set Test Variable    ${PROFILE_CALLS}    ${calls}
    RETURN    ${PROFILE_RESULT}

Accept Terms And Conditions
    RETURN    ${TERMS_RESULT}

Mark Health Checkpoint
    [Arguments]    ${stage}
    Append To List    ${CHECKPOINTS}    ${stage}

Wait For Landing Destination
    [Arguments]    ${destination_locator}    ${timeout}
    RETURN    NEXT

Set Health Check Blocker
    [Arguments]    ${code}    ${message}    ${directory}
    Set Test Variable    ${BLOCKER_CODE}    ${code}

Persist ETB Readiness Summary
    [Arguments]    ${output_dir}    &{metadata}
    No Operation

Wait Until Check DOPA Fill Laser Code Is Displayed
    ${calls}=    Evaluate    $DOPA_CALLS + 1
    Set Test Variable    ${DOPA_CALLS}    ${calls}
    Fail    DOPA_BOUNDARY_REACHED

Select Date Of Birth
    [Arguments]    ${unused}
    No Operation
'''


class ETBDopaBoundaryTests(unittest.TestCase):
    def test_exact_production_boundary_behaviors(self):
        for path in (PROFILE, COMMON, ETB,
                     ROOT / 'locators/android/etb/check_dopa_fill_laser_code_locators.resource',
                     ROOT / 'resources/pages/etb/check_dopa_fill_laser_code_page.resource',
                     ROOT / 'resources/app/app_keywords.resource',
                     ROOT / 'resources/pages/common_onboarding/landing_screen_page.resource',
                     ROOT / 'package.json'):
            print('SHA256 ' + str(path.relative_to(ROOT)) + ' ' + hashlib.sha256(path.read_bytes()).hexdigest())
        with tempfile.TemporaryDirectory(prefix='bbl-dopa-boundary-') as directory:
            root = Path(directory)
            resource = root / 'production_boundary.resource'
            resource.write_text('*** Keywords ***\n' + '\n'.join([
                keyword_body(PROFILE, 'Tap Profile Next'),
                keyword_body(COMMON, 'Common Onboarding Flow'),
                keyword_body(ETB, 'Complete ETB Onboarding'),
            ]), encoding='utf-8')
            input_stub = root / 'tell_us_about_you_page.resource'
            input_stub.write_text('*** Keywords ***\nInput Citizen ID\n    [Arguments]    ${unused}\n    No Operation\nInput Mobile Number\n    [Arguments]    ${unused}\n    No Operation\n', encoding='utf-8')
            noop_names = (
                'Wait Until Landing Screen Is Displayed', 'Switch Landing Language To English',
                'Tap Landing Ready Button', 'Allow Android Permission If Visible',
                'Wait Until Terms And Conditions Screen Is Displayed', 'Scroll Down Terms And Conditions',
                'Wait Until Tell Us About You Screen Is Displayed', 'Wait Until Fields Are Blurred',
            )
            noops = '\n'.join(name + '\n    No Operation\n' for name in noop_names)
            suite = root / 'boundary.robot'
            suite.write_text(
                '*** Settings ***\nLibrary    Collections\nResource    production_boundary.resource\nResource    tell_us_about_you_page.resource\n\n'
                '*** Variables ***\n${TERMS_AND_CONDITIONS_WEBVIEW}    SYNTHETIC_TERMS\n${NCBD_LOADING_TIMEOUT}    40s\n\n'
                + TESTS + '\n' + noops,
                encoding='utf-8',
            )
            code = run(str(suite), outputdir=directory, log='NONE', report='NONE',
                       console='none', stdout=io.StringIO(), stderr=io.StringIO())
            result = ExecutionResult(str(root / 'output.xml'))
            self.assertEqual(len(result.suite.tests), 10)
            print('DOPA_BOUNDARY_CASES=10')
            for case in result.suite.tests:
                print(case.name + '=' + case.status)
            self.assertEqual(code, 0, 'DOPA_BOUNDARY_SYNTHETIC_CONTRACT_FAILED')


if __name__ == '__main__':
    unittest.main(verbosity=2)
