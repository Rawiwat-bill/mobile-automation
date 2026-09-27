"""Opt-in ETB DOB controller: exact committed date, settled wheels, bounded I/O.

Does not load/modify test data, submit Profile Next, reset the app, call CIS,
set app state, or alter driver settings. Production locators are passed from
Robot resources. The legacy/NTB wheel implementation remains unchanged.
All public diagnostics and return values deliberately exclude date values.
"""
from __future__ import annotations

from dataclasses import dataclass, field
from datetime import date
import math
import re
import subprocess
import time
from typing import Callable, Protocol

try:
    from robot.api.deco import keyword
except ImportError:  # The core can be tested without Robot/Appium installed.
    def keyword(name):
        return lambda function: function

ROBOT_AUTO_KEYWORDS = False
_MONTHS = ('january', 'february', 'march', 'april', 'may', 'june',
           'july', 'august', 'september', 'october', 'november', 'december')
_MONTH_NUMBERS = {token: i for i, name in enumerate(_MONTHS, 1)
                  for token in (name, name[:3])}


class DOBError(AssertionError):
    """Fixed non-sensitive diagnostic; never embed upstream exceptions."""


@dataclass(frozen=True)
class ExactDate:
    day: int = field(repr=False)
    month: int = field(repr=False)
    year: int = field(repr=False)

    def __post_init__(self):
        try:
            date(self.year, self.month, self.day)
        except (ValueError, TypeError, OverflowError):
            raise DOBError('DOB_INVALID_CALENDAR_INPUT') from None

    @property
    def ymd(self):
        return self.year, self.month, self.day


def month_number(token: object) -> int:
    text = str(token).strip().lower()
    if re.fullmatch(r'[0-9]{1,2}', text):
        number = int(text)
    else:
        number = _MONTH_NUMBERS.get(text, 0)
    if not 1 <= number <= 12:
        raise DOBError('DOB_MONTH_UNSUPPORTED')
    return number


def parse_dmy(value: object) -> ExactDate:
    """Only explicit Gregorian D-M-Y; no fuzzy parsing or silent correction."""
    text = str(value).strip()
    match = re.fullmatch(r'([0-9]{1,2})([-/ ])([0-9]{1,2}|[A-Za-z]+)\2([0-9]{4})', text)
    if match is None:
        raise DOBError('DOB_DISPLAY_FORMAT_UNSUPPORTED')
    return ExactDate(int(match[1]), month_number(match[3]), int(match[4]))


def parse_wheel(value: object, wheel: str) -> int:
    text = str(value).strip()
    if ',' not in text:
        raise DOBError('DOB_PICKER_ACCESSIBILITY_VALUE_UNAVAILABLE')
    token = text.rsplit(',', 1)[1].strip()
    if wheel == 'month':
        return month_number(token)
    if not re.fullmatch(r'[0-9]{1,4}', token):
        raise DOBError('DOB_PICKER_ACCESSIBILITY_VALUE_UNAVAILABLE')
    number = int(token)
    maximum = 31 if wheel == 'day' else 9999
    if wheel not in ('day', 'year') or not 1 <= number <= maximum:
        raise DOBError('DOB_PICKER_ACCESSIBILITY_VALUE_UNAVAILABLE')
    return number


@dataclass(frozen=True)
class Policy:
    total_seconds: float = 45.0
    # Strict acceptance settle: used for initial state, target acceptance,
    # final three-wheel proof and committed field verification.
    settle_seconds: float = 0.35
    poll_seconds: float = 0.10
    minimum_samples: int = 3
    # Intermediate settle: only used to measure movement after a swipe.
    # It can steer the next gesture but can never directly authorize PASS.
    intermediate_settle_seconds: float = 0.075
    intermediate_poll_seconds: float = 0.075
    intermediate_samples: int = 2
    max_gestures: int = 50
    no_progress_limit: int = 3
    drag_ms: int = 180

    def __post_init__(self):
        if not (math.isfinite(self.total_seconds) and self.total_seconds > 0
                and 0 < self.poll_seconds <= self.settle_seconds < self.total_seconds
                and self.minimum_samples >= 2
                and 0 < self.intermediate_poll_seconds <= self.intermediate_settle_seconds < self.total_seconds
                and self.intermediate_samples >= 2
                and self.max_gestures > 0
                and self.no_progress_limit > 0 and 100 <= self.drag_ms <= 1000):
            raise DOBError('DOB_POLICY_INVALID')


