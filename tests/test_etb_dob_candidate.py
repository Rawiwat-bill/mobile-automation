"""Deterministic DOB safety regression; synthetic dates, zero mobile/network I/O."""
from __future__ import annotations
import calendar
from datetime import date, timedelta
import math
from pathlib import Path
import sys
import unittest
from unittest.mock import patch
ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT))
from libraries.etb_dob_candidate import (DOBError, ExactDate, Policy,
    ExactDOBController, AppiumDOBPort, gesture_points, month_number, parse_dmy, parse_wheel)

class Clock:
    def __init__(self): self.now=0.0
    def __call__(self): return self.now
    def pause(self, seconds): self.now+=seconds

class FakePort:
    def __init__(self, clock, initial=(2026,9,23)):
        self.clock=clock
        self.values=dict(zip(('year','month','day'),initial))
        self.actions=[]
        self.samples={}
        self.committed_override=None
        self.no_progress=False
        self.closed=False
        self.opened=False
        self.confirmed=False
        self.read_delay=0.002
    def io(self): self.clock.pause(self.read_delay)
    def open_picker(self): self.io(); self.opened=True; self.actions.append('open')
    def read_wheel(self,wheel):
        self.io()
        sequence=self.samples.get(wheel,[])
        if sequence:
            value=sequence.pop(0)
            self.values[wheel]=value
        return self.values[wheel]
    def swipe(self,wheel,direction,fraction,duration):
        self.io(); self.actions.append('swipe')
        if self.no_progress: return
        low,high=(1900,2030) if wheel=='year' else ((1,12) if wheel=='month' else (1,calendar.monthrange(self.values['year'],self.values['month'])[1]))
        steps=max(1,round(fraction*10))
        self.values[wheel]=min(high,max(low,self.values[wheel]+direction*steps))
        if wheel in ('year','month'):
            self.values['day']=min(self.values['day'],calendar.monthrange(self.values['year'],self.values['month'])[1])
    def confirm(self): self.io(); self.confirmed=True; self.closed=True; self.actions.append('confirm')
    def picker_closed(self): self.io(); return self.closed
    def blur(self): self.io(); self.actions.append('blur')
    def read_committed(self):
        self.io()
        if self.committed_override is not None: return self.committed_override
        return f"{self.values['day']:02d}-{self.values['month']:02d}-{self.values['year']:04d}"

def engine(port=None, clock=None, **policy):
    clock=clock or Clock(); port=port or FakePort(clock)
    settings=dict(total_seconds=45,settle_seconds=0.035,poll_seconds=0.01,minimum_samples=3,intermediate_settle_seconds=0.015,intermediate_poll_seconds=0.005,intermediate_samples=2)
    settings.update(policy)
    return ExactDOBController(port,Policy(**settings),clock,clock.pause),port,clock

