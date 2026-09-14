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
        default_version = {
            "SIT": "versionName=1.12.11-16-Unshield versionCode=16",
            "DEV": "versionName=1.14.0-debug-network-post-mmp-1-alpha-12-170-Unshield versionCode=170",
        }.get(os.environ.get("ETB_ENVIRONMENT", "DEV").upper(), "versionName=synthetic versionCode=1")
        return os.environ.get("GUARD_VERSION", default_version)
    if args[:4] == ("shell", "cmd", "package", "resolve-activity"):
        return args[-1] + "/" + os.environ.get("GUARD_ACTIVITY", "com.bangkokbank.blue.MainActivity")
    raise AssertionError("UNREVIEWED_ADB_OR_MUTATION")

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

    def test_cross_environment_serial_is_closed(self):
        for environment, serial in (("DEV", "emulator-5556"), ("SIT", "emulator-5554")):
            with self.subTest(environment=environment):
                self.trace.unlink(missing_ok=True)
                result, events = self.run_fixture(env={"ETB_ENVIRONMENT": environment, "DEVICE_UDID": serial})
                self.assert_no_mutations(events)
                self.assertEqual(result.returncode, 3)
                self.assertNotIn("probe", [e["op"] for e in events])
                self.assertNotIn("external", [e["op"] for e in events])

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
        source = (ROOT / "run").read_text()
        function = source[source.index("adb_target() {\n"):source.index("\npackage_installed() {\n")]
        script = "set -euo pipefail\n" + function + '\nadb() { printf called; }\nadb_target shell pm clear com.example.synthetic\n'
        result = subprocess.run(["/bin/bash", "--noprofile", "--norc", "-c", script],
                                env={"PATH": "/usr/bin:/bin", "DEVICE_UDID": ""},
                                capture_output=True, text=True, timeout=5)
        self.assertNotIn("called", result.stdout)
        self.assertEqual(result.returncode, 3)


class ReadinessReadOnlyTests(unittest.TestCase):
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
    suite.addTests(loader.loadTestsFromTestCase(ReadinessReadOnlyTests))
    suite.addTests(loader.loadTestsFromTestCase(BASE.ProfileConsumerContractTests))
    return suite


if __name__ == "__main__":
    for relative in ("run", "tools/real_device_preflight.py", "tests/test_etb_profile_contract.py", "tests/test_etb_target_guard.py", "package.json"):
        path = ROOT / relative
        print("TARGET_SOURCE " + relative + " sha256=" + hashlib.sha256(path.read_bytes()).hexdigest() + " mode=" + oct(path.stat().st_mode & 0o777), flush=True)
    unittest.main(verbosity=2)
