"""TC004 picker recovery uses synthetic dates and no device/backend I/O."""
import unittest
from unittest.mock import Mock, patch

from libraries import etb_dob_candidate as dob
from tests.test_etb_dob_candidate import Clock, FakePort


class TC004DOBRecoveryTests(unittest.TestCase):
    def setUp(self):
        self.clock = Clock()
        self.port = FakePort(self.clock, initial=(2000, 11, 9))
        self.port.driver = object()
        self.port.last_failure = 'DOB_DEADLINE_EXCEEDED'
        self.port.tc004_resume_used = False
        self.port.element = Mock()

    def invoke(self, diagnostic=True, driver_matches=True):
        controller = dob.ExactDOBController
        driver = self.port.driver if driver_matches else object()
        with patch.object(dob, '_LAST_DOB_PORT', self.port), \
                patch.object(dob, '_driver', return_value=driver), \
                patch('robot.libraries.BuiltIn.BuiltIn.get_variable_value', return_value=diagnostic), \
                patch.object(dob, 'ExactDOBController', side_effect=lambda p: controller(p, clock=self.clock, pause=self.clock.pause)):
            return dob.select_etb_dob_exact('09-11-2000', *(['xpath=synthetic'] * 7), resume_tc004=True)

    def test_resume_proves_exact_date_without_reopening_or_submitting_profile(self):
        result = self.invoke()
        self.assertTrue(result['exact_match'])
        self.assertFalse(result['profile_next_submitted'])
        self.assertNotIn('open', self.port.actions)
        self.assertEqual(self.port.actions.count('confirm'), 1)
        self.assertEqual([c.args[0] for c in self.port.element.call_args_list], ['year', 'month', 'day', 'done'])
        with self.assertRaisesRegex(dob.DOBError, 'DOB_TC004_RESUME_NOT_ALLOWED'):
            self.invoke()

    def test_non_tc004_wrong_session_and_other_failure_are_rejected(self):
        for diagnostic, driver_matches, reason in [(False, True, 'DOB_DEADLINE_EXCEEDED'), (True, False, 'DOB_DEADLINE_EXCEEDED'), (True, True, 'DOB_ELEMENT_MISSING_OR_AMBIGUOUS')]:
            with self.subTest(diagnostic=diagnostic, driver_matches=driver_matches, reason=reason):
                self.port.last_failure = reason
                with self.assertRaisesRegex(dob.DOBError, 'DOB_TC004_RESUME_NOT_ALLOWED'):
                    self.invoke(diagnostic, driver_matches)
        self.assertEqual(self.port.actions, [])

    def test_missing_picker_fails_without_reopening_and_consumes_recovery(self):
        self.port.element.side_effect = dob.DOBError('DOB_ELEMENT_MISSING_OR_AMBIGUOUS')
        with self.assertRaisesRegex(dob.DOBError, 'DOB_ELEMENT_MISSING_OR_AMBIGUOUS'):
            self.invoke()
        self.assertTrue(self.port.tc004_resume_used)
        self.assertEqual(self.port.actions, [])

    def test_resume_retains_deadline_and_exact_committed_value_check(self):
        self.port.read_delay = 46
        with self.assertRaisesRegex(dob.DOBError, 'DOB_DEADLINE_EXCEEDED'):
            self.invoke()
        self.setUp()
        self.port.committed_override = '10-11-2000'
        with self.assertRaisesRegex(dob.DOBError, 'DOB_COMMITTED_VALUE_MISMATCH'):
            self.invoke()


if __name__ == '__main__':
    unittest.main()
