"""Exercise the production Product Selection keyword with synthetic UI boundaries."""
import io
import tempfile
import unittest
from pathlib import Path
from robot import run
from robot.api import ExecutionResult

ROOT = Path(__file__).resolve().parents[1]
PAGE = ROOT / 'resources/pages/etb/product_selection_page.resource'
LOCATORS = ROOT / 'locators/android/etb/product_selection_locators.resource'

FAKE = '''
from robot.libraries.BuiltIn import BuiltIn
class Row:
    def __init__(self, name, enabled=True, visible=True):
        self.name, self.enabled, self.visible = name, enabled, visible
    def find_elements(self, strategy, value):
        assert strategy == 'xpath' and 'TextProductName_' in value
        return [self.name]
class FakeUI:
    ROBOT_LIBRARY_SCOPE = 'TEST'
    def configure(self, scenario):
        self.rows = [Row('e-Savings Account')]
        self.selected = scenario in ('preselected', 'multiple_selected')
        self.summary = '0 selected' if scenario == 'zero_summary' else '2 selected' if scenario == 'multiple_selected' else '1 selected'
        self.hidden_summary = scenario == 'hidden_summary'
        self.pending_reads = 1 if scenario == 'delayed_summary' else 0
        self.blocked = scenario == 'no_selection'
        self.clicks = []
        if scenario == 'saving': self.rows = [Row('Saving Account')]
        if scenario == 'mixed': self.rows = [Row('Credit Card'), Row('e-Savings Account', False), Row('Saving Account', True, False), Row('Saving Account')]
        if scenario == 'unsupported': self.rows = [Row('Credit Card')]
        if scenario == 'empty': self.rows = []
    def get_webelements(self, locator):
        if 'TouchableOpacity_' in locator: return self.rows
        if 'TextProductName_' in locator: return [r.name for r in self.rows]
        if 'selected' in locator:
            if self.selected and self.pending_reads:
                self.pending_reads -= 1
                return []
            return [self.summary] if self.selected else []
        if 'CheckBox' in locator: return ['native-checkbox']
        return [locator]
    def get_source(self): return '<node resource-id="screenProductSelection_textTitle"/>'
    def element_should_be_enabled(self, element): pass
    def get_text(self, element): return element
    def get_element_attribute(self, element, attribute):
        if attribute in ('checked', 'selected'): raise AssertionError('NATIVE_CHECKBOX_STATE_MUST_NOT_BE_READ')
        assert attribute == 'enabled'
        return str(element.enabled).lower()
    def element_should_be_visible_now(self, element):
        if isinstance(element, Row): assert element.visible, 'NOT_VISIBLE'
        elif 'selected' in element: assert self.selected and not self.hidden_summary, 'NO_VISIBLE_SELECTION'
    def wait_until_element_is_visible(self, locator, timeout=None):
        self.element_should_be_visible_now(locator)
    def click_element(self, element):
        if isinstance(element, Row):
            assert element.name in ('Saving Account','e-Savings Account') and element.enabled and element.visible
            self.clicks.append('ROW')
            if not self.blocked: self.selected = True
        elif 'buttonConfirm' in element:
            assert self.selected, 'CONFIRM_BEFORE_SELECTION'
            self.clicks.append('CONFIRM')
        else: raise AssertionError('WRONG_CLICK_TARGET')
    def verify_clicks(self, expected):
        assert self.clicks == expected, str(self.clicks)
'''