class Port(Protocol):
    def open_picker(self) -> None: ...
    def read_wheel(self, wheel: str) -> int: ...
    def swipe(self, wheel: str, direction: int, fraction: float, duration: int) -> None: ...
    def confirm(self) -> None: ...
    def picker_closed(self) -> bool: ...
    def blur(self) -> None: ...
    def read_committed(self) -> str: ...


class ExactDOBController:
    def __init__(self, port: Port, policy: Policy | None = None,
                 clock: Callable[[], float] = time.monotonic,
                 pause: Callable[[float], None] = time.sleep):
        self.port, self.policy = port, policy or Policy()
        self.clock, self.pause = clock, pause
        self.metrics = {}
        self.started = self.deadline = 0.0

    def check(self):
        if self.clock() >= self.deadline:
            raise DOBError('DOB_DEADLINE_EXCEEDED')

    def io(self, function, *args):
        self.check()
        try:
            result = function(*args)
        except DOBError:
            raise
        except Exception:
            raise DOBError('DOB_UI_OPERATION_FAILED') from None
        # Never turn an operation returning after the deadline into PASS.
        self.check()
        return result

    def stable(self, function, *, minimum_samples=None, settle_seconds=None, poll_seconds=None):
        minimum_samples = self.policy.minimum_samples if minimum_samples is None else minimum_samples
        settle_seconds = self.policy.settle_seconds if settle_seconds is None else settle_seconds
        poll_seconds = self.policy.poll_seconds if poll_seconds is None else poll_seconds
        previous = object()
        changed_at, count = self.clock(), 0
        while True:
            value = self.io(function)
            self.metrics['samples'] += 1
            now = self.clock()
            if value == previous:
                count += 1
            else:
                previous, count, changed_at = value, 1, now
            if count >= minimum_samples and now - changed_at >= settle_seconds:
                self.check()
                return value
            self.pause(min(poll_seconds, max(0.0, self.deadline - now)))

    def intermediate_stable(self, function):
        return self.stable(
            function,
            minimum_samples=self.policy.intermediate_samples,
            settle_seconds=self.policy.intermediate_settle_seconds,
            poll_seconds=self.policy.intermediate_poll_seconds,
        )

    def select_wheel(self, wheel: str, target: int):
        started = self.clock()
        samples_before = self.metrics['samples']
        gestures_before = self.metrics['gestures']
        current = self.stable(lambda: self.port.read_wheel(wheel))
        no_progress, fraction = 0, 0.40
        while current != target:
            if self.metrics['gestures'] >= self.policy.max_gestures:
                raise DOBError('DOB_GESTURE_LIMIT')
            direction = 1 if target > current else -1
            distance = abs(target - current)
            # Geometry is relative to the verified live wheel. Never assume wrap.
            if distance <= 2:
                fraction = min(fraction, 0.20)
            self.io(self.port.swipe, wheel, direction, fraction, self.policy.drag_ms)
            self.metrics['gestures'] += 1

            # A fast bounded settle is enough to steer the next gesture, but is
            # never enough to authorize target acceptance. If it appears to hit
            # the target, repeat the strict settle before leaving the wheel.
            following = self.intermediate_stable(lambda: self.port.read_wheel(wheel))
            if following == target:
                following = self.stable(lambda: self.port.read_wheel(wheel))

            delta = abs(following - current)
            self.metrics['wheel_step_deltas'].setdefault(wheel, []).append(delta)
            if delta == 0:
                no_progress += 1
                if no_progress >= self.policy.no_progress_limit:
                    raise DOBError('DOB_PICKER_NO_PROGRESS')
            else:
                no_progress = 0
                if (target - current) * (target - following) < 0:
                    self.metrics['overshoot_corrections'] += 1
                # Recalibrate only from an observed settled movement. Re-evaluate
                # direction after every gesture; never chain unobserved swipes.
                fraction = max(0.04, min(0.60, fraction * abs(target - following) / delta))
            current = following
        self.metrics['wheel_seconds'][wheel] = round(self.clock() - started, 4)
        self.metrics['wheel_samples'][wheel] = self.metrics['samples'] - samples_before
        self.metrics['wheel_gestures'][wheel] = self.metrics['gestures'] - gestures_before

    def select(self, expected: ExactDate):
        if not isinstance(expected, ExactDate):
            raise DOBError('DOB_EXPECTED_DATE_INVALID')
        self.started = self.clock()
        self.deadline = self.started + self.policy.total_seconds
        self.metrics = {'strategy': 'STABLE_V1', 'status': 'RUNNING', 'samples': 0,
                        'gestures': 0, 'overshoot_corrections': 0,
                        'wheel_seconds': {}, 'wheel_samples': {}, 'wheel_gestures': {},
                        'wheel_step_deltas': {}, 'stage_seconds': {},
                        'exact_match': False, 'profile_next_submitted': False}
        try:
            stage_started = self.clock()
            self.io(self.port.open_picker)
            self.metrics['stage_seconds']['open_picker'] = round(self.clock() - stage_started, 4)

            for wheel, target in zip(('year', 'month', 'day'), expected.ymd):
                self.select_wheel(wheel, target)

            # Year/month changes may clamp day; prove the complete tuple again.
            stage_started = self.clock()
            actual = self.stable(lambda: tuple(self.port.read_wheel(w) for w in ('year', 'month', 'day')))
            self.metrics['stage_seconds']['final_triple'] = round(self.clock() - stage_started, 4)
            if actual != expected.ymd:
                raise DOBError('DOB_WHEEL_TRIPLE_MISMATCH')

            stage_started = self.clock()
            self.io(self.port.confirm)
            while not self.io(self.port.picker_closed):
                self.pause(min(self.policy.poll_seconds, max(0.0, self.deadline-self.clock())))
            self.io(self.port.blur)
            self.metrics['stage_seconds']['confirm_close_blur'] = round(self.clock() - stage_started, 4)

            stage_started = self.clock()
            committed = self.stable(lambda: parse_dmy(self.port.read_committed()))
            self.metrics['stage_seconds']['committed_proof'] = round(self.clock() - stage_started, 4)
            if committed != expected:
                raise DOBError('DOB_COMMITTED_VALUE_MISMATCH')
            self.check()
            self.metrics.update(status='PASS', exact_match=True)
        except Exception as error:
            code = str(error) if isinstance(error, DOBError) else 'DOB_UI_OPERATION_FAILED'
            self.metrics.update(status='FAIL', reason=code)
            raise DOBError(code) from None
        finally:
            self.metrics['elapsed_seconds'] = round(self.clock()-self.started, 4)
        return dict(self.metrics)


