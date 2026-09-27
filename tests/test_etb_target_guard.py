"""F08 offline checks: actual runner/identity guard, closed device/Robot mocks.

Never invoke the real runner entry point. Reuse the T01 synthetic fixture and
its process/network-denying Python bridge. No approved profiles are loaded.
"""
from __future__ import annotations

import contextlib
import hashlib
import io
import json
import os
from pathlib import Path
import shlex
import subprocess
import sys
import tempfile
import types
import unittest
from unittest.mock import patch

sys.dont_write_bytecode = True
ROOT = Path(__file__).resolve().parents[1]
BASE = types.ModuleType("profile_contract_fixture")
BASE.__file__ = str(ROOT / "tests/test_etb_profile_contract.py")
exec(compile(Path(BASE.__file__).read_text(), BASE.__file__, "exec"), BASE.__dict__)

# The tested guard source is read as code only, with no __main__ invocation.
# Every ADB operation is replaced by this finite read-only response table.
_GUARD_BRIDGE = r'''
import subprocess

def fake_adb(serial, *args, **kwargs):
    record("identity_read", serial=serial, args=list(args))
    if os.environ.get("GUARD_IO_ERROR") == "1":
        raise subprocess.TimeoutExpired("mock-adb", 10)
    if args == ("get-state",):
        return os.environ.get("GUARD_STATE", "device")
    if args[:2] == ("shell", "getprop"):
        properties = {
            "ro.kernel.qemu": os.environ.get("GUARD_QEMU", "1"),
            "sys.boot_completed": os.environ.get("GUARD_BOOT", "1"),
            "ro.boot.qemu.avd_name": os.environ.get("GUARD_AVD", "local_android_36"),
            "ro.product.manufacturer": os.environ.get("GUARD_MAKER", "HUAWEI"),
            "ro.product.model": os.environ.get("GUARD_MODEL", "MGA-LX3"),
        }
        if args[2] not in properties:
            raise AssertionError("UNREVIEWED_PROPERTY")
        return properties[args[2]]
    if args[:3] == ("shell", "pm", "path"):
        return "" if os.environ.get("GUARD_NO_PACKAGE") == "1" else "package:/synthetic/base.apk\n"
    if args[:3] == ("shell", "dumpsys", "package"):
        environment = os.environ.get("ETB_ENVIRONMENT", "DEV").upper()
        release = os.environ.get("ETB_PRODUCT_RELEASE", "POST_MMP_1")
        default_version = {
            ("SIT", "POST_MMP_1"): "versionName=1.12.11-16-Unshield versionCode=16",
            ("SIT", "MMP_LOT2_V2"): "versionName=1.12.11-16-Unshield versionCode=16",
            ("DEV", "POST_MMP_1"): "versionName=1.14.0-debug-network-post-mmp-1-alpha-24-191-Unshield versionCode=191",
            ("DEV", "MMP_LOT2_V2"): "versionName=1.13.9-145-Unshield-VPN-release-opo-fixed-tandc-not-display versionCode=145",
        }.get((environment, release), "versionName=synthetic versionCode=1")
        return os.environ.get("GUARD_VERSION", default_version)
    if args[:4] == ("shell", "cmd", "package", "resolve-activity"):
        return args[-1] + "/" + os.environ.get("GUARD_ACTIVITY", "com.bangkokbank.blue.MainActivity")
    raise AssertionError("UNREVIEWED_ADB_OR_MUTATION")

libraries_package = types.ModuleType("libraries")
libraries_package.__path__ = [str(Path(__file__).resolve().parent / "libraries")]
android_adb_module = types.ModuleType("libraries.android_adb")
android_adb_module.resolve_adb_executable = lambda: "/synthetic/adb"
sys.modules["libraries"] = libraries_package
sys.modules["libraries.android_adb"] = android_adb_module

tools_package = types.ModuleType("tools")
tools_package.__path__ = []
guard_module = types.ModuleType("tools.real_device_preflight")
guard_module.__file__ = os.environ["GUARD_SOURCE"]
exec(compile(Path(guard_module.__file__).read_text(), guard_module.__file__, "exec"), guard_module.__dict__)
guard_module.adb = fake_adb
sys.modules["tools"] = tools_package
sys.modules["tools.real_device_preflight"] = guard_module
'''


