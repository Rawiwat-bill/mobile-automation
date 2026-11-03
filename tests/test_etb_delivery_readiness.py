from __future__ import annotations

import importlib.util
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
GUARD_PATH = ROOT / "tools" / "etb_delivery_guard.py"


def _load_guard():
    if not GUARD_PATH.exists():
        raise AssertionError("DELIVERY_GUARD_MISSING")
    spec = importlib.util.spec_from_file_location("etb_delivery_guard", GUARD_PATH)
    if spec is None or spec.loader is None:
        raise AssertionError("DELIVERY_GUARD_IMPORT_FAILED")
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


def _git(repo: Path, *args: str) -> None:
    subprocess.run(
        ["git", *args],
        cwd=repo,
        check=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True,
    )


class ETBDeliveryReadinessContractTests(unittest.TestCase):
    def test_sensitive_path_policy_denies_private_and_generated_artifacts(self):
        guard = _load_guard()
        denied = (
            "reports/run-etb/TC-ETB-001/output.xml",
            "reports/investigation/private_local/screen.png",
            "tmp/private_local/page.xml",
            ".env",
            "local/etb.yaml",
            "testdata/onboarding/customer.yaml",
            "testdata/onboarding/etb.local.yaml",
            "testdata/onboarding/sample.secret.yaml",
            "apps/android/app-dev.apk",
            "nested/output.xml",
            "debug.log",
        )
        for path in denied:
            with self.subTest(path=path):
                self.assertTrue(guard.is_sensitive_path(path), path)

        allowed = (
            "testdata/onboarding/etb_cases.yaml",
            "testdata/onboarding/etb.example.yaml",
            "tests/test_etb_delivery_readiness.py",
            "libraries/evidence_scope.py",
            "tools/etb_delivery_guard.py",
        )
        for path in allowed:
            with self.subTest(path=path):
                self.assertFalse(guard.is_sensitive_path(path), path)

    def test_fingerprint_is_order_independent_and_content_sensitive(self):
        guard = _load_guard()
        first = [
            ("M", "b.txt", "hash-b"),
            ("A", "a.txt", "hash-a"),
        ]
        second = list(reversed(first))
        changed = [
            ("M", "b.txt", "hash-b-CHANGED"),
            ("A", "a.txt", "hash-a"),
        ]
        self.assertEqual(guard.stable_fingerprint(first), guard.stable_fingerprint(second))
        self.assertNotEqual(guard.stable_fingerprint(first), guard.stable_fingerprint(changed))

    def test_temp_repo_detects_staged_sensitive_path_and_fingerprints_dirty_snapshot(self):
        guard = _load_guard()
        with tempfile.TemporaryDirectory(prefix="bbl-delivery-") as temp:
            repo = Path(temp)
            _git(repo, "init")
            _git(repo, "config", "user.email", "synthetic@example.invalid")
            _git(repo, "config", "user.name", "Synthetic Test")

            (repo / "safe.txt").write_text("base\n", encoding="utf-8")
            _git(repo, "add", "safe.txt")
            _git(repo, "commit", "-m", "base")

            (repo / "safe.txt").write_text("changed\n", encoding="utf-8")
            risky = repo / "private_local" / "raw.xml"
            risky.parent.mkdir()
            risky.write_text("<synthetic/>\n", encoding="utf-8")
            _git(repo, "add", "private_local/raw.xml")
            (repo / "untracked.txt").write_text("one\n", encoding="utf-8")

            first = guard.collect_snapshot(repo)
            audit = guard.audit_repository(repo)
            second = guard.collect_snapshot(repo)

            self.assertEqual(first.worktree_fingerprint, second.worktree_fingerprint)
            self.assertEqual(first.staged_fingerprint, second.staged_fingerprint)
            self.assertEqual(first.staged_count, 1)
            self.assertEqual(first.modified_count, 1)
            self.assertEqual(first.untracked_count, 1)
            self.assertFalse(audit.safe)
            self.assertEqual(audit.sensitive_count, 1)

            (repo / "untracked.txt").write_text("two\n", encoding="utf-8")
            third = guard.collect_snapshot(repo)
            self.assertNotEqual(first.worktree_fingerprint, third.worktree_fingerprint)
            self.assertEqual(first.staged_fingerprint, third.staged_fingerprint)

    def test_current_repository_has_no_sensitive_tracked_or_staged_paths(self):
        guard = _load_guard()
        audit = guard.audit_repository(ROOT)
        self.assertTrue(audit.safe, f"SENSITIVE_TRACKED_OR_STAGED_COUNT={audit.sensitive_count}")
        self.assertEqual(audit.sensitive_count, 0)

    def test_gitignore_keeps_private_outputs_and_local_data_out_of_git(self):
        text = (ROOT / ".gitignore").read_text(encoding="utf-8")
        for expected in (
            "/reports/*",
            "/local/",
            "testdata/onboarding/*.yaml",
            "*.local.yaml",
            "*.secret.yaml",
            ".env",
            "apps/android/*.apk",
            "*.log",
        ):
            with self.subTest(expected=expected):
                self.assertIn(expected, text)


if __name__ == "__main__":
    unittest.main(verbosity=2)