def gesture_points(rect: dict, direction: int, fraction: float):
    try:
        x, y, width, height = (float(rect[k]) for k in ('x', 'y', 'width', 'height'))
    except (KeyError, TypeError, ValueError):
        raise DOBError('DOB_PICKER_GEOMETRY_INVALID') from None
    if not all(math.isfinite(v) for v in (x, y, width, height, fraction)) or min(width, height) <= 0 or x < 0 or y < 0 or direction not in (-1, 1) or not 0 < fraction < 1:
        raise DOBError('DOB_PICKER_GEOMETRY_INVALID')
    cx, cy = x+width/2, y+height/2
    half = height*fraction/2
    points = tuple(int(v) for v in (cx, cy+direction*half, cx, cy-direction*half))
    if not all(x < px < x+width and y < py < y+height for px, py in (points[:2], points[2:])):
        raise DOBError('DOB_GESTURE_OUTSIDE_PICKER')
    return points


class AppiumDOBPort:
    """Lazy Appium adapter. No date values are used as selectors or logged."""
    def __init__(self, driver, locators: dict):
        self.driver, self.locators, self.elements = driver, dict(locators), {}

    def element(self, key):
        from selenium.common.exceptions import StaleElementReferenceException
        from appium.webdriver.common.appiumby import AppiumBy
        locator = self.locators[key]
        if not locator.startswith('xpath='):
            raise DOBError('DOB_LOCATOR_UNSUPPORTED')

        deadline = time.monotonic() + 1.5
        last_count = 0
        last_actionable = False
        while True:
            element = self.elements.get(key)
            if element is not None:
                try:
                    if element.is_displayed() and element.is_enabled():
                        return element
                    last_count, last_actionable = 1, False
                except StaleElementReferenceException:
                    pass
                self.elements.pop(key, None)

            try:
                found = self.driver.find_elements(AppiumBy.XPATH, locator[6:])
                last_count = len(found)
                if last_count == 1:
                    candidate = found[0]
                    if candidate.is_displayed() and candidate.is_enabled():
                        self.elements[key] = candidate
                        return candidate
                    last_actionable = False
                else:
                    last_actionable = False
            except StaleElementReferenceException:
                self.elements.pop(key, None)

            if time.monotonic() >= deadline:
                if last_count != 1:
                    raise DOBError('DOB_ELEMENT_MISSING_OR_AMBIGUOUS')
                if not last_actionable:
                    raise DOBError('DOB_ELEMENT_NOT_ACTIONABLE')
                raise DOBError('DOB_ELEMENT_STALE')
            time.sleep(0.05)

    def open_picker(self):
        self.element('open').click()
        self.elements.clear()

    def read_wheel(self, wheel):
        element = self.element(wheel)
        return parse_wheel(element.get_attribute('content-desc'), wheel)

    def swipe(self, wheel, direction, fraction, duration):
        rect = self.element(wheel).rect
        x1, y1, x2, y2 = gesture_points(rect, direction, fraction)
        capabilities = getattr(self.driver, 'capabilities', {}) or {}
        serial = capabilities.get('udid') or capabilities.get('appium:udid')
        if not isinstance(serial, str) or not serial:
            raise DOBError('DOB_DEVICE_IDENTITY_UNAVAILABLE')
        from libraries.android_adb import resolve_adb_executable
        try:
            result = subprocess.run(
                [
                    resolve_adb_executable(), '-s', serial, 'shell', 'input', 'swipe',
                    str(x1), str(y1), str(x2), str(y2), str(int(duration)),
                ],
                capture_output=True,
                text=True,
                timeout=max(3.0, (float(duration) / 1000.0) + 2.0),
                check=False,
            )
        except (OSError, subprocess.TimeoutExpired):
            raise DOBError('DOB_GESTURE_FAILED') from None
        if result.returncode != 0:
            raise DOBError('DOB_GESTURE_FAILED')

    def confirm(self):
        self.element('done').click()
        self.elements.clear()

    def picker_closed(self):
        from appium.webdriver.common.appiumby import AppiumBy
        xpaths = [self.locators[name][6:] for name in ('year', 'month', 'day')]
        if any(not self.locators[name].startswith('xpath=') for name in ('year', 'month', 'day')):
            raise DOBError('DOB_LOCATOR_UNSUPPORTED')
        union = ' | '.join(f'({xpath})' for xpath in xpaths)
        return not any(e.is_displayed() for e in self.driver.find_elements(AppiumBy.XPATH, union))

    def blur(self):
        # Screen-specific existing title, not a hard-coded blank coordinate.
        self.element('blur').click()
        self.elements.clear()

    def read_committed(self):
        element = self.element('field')
        if str(element.get_attribute('focused')).lower() != 'false':
            raise DOBError('DOB_FIELD_NOT_BLURRED')
        return element.text