class RunnerTargetGuardTests(BASE.RunnerProfileContractTests):
    """The inherited T01 assertions are also run against the real guard body."""

    def setUp(self):
        bridge = BASE._BRIDGE.replace("args = sys.argv[1:]", _GUARD_BRIDGE + "\nargs = sys.argv[1:]")
        bridge = bridge.replace(
            'variables=variables, names=[c["name"] for c in cases])',
            'variables=variables, names=[c["name"] for c in cases], '
            'child_env={k: os.environ.get(k) for k in '
            '("ETB_ENVIRONMENT", "ANDROID_EXECUTION_TARGET", "DEVICE_UDID", "APP_PACKAGE", "APP_ACTIVITY")})',
        )
        bridge = bridge.replace(
            'else:\n    raise RuntimeError("UNEXPECTED_PYTHON_BOUNDARY")',
            'elif args and args[0].endswith("tools/appium_server.py") and args[1:] == ["--ensure"]:\n'
            '    record("appium_preflight")\n'
            '    print("APPIUM_RUNTIME_READY=YES driver=uiautomator2 sdk=READY receipt=PASS")\n'
            'elif args and args[0].endswith("must-not-be-called.py"):\n'
            '    record("physical_readiness")\n'
            '    sys.exit(3 if os.environ.get("GUARD_READINESS_FAIL") == "1" else 0)\n'
            'else:\n    raise RuntimeError("UNEXPECTED_PYTHON_BOUNDARY")',
        )
        with patch.object(BASE, "_BRIDGE", bridge):
            super().setUp()
        self.env["GUARD_SOURCE"] = str(ROOT / "tools/real_device_preflight.py")
        self.env["DEVICE_UDID"] = "emulator-5554"

    def run_fixture(self, args=None, env=None):
        supplied = dict(env or {})
        environment = supplied.get("ETB_ENVIRONMENT", "DEV").upper()
        serial, avd = {
            "DEV": ("emulator-5554", "local_android_36"),
            "SIT": ("emulator-5556", "Pixel_8"),
            "DEV_MOCK": ("emulator-5558", "Pixel_10"),
        }.get(environment, ("emulator-5554", "local_android_36"))
        supplied.setdefault("DEVICE_UDID", serial)
        supplied.setdefault("GUARD_AVD", avd)
        return super().run_fixture(args, supplied)

    def test_explicit_runtime_target_survives_local_env_defaults(self):
        config = ROOT / "tools/runner/etb_configuration.sh"
        with tempfile.TemporaryDirectory() as temporary:
            temp_root = Path(temporary)
            env_dir = temp_root / "local/env"
            env_dir.mkdir(parents=True)
            (env_dir / "etb.env").write_text(
                "ETB_ENVIRONMENT=DEV\n"
                "ANDROID_EXECUTION_TARGET=REAL\n"
                "DEVICE_UDID=synthetic-physical-device\n",
                encoding="utf-8",
            )
            script = (
                "set -euo pipefail\n"
                f"ROOT={shlex.quote(str(temp_root))}\n"
                "dry_run=false\n"
                f"source {shlex.quote(str(config))}\n"
                "export ETB_ENVIRONMENT=DEV\n"
                "export ANDROID_EXECUTION_TARGET=DIAGNOSTIC_CONTROL\n"
                "export DEVICE_UDID=emulator-5554\n"
                "load_etb_runtime_configuration\n"
                "printf '%s|%s|%s\\n' \"$ETB_ENVIRONMENT\" \"$ANDROID_EXECUTION_TARGET\" \"$DEVICE_UDID\"\n"
            )
            result = subprocess.run(
                ["/bin/bash", "--noprofile", "--norc", "-c", script],
                capture_output=True,
                text=True,
                env={"PATH": "/usr/bin:/bin"},
                check=False,
            )
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertEqual(result.stdout.strip(), "DEV|DIAGNOSTIC_CONTROL|emulator-5554")

    def assert_no_mutations(self, events):
        self.assertEqual([e["op"] for e in events if e["op"] in {
            "prepare", "cleanup", "device_preflight_stub", "robot", "forbidden_command",
        }], [])

    def test_missing_serial_is_closed_for_both_targets(self):
        for target in ("REAL", "DIAGNOSTIC_CONTROL"):
            with self.subTest(target=target):
                self.trace.unlink(missing_ok=True)
                result, events = self.run_fixture(env={"ANDROID_EXECUTION_TARGET": target, "DEVICE_UDID": ""})
                self.assert_no_mutations(events)
                self.assertEqual(result.returncode, 3)

    def test_unapproved_emulator_identity_pairs_are_closed(self):
        cases = (
            {"ETB_ENVIRONMENT": "DEV", "DEVICE_UDID": "emulator-5556", "GUARD_AVD": "local_android_36"},
            {"ETB_ENVIRONMENT": "SIT", "DEVICE_UDID": "emulator-5554", "GUARD_AVD": "local_android_36"},
        )
        for overrides in cases:
            with self.subTest(overrides=overrides):
                self.trace.unlink(missing_ok=True)
                result, events = self.run_fixture(env=overrides)
                self.assert_no_mutations(events)
                self.assertEqual(result.returncode, 3)
                self.assertNotIn("probe", [e["op"] for e in events])
                self.assertNotIn("external", [e["op"] for e in events])

    def test_dev_pixel10_playstore_is_approved_diagnostic_target(self):
        result, events = self.run_fixture(env={
            "ETB_ENVIRONMENT": "DEV",
            "ANDROID_EXECUTION_TARGET": "DIAGNOSTIC_CONTROL",
            "DEVICE_UDID": "emulator-5556",
            "GUARD_AVD": "Pixel_10_PlayStore",
        })
        self.assert_success(result)
        runtime = [event for event in events if event["op"] == "robot"]
        self.assertEqual(len(runtime), 1)
        self.assertEqual(runtime[0]["child_env"]["DEVICE_UDID"], "emulator-5556")

    def test_dev_mmp_build_145_is_release_bound_and_post_mmp_191_is_rejected_for_mmp(self):
        result, events = self.run_fixture(env={
            "ETB_ENVIRONMENT": "DEV",
            "ETB_PRODUCT_RELEASE": "MMP_LOT2_V2",
            "ANDROID_EXECUTION_TARGET": "DIAGNOSTIC_CONTROL",
            "DEVICE_UDID": "emulator-5556",
            "GUARD_AVD": "Pixel_10_PlayStore",
        })
        self.assert_success(result)
        runtime = [event for event in events if event["op"] == "robot"]
        self.assertEqual(len(runtime), 1)
        self.assertIn("ETB_PRODUCT_RELEASE:MMP_LOT2_V2", runtime[0]["variables"])

        self.trace.unlink(missing_ok=True)
        result, events = self.run_fixture(env={
            "ETB_ENVIRONMENT": "DEV",
            "ETB_PRODUCT_RELEASE": "MMP_LOT2_V2",
            "ANDROID_EXECUTION_TARGET": "DIAGNOSTIC_CONTROL",
            "DEVICE_UDID": "emulator-5556",
            "GUARD_AVD": "Pixel_10_PlayStore",
            "GUARD_VERSION": "versionName=1.14.0-debug-network-post-mmp-1-alpha-24-191-Unshield versionCode=191",
        })
        self.assertEqual(result.returncode, 3)
        self.assertNotIn("robot", [event["op"] for event in events])

    def test_bad_observed_identity_or_package_stops_before_preparation(self):
        for override in (
            {"GUARD_AVD": "WRONG_AVD"}, {"GUARD_AVD": ""},
            {"GUARD_STATE": "offline"}, {"GUARD_STATE": "unauthorized"},
            {"GUARD_QEMU": "0"}, {"GUARD_BOOT": "0"},
            {"GUARD_ACTIVITY": "wrong.Activity"}, {"GUARD_VERSION": ""},
            {"GUARD_NO_PACKAGE": "1"}, {"GUARD_IO_ERROR": "1"},
        ):
            with self.subTest(override=override):
                self.trace.unlink(missing_ok=True)
                result, events = self.run_fixture(env=override)
                self.assert_no_mutations(events)
                self.assertEqual(result.returncode, 3)

    def test_real_target_cannot_use_emulator(self):
        result, events = self.run_fixture(env={"ANDROID_EXECUTION_TARGET": "REAL"})
        self.assert_no_mutations(events)
        self.assertEqual(result.returncode, 3)

    def test_oppo_cph2781_is_approved_real_target(self):
        result, events = self.run_fixture(env={
            "ANDROID_EXECUTION_TARGET": "REAL",
            "DEVICE_UDID": "SYNTHETIC_OPPO_DEVICE",
            "GUARD_QEMU": "0",
            "GUARD_MAKER": "OPPO",
            "GUARD_MODEL": "CPH2781",
        })
        self.assert_success(result)
        runtime = [event for event in events if event["op"] == "robot"]
        self.assertEqual(len(runtime), 1)
        self.assertEqual(runtime[0]["child_env"]["DEVICE_UDID"], "SYNTHETIC_OPPO_DEVICE")

    def test_physical_readiness_failure_is_before_package_and_cis(self):
        result, events = self.run_fixture(env={
            "ANDROID_EXECUTION_TARGET": "REAL", "DEVICE_UDID": "SYNTHETIC_REAL_DEVICE",
            "GUARD_QEMU": "0", "GUARD_READINESS_FAIL": "1",
        })
        self.assert_no_mutations(events)
        self.assertEqual(result.returncode, 3)
        self.assertIn("physical_readiness", [e["op"] for e in events])
        self.assertNotIn("probe", [e["op"] for e in events])

    def test_wrong_physical_model_is_closed(self):
        result, events = self.run_fixture(env={
            "ANDROID_EXECUTION_TARGET": "REAL", "DEVICE_UDID": "SYNTHETIC_REAL_DEVICE",
            "GUARD_QEMU": "0", "GUARD_MODEL": "WRONG_MODEL",
        })
        self.assert_no_mutations(events)
        self.assertEqual(result.returncode, 3)

    def test_normalized_config_is_exported_and_forwarded_once(self):
        for environment, target in (("dev", "emulator"), ("sit", "DIAGNOSTIC_CONTROL"), ("DEV", "real")):
            with self.subTest(environment=environment, target=target):
                self.trace.unlink(missing_ok=True)
                overrides = {"ETB_ENVIRONMENT": environment, "ANDROID_EXECUTION_TARGET": target}
                if target == "real":
                    overrides.update(DEVICE_UDID="SYNTHETIC_REAL_DEVICE", GUARD_QEMU="0")
                result, events = self.run_fixture(env=overrides)
                self.assert_success(result)
                expected = {
                    "ETB_ENVIRONMENT": environment.upper(),
                    "ANDROID_EXECUTION_TARGET": "REAL" if target == "real" else "DIAGNOSTIC_CONTROL",
                    "DEVICE_UDID": "SYNTHETIC_REAL_DEVICE" if target == "real" else ("emulator-5556" if environment == "sit" else "emulator-5554"),
                    "APP_PACKAGE": "com.bangkokbank.blue.sit" if environment == "sit" else "com.bangkokbank.blue.dev",
                    "APP_ACTIVITY": "com.bangkokbank.blue.MainActivity",
                }
                runtime = [e for e in events if e["op"] == "robot"]
                self.assertEqual(len(runtime), 1)
                self.assertEqual(runtime[0]["child_env"], expected)
                for key, value in expected.items():
                    self.assertEqual([v for v in runtime[0]["variables"] if v.startswith(key + ":")], [key + ":" + value])
                operations = [e["op"] for e in events]
                self.assertLess(operations.index("identity_read"), operations.index("device_preflight_stub"))

    def test_adb_target_never_falls_back_to_default(self):
        source = (ROOT / "tools/runner/android_environment.sh").read_text()
        function = source[source.index("adb_target() {\n"):source.index("\npackage_installed() {\n")]
        script = "set -euo pipefail\n" + function + '\nadb() { printf called; }\nadb_target shell pm clear com.example.synthetic\n'
        result = subprocess.run(["/bin/bash", "--noprofile", "--norc", "-c", script],
                                env={"PATH": "/usr/bin:/bin", "DEVICE_UDID": ""},
                                capture_output=True, text=True, timeout=5)
        self.assertNotIn("called", result.stdout)
        self.assertEqual(result.returncode, 3)

    def test_adb_target_uses_runtime_resolved_absolute_adb(self):
        source = (ROOT / "tools/runner/android_environment.sh").read_text()
        function = source[source.index("adb_target() {\n"):source.index("\npackage_installed() {\n")]
        with tempfile.TemporaryDirectory(prefix="bbl-adb-target-") as temporary:
            root = Path(temporary)
            fake_adb = root / "adb"
            fake_adb.write_text("#!/bin/sh\nprintf '%s\\n' \"$*\"\n", encoding="utf-8")
            fake_adb.chmod(0o755)
            resolver = root / "resolver"
            resolver.write_text(
                "#!/bin/sh\nprintf '%s\\n' \"$FAKE_ADB\"\n",
                encoding="utf-8",
            )
            resolver.chmod(0o755)
            script = (
                "set -euo pipefail\n"
                + function
                + "\nadb_target get-state\n"
            )
            result = subprocess.run(
                ["/bin/bash", "--noprofile", "--norc", "-c", script],
                env={
                    "PATH": "/usr/bin:/bin",
                    "DEVICE_UDID": "emulator-5554",
                    "PYTHON_BIN": str(resolver),
                    "ROOT": str(root),
                    "FAKE_ADB": str(fake_adb),
                },
                capture_output=True,
                text=True,
                timeout=5,
            )
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertEqual(result.stdout.strip(), "-s emulator-5554 get-state")


    def test_etb_dob_strategy_defaults_to_stable_v1(self):
        result, events = self.run_fixture()
        self.assert_success(result)
        runtime = [event for event in events if event["op"] == "robot"]
        self.assertEqual(len(runtime), 1)
        self.assertIn("ETB_DOB_STRATEGY:STABLE_V1", runtime[0]["variables"])

    def test_etb_dob_strategy_allows_legacy_override_and_rejects_unknown(self):
        result, events = self.run_fixture(env={"ETB_DOB_STRATEGY": "LEGACY"})
        self.assert_success(result)
        runtime = [event for event in events if event["op"] == "robot"]
        self.assertEqual(len(runtime), 1)
        self.assertIn("ETB_DOB_STRATEGY:LEGACY", runtime[0]["variables"])

        self.trace.unlink(missing_ok=True)
        result, events = self.run_fixture(env={"ETB_DOB_STRATEGY": "WRONG"})
        self.assertEqual(result.returncode, 2)
        self.assertNotIn("robot", [event["op"] for event in events])