class ExactDateTests(unittest.TestCase):
    def test_numeric_formats_are_semantically_exact(self):
        for value in ('09-11-2000','9-11-2000','09/11/2000','09 11 2000'):
            self.assertEqual(parse_dmy(value),ExactDate(9,11,2000))
    def test_english_full_and_abbreviated_months(self):
        for value in ('09 Nov 2000','09 November 2000','09-NOV-2000'):
            self.assertEqual(parse_dmy(value),ExactDate(9,11,2000))
    def test_leap_day_valid(self): self.assertEqual(parse_dmy('29-02-2000'),ExactDate(29,2,2000))
    def test_non_leap_day_is_not_normalized(self):
        with self.assertRaisesRegex(DOBError,'DOB_INVALID_CALENDAR_INPUT'): parse_dmy('29-02-2001')
    def test_impossible_end_month_is_not_normalized(self):
        with self.assertRaises(DOBError): parse_dmy('31-04-2000')
    def test_ambiguous_iso_not_silently_reinterpreted(self):
        with self.assertRaises(DOBError): parse_dmy('2000-11-09')
    def test_mixed_delimiters_rejected(self):
        with self.assertRaises(DOBError): parse_dmy('09/11-2000')
    def test_trailing_error_text_rejected(self):
        with self.assertRaises(DOBError): parse_dmy('09-11-2000 WRONG')
    def test_unsupported_locale_rejected(self):
        with self.assertRaises(DOBError): parse_dmy('09 พฤศจิกายน 2000')
    def test_invalid_month_is_fixed_diagnostic(self):
        for value in ('13','0','NotAMonth'):
            with self.assertRaisesRegex(DOBError,'^DOB_MONTH_UNSUPPORTED$'): month_number(value)
    def test_repr_does_not_expose_date(self):
        self.assertNotIn('2000',repr(ExactDate(9,11,2000)))
    def test_all_calendar_dates_1900_to_2100_roundtrip(self):
        current=date(1900,1,1); end=date(2100,12,31)
        while current<=end:
            value=current.strftime('%d-%m-%Y')
            self.assertEqual(parse_dmy(value).ymd,(current.year,current.month,current.day))
            current+=timedelta(days=1)
    def test_wheel_accessibility_parsing(self):
        self.assertEqual(parse_wheel('Year picker, 2000','year'),2000)
        self.assertEqual(parse_wheel('Month picker, November','month'),11)
        self.assertEqual(parse_wheel('Date picker, 09','day'),9)
    def test_missing_wheel_selected_value_fails(self):
        for value in ('',None,'2000','Year picker, many values'):
            with self.assertRaises(DOBError): parse_wheel(value,'year')
    def test_wheel_ranges_checked(self):
        for value,wheel in [('Date picker, 32','day'),('Month picker, 13','month'),('Year picker, 0','year')]:
            with self.assertRaises(DOBError): parse_wheel(value,wheel)

