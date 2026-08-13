from __future__ import annotations

import tempfile
import unittest
from pathlib import Path

import yaml

from libraries.config_loader import load_profile


DEFAULTS = ("etb", "ntb_ilove", "ntb_somjai")


def _write_safe_profiles(base: Path) -> None:
    for name in DEFAULTS:
        data = {
            "profile": {
                "citizen_id": "SYNTHETIC_CITIZEN_ID",
                "date_of_birth": "2000-01-01",
                "mobile_number": "SYNTHETIC_PHONE",
            }
        }
        if name.startswith("ntb_"):
            data.update({"ocr": {}, "dopa": {}, "otp": {}, "pin": {}})
        (base / f"{name}.yaml").write_text(yaml.safe_dump(data), encoding="utf-8")


class DefaultProfileTests(unittest.TestCase):
    def test_safe_local_profiles_resolve_without_committed_private_data(self) -> None:
        with tempfile.TemporaryDirectory(prefix="default-profile-") as directory:
            base = Path(directory)
            _write_safe_profiles(base)
            for name in DEFAULTS:
                resolved = load_profile(name, str(base))
                self.assertIsInstance(resolved, dict)
            self.assertEqual(load_profile("ilove", str(base)), load_profile("ntb_ilove", str(base)))
            self.assertEqual(load_profile("somjai", str(base)), load_profile("ntb_somjai", str(base)))

    def test_matching_local_override_wins(self) -> None:
        with tempfile.TemporaryDirectory(prefix="local-profile-") as directory:
            base = Path(directory)
            (base / "etb.yaml").write_text(
                "profile:\n  pin: original\n",
                encoding="utf-8",
            )
            (base / "etb.local.yaml").write_text(
                "profile:\n  pin: override\n",
                encoding="utf-8",
            )
            resolved = load_profile("etb", str(base))
            self.assertEqual(resolved["profile"]["pin"], "override")

    def test_explicit_profile_and_missing_profile(self) -> None:
        with tempfile.TemporaryDirectory(prefix="explicit-profile-") as directory:
            base = Path(directory)
            _write_safe_profiles(base)
            selected = load_profile("ntb_somjai", str(base))
            self.assertIn("dopa", selected)
        with self.assertRaisesRegex(ValueError, "Unknown onboarding profile"):
            load_profile("does_not_exist")


if __name__ == "__main__":
    unittest.main()