class SharedAdbResolverTests(unittest.TestCase):
    def test_robot_adb_library_uses_resolved_executable(self):
        import libraries.adb_device as module

        completed = subprocess.CompletedProcess([], 0, stdout="device\n", stderr="")
        with patch.object(module, "resolve_adb_executable", return_value="/synthetic/adb"), \
             patch.object(module.subprocess, "run", return_value=completed) as run_mock:
            result = module._adb("emulator-5554", "get-state")
        self.assertEqual(result, "device\n")
        self.assertEqual(
            run_mock.call_args.args[0],
            ["/synthetic/adb", "-s", "emulator-5554", "get-state"],
        )

    def test_startup_diagnostic_uses_resolved_executable(self):
        import libraries.startup_state as module

        dump = subprocess.CompletedProcess([], 0, stdout="", stderr="")
        source = subprocess.CompletedProcess(
            [], 0, stdout='<node resource-id="screenLanding_skipButton" />', stderr=""
        )
        with patch.dict(
            os.environ,
            {
                "ANDROID_EXECUTION_TARGET": "DIAGNOSTIC_CONTROL",
                "DEVICE_UDID": "emulator-5554",
            },
            clear=False,
        ), patch.object(
            module, "resolve_adb_executable", return_value="/synthetic/adb"
        ), patch.object(
            module.subprocess, "run", side_effect=[dump, source]
        ) as run_mock:
            state = module._diagnostic_adb_state()
        self.assertEqual(state, "LANDING")
        self.assertEqual(run_mock.call_count, 2)
        for call in run_mock.call_args_list:
            self.assertEqual(call.args[0][0], "/synthetic/adb")


