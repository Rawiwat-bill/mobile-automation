"""Execute the real Landing Robot keyword with fully synthetic, in-process UI I/O.

Suite-level keywords intercept every Appium/ADB boundary. Read-only polling is
accelerated to two attempts; production timeout/interval literals are asserted.
No device, network, profile data, or banking logs are accessed.
"""
import io
import tempfile
import unittest
from pathlib import Path

from robot import run
from robot.api import ExecutionResult

ROOT = Path(__file__).resolve().parents[1]
_STATE = {}
SCENARIOS = {
    'skip_to_ready': ('SKIP', 'READY', 'NONE'),
    'initial_ready': ('READY', 'READY', 'NONE'),
    'skip_to_skip': ('SKIP', 'SKIP', 'NONE'),
    'ready_to_ready': ('READY', 'READY', 'READY'),
    'ready_stuck_after_skip': ('SKIP', 'READY', 'READY'),
    'ambiguous_after_skip': ('SKIP', 'BOTH', 'NONE'),
    'unknown_initial': ('NONE', 'NONE', 'NONE'),
}


def configure_landing(scenario, skip_locator, ready_locator):
    initial, after_skip, after_ready = SCENARIOS[scenario]
    _STATE.clear()
    _STATE.update(
        mode='action',
        state=initial,
        after_skip=after_skip,
        after_ready=after_ready,
        locators={skip_locator: 'SKIP', ready_locator: 'READY'},
        generation=0,
        events=[],
        taps=[],
    )


def configure_destination(state, destination_locator, gub_locator):
    _STATE.clear()
    _STATE.update(
        mode='destination',
        state=state,
        destination_locator=destination_locator,
        gub_locator=gub_locator,
        events=[],
        taps=[],
    )


def _action(locator):
    if locator not in _STATE['locators']:
        raise AssertionError('LANDING_MOCK_UNEXPECTED_LOCATOR')
    return _STATE['locators'][locator]


def mock_visible(locator):
    if _STATE.get('mode') == 'destination':
        if locator == _STATE['destination_locator'] and _STATE['state'] == 'TERMS':
            return
        if locator == _STATE['gub_locator'] and _STATE['state'] == 'GUB':
            return
        raise AssertionError('LANDING_MOCK_NOT_VISIBLE')
    action = _action(locator)
    if _STATE['state'] not in (action, 'BOTH'):
        raise AssertionError('LANDING_MOCK_NOT_VISIBLE')


def _rect(action):
    generation = _STATE['generation']
    if action == 'SKIP':
        return dict(x=100, y=200, width=80, height=40)
    return dict(x=350 + 10 * generation, y=600 + 20 * generation, width=200, height=70)


def mock_rect(locator):
    mock_visible(locator)
    action = _action(locator)
    _STATE['events'].append(('rect', action, _STATE['generation']))
    return _rect(action)


def mock_adb(*args):
    if len(args) != 4 or args[:2] != ('input', 'tap'):
        raise AssertionError('LANDING_MOCK_UNEXPECTED_ADB_COMMAND')
    action = _STATE['state']
    if action not in ('SKIP', 'READY'):
        raise AssertionError('LANDING_MOCK_AMBIGUOUS_TAP')
    rect = _rect(action)
    expected = (int(rect['x'] + rect['width'] / 2), int(rect['y'] + rect['height'] / 2))
    if tuple(map(int, args[2:])) != expected:
        raise AssertionError('LANDING_MOCK_STALE_OR_WRONG_BOUNDS')
    _STATE['events'].append(('tap', action, _STATE['generation']))
    _STATE['taps'].append(action)
    _STATE['state'] = _STATE['after_skip'] if action == 'SKIP' else _STATE['after_ready']
    _STATE['generation'] += 1


def assert_mock_contract(actions):
    expected = [] if actions == 'NONE' else actions.split(',')
    if _STATE['taps'] != expected:
        raise AssertionError('LANDING_MOCK_TAP_COUNT_OR_IDENTITY_MISMATCH')
    events = []
    for generation, action in enumerate(expected):
        events.extend([('rect', action, generation), ('tap', action, generation)])
    if _STATE['events'] != events:
        raise AssertionError('LANDING_MOCK_BOUNDS_NOT_REACQUIRED_AT_ACTION_BOUNDARY')


