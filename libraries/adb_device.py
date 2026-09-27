import hashlib
import json
import re
import subprocess
import time
import xml.etree.ElementTree as ET
from datetime import datetime, timezone
from pathlib import Path

from robot.api.deco import keyword, not_keyword
from robot.libraries.BuiltIn import BuiltIn

from libraries.android_adb import resolve_adb_executable
from libraries.evidence_scope import resolve_private_evidence_dir

_TEXT_ATTRIBUTE = re.compile(r'\b(text|content-desc|hint|value|password)="[^"]*"')
_EXACT_ERROR_CODE_PATTERN = re.compile(r"\b(?:AJI-001|RGI-\d+)\b")
_BOUNDS_PATTERN = re.compile(r"^\[(\d+),(\d+)\]\[(\d+),(\d+)\]$")
_AERR_CLOSE_ID = "android:id/aerr_close"
_AERR_WAIT_ID = "android:id/aerr_wait"
_TERMINAL_STATES = {"LANDING", "PERMISSION_DIALOG", "TERMS", "KNOWN_ERROR"}


@not_keyword
def _adb(serial, *args, timeout=10, check=True):
    result = subprocess.run(
        [resolve_adb_executable(), "-s", serial, *args], capture_output=True, text=True, timeout=timeout
    )
    if check and result.returncode:
        raise RuntimeError((result.stderr or result.stdout).strip() or f"adb failed: {args}")
    return (result.stdout or "").replace("\r", "")


@not_keyword
def _sanitized_source(source):
    return _TEXT_ATTRIBUTE.sub(lambda match: f'{match.group(1)}="[REDACTED]"', source)


@not_keyword
def _classify_startup_error_marker(source):
    exact = _EXACT_ERROR_CODE_PATTERN.search(source)
    if exact:
        return exact.group(0)
    if "Something went wrong on our side" in source or "Please try again later" in source:
        return "GENERIC_SERVICE_ERROR"
    if "Close app" in source:
        return "GENERIC_CLOSE_APP_ERROR"
    if "The app requires newer operating system" in source:
        return "UNSUPPORTED_OS"
    return ""


@not_keyword
def _foreground(serial):
    text = _adb(serial, "shell", "dumpsys", "window", "displays", check=False)
    match = re.search(r"mCurrentFocus=Window\{.*? u0 ([^ }]+)", text)
    return match.group(1) if match else ""


@not_keyword
def _dump_source(serial):
    remote_xml = "/sdcard/etb_startup.xml"
    try:
        _adb(serial, "shell", "rm", "-f", remote_xml, timeout=5, check=True)
    except (RuntimeError, subprocess.TimeoutExpired) as exc:
        raise AssertionError("ADB_UI_DUMP_RESET_FAILED") from exc

    try:
        _adb(
            serial,
            "shell",
            "uiautomator",
            "dump",
            "--compressed",
            remote_xml,
            timeout=12,
            check=True,
        )
    except subprocess.TimeoutExpired as exc:
        raise AssertionError("ADB_UI_DUMP_TIMEOUT") from exc
    except RuntimeError as exc:
        raise AssertionError("ADB_UI_DUMP_FAILED") from exc

    try:
        source = _adb(
            serial,
            "shell",
            "cat",
            remote_xml,
            timeout=12,
            check=True,
        )
    except subprocess.TimeoutExpired as exc:
        raise AssertionError("ADB_UI_DUMP_READ_TIMEOUT") from exc
    except RuntimeError as exc:
        raise AssertionError("ADB_UI_DUMP_READ_FAILED") from exc

    if not source.strip():
        raise AssertionError("ADB_UI_DUMP_EMPTY")
    return source


@not_keyword
def _has_exact_resource_id(source, resource_id):
    return f'resource-id="{resource_id}"' in source


