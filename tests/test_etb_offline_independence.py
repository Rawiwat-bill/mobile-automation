from __future__ import annotations

import hashlib
import os
import subprocess
import sys
import tempfile
import types
import unittest
from pathlib import Path
from unittest.mock import patch

# This contract must not depend on globally installed PyYAML. The selected tests
# never parse real YAML; any unexpected YAML access is therefore a contract failure.
_yaml_stub = types.ModuleType("yaml")
def _unexpected_yaml_access(*args, **kwargs):
    raise AssertionError("OFFLINE_INDEPENDENCE_UNEXPECTED_YAML_ACCESS")
_yaml_stub.safe_load = _unexpected_yaml_access
sys.modules.setdefault("yaml", _yaml_stub)

from tests.test_cis_preparation import CisPreparationTests

ROOT = Path(__file__).resolve().parents[1]
RUNNER = ROOT / "run"
CIS_TEST = ROOT / "tests/test_cis_preparation.py"


class ETBOfflineIndependenceTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        print("SHA256 run " + hashlib.sha256(RUNNER.read_bytes()).hexdigest())
        print(
            "SHA256 tests/test_cis_preparation.py "
            + hashlib.sha256(CIS_TEST.read_bytes()).hexdigest()
        )

    def test_dry_run_tc001_needs_no_device_backend_or_profile(self) -> None:
        with tempfile.TemporaryDirectory(prefix="etb-dryrun-offline-") as directory:
            missing_profile = Path(directory) / "missing-etb-cases.yaml"
            env = os.environ.copy()
            env.update(
                {
                    "ETB_ENVIRONMENT": "DEV",
                    "ANDROID_EXECUTION_TARGET": "REAL",
                    "DEVICE_UDID": "",
                    "ETB_CASE_PROFILES": str(missing_profile),
                    "HOME": directory,
                    "CIS_CLEAR_URL": "https://127.0.0.1:9/must-not-be-used",
                }
            )
            result = subprocess.run(
                [str(RUNNER), "etb", "TC-ETB-001", "--dry-run"],
                cwd=ROOT,
                env=env,
                capture_output=True,
                text=True,
                timeout=30,
                check=False,
            )
        combined = result.stdout + result.stderr
        self.assertEqual(result.returncode, 0, combined)
        self.assertIn("ETB dry-run selection: 1 testcase(s)", result.stdout)
        self.assertNotIn("TARGET_GUARD=", combined)
        self.assertNotIn("CIS preflight", combined)
        self.assertNotIn("ETB preflight:", combined)
        self.assertNotIn("REAL_DEVICE_PREFLIGHT", combined)

    def test_named_profile_cis_unit_forbids_real_profile_loader(self) -> None:
        case = CisPreparationTests(
            "test_approved_profile_name_resolves_without_filesystem_path"
        )
        result = unittest.TestResult()
        with patch(
            "libraries.cis_preparation._load_profile",
            side_effect=AssertionError("LOCAL_PROFILE_ACCESS_FORBIDDEN"),
        ):
            case.run(result)
        details = [str(item[1]) for item in result.failures + result.errors]
        self.assertTrue(result.wasSuccessful(), "\n".join(details))


if __name__ == "__main__":
    unittest.main(verbosity=2)