def _suite_text():
    return '''*** Settings ***
Resource    {resource}
Library    {library}    WITH NAME    F05Mock

*** Test Cases ***
Skip Progresses To Ready With Fresh Bounds
    Configure Landing    skip_to_ready    ${{LANDING_SKIP_BUTTON}}    ${{LANDING_READY_BUTTON}}
    Tap Landing Ready Button
    Assert Mock Contract    SKIP,READY

Initially Ready Is Tapped Once
    Configure Landing    initial_ready    ${{LANDING_SKIP_BUTTON}}    ${{LANDING_READY_BUTTON}}
    Tap Landing Ready Button
    Assert Mock Contract    READY

Skip Remaining Skip Must Not Retap
    Configure Landing    skip_to_skip    ${{LANDING_SKIP_BUTTON}}    ${{LANDING_READY_BUTTON}}
    Run Keyword And Expect Error    *LANDING*    Tap Landing Ready Button
    Assert Mock Contract    SKIP

Ready Remaining Ready Must Not Retap
    Configure Landing    ready_to_ready    ${{LANDING_SKIP_BUTTON}}    ${{LANDING_READY_BUTTON}}
    Run Keyword And Expect Error    *LANDING*    Tap Landing Ready Button
    Assert Mock Contract    READY

Ready Stuck After Skip Must Not Tap A Third Time
    Configure Landing    ready_stuck_after_skip    ${{LANDING_SKIP_BUTTON}}    ${{LANDING_READY_BUTTON}}
    Run Keyword And Expect Error    *LANDING*    Tap Landing Ready Button
    Assert Mock Contract    SKIP,READY

Ambiguous Progression Must Not Tap Ready
    Configure Landing    ambiguous_after_skip    ${{LANDING_SKIP_BUTTON}}    ${{LANDING_READY_BUTTON}}
    Run Keyword And Expect Error    *LANDING*    Tap Landing Ready Button
    Assert Mock Contract    SKIP

Unknown Initial Action Must Not Tap
    Configure Landing    unknown_initial    ${{LANDING_SKIP_BUTTON}}    ${{LANDING_READY_BUTTON}}
    Run Keyword And Expect Error    *LANDING*    Tap Landing Ready Button
    Assert Mock Contract    NONE

Terms Destination Is Accepted
    Configure Destination    TERMS    xpath=//android.webkit.WebView    ${{LANDING_FULL_SCREEN_GUB_CTA}}
    ${{result}}=    Wait For Landing Destination    xpath=//android.webkit.WebView    40s
    Should Be Equal    ${{result}}    NEXT

Landing Full Screen Gub Fails Fast
    Configure Destination    GUB    xpath=//android.webkit.WebView    ${{LANDING_FULL_SCREEN_GUB_CTA}}
    Run Keyword And Expect Error
    ...    *LANDING_FULL_SCREEN_GUB_AFTER_ACTION*
    ...    Wait For Landing Destination    xpath=//android.webkit.WebView    40s

Missing Landing Destination Is Bounded Failure
    Configure Destination    NONE    xpath=//android.webkit.WebView    ${{LANDING_FULL_SCREEN_GUB_CTA}}
    Run Keyword And Expect Error
    ...    *LANDING_DESTINATION_NOT_OBSERVED*
    ...    Wait For Landing Destination    xpath=//android.webkit.WebView    40s

*** Keywords ***
Element Should Be Visible
    [Arguments]    ${{locator}}
    F05Mock.Mock Visible    ${{locator}}

Wait Until Element Is Visible
    [Arguments]    ${{locator}}    ${{timeout}}
    F05Mock.Mock Visible    ${{locator}}

Get Element Rect
    [Arguments]    ${{locator}}
    ${{rect}}=    F05Mock.Mock Rect    ${{locator}}
    RETURN    ${{rect}}

Execute Adb Shell
    [Arguments]    @{{args}}
    F05Mock.Mock Adb    @{{args}}

Wait Until Keyword Succeeds
    [Arguments]    ${{timeout}}    ${{interval}}    ${{keyword}}    @{{args}}
    ${{destination_poll}}=    Run Keyword And Return Status
    ...    Should Be Equal    ${{keyword}}    Landing Destination Marker Should Be Visible
    IF    ${{destination_poll}}
        Should Be Equal    ${{timeout}}    40s
    ELSE
        Should Be Equal    ${{timeout}}    10s
    END
    Should Be Equal    ${{interval}}    500ms
    BuiltIn.Wait Until Keyword Succeeds    2x    0s    ${{keyword}}    @{{args}}
'''.format(resource=ROOT / 'resources/pages/common_onboarding/landing_screen_page.resource', library=Path(__file__).resolve())


class F05LandingTransitionTests(unittest.TestCase):
    def _run_suite(self, dryrun=False):
        with tempfile.TemporaryDirectory(prefix='bbl-f05-contract-') as directory:
            suite = Path(directory) / 'f05.robot'
            suite.write_text(_suite_text(), encoding='utf-8')
            stdout, stderr = io.StringIO(), io.StringIO()
            code = run(
                str(suite),
                outputdir=directory,
                log='NONE',
                report='NONE',
                console='none',
                stdout=stdout,
                stderr=stderr,
                dryrun=dryrun,
            )
            result = ExecutionResult(str(Path(directory) / 'output.xml'))
            print('F05_' + ('DRYRUN' if dryrun else 'BEHAVIOR') + '_CASES=' + str(len(result.suite.tests)))
            for case in result.suite.tests:
                print(case.name + '=' + case.status)
            self.assertEqual(len(result.suite.tests), 10)
            self.assertEqual(code, 0, 'Synthetic F05 contract failed: ' + str(result.suite.statistics))

    def test_common_flow_preserves_proven_40s_terms_destination_budget(self):
        common_flow = (
            ROOT / 'resources/keywords/common_onboarding/common_onboarding_keyword.resource'
        ).read_text(encoding='utf-8')
        app_constants = (
            ROOT / 'resources/app/app_constants.resource'
        ).read_text(encoding='utf-8')
        self.assertIn(
            'Wait For Landing Destination    ${TERMS_AND_CONDITIONS_WEBVIEW}    ${NCBD_LOADING_TIMEOUT}',
            common_flow,
        )
        self.assertRegex(
            app_constants,
            r'(?m)^\$\{NCBD_LOADING_TIMEOUT\}\s+40s$',
        )

    def test_landing_behavior(self):
        self._run_suite()

    def test_landing_robot_dryrun(self):
        self._run_suite(dryrun=True)


if __name__ == '__main__':
    unittest.main(verbosity=2)