class ProductSelectionRowInteractionTests(unittest.TestCase):
    def test_real_keyword_selects_visible_supported_row_and_requires_ui_acknowledgement(self):
        body = PAGE.read_text().split('*** Keywords ***', 1)[1]
        events = ['Visible', 'List Not Rendered', 'Rows Available', 'State', 'Action Start', 'Action End', 'Confirm Available', 'Confirm Start', 'Confirm End']
        stubs = ''.join('\nRecord Product Selection '+name+'\n    [Arguments]    ${output_dir}\n    No Operation\n' for name in events)
        cases = '''*** Test Cases ***
E Saving Alone
    Configure    e_saving
    Complete Product Selection    ${CATEGORIES}    category_policy=ANY_SUPPORTED
    Verify Clicks    ${ROW_CONFIRM}
Saving Alone
    Configure    saving
    Complete Product Selection    ${CATEGORIES}    category_policy=ANY_SUPPORTED
    Verify Clicks    ${ROW_CONFIRM}
Skips Unsupported Disabled And Hidden Rows
    Configure    mixed
    Complete Product Selection    ${CATEGORIES}    category_policy=ANY_SUPPORTED
    Verify Clicks    ${ROW_CONFIRM}
Existing Visible Selection Is Not Toggled
    Configure    preselected
    Complete Product Selection    ${CATEGORIES}    category_policy=ANY_SUPPORTED
    Verify Clicks    ${CONFIRM_ONLY}
No Visible Selection Never Confirms
    Configure    no_selection
    Run Keyword And Expect Error    *PRODUCT_SELECTION_NO_ITEM_SELECTED*    Complete Product Selection    ${CATEGORIES}    category_policy=ANY_SUPPORTED
    Verify Clicks    ${ROW_ONLY}
Unsupported Only Never Confirms
    Configure    unsupported
    Run Keyword And Expect Error    *SUPPORTED_CATEGORIES_MISSING*    Complete Product Selection    ${CATEGORIES}    category_policy=ANY_SUPPORTED
    Verify Clicks    ${EMPTY_LIST}
Empty List Never Confirms
    Configure    empty
    Run Keyword And Expect Error    *PRODUCT_SELECTION*    Complete Product Selection    ${CATEGORIES}    category_policy=ANY_SUPPORTED
    Verify Clicks    ${EMPTY_LIST}
Zero Summary Never Confirms
    Configure    zero_summary
    Run Keyword And Expect Error    *PRODUCT_SELECTION_NO_ITEM_SELECTED*    Complete Product Selection    ${CATEGORIES}    category_policy=ANY_SUPPORTED
    Verify Clicks    ${ROW_ONLY}
Hidden Summary Never Confirms
    Configure    hidden_summary
    Run Keyword And Expect Error    *PRODUCT_SELECTION_NO_ITEM_SELECTED*    Complete Product Selection    ${CATEGORIES}    category_policy=ANY_SUPPORTED
    Verify Clicks    ${ROW_ONLY}
Multiple Selected Summary Is Preserved
    Configure    multiple_selected
    Complete Product Selection    ${CATEGORIES}    category_policy=ANY_SUPPORTED
    Verify Clicks    ${CONFIRM_ONLY}
Delayed Summary Waits Without Repeating Click
    Configure    delayed_summary
    Set Test Variable    ${NCBD_LOADING_TIMEOUT}    1s
    Complete Product Selection    ${CATEGORIES}    category_policy=ANY_SUPPORTED
    Verify Clicks    ${ROW_CONFIRM}
Diagnostic Empty List Never Confirms
    Configure    empty
    ${result}=    Complete Product Selection    ${CATEGORIES}    diagnostic_mode=${True}    category_policy=ANY_SUPPORTED
    Should Be Equal    ${result}    CONFIRM_AVAILABLE_WITHOUT_ITEMS
    Verify Clicks    ${EMPTY_LIST}
Diagnostic E Saving Alone
    Configure    e_saving
    Complete Product Selection    ${CATEGORIES}    diagnostic_mode=${True}    category_policy=ANY_SUPPORTED
    Verify Clicks    ${ROW_CONFIRM}
'''
        with tempfile.TemporaryDirectory(prefix='bbl-product-row-') as directory:
            p = Path(directory)
            (p/'FakeUI.py').write_text(FAKE)
            (p/'page.resource').write_text('*** Keywords ***\n'+body)
            (p/'row.robot').write_text(f'''*** Settings ***
Library    FakeUI.py
Library    Collections
Library    OperatingSystem
Library    {ROOT / 'libraries/product_selection_contract.py'}
Resource    {LOCATORS}
Resource    page.resource
*** Variables ***
${{NCBD_LOADING_TIMEOUT}}    0.05s
@{{CATEGORIES}}    Saving    e-Saving
@{{ROW_CONFIRM}}    ROW    CONFIRM
@{{ROW_ONLY}}    ROW
@{{CONFIRM_ONLY}}    CONFIRM
@{{EMPTY_LIST}}
'''+cases+'\n*** Keywords ***\n'+stubs)
            code = run(str(p/'row.robot'), outputdir=str(p), console='none', stdout=io.StringIO(), stderr=io.StringIO(), log='NONE', report='NONE')
            result = ExecutionResult(str(p/'output.xml'))
            errors = '\n'.join(t.name+': '+t.message for t in result.suite.tests if t.status != 'PASS')
            self.assertEqual(code, 0, errors)
            self.assertEqual(len(result.suite.tests), 13)

if __name__ == '__main__': unittest.main()
