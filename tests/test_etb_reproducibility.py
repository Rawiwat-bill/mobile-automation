from __future__ import annotations

import importlib.util
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
GUARD_PATH = ROOT / "tools" / "etb_reproducibility_guard.py"


def _load_guard():
    if not GUARD_PATH.exists():
        raise AssertionError("ETB_REPRODUCIBILITY_GUARD_MISSING")
    spec = importlib.util.spec_from_file_location("etb_reproducibility_guard", GUARD_PATH)
    if spec is None or spec.loader is None:
        raise AssertionError("ETB_REPRODUCIBILITY_GUARD_IMPORT_FAILED")
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


def _git(repo: Path, *args: str) -> str:
    completed = subprocess.run(
        ["git", *args],
        cwd=repo,
        check=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True,
    )
    return completed.stdout.strip()


class ETBReproducibilityContractTests(unittest.TestCase):
    def test_manifest_and_lock_are_safe_and_exact(self):
        guard = _load_guard()
        manifest = guard.load_manifest(ROOT)
        self.assertEqual(manifest["schema"], "bbl-mobile-delivery/v1")
        self.assertEqual(guard.validate_lock(ROOT, manifest), ())

        required = set(manifest["required_current_paths"])
        local_only = set(manifest["local_only_inputs"])
        self.assertFalse(required & local_only)
        self.assertIn("apps/android/app-dev.apk", local_only)
        self.assertIn("apps/android/app-sit-mmplot2.apk", local_only)
        for relative in required:
            with self.subTest(relative=relative):
                self.assertTrue((ROOT / relative).is_file(), relative)
                lower = relative.lower()
                self.assertNotIn("private_local", lower)
                self.assertFalse(lower.startswith("reports/"), relative)
                self.assertFalse(lower.startswith("local/"), relative)
                self.assertFalse(lower.startswith(".runtime/"), relative)
                self.assertFalse(lower.endswith(".local.yaml"), relative)
                self.assertFalse(lower.endswith(".apk"), relative)

    def test_index_gap_detects_untracked_and_unstaged_current_content(self):
        guard = _load_guard()
        with tempfile.TemporaryDirectory(prefix="bbl-repro-index-") as temp:
            repo = Path(temp)
            _git(repo, "init")
            _git(repo, "config", "user.email", "synthetic@example.invalid")
            _git(repo, "config", "user.name", "Synthetic Test")
            (repo / "tracked.txt").write_text("base\n", encoding="utf-8")
            _git(repo, "add", "tracked.txt")
            _git(repo, "commit", "-m", "base")

            (repo / "tracked.txt").write_text("current\n", encoding="utf-8")
            (repo / "new.txt").write_text("new\n", encoding="utf-8")
            manifest = {"required_current_paths": ["tracked.txt", "new.txt"]}

            gaps = set(guard.index_transfer_gaps(repo, manifest))
            self.assertIn("INDEX_DIFFERS_FROM_WORKTREE:tracked.txt", gaps)
            self.assertIn("MISSING_FROM_INDEX:new.txt", gaps)

    def test_index_gap_closes_when_index_matches_current_content(self):
        guard = _load_guard()
        with tempfile.TemporaryDirectory(prefix="bbl-repro-index-green-") as temp:
            repo = Path(temp)
            _git(repo, "init")
            _git(repo, "config", "user.email", "synthetic@example.invalid")
            _git(repo, "config", "user.name", "Synthetic Test")
            (repo / "tracked.txt").write_text("current\n", encoding="utf-8")
            _git(repo, "add", "tracked.txt")
            manifest = {"required_current_paths": ["tracked.txt"]}
            self.assertEqual(guard.index_transfer_gaps(repo, manifest), ())

    def test_index_snapshot_materialization_ignores_unstaged_worktree_content(self):
        guard = _load_guard()
        with tempfile.TemporaryDirectory(prefix="bbl-repro-index-snapshot-") as temp:
            repo = Path(temp) / "repo"
            candidate = Path(temp) / "candidate"
            repo.mkdir()
            candidate.mkdir()
            _git(repo, "init")
            _git(repo, "config", "user.email", "synthetic@example.invalid")
            _git(repo, "config", "user.name", "Synthetic Test")
            (repo / "tracked.txt").write_text("index-version\n", encoding="utf-8")
            _git(repo, "add", "tracked.txt")
            (repo / "tracked.txt").write_text("worktree-version\n", encoding="utf-8")

            manifest = {
                "required_current_paths": ["tracked.txt"],
                "required_source_examples": [],
            }
            guard.materialize_index_snapshot(repo, candidate, manifest)

            self.assertEqual(
                (candidate / "tracked.txt").read_text(encoding="utf-8"),
                "index-version\n",
            )


    def test_candidate_snapshot_excludes_staged_unrelated_changes(self):
        guard = _load_guard()
        with tempfile.TemporaryDirectory(prefix="bbl-repro-boundary-") as temp:
            repo = Path(temp) / "repo"
            candidate = Path(temp) / "candidate"
            repo.mkdir()
            candidate.mkdir()
            _git(repo, "init")
            _git(repo, "config", "user.email", "synthetic@example.invalid")
            _git(repo, "config", "user.name", "Synthetic Test")

            (repo / "required.txt").write_text("head-required\n", encoding="utf-8")
            (repo / "unrelated.txt").write_text("head-unrelated\n", encoding="utf-8")
            _git(repo, "add", "required.txt", "unrelated.txt")
            _git(repo, "commit", "-m", "base")

            (repo / "required.txt").write_text("candidate-required\n", encoding="utf-8")
            _git(repo, "add", "required.txt")
            (repo / "unrelated.txt").write_text("staged-unrelated\n", encoding="utf-8")
            _git(repo, "add", "unrelated.txt")

            manifest = {
                "required_current_paths": ["required.txt"],
                "required_source_examples": [],
            }
            missing = guard.materialize_index_snapshot(repo, candidate, manifest)
            self.assertEqual(missing, ())
            self.assertEqual(
                (candidate / "required.txt").read_text(encoding="utf-8"),
                "candidate-required\n",
            )
            self.assertEqual(
                (candidate / "unrelated.txt").read_text(encoding="utf-8"),
                "head-unrelated\n",
            )

    def test_current_index_direct_robot_dryrun_passes(self):
        guard = _load_guard()
        manifest = guard.load_manifest(ROOT)
        with tempfile.TemporaryDirectory(prefix="bbl-repro-index-robot-") as temp:
            candidate = Path(temp) / "repo"
            candidate.mkdir()
            missing = guard.materialize_index_snapshot(ROOT, candidate, manifest)
            self.assertEqual(missing, ())

            profile_path = Path(temp) / "missing-no-profile.yaml"
            completed = subprocess.run(
                [
                    str(ROOT / ".venv" / "bin" / "python"),
                    "-m",
                    "robot",
                    "--dryrun",
                    "--console",
                    "verbose",
                    "--output",
                    "NONE",
                    "--log",
                    "NONE",
                    "--report",
                    "NONE",
                    "--variable",
                    f"ETB_CASE_PROFILES:{profile_path}",
                    "--test",
                    "TC-ETB-001 Positive Registration Success",
                    "tests/android/etb/etb_regression.robot",
                ],
                cwd=candidate,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True,
            )
            self.assertEqual(
                completed.returncode,
                0,
                completed.stdout + "\n" + completed.stderr,
            )

    def test_current_candidate_snapshot_is_clean_and_tc001_dryrun_passes(self):
        guard = _load_guard()
        manifest = guard.load_manifest(ROOT)
        candidate = guard.build_candidate_snapshot(
            ROOT,
            manifest,
            python_bin=str(ROOT / ".venv" / "bin" / "python"),
        )
        self.assertTrue(candidate.clean, candidate.status_text)
        self.assertTrue(
            candidate.dry_run_passed,
            candidate.status_text + "\n" + candidate.output,
        )
        self.assertEqual(candidate.selected_count, 1)
        self.assertNotIn("TARGET_GUARD=", candidate.output)
        self.assertNotIn("CIS preflight", candidate.output)
        self.assertNotIn("REAL_DEVICE_PREFLIGHT", candidate.output)


if __name__ == "__main__":
    unittest.main(verbosity=2)
