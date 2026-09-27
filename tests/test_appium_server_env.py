from __future__ import annotations

import importlib.util
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

ROOT = Path(__file__).resolve().parents[1]
MODULE_PATH = ROOT / "tools" / "appium_server.py"
SPEC = importlib.util.spec_from_file_location("appium_server_contract", MODULE_PATH)
assert SPEC and SPEC.loader
MODULE = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(MODULE)


class AppiumServerEnvironmentTests(unittest.TestCase):
    def test_real_account_home_and_sdk_override_sandboxed_runtime(self):
        env = MODULE.build_environment(
            {"HOME": "/sandbox/project", "PATH": "/usr/bin:/bin"},
            home=Path("/Users/synthetic"),
            sdk_root=Path("/synthetic/android-sdk"),
        )
        self.assertEqual(env["HOME"], "/Users/synthetic")
        self.assertEqual(env["APPIUM_HOME"], "/Users/synthetic/.appium")
        self.assertEqual(env["ANDROID_HOME"], "/synthetic/android-sdk")
        self.assertEqual(env["ANDROID_SDK_ROOT"], "/synthetic/android-sdk")
        self.assertEqual(env["PATH"], "/usr/bin:/bin")

    def test_sdk_root_can_be_resolved_from_account_home(self):
        with tempfile.TemporaryDirectory(prefix="bbl-appium-home-") as directory:
            home = Path(directory)
            adb = home / "Library" / "Android" / "sdk" / "platform-tools" / "adb"
            adb.parent.mkdir(parents=True)
            adb.write_text("", encoding="utf-8")
            resolved = MODULE.resolve_android_sdk_root({}, home=home)
        self.assertEqual(resolved, home / "Library" / "Android" / "sdk")

    def test_default_server_argv_keeps_uiautomator2_adb_shell_permission(self):
        argv = MODULE.build_argv("/synthetic/appium")
        self.assertEqual(argv[0], "/synthetic/appium")
        self.assertIn("--address", argv)
        self.assertIn("127.0.0.1", argv)
        self.assertIn("--allow-insecure=uiautomator2:adb_shell", argv)
        self.assertNotIn("--use-plugins=inspector", argv)

    def test_inspector_mode_is_explicit(self):
        argv = MODULE.build_argv("/synthetic/appium", inspector=True)
        self.assertIn("--use-plugins=inspector", argv)
        self.assertIn("--allow-cors", argv)

    def test_runtime_receipt_binds_pid_appium_home_and_sdk(self):
        env = {
            "APPIUM_HOME": "/Users/synthetic/.appium",
            "ANDROID_SDK_ROOT": "/Users/synthetic/Library/Android/sdk",
        }
        payload = MODULE.runtime_receipt_payload(env, pid=4242)
        self.assertEqual(payload["schema"], "bbl-appium-runtime/v1")
        self.assertEqual(payload["pid"], 4242)
        self.assertTrue(MODULE.receipt_matches_environment(payload, env))

    def test_runtime_receipt_rejects_wrong_extension_home(self):
        env = {
            "APPIUM_HOME": "/Users/synthetic/.appium",
            "ANDROID_SDK_ROOT": "/Users/synthetic/Library/Android/sdk",
        }
        payload = MODULE.runtime_receipt_payload(env, pid=4242)
        payload["appium_home"] = "/sandbox/.appium"
        self.assertFalse(MODULE.receipt_matches_environment(payload, env))

    def test_ensure_reuses_ready_managed_runtime_without_spawning(self):
        with patch.object(
            MODULE, "check_runtime_readiness", return_value=(True, "READY")
        ), patch.object(MODULE.subprocess, "Popen") as popen:
            ready, category = MODULE.ensure_runtime_readiness()
        self.assertTrue(ready)
        self.assertEqual(category, "READY")
        popen.assert_not_called()

    def test_ensure_refuses_unknown_listener_without_killing_or_adopting(self):
        with patch.object(
            MODULE,
            "check_runtime_readiness",
            return_value=(False, "APPIUM_RUNTIME_PID_NOT_ALIVE"),
        ), patch.object(
            MODULE, "_listener_pids", return_value={4242}
        ), patch.object(MODULE.subprocess, "Popen") as popen:
            ready, category = MODULE.ensure_runtime_readiness()
        self.assertFalse(ready)
        self.assertEqual(category, "APPIUM_UNMANAGED_LISTENER")
        popen.assert_not_called()

    def test_etb_runner_ensures_managed_appium_before_cis(self):
        runner = (ROOT / "tools" / "runner" / "etb_runner.sh").read_text(encoding="utf-8")
        preflight = (ROOT / "tools" / "runner" / "etb_preflight.sh").read_text(encoding="utf-8")
        target = runner.index("run_etb_target_preflight")
        network = runner.index("run_etb_network_preflight")
        appium = runner.index("run_etb_appium_preflight")
        cis = runner.index("run_etb_cis_preflight")
        self.assertLess(target, network)
        self.assertLess(network, appium)
        self.assertLess(appium, cis)
        self.assertIn('"$ROOT/tools/appium_server.py" --reconcile', preflight)
        self.assertIn("APPIUM_RUNTIME_GATE=CLOSED", preflight)


if __name__ == "__main__":
    unittest.main(verbosity=2)