@not_keyword
def _stale_aerr_close_center(source):
    if not (
        _has_exact_resource_id(source, _AERR_CLOSE_ID)
        and _has_exact_resource_id(source, _AERR_WAIT_ID)
    ):
        return None

    try:
        root = ET.fromstring(source)
    except ET.ParseError as exc:
        raise AssertionError("ADB_STALE_AERR_CLOSE_BOUNDS_NOT_FOUND") from exc

    for node in root.iter():
        if node.attrib.get("resource-id") != _AERR_CLOSE_ID:
            continue
        match = _BOUNDS_PATTERN.fullmatch(node.attrib.get("bounds", ""))
        if not match:
            break
        x1, y1, x2, y2 = (int(value) for value in match.groups())
        return ((x1 + x2) // 2, (y1 + y2) // 2)
    raise AssertionError("ADB_STALE_AERR_CLOSE_BOUNDS_NOT_FOUND")


_TRANSIENT_POST_RESET_DUMP_ERRORS = {
    "ADB_UI_DUMP_RESET_FAILED",
    "ADB_UI_DUMP_TIMEOUT",
    "ADB_UI_DUMP_FAILED",
    "ADB_UI_DUMP_READ_TIMEOUT",
    "ADB_UI_DUMP_READ_FAILED",
    "ADB_UI_DUMP_EMPTY",
}


@not_keyword
def _recover_uiautomator_dump_after_transient(serial):
    if not str(serial).startswith("emulator-"):
        return
    _adb(serial, "shell", "input", "keyevent", "KEYCODE_WAKEUP", timeout=5, check=False)
    _adb(serial, "shell", "wm", "dismiss-keyguard", timeout=5, check=False)


@not_keyword
def _dump_source_after_reset(serial, max_attempts=3, retry_delay=0.5):
    for attempt in range(max_attempts):
        try:
            return _dump_source(serial)
        except AssertionError as exc:
            if (
                str(exc) not in _TRANSIENT_POST_RESET_DUMP_ERRORS
                or attempt + 1 >= max_attempts
            ):
                raise
            _recover_uiautomator_dump_after_transient(serial)
            time.sleep(retry_delay)
    raise AssertionError("ADB_UI_DUMP_FAILED")


@not_keyword
def _dismiss_stale_emulator_aerr_after_reset(serial):
    source = _dump_source_after_reset(serial)
    center = _stale_aerr_close_center(source)
    if center is None:
        return

    _adb(serial, "shell", "input", "tap", str(center[0]), str(center[1]))
    time.sleep(0.5)
    source_after = _dump_source_after_reset(serial)
    if _has_exact_resource_id(source_after, _AERR_CLOSE_ID) or _has_exact_resource_id(
        source_after, _AERR_WAIT_ID
    ):
        raise AssertionError("ADB_STALE_AERR_DISMISS_FAILED")


@not_keyword
def _capture_final_screenshot(serial, destination):
    with destination.open("wb") as handle:
        subprocess.run(
            [resolve_adb_executable(), "-s", serial, "exec-out", "screencap", "-p"],
            stdout=handle,
            stderr=subprocess.DEVNULL,
            check=False,
            timeout=10,
        )


@not_keyword
def _classify_startup_state(source, foreground):
    if "screenLanding_skipButton" in source or "screenLanding_buttonReady" in source:
        return "LANDING"
    if "permissioncontroller" in source.lower() or "GrantPermissionsActivity" in foreground:
        return "PERMISSION_DIALOG"
    if "Terms and Conditions" in source or "termsAndConditions" in source:
        return "TERMS"
    if _classify_startup_error_marker(source):
        return "KNOWN_ERROR"
    if "com.bangkokbank.blue" in foreground:
        return "STARTUP_TRANSITION"
    if not foreground or "launcher" in foreground.lower():
        return "APP_INITIALIZING"
    return "UNKNOWN"


@keyword("Get App Pid")
def get_app_pid(serial, package):
    return _adb(serial, "shell", "pidof", package, check=False).strip()



@keyword("Get Android Screenshot Hash")
def get_android_screenshot_hash(serial):
    """Return a sanitized visual-state hash using the canonical ADB executable."""
    try:
        result = subprocess.run(
            [resolve_adb_executable(), "-s", serial, "exec-out", "screencap", "-p"],
            capture_output=True,
            timeout=10,
            check=False,
        )
    except subprocess.TimeoutExpired as exc:
        raise AssertionError("ADB_SCREENSHOT_HASH_TIMEOUT") from exc
    except OSError as exc:
        raise AssertionError("ADB_SCREENSHOT_HASH_FAILED") from exc

    if result.returncode != 0 or not result.stdout:
        raise AssertionError("ADB_SCREENSHOT_HASH_FAILED")
    return hashlib.sha256(result.stdout).hexdigest()[:16]


@not_keyword
def _terms_content_ready_from_source(source):
    content_present = (
        "I have read and understood" in source
        or "ข้าพเจ้าได้อ่านและทำความเข้าใจกับข้อตกลงการใช้บริการ" in source
    )
    accept_present = any(
        marker in source
        for marker in (
            'text="Accept"',
            'content-desc="Accept"',
            'text="ยอมรับ"',
            'content-desc="ยอมรับ"',
        )
    )
    return content_present and accept_present


@not_keyword
def _terms_content_loaded_from_source(source):
    if not isinstance(source, str) or not source.strip():
        return False
    try:
        root = ET.fromstring(source)
    except ET.ParseError as exc:
        raise AssertionError("TERMS_SOURCE_INVALID") from exc

    for webview in root.iter():
        webview_class = webview.attrib.get("class", webview.tag)
        if webview_class != "android.webkit.WebView":
            continue
        for node in webview.iter():
            node_class = node.attrib.get("class", node.tag)
            if node_class == "android.widget.TextView" and (
                node.attrib.get("text", "").strip()
                or node.attrib.get("content-desc", "").strip()
            ):
                return True
    return False


@keyword("Terms Content Loaded From Source")
def terms_content_loaded_from_source(source):
    """Return whether the Terms WebView exposes any hydrated agreement text."""
    return _terms_content_loaded_from_source(source)


@keyword("Terms Content Ready Via Adb")
def terms_content_ready_via_adb(serial):
    """Return True only when the ADB hierarchy proves hydrated Terms content and Accept."""
    return _terms_content_ready_from_source(_dump_source(serial))


@keyword("Consent Acknowledgement Present Via Adb")
def consent_acknowledgement_present_via_adb(serial):
    """Read the consent acknowledgement marker from the canonical ADB hierarchy."""
    source = _dump_source(serial)
    return (
        "I have read and understood" in source
        or "ข้าพเจ้าได้อ่านและทำความเข้าใจกับข้อตกลงการใช้บริการ" in source
    )


@keyword("Get Foreground Component")
def get_foreground_component(serial):
    return _foreground(serial)


@keyword("Force Stop Android Application")
def force_stop_android_application(serial, package):
    _adb(serial, "shell", "am", "force-stop", package)
    return "PASS"


@keyword("Reset Android Application Before Session")
def reset_android_application_before_session(serial, package):
    _adb(serial, "shell", "am", "force-stop", package)
    clear_result = _adb(serial, "shell", "pm", "clear", package, timeout=20)
    if "success" not in clear_result.lower():
        raise AssertionError("ADB_PM_CLEAR_FAILED")
    if str(serial).startswith("emulator-"):
        _dismiss_stale_emulator_aerr_after_reset(serial)
    return "PASS"


@keyword("Start And Observe Real Device")
def start_and_observe_real_device(
    serial,
    package,
    activity,
    output_dir,
    timeout=90,
    interval=1,
):
    """Start the target with ADB and return sanitized startup metadata.

    On emulators only, one bounded interim force-stop/relaunch is allowed when
    startup remains in STARTUP_TRANSITION for 30 seconds. The recovery does not
    clear application data and is never applied to physical REAL devices.
    """
    evidence_dir = Path(
        resolve_private_evidence_dir(output_dir, case_id=_current_case_id())
    ) / "device"
    evidence_dir.mkdir(parents=True, exist_ok=True)

    timeline = []
    terminal_state = "UNKNOWN"
    error_marker = ""
    observation_error = ""
    source = ""
    foreground = ""
    startup_relaunch_count = 0
    transition_relaunch_after_seconds = 30.0

    def launch_target():
        start = _adb(serial, "shell", "am", "start", "-n", f"{package}/{activity}")
        if "Error" in start:
            raise AssertionError("ADB_APP_START_FAILED")

    def observe_window(window_timeout, break_stuck_transition=False):
        nonlocal source, foreground, error_marker, observation_error
        window_started = time.monotonic()
        observed_terminal_state = "UNKNOWN"

        while time.monotonic() - window_started <= float(window_timeout):
            elapsed = round(time.monotonic() - window_started, 3)
            try:
                source = _dump_source(serial)
                observation_error = ""
            except AssertionError as exc:
                candidate_error = str(exc)
                if not candidate_error.startswith("ADB_UI_DUMP_"):
                    raise
                source = ""
                error_marker = ""
                observation_error = candidate_error
                foreground = _foreground(serial)
                state = "SOURCE_UNAVAILABLE"
                if (
                    not timeline
                    or timeline[-1]["state"] != state
                    or timeline[-1].get("observation_error") != observation_error
                ):
                    timeline.append(
                        {
                            "state": state,
                            "elapsed_seconds": elapsed,
                            "foreground_target": foreground.startswith(package + "/"),
                            "observation_error": observation_error,
                            "startup_attempt": startup_relaunch_count,
                        }
                    )
                observed_terminal_state = state
                time.sleep(float(interval))
                continue

            foreground = _foreground(serial)
            error_marker = _classify_startup_error_marker(source)
            state = _classify_startup_state(source, foreground)

            if not timeline or timeline[-1]["state"] != state:
                event = {
                    "state": state,
                    "elapsed_seconds": elapsed,
                    "foreground_target": foreground.startswith(package + "/"),
                    "startup_attempt": startup_relaunch_count,
                }
                if error_marker:
                    event["startup_error_marker"] = error_marker
                timeline.append(event)

            observed_terminal_state = state
            if state in _TERMINAL_STATES:
                break
            if (
                break_stuck_transition
                and state == "STARTUP_TRANSITION"
                and elapsed >= transition_relaunch_after_seconds
            ):
                break
            time.sleep(float(interval))

        return observed_terminal_state

    launch_target()
    terminal_state = observe_window(
        timeout,
        break_stuck_transition=str(serial).startswith("emulator-"),
    )

    if str(serial).startswith("emulator-") and terminal_state == "STARTUP_TRANSITION":
        _adb(serial, "shell", "am", "force-stop", package)
        time.sleep(2.0)
        startup_relaunch_count = 1
        timeline.append(
            {
                "state": "INTERIM_FORCE_STOP_RELAUNCH",
                "elapsed_seconds": 0.0,
                "foreground_target": False,
                "startup_attempt": startup_relaunch_count,
            }
        )
        launch_target()
        terminal_state = observe_window(timeout, break_stuck_transition=False)

    _capture_final_screenshot(serial, evidence_dir / "real_startup_last.png")
    (evidence_dir / "real_startup_landing.xml").write_text(
        _sanitized_source(source), encoding="utf-8"
    )

    app_pid_before_attach = get_app_pid(serial, package)
    result = {
        "artifact_classification": "PRIVATE_LOCAL",
        "timestamp_utc": datetime.now(timezone.utc).isoformat(),
        "execution_target": "ADB_STARTUP_OBSERVER",
        "launch_result": "PASS",
        "terminal_state": terminal_state,
        "startup_error_marker": error_marker,
        "app_pid_before_attach": app_pid_before_attach,
        "timeout_seconds": float(timeout),
        "poll_interval_seconds": float(interval),
        "startup_relaunch_count": startup_relaunch_count,
        "transition_relaunch_after_seconds": transition_relaunch_after_seconds,
        "timeline": timeline,
    }
    (evidence_dir / "real_startup_timeline.json").write_text(
        json.dumps(result, indent=2) + "\n", encoding="utf-8"
    )
    (evidence_dir / "real_startup_summary.json").write_text(
        json.dumps(result, indent=2) + "\n", encoding="utf-8"
    )

    if terminal_state not in _TERMINAL_STATES:
        observation_suffix = (
            f" observation_error={observation_error}" if observation_error else ""
        )
        raise AssertionError(
            f"ADB_STARTUP_TERMINAL_STATE={terminal_state} marker={error_marker or 'NONE'}{observation_suffix}"
        )
    if terminal_state == "KNOWN_ERROR":
        raise AssertionError(
            f"ADB_STARTUP_TERMINAL_STATE=KNOWN_ERROR marker={error_marker or 'NONE'}"
        )
    return result


@not_keyword
def _current_case_id():
    try:
        test_name = BuiltIn().get_variable_value("${TEST NAME}", "")
    except Exception:
        return None
    match = re.match(r"^(TC-ETB-\d{3})(?:\s|$)", str(test_name))
    return match.group(1) if match else None