class ControllerSafetyTests(unittest.TestCase):
    def test_initial_transient_target_does_not_return_early(self):
        c=Clock(); p=FakePort(c,(2002,1,1)); p.samples['year']=[2000,2001,2001,2001,2001,2001]
        e,_,_=engine(p,c)
        result=e.select(ExactDate(1,1,2000))
        self.assertTrue(result['exact_match']); self.assertGreater(result['gestures'],0)
        self.assertEqual(p.values['year'],2000)
    def test_post_swipe_transient_target_then_overshoot_recovered(self):
        c=Clock(); p=FakePort(c,(2002,1,1)); original=p.swipe
        def swipe(*args):
            original(*args)
            if len([a for a in p.actions if a=='swipe'])==1:
                p.samples['year']=[2000,1999,1999,1999,1999,1999]
        p.swipe=swipe
        e,_,_=engine(p,c)
        self.assertTrue(e.select(ExactDate(1,1,2000))['exact_match'])
        self.assertGreater(e.metrics['gestures'],1)
    def test_correct_already_selected_requires_settle_and_commit(self):
        e,p,c=engine(); expected=ExactDate(23,9,2026)
        result=e.select(expected)
        self.assertGreater(result['samples'],10)
        self.assertEqual(result['gestures'],0)
        self.assertEqual(p.actions,['open','confirm','blur'])
    def test_no_progress_is_bounded(self):
        e,p,c=engine(); p.no_progress=True
        with self.assertRaisesRegex(DOBError,'DOB_PICKER_NO_PROGRESS'): e.select(ExactDate(1,1,2000))
        self.assertFalse(p.confirmed)
        self.assertEqual(e.metrics['gestures'],3)
    def test_read_after_deadline_cannot_pass(self):
        e,p,c=engine(total_seconds=0.10)
        p.read_delay=0.11
        with self.assertRaisesRegex(DOBError,'DOB_DEADLINE_EXCEEDED'): e.select(ExactDate(23,9,2026))
        self.assertFalse(e.metrics['exact_match'])
    def test_confirm_after_deadline_cannot_pass(self):
        e,p,c=engine(total_seconds=1.0)
        def confirm(): c.pause(2.0); p.closed=True
        p.confirm=confirm
        with self.assertRaisesRegex(DOBError,'DOB_DEADLINE_EXCEEDED'): e.select(ExactDate(23,9,2026))
    def test_committed_wrong_date_never_passes(self):
        e,p,c=engine(); p.committed_override='22-09-2026'
        with self.assertRaisesRegex(DOBError,'DOB_COMMITTED_VALUE_MISMATCH'): e.select(ExactDate(23,9,2026))
        self.assertFalse(e.metrics['exact_match'])
    def test_malformed_committed_value_fails(self):
        e,p,c=engine(); p.committed_override='unreadable'
        with self.assertRaisesRegex(DOBError,'DOB_DISPLAY_FORMAT_UNSUPPORTED'): e.select(ExactDate(23,9,2026))
    def test_year_month_changes_clamp_day_and_day_is_reselected(self):
        c=Clock(); p=FakePort(c,(2024,1,31)); e,_,_=engine(p,c)
        self.assertTrue(e.select(ExactDate(28,2,2001))['exact_match'])
        self.assertEqual(p.values,{'year':2001,'month':2,'day':28})
    def test_leap_year_selects_exact_day(self):
        c=Clock(); p=FakePort(c,(2001,2,28)); e,_,_=engine(p,c)
        self.assertTrue(e.select(ExactDate(29,2,2000))['exact_match'])
    def test_all_wheels_checked_again_before_done(self):
        c=Clock(); p=FakePort(c,(2026,9,23)); reads={'day':0}; original=p.read_wheel
        def read(w):
            if w=='day':
                reads[w]+=1
                if reads[w]>=5: p.values['year']=2025
            return original(w)
        p.read_wheel=read; e,_,_=engine(p,c)
        with self.assertRaisesRegex(DOBError,'DOB_WHEEL_TRIPLE_MISMATCH'): e.select(ExactDate(23,9,2026))
        self.assertFalse(p.confirmed)
    def test_never_closing_picker_times_out_without_blur(self):
        e,p,c=engine(total_seconds=0.8); p.picker_closed=lambda: False
        with self.assertRaisesRegex(DOBError,'DOB_DEADLINE_EXCEEDED'): e.select(ExactDate(23,9,2026))
        self.assertNotIn('blur',p.actions)
    def test_upstream_exception_is_not_exposed(self):
        e,p,c=engine()
        def fail(): raise RuntimeError('SENSITIVE_VALUE_MUST_NOT_LEAK')
        p.open_picker=fail
        with self.assertRaisesRegex(DOBError,'^DOB_UI_OPERATION_FAILED$') as caught: e.select(ExactDate(1,1,2000))
        self.assertNotIn('SENSITIVE_VALUE',str(caught.exception))
    def test_gesture_limit_is_real(self):
        e,p,c=engine(max_gestures=1)
        with self.assertRaisesRegex(DOBError,'DOB_GESTURE_LIMIT'): e.select(ExactDate(1,1,1900))
        self.assertFalse(p.confirmed)
    def test_metrics_reset_for_each_interaction(self):
        e,p,c=engine(); e.select(ExactDate(1,1,2000)); first=e.metrics['gestures']
        second=e.select(ExactDate(1,1,2000))
        self.assertGreater(first,0); self.assertEqual(second['gestures'],0)
    def test_metrics_contain_no_dates(self):
        e,p,c=engine(); result=e.select(ExactDate(9,11,2000))
        self.assertNotIn('2000',str(result)); self.assertNotIn('09-11',str(result))
        self.assertFalse(result['profile_next_submitted'])
    def test_invalid_input_rejected_before_ui(self):
        e,p,c=engine()
        with self.assertRaises(DOBError): e.select('not an ExactDate')
        self.assertEqual(p.actions,[])
    def test_oscillating_wheel_times_out_not_false_pass(self):
        e,p,c=engine(total_seconds=0.8); p.samples['year']=[2000,2001]*100
        with self.assertRaisesRegex(DOBError,'DOB_DEADLINE_EXCEEDED'): e.select(ExactDate(1,1,2000))
        self.assertFalse(p.confirmed)

