"""Bounded startup-state observation for the Robot-owned application launch."""

from __future__ import annotations

import os
import re
import subprocess
import time
from typing import Any, cast

from robot.libraries.BuiltIn import BuiltIn

from libraries.android_adb import resolve_adb_executable

_LANDING_MARKERS = ("screenLanding_skipButton", "screenLanding_buttonReady")
_TERMS_MARKERS = ("Terms and Conditions", "termsAndConditions")
_EXACT_ERROR_TEXT_MARKERS = (
    "Something went wrong on our side",
    "Please try again later",
    "Close app",
    "The app requires newer operating system",
)
_EXACT_ERROR_CODE_PATTERN = re.compile(r"\b(?:RGI-\d+|AJI-001)\b")
_TERMINAL_STATES = {"LANDING", "PERMISSION_DIALOG", "TERMS", "KNOWN_ERROR"}


def _appium() -> Any:
    return cast(Any, BuiltIn().get_library_instance("AppiumLibrary"))


def _snapshot() -> tuple[str, str]:
    appium = _appium()
    try:
        source = str(appium._current_application().page_source)
    except Exception:
        source = ""
    try:
        activity = str(appium.get_activity())
    except Exception:
        activity = ""
    return source, activity


def _classify(source: str, activity: str) -> str:
    if any(marker in source for marker in _LANDING_MARKERS):
        return "LANDING"
    if "permissioncontroller" in source.lower() or "GrantPermissionsActivity" in activity:
        return "PERMISSION_DIALOG"
    if any(marker in source for marker in _TERMS_MARKERS):
        return "TERMS"
    if any(marker in source for marker in _EXACT_ERROR_TEXT_MARKERS) or _EXACT_ERROR_CODE_PATTERN.search(source):
        return "KNOWN_ERROR"
    if activity and "com.bangkokbank.blue" not in activity:
        return "UNKNOWN"
    if source or activity:
        return "STARTUP_TRANSITION"
    return "APP_INITIALIZING"


def _diagnostic_adb_state() -> str:
    """Return only a sanitized classified ADB hierarchy state for diagnostic control."""
    if os.getenv("ANDROID_EXECUTION_TARGET", "") != "DIAGNOSTIC_CONTROL":
        return "NOT_APPLICABLE"
    serial = os.getenv("DEVICE_UDID", "")
    if not serial:
        return "DEVICE_UDID_MISSING"
    dump_path = "/sdcard/etb_startup_diag.xml"
    try:
        dump = subprocess.run(
            [resolve_adb_executable(), "-s", serial, "shell", "uiautomator", "dump", "--compressed", dump_path],
            capture_output=True,
            text=True,
            timeout=10,
            check=False,
        )
        if dump.returncode != 0:
            return "ADB_DUMP_FAILED"
        source = subprocess.run(
            [resolve_adb_executable(), "-s", serial, "shell", "cat", dump_path],
            capture_output=True,
            text=True,
            timeout=10,
            check=False,
        )
        if source.returncode != 0:
            return "ADB_READ_FAILED"
        return _classify(source.stdout, "com.bangkokbank.blue.MainActivity")
    except (OSError, subprocess.TimeoutExpired):
        return "ADB_PROBE_FAILED"


def wait_for_real_device_startup_state(timeout: float = 60.0, interval: float = 0.5) -> str:
    """Poll the current Robot session until a bounded actionable state appears."""
    deadline = time.monotonic() + float(timeout)
    last_state = "APP_INITIALIZING"
    while True:
        source, activity = _snapshot()
        state = _classify(source, activity)
        if state != last_state:
            BuiltIn().log(f"STARTUP_STATE={state}", level="INFO")
            last_state = state
        if state in _TERMINAL_STATES:
            return state
        remaining = deadline - time.monotonic()
        if remaining <= 0:
            adb_state = _diagnostic_adb_state()
            raise AssertionError(
                f"STARTUP_STATE_TIMEOUT last_state={last_state} timeout_seconds={timeout} adb_state={adb_state}"
            )
        time.sleep(min(float(interval), remaining))