class ReadinessReadOnlyTests(unittest.TestCase):
    def test_adb_get_state_retries_transient_device_not_found(self):
        module = types.ModuleType("preflight_adb_retry")
        exec(compile((ROOT / "tools/real_device_preflight.py").read_text(), "<preflight>", "exec"), module.__dict__)
        warmup = subprocess.CompletedProcess([], 0, stdout="List of devices attached\n", stderr="")
        missing = subprocess.CompletedProcess([], 1, stdout="", stderr="error: device 'emulator-5554' not found")
        ready = subprocess.CompletedProcess([], 0, stdout="device\n", stderr="")
        with patch.object(module, "_resolve_adb_executable", return_value="/synthetic/adb"), \
             patch.object(module.subprocess, "run", side_effect=[warmup, missing, ready]) as run_mock, \
             patch.object(module.time, "sleep") as sleep_mock:
            result = module.adb("emulator-5554", "get-state")
        self.assertEqual(result, "device\n")
        self.assertEqual(run_mock.call_count, 3)
        self.assertEqual(run_mock.call_args_list[0].args[0], ["/synthetic/adb", "devices"])
        sleep_mock.assert_called_once_with(0.5)

    def test_adb_get_state_does_not_retry_offline(self):
        module = types.ModuleType("preflight_adb_offline")
        exec(compile((ROOT / "tools/real_device_preflight.py").read_text(), "<preflight>", "exec"), module.__dict__)
        warmup = subprocess.CompletedProcess([], 0, stdout="List of devices attached\n", stderr="")
        offline = subprocess.CompletedProcess([], 1, stdout="", stderr="error: device offline")
        with patch.object(module, "_resolve_adb_executable", return_value="/synthetic/adb"), \
             patch.object(module.subprocess, "run", side_effect=[warmup, offline]) as run_mock, \
             patch.object(module.time, "sleep") as sleep_mock:
            with self.assertRaisesRegex(RuntimeError, "^ADB_DEVICE_OFFLINE$"):
                module.adb("emulator-5554", "get-state")
        self.assertEqual(run_mock.call_count, 2)
        self.assertEqual(run_mock.call_args_list[0].args[0], ["/synthetic/adb", "devices"])
        sleep_mock.assert_not_called()

    def test_adb_get_state_falls_back_only_after_two_exact_device_list_confirmations(self):
        module = types.ModuleType("preflight_adb_confirmed_fallback")
        exec(compile((ROOT / "tools/real_device_preflight.py").read_text(), "<preflight>", "exec"), module.__dict__)
        listed = subprocess.CompletedProcess(
            [], 0, stdout="List of devices attached\nemulator-5554\tdevice\n", stderr=""
        )
        missing = subprocess.CompletedProcess([], 1, stdout="", stderr="error: device 'emulator-5554' not found")
        with patch.object(module, "_resolve_adb_executable", return_value="/synthetic/adb"), \
             patch.object(module.subprocess, "run", side_effect=[listed, missing, missing, missing, listed]) as run_mock, \
             patch.object(module.time, "sleep") as sleep_mock:
            result = module.adb("emulator-5554", "get-state")
        self.assertEqual(result, "device\n")
        self.assertEqual(run_mock.call_count, 5)
        self.assertEqual(sleep_mock.call_count, 2)

    def test_adb_get_state_never_falls_back_when_confirmation_loses_device(self):
        module = types.ModuleType("preflight_adb_unconfirmed_fallback")
        exec(compile((ROOT / "tools/real_device_preflight.py").read_text(), "<preflight>", "exec"), module.__dict__)
        listed = subprocess.CompletedProcess(
            [], 0, stdout="List of devices attached\nemulator-5554\tdevice\n", stderr=""
        )
        missing = subprocess.CompletedProcess([], 1, stdout="", stderr="error: device 'emulator-5554' not found")
        absent = subprocess.CompletedProcess([], 0, stdout="List of devices attached\n", stderr="")
        with patch.object(module, "_resolve_adb_executable", return_value="/synthetic/adb"), \
             patch.object(module.subprocess, "run", side_effect=[listed, missing, missing, missing, absent]) as run_mock, \
             patch.object(module.time, "sleep") as sleep_mock:
            with self.assertRaisesRegex(RuntimeError, "^ADB_DEVICE_NOT_FOUND$"):
                module.adb("emulator-5554", "get-state")
        self.assertEqual(run_mock.call_count, 5)
        self.assertEqual(sleep_mock.call_count, 2)

    def test_readiness_does_not_wake_device(self):
        module = types.ModuleType("preflight_under_test")
        exec(compile((ROOT / "tools/real_device_preflight.py").read_text(), "<preflight>", "exec"), module.__dict__)
        seen = []
        def adb(serial, *args, **kwargs):
            seen.append(args)
            if args == ("get-state",):
                return "device"
            if args[:3] == ("shell", "pm", "path"):
                return "package:/synthetic/base.apk"
            if args[:3] == ("shell", "settings", "get"):
                return "1"
            if args[:3] == ("shell", "dumpsys", "package"):
                return "versionName=synthetic versionCode=1"
            if args[:4] == ("shell", "cmd", "package", "resolve-activity"):
                return "com.bangkokbank.blue.dev/com.bangkokbank.blue.MainActivity"
            return ""
        def prop(serial, name):
            return {"ro.product.manufacturer": "HUAWEI", "ro.product.model": "MGA-LX3"}.get(name, "10")
        with tempfile.TemporaryDirectory() as temporary, contextlib.redirect_stdout(io.StringIO()), contextlib.redirect_stderr(io.StringIO()), patch.object(module, "adb", side_effect=adb), patch.object(module, "prop", side_effect=prop), patch.object(module, "keyguard_inactive", return_value=False), patch.object(module, "appium_ready", return_value=True), patch.object(module.subprocess, "run", return_value=subprocess.CompletedProcess([], 0, stdout="SYNTHETIC_REAL_DEVICE\tdevice\n")):
            result = module.readiness("SYNTHETIC_REAL_DEVICE", Path(temporary), "http://example.invalid", module.PACKAGE, module.ACTIVITY)
        self.assertEqual(result["checks"]["DEVICE_UNLOCKED"], "NO")
        self.assertEqual([args for args in seen if "input" in args], [])


def load_tests(loader, tests, pattern):
    suite = unittest.TestSuite()
    suite.addTests(loader.loadTestsFromTestCase(RunnerTargetGuardTests))
    suite.addTests(loader.loadTestsFromTestCase(SharedAdbResolverTests))
    suite.addTests(loader.loadTestsFromTestCase(ReadinessReadOnlyTests))
    suite.addTests(loader.loadTestsFromTestCase(BASE.ProfileConsumerContractTests))
    return suite


if __name__ == "__main__":
    for relative in ("run", "tools/runner/etb_runner.sh", "tools/runner/etb_configuration.sh", "tools/runner/etb_selection.sh", "tools/runner/etb_preflight.sh", "tools/runner/etb_execution.sh", "tools/runner/etb_runtime.py", "tools/runner/android_environment.sh", "tools/real_device_preflight.py", "tests/test_etb_profile_contract.py", "tests/test_etb_target_guard.py", "package.json"):
        path = ROOT / relative
        print("TARGET_SOURCE " + relative + " sha256=" + hashlib.sha256(path.read_bytes()).hexdigest() + " mode=" + oct(path.stat().st_mode & 0o777), flush=True)
    unittest.main(verbosity=2)