class GeometryTests(unittest.TestCase):
    def test_all_points_are_in_both_axes(self):
        rect={'x':700,'y':1000,'width':300,'height':800}
        for direction in (-1,1):
            for fraction in (.04,.2,.4,.6):
                x1,y1,x2,y2=gesture_points(rect,direction,fraction)
                self.assertTrue(700<x1<1000 and 700<x2<1000 and 1000<y1<1800 and 1000<y2<1800)
    def test_negative_x_rejected(self):
        with self.assertRaises(DOBError): gesture_points({'x':-500,'y':1000,'width':100,'height':100},1,.4)
    def test_nonfinite_geometry_rejected(self):
        with self.assertRaises(DOBError): gesture_points({'x':math.nan,'y':1000,'width':100,'height':100},1,.4)
    def test_zero_geometry_rejected(self):
        with self.assertRaises(DOBError): gesture_points({'x':100,'y':1000,'width':0,'height':100},1,.4)
    def test_invalid_fraction_rejected(self):
        for fraction in (0,1,2,math.nan):
            with self.assertRaises(DOBError): gesture_points({'x':1,'y':1,'width':100,'height':100},1,fraction)
    def test_invalid_direction_rejected(self):
        with self.assertRaises(DOBError): gesture_points({'x':1,'y':1,'width':100,'height':100},0,.4)
    def test_invalid_policy_rejected(self):
        for args in ({'total_seconds':0},{'minimum_samples':1},{'drag_ms':1},{'settle_seconds':0}):
            with self.assertRaises(DOBError): Policy(**args)

class AppiumPortReacquireTests(unittest.TestCase):
    class Element:
        def __init__(self, displayed=True, enabled=True, stale=False):
            self.displayed=displayed; self.enabled=enabled; self.stale=stale
            self.rect={'x':100,'y':200,'width':400,'height':120}
        def is_displayed(self):
            if self.stale:
                from selenium.common.exceptions import StaleElementReferenceException
                raise StaleElementReferenceException()
            return self.displayed
        def is_enabled(self):
            return self.enabled

    class Driver:
        def __init__(self, elements):
            self.elements=list(elements); self.calls=0
            self.capabilities={'udid':'REAL-DEVICE'}
        def find_elements(self, by, locator):
            self.calls += 1
            return list(self.elements)

    def test_single_actionable_candidate_wins_over_transient_duplicate(self):
        hidden=self.Element(displayed=False, enabled=True)
        live=self.Element(displayed=True, enabled=True)
        driver=self.Driver([hidden,live])
        port=AppiumDOBPort(driver, {'open':'xpath=//*[@resource-id="dob"]'})
        self.assertIs(port.element('open'), live)
        self.assertEqual(driver.calls, 1)

    def test_stale_cached_reference_is_reacquired(self):
        stale=self.Element(stale=True)
        live=self.Element()
        driver=self.Driver([live])
        port=AppiumDOBPort(driver, {'open':'xpath=//*[@resource-id="dob"]'})
        port.elements['open']=stale
        self.assertIs(port.element('open'), live)
        self.assertEqual(driver.calls, 1)

    def test_open_picker_uses_device_bound_adb_center_tap(self):
        live=self.Element()
        driver=self.Driver([live])
        port=AppiumDOBPort(driver, {'open':'xpath=//*[@resource-id="dob"]'})
        with (
            patch('libraries.android_adb.resolve_adb_executable', return_value='/adb'),
            patch('libraries.etb_dob_candidate.subprocess.run') as run,
        ):
            run.return_value.returncode=0
            run.return_value.stdout=''
            run.return_value.stderr=''
            port.open_picker()
        run.assert_called_once_with(
            ['/adb','-s','REAL-DEVICE','shell','input','tap','300','260'],
            capture_output=True,
            text=True,
            timeout=5.0,
            check=False,
        )

if __name__=='__main__': unittest.main(verbosity=2)