def _driver():
    from robot.libraries.BuiltIn import BuiltIn
    return BuiltIn().get_library_instance('AppiumLibrary')._current_application()


@keyword('Select ETB DOB Exact')
def select_etb_dob_exact(expected, open_locator, year_locator, month_locator,
                         day_locator, done_locator, field_locator, blur_locator):
    """Returns only non-sensitive metrics. Requires the DOB output sanitizer."""
    target = parse_dmy(expected)
    port = AppiumDOBPort(_driver(), dict(open=open_locator, year=year_locator,
        month=month_locator, day=day_locator, done=done_locator,
        field=field_locator, blur=blur_locator))
    return ExactDOBController(port).select(target)


@keyword('Verify Committed DOB Exact')
def verify_committed_dob_exact(day, month, year, field_locator):
    try:
        target = ExactDate(int(day), month_number(month), int(year))
    except (ValueError, TypeError, OverflowError):
        raise DOBError('DOB_EXPECTED_DATE_INVALID') from None
    port = AppiumDOBPort(_driver(), {'field': field_locator})
    engine = ExactDOBController(port, Policy(total_seconds=5.0))
    engine.started=engine.clock()
    engine.deadline=engine.started+engine.policy.total_seconds
    engine.metrics={'samples':0}
    actual=engine.stable(lambda: parse_dmy(port.read_committed()))
    if actual != target:
        raise DOBError('DOB_COMMITTED_VALUE_MISMATCH')
    return True
