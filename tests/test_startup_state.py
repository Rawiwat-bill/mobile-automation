"""Focused tests for fail-closed startup classification and ETB Landing/reset ownership."""

import inspect
import subprocess
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

from libraries import adb_device, startup_state
from libraries.startup_state import _classify

ROOT = Path(__file__).resolve().parents[1]


class StartupStateTests(unittest.TestCase):
    def test_wrapper_only_is_non_terminal_transition(self):
        self.assertEqual(
            _classify('resource-id="security-error-container"', "com.bangkokbank.blue.MainActivity"),
            "STARTUP_TRANSITION",
        )

    def test_wrapper_with_landing_marker_is_landing(self):
        source = 'resource-id="security-error-container" resource-id="screenLanding_skipButton"'
        self.assertEqual(_classify(source, "com.bangkokbank.blue.MainActivity"), "LANDING")

    def test_wrapper_with_exact_generic_error_is_known_error(self):
        source = 'resource-id="security-error-container" text="Something went wrong on our side"'
        self.assertEqual(_classify(source, "com.bangkokbank.blue.MainActivity"), "KNOWN_ERROR")

    def test_wrapper_with_rgi_106_is_known_error(self):
        source = 'resource-id="security-error-container" text="RGI-106"'
        self.assertEqual(_classify(source, "com.bangkokbank.blue.MainActivity"), "KNOWN_ERROR")

    def test_default_startup_timeout_is_60_seconds(self):
        parameter = inspect.signature(startup_state.wait_for_real_device_startup_state).parameters["timeout"]
        self.assertEqual(parameter.default, 60.0)

    def test_landing_after_45_seconds_is_accepted_before_default_timeout(self):
        clock = {"now": 0.0}

        def fake_monotonic():
            return clock["now"]

        def fake_sleep(seconds):
            clock["now"] += seconds

        def fake_snapshot():
            if clock["now"] >= 45.5:
                return ('resource-id="screenLanding_skipButton"', "com.bangkokbank.blue.MainActivity")
            return ('resource-id="security-error-container"', "com.bangkokbank.blue.MainActivity")

        with (
            patch.object(startup_state.time, "monotonic", side_effect=fake_monotonic),
            patch.object(startup_state.time, "sleep", side_effect=fake_sleep),
            patch.object(startup_state, "_snapshot", side_effect=fake_snapshot),
            patch.object(startup_state.BuiltIn, "log", return_value=None),
        ):
            result = startup_state.wait_for_real_device_startup_state()

        self.assertEqual(result, "LANDING")
        self.assertGreaterEqual(clock["now"], 45.5)
        self.assertLess(clock["now"], 60.0)

    def test_adb_dump_removes_previous_xml_before_capture(self):
        calls = []

        def fake_adb(serial, *args, **kwargs):
            calls.append((args, kwargs))
            if args[:2] == ("shell", "cat"):
                return "<hierarchy />"
            return ""

        with patch.object(adb_device, "_adb", side_effect=fake_adb):
            source = adb_device._dump_source("emulator-5554")

        self.assertEqual(source, "<hierarchy />")
        self.assertEqual(
            calls[0][0],
            ("shell", "rm", "-f", "/sdcard/etb_startup.xml"),
        )
        self.assertEqual(
            calls[1][0],
            (
                "shell",
                "uiautomator",
                "dump",
                "--compressed",
                "/sdcard/etb_startup.xml",
            ),
        )
        self.assertEqual(calls[2][0], ("shell", "cat", "/sdcard/etb_startup.xml"))

    def test_adb_dump_failure_never_reads_stale_xml(self):
        calls = []

        def fake_adb(serial, *args, **kwargs):
            calls.append((args, kwargs))
            if args[:3] == ("shell", "uiautomator", "dump"):
                if kwargs.get("check"):
                    raise RuntimeError("synthetic dump failure")
                return ""
            if args[:2] == ("shell", "cat"):
                return '<hierarchy resource-id="Transition_Screen_Logo_Icon" />'
            return ""

        with patch.object(adb_device, "_adb", side_effect=fake_adb):
            with self.assertRaisesRegex(AssertionError, "ADB_UI_DUMP_FAILED"):
                adb_device._dump_source("emulator-5554")

        self.assertFalse(any(args[:2] == ("shell", "cat") for args, _ in calls))

    def test_adb_dump_timeout_is_sanitized_and_never_reads_stale_xml(self):
        calls = []

        def fake_adb(serial, *args, **kwargs):
            calls.append((args, kwargs))
            if args[:3] == ("shell", "uiautomator", "dump"):
                raise subprocess.TimeoutExpired(cmd=["adb", "uiautomator", "dump"], timeout=12)
            if args[:2] == ("shell", "cat"):
                return '<hierarchy resource-id="Transition_Screen_Logo_Icon" />'
            return ""

        with patch.object(adb_device, "_adb", side_effect=fake_adb):
            with self.assertRaisesRegex(AssertionError, "ADB_UI_DUMP_TIMEOUT"):
                adb_device._dump_source("emulator-5554")

        self.assertFalse(any(args[:2] == ("shell", "cat") for args, _ in calls))

    def test_reset_dismisses_exact_stale_aerr_after_pm_clear(self):
        stale = (
            '<hierarchy>'
            '<node resource-id="android:id/aerr_close" bounds="[100,200][300,400]" />'
            '<node resource-id="android:id/aerr_wait" bounds="[310,200][510,400]" />'
            '</hierarchy>'
        )
        calls = []

        def fake_adb(serial, *args, **kwargs):
            calls.append(args)
            if args[:3] == ("shell", "pm", "clear"):
                return "Success\n"
            return ""

        with (
            patch.object(adb_device, "_adb", side_effect=fake_adb),
            patch.object(adb_device, "_dump_source", side_effect=[stale, "<hierarchy />"]),
            patch.object(adb_device.time, "sleep", return_value=None),
        ):
            result = adb_device.reset_android_application_before_session("emulator-5554", "package")

        self.assertEqual(result, "PASS")
        self.assertIn(("shell", "input", "tap", "200", "300"), calls)

    def test_reset_fails_closed_when_stale_aerr_remains_after_tap(self):
        stale = (
            '<hierarchy>'
            '<node resource-id="android:id/aerr_close" bounds="[100,200][300,400]" />'
            '<node resource-id="android:id/aerr_wait" bounds="[310,200][510,400]" />'
            '</hierarchy>'
        )

        def fake_adb(serial, *args, **kwargs):
            if args[:3] == ("shell", "pm", "clear"):
                return "Success\n"
            return ""

        with (
            patch.object(adb_device, "_adb", side_effect=fake_adb),
            patch.object(adb_device, "_dump_source", side_effect=[stale, stale]),
            patch.object(adb_device.time, "sleep", return_value=None),
        ):
            with self.assertRaisesRegex(AssertionError, "ADB_STALE_AERR_DISMISS_FAILED"):
                adb_device.reset_android_application_before_session("emulator-5554", "package")

    def test_reset_does_not_tap_incomplete_aerr_marker_set(self):
        close_only = (
            '<hierarchy>'
            '<node resource-id="android:id/aerr_close" bounds="[100,200][300,400]" />'
            '</hierarchy>'
        )
        calls = []

        def fake_adb(serial, *args, **kwargs):
            calls.append(args)
            if args[:3] == ("shell", "pm", "clear"):
                return "Success\n"
            return ""

        with (
            patch.object(adb_device, "_adb", side_effect=fake_adb),
            patch.object(adb_device, "_dump_source", return_value=close_only) as dump_source,
        ):
            result = adb_device.reset_android_application_before_session("emulator-5554", "package")

        self.assertEqual(result, "PASS")
        dump_source.assert_called_once_with("emulator-5554")
        self.assertFalse(any(call[:3] == ("shell", "input", "tap") for call in calls))

    def test_reset_fails_closed_when_stale_aerr_close_bounds_missing(self):
        malformed = (
            '<hierarchy>'
            '<node resource-id="android:id/aerr_close" bounds="" />'
            '<node resource-id="android:id/aerr_wait" bounds="[310,200][510,400]" />'
            '</hierarchy>'
        )

        def fake_adb(serial, *args, **kwargs):
            if args[:3] == ("shell", "pm", "clear"):
                return "Success\n"
            return ""

        with (
            patch.object(adb_device, "_adb", side_effect=fake_adb),
            patch.object(adb_device, "_dump_source", return_value=malformed),
        ):
            with self.assertRaisesRegex(AssertionError, "ADB_STALE_AERR_CLOSE_BOUNDS_NOT_FOUND"):
                adb_device.reset_android_application_before_session("emulator-5554", "package")

    def test_reset_non_emulator_does_not_inspect_aerr_ui(self):
        def fake_adb(serial, *args, **kwargs):
            if args[:3] == ("shell", "pm", "clear"):
                return "Success\n"
            return ""

        with (
            patch.object(adb_device, "_adb", side_effect=fake_adb),
            patch.object(adb_device, "_dump_source") as dump_source,
        ):
            result = adb_device.reset_android_application_before_session("REAL-DEVICE", "package")

        self.assertEqual(result, "PASS")
        dump_source.assert_not_called()

    def test_etb_runner_owns_reset_before_appium_session(self):
        app_keywords = (ROOT / "resources/app/app_keywords.resource").read_text(encoding="utf-8")
        adb_start = (
            "Start And Observe Real Device    ${DEVICE_UDID}    ${APP_PACKAGE}    "
            "${APP_ACTIVITY}    ${OUTPUT DIR}    timeout=90"
        )
        appium_open = "Open Application    ${APPIUM_URL}    &{capabilities}"

        self.assertIn("[Arguments]    ${no_reset}=${False}", app_keywords)
        self.assertIn("Get Environment Variable    ETB_CASE_PROFILES    ${EMPTY}", app_keywords)
        self.assertIn(
            "Set To Dictionary    ${capabilities}    appium:noReset=${True}    appium:autoLaunch=${False}    appium:dontStopAppOnReset=${True}    appium:forceAppLaunch=${False}    appium:shouldTerminateApp=${False}",
            app_keywords,
        )
        self.assertIn(adb_start, app_keywords)
        self.assertIn(appium_open, app_keywords)
        self.assertLess(app_keywords.index(adb_start), app_keywords.index(appium_open))
        self.assertIn("Set To Dictionary    ${capabilities}    noReset=${no_reset}", app_keywords)

    def test_adb_observer_does_not_reuse_source_across_transient_dump_failure(self):
        clock = {"now": 0.0}
        transition = '<hierarchy><node resource-id="Transition_Screen_Logo_Icon" /></hierarchy>'
        landing = '<hierarchy><node resource-id="screenLanding_skipButton" /></hierarchy>'
        package = "com.bangkokbank.blue.dev"
        foreground = f"{package}/com.bangkokbank.blue.MainActivity"

        def fake_monotonic():
            return clock["now"]

        def fake_sleep(seconds):
            clock["now"] += float(seconds)

        def fake_adb(serial, *args, **kwargs):
            if args[:3] == ("shell", "am", "start"):
                return "Starting: Intent"
            return ""

        with tempfile.TemporaryDirectory() as output_dir:
            with (
                patch.object(adb_device, "_adb", side_effect=fake_adb),
                patch.object(
                    adb_device,
                    "_dump_source",
                    side_effect=[
                        transition,
                        AssertionError("ADB_UI_DUMP_READ_FAILED"),
                        landing,
                    ],
                ),
                patch.object(adb_device, "_foreground", return_value=foreground),
                patch.object(adb_device, "_capture_final_screenshot", return_value=None),
                patch.object(adb_device, "get_app_pid", return_value="123"),
                patch.object(adb_device.time, "monotonic", side_effect=fake_monotonic),
                patch.object(adb_device.time, "sleep", side_effect=fake_sleep),
            ):
                result = adb_device.start_and_observe_real_device(
                    "emulator-5554",
                    package,
                    "com.bangkokbank.blue.MainActivity",
                    output_dir,
                    timeout=5,
                    interval=1,
                )

        self.assertEqual(result["terminal_state"], "LANDING")
        self.assertEqual(
            [event["state"] for event in result["timeline"]],
            ["STARTUP_TRANSITION", "SOURCE_UNAVAILABLE", "LANDING"],
        )
        self.assertEqual(
            result["timeline"][1]["observation_error"],
            "ADB_UI_DUMP_READ_FAILED",
        )

    def test_adb_observer_all_source_failures_are_explicit(self):
        clock = {"now": 0.0}
        package = "com.bangkokbank.blue.dev"

        def fake_monotonic():
            return clock["now"]

        def fake_sleep(seconds):
            clock["now"] += float(seconds)

        def fake_adb(serial, *args, **kwargs):
            if args[:3] == ("shell", "am", "start"):
                return "Starting: Intent"
            return ""

        with tempfile.TemporaryDirectory() as output_dir:
            with (
                patch.object(adb_device, "_adb", side_effect=fake_adb),
                patch.object(
                    adb_device,
                    "_dump_source",
                    side_effect=AssertionError("ADB_UI_DUMP_READ_FAILED"),
                ),
                patch.object(
                    adb_device,
                    "_foreground",
                    return_value=f"{package}/com.bangkokbank.blue.MainActivity",
                ),
                patch.object(adb_device, "_capture_final_screenshot", return_value=None),
                patch.object(adb_device, "get_app_pid", return_value="123"),
                patch.object(adb_device.time, "monotonic", side_effect=fake_monotonic),
                patch.object(adb_device.time, "sleep", side_effect=fake_sleep),
            ):
                with self.assertRaisesRegex(
                    AssertionError,
                    "ADB_STARTUP_TERMINAL_STATE=SOURCE_UNAVAILABLE.*ADB_UI_DUMP_READ_FAILED",
                ):
                    adb_device.start_and_observe_real_device(
                        "emulator-5554",
                        package,
                        "com.bangkokbank.blue.MainActivity",
                        output_dir,
                        timeout=2,
                        interval=1,
                    )

    def test_adb_observer_does_not_swallow_unrelated_assertions(self):
        package = "com.bangkokbank.blue.dev"

        def fake_adb(serial, *args, **kwargs):
            if args[:3] == ("shell", "am", "start"):
                return "Starting: Intent"
            return ""

        with tempfile.TemporaryDirectory() as output_dir:
            with (
                patch.object(adb_device, "_adb", side_effect=fake_adb),
                patch.object(
                    adb_device,
                    "_dump_source",
                    side_effect=AssertionError("UNRELATED_INVARIANT"),
                ),
                patch.object(adb_device, "_capture_final_screenshot", return_value=None),
            ):
                with self.assertRaisesRegex(AssertionError, "UNRELATED_INVARIANT"):
                    adb_device.start_and_observe_real_device(
                        "emulator-5554",
                        package,
                        "com.bangkokbank.blue.MainActivity",
                        output_dir,
                        timeout=2,
                        interval=1,
                    )

    def test_adb_observer_screencap_is_after_polling_loop(self):
        adb_device_source = (ROOT / "libraries/adb_device.py").read_text(encoding="utf-8")
        loop = "while time.monotonic() - started_at <= float(timeout):"
        final_capture = '_capture_final_screenshot(serial, evidence_dir / "real_startup_last.png")'
        self.assertIn(loop, adb_device_source)
        self.assertIn(final_capture, adb_device_source)
        self.assertLess(adb_device_source.index(loop), adb_device_source.index(final_capture))
        loop_body = adb_device_source[adb_device_source.index(loop):adb_device_source.index(final_capture)]
        self.assertNotIn("screencap", loop_body)

    def test_landing_action_reacquires_fresh_bounds_at_tap_time(self):
        landing_page = (
            ROOT / "resources/pages/common_onboarding/landing_screen_page.resource"
        ).read_text(encoding="utf-8")
        start = landing_page.index("Tap Landing Ready Button\n")
        body = landing_page[start:]
        self.assertIn("Element Should Be Visible    ${LANDING_SKIP_BUTTON}", body)
        self.assertIn("Get Element Rect    ${LANDING_SKIP_BUTTON}", body)
        self.assertIn("Get Element Rect    ${LANDING_READY_BUTTON}", body)
        self.assertIn("LANDING_ACTION_TAPPED=ADB_FRESH_BOUNDS", body)
        self.assertIn(
            "Wait Until Keyword Succeeds    10s    500ms    Landing Action Should Be Gone",
            body,
        )
        self.assertNotIn(
            "Should Not Be Empty    ${LANDING_ACTION_RECT}    LANDING_ACTION_BOUNDS_NOT_CAPTURED",
            body,
        )


if __name__ == "__main__":
    unittest.main(verbosity=2)
