from __future__ import annotations

import hashlib
import json
import os
import re
import stat
import subprocess
import tempfile
from dataclasses import dataclass
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
MANIFEST = Path("configs/mobile_delivery_manifest.json")
_EXACT_REQUIREMENT = re.compile(r"^[A-Za-z0-9_.-]+==[^=\s]+$")
_REQUIRED_PACKAGES = {
    "robotframework",
    "robotframework-appiumlibrary",
    "pyyaml",
    "pillow",
}


@dataclass(frozen=True)
class CandidateResult:
    clean: bool
    dry_run_passed: bool
    selected_count: int
    output: str
    status_text: str


def _run(
    command: list[str],
    *,
    cwd: Path,
    env: dict[str, str] | None = None,
    check: bool = False,
) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        command,
        cwd=cwd,
        env=env,
        check=check,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True,
    )


def _git_bytes(repo: Path, *args: str) -> bytes:
    completed = subprocess.run(
        ["git", *args],
        cwd=repo,
        check=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
    )
    return completed.stdout


def _git_paths(repo: Path, *args: str) -> tuple[str, ...]:
    return tuple(
        item.decode("utf-8", errors="surrogateescape")
        for item in _git_bytes(repo, *args).split(b"\0")
        if item
    )


def _sensitive_path(relative: str) -> bool:
    normalized = relative.replace("\\", "/").lstrip("./")
    lower = normalized.lower()
    parts = tuple(part.lower() for part in Path(normalized).parts)
    name = Path(normalized).name.lower()
    if "private_local" in parts:
        return True
    if lower.startswith(("reports/", "local/", ".runtime/")):
        return True
    if lower == ".env" or name == ".env":
        return True
    if lower.endswith((".local.yaml", ".secret.yaml", ".apk", ".log")):
        return True
    if name in {"output.xml", "log.html", "report.html"}:
        return True
    if lower.startswith("testdata/onboarding/") and lower.endswith(".yaml"):
        return lower not in {
            "testdata/onboarding/etb_cases.yaml",
            "testdata/onboarding/etb.example.yaml",
        }
    return False


def load_manifest(root: Path = ROOT) -> dict[str, Any]:
    path = Path(root) / MANIFEST
    value = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(value, dict):
        raise ValueError("MOBILE_DELIVERY_MANIFEST_INVALID")
    return value


def validate_lock(root: Path, manifest: dict[str, Any]) -> tuple[str, ...]:
    lock_name = str(manifest.get("python_lock", ""))
    lock_path = Path(root) / lock_name
    if not lock_name or not lock_path.is_file():
        return ("PYTHON_LOCK_MISSING",)

    errors: list[str] = []
    packages: set[str] = set()
    for number, raw in enumerate(lock_path.read_text(encoding="utf-8").splitlines(), 1):
        line = raw.strip()
        if not line or line.startswith("#"):
            continue
        if not _EXACT_REQUIREMENT.fullmatch(line):
            errors.append(f"NON_EXACT_LOCK_ENTRY:{number}")
            continue
        name = line.split("==", 1)[0].lower().replace("_", "-")
        packages.add(name)

    for required in sorted(_REQUIRED_PACKAGES - packages):
        errors.append(f"LOCK_PACKAGE_MISSING:{required}")
    return tuple(errors)


def _index_blob(repo: Path, relative: str) -> bytes | None:
    completed = subprocess.run(
        ["git", "show", f":{relative}"],
        cwd=repo,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
    )
    return completed.stdout if completed.returncode == 0 else None


def _index_mode(repo: Path, relative: str) -> str | None:
    completed = _run(["git", "ls-files", "--stage", "--", relative], cwd=repo)
    if completed.returncode != 0 or not completed.stdout.strip():
        return None
    return completed.stdout.split(maxsplit=1)[0]


def index_transfer_gaps(repo: Path, manifest: dict[str, Any]) -> tuple[str, ...]:
    repo = Path(repo).resolve()
    gaps: list[str] = []
    for relative in manifest.get("required_current_paths", []):
        relative = str(relative)
        current = repo / relative
        if not current.is_file():
            gaps.append(f"MISSING_WORKTREE:{relative}")
            continue
        indexed = _index_blob(repo, relative)
        if indexed is None:
            gaps.append(f"MISSING_FROM_INDEX:{relative}")
            continue
        if hashlib.sha256(indexed).digest() != hashlib.sha256(current.read_bytes()).digest():
            gaps.append(f"INDEX_DIFFERS_FROM_WORKTREE:{relative}")
            continue

        index_mode = _index_mode(repo, relative)
        current_exec = bool(current.stat().st_mode & stat.S_IXUSR)
        expected_mode = "100755" if current_exec else "100644"
        if index_mode and index_mode != expected_mode:
            gaps.append(f"INDEX_MODE_DIFFERS:{relative}:{index_mode}->{expected_mode}")
    return tuple(gaps)


def _head_paths(repo: Path) -> tuple[str, ...]:
    completed = subprocess.run(
        ["git", "ls-tree", "-r", "--name-only", "-z", "HEAD"],
        cwd=repo,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
    )
    if completed.returncode != 0:
        return ()
    return tuple(
        item.decode("utf-8", errors="surrogateescape")
        for item in completed.stdout.split(b"\0")
        if item
    )


def _head_blob(repo: Path, relative: str) -> bytes | None:
    completed = subprocess.run(
        ["git", "show", f"HEAD:{relative}"],
        cwd=repo,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
    )
    return completed.stdout if completed.returncode == 0 else None


def _head_mode(repo: Path, relative: str) -> str | None:
    completed = _run(["git", "ls-tree", "HEAD", "--", relative], cwd=repo)
    if completed.returncode != 0 or not completed.stdout.strip():
        return None
    return completed.stdout.split(maxsplit=1)[0]


def _candidate_snapshot_paths(repo: Path, manifest: dict[str, Any]) -> tuple[str, ...]:
    head_tracked = set(_head_paths(repo))
    explicit = {
        str(path)
        for key in ("required_current_paths", "required_source_examples")
        for path in manifest.get(key, [])
    }
    return tuple(sorted(head_tracked | explicit))


def materialize_index_snapshot(
    repo: Path,
    destination: Path,
    manifest: dict[str, Any],
) -> tuple[str, ...]:
    repo = Path(repo).resolve()
    destination = Path(destination)
    explicit_required = {
        str(path)
        for key in ("required_current_paths", "required_source_examples")
        for path in manifest.get(key, [])
    }
    missing: list[str] = []

    for relative in _candidate_snapshot_paths(repo, manifest):
        if _sensitive_path(relative):
            continue

        if relative in explicit_required:
            blob = _index_blob(repo, relative)
            mode = _index_mode(repo, relative)
        else:
            blob = _head_blob(repo, relative)
            mode = _head_mode(repo, relative)

        if blob is None or mode is None:
            if relative in explicit_required:
                missing.append(relative)
            continue

        target = destination / relative
        target.parent.mkdir(parents=True, exist_ok=True)
        if mode == "120000":
            target.symlink_to(blob.decode("utf-8", errors="surrogateescape"))
            continue

        target.write_bytes(blob)
        target.chmod(0o755 if mode == "100755" else 0o644)

    return tuple(sorted(missing))


def build_candidate_snapshot(
    root: Path,
    manifest: dict[str, Any],
    *,
    python_bin: str,
) -> CandidateResult:
    root = Path(root).resolve()

    with tempfile.TemporaryDirectory(prefix="bbl-etb-clean-snapshot-") as temp:
        candidate = Path(temp) / "repo"
        candidate.mkdir()

        missing = materialize_index_snapshot(root, candidate, manifest)
        if missing:
            text = "CANDIDATE_REQUIRED_SOURCE_MISSING=" + ",".join(missing)
            return CandidateResult(False, False, 0, text, text)

        lock_errors = validate_lock(candidate, manifest)
        if lock_errors:
            text = "LOCK_INVALID=" + ",".join(lock_errors)
            return CandidateResult(False, False, 0, text, text)

        _run(["git", "init"], cwd=candidate, check=True)
        _run(["git", "config", "user.email", "synthetic@example.invalid"], cwd=candidate, check=True)
        _run(["git", "config", "user.name", "Synthetic Repro Proof"], cwd=candidate, check=True)
        _run(["git", "add", "-A"], cwd=candidate, check=True)
        _run(["git", "commit", "-m", "candidate snapshot"], cwd=candidate, check=True)
        clean_before = _run(["git", "status", "--porcelain"], cwd=candidate, check=True).stdout.strip() == ""

        home = Path(temp) / "home"
        home.mkdir()
        env = os.environ.copy()
        env.update(
            {
                "PYTHON_BIN": str(python_bin),
                "ETB_ENVIRONMENT": "DEV",
                "ANDROID_EXECUTION_TARGET": "REAL",
                "DEVICE_UDID": "",
                "ETB_CASE_PROFILES": str(Path(temp) / "missing-no-profile.yaml"),
                "HOME": str(home),
                "CIS_CLEAR_URL": "http://127.0.0.1:1/unreachable",
            }
        )
        dry_run = _run(["./run", "etb", "TC-ETB-001", "--dry-run"], cwd=candidate, env=env)
        output = dry_run.stdout + dry_run.stderr
        match = re.search(r"ETB dry-run selection:\s*(\d+)\s*testcase", output)
        selected = int(match.group(1)) if match else 0
        forbidden = ("TARGET_GUARD=", "CIS preflight", "REAL_DEVICE_PREFLIGHT")
        dry_run_passed = dry_run.returncode == 0 and selected == 1 and not any(token in output for token in forbidden)

        clean_after = _run(["git", "status", "--porcelain"], cwd=candidate, check=True).stdout.strip() == ""
        clean = clean_before and clean_after
        status = (
            f"CANDIDATE_CLEAN={'PASS' if clean else 'FAIL'} "
            f"CANDIDATE_DRY_RUN={'PASS' if dry_run_passed else 'FAIL'} "
            f"SELECTED={selected} EXIT={dry_run.returncode}"
        )
        return CandidateResult(clean, dry_run_passed, selected, output, status)


def main() -> int:
    manifest = load_manifest(ROOT)
    lock_errors = validate_lock(ROOT, manifest)
    python_bin = ROOT / ".venv" / "bin" / "python"
    candidate = build_candidate_snapshot(ROOT, manifest, python_bin=str(python_bin))
    gaps = index_transfer_gaps(ROOT, manifest)

    print(f"MOBILE_LOCK={'PASS' if not lock_errors else 'FAIL'}")
    for error in lock_errors:
        print(f"LOCK_ERROR={error}")
    print(f"CANDIDATE_CLEAN_SNAPSHOT={'PASS' if candidate.clean else 'FAIL'}")
    print(f"CANDIDATE_DRY_RUN={'PASS' if candidate.dry_run_passed else 'FAIL'}")
    print(f"CANDIDATE_SELECTED_COUNT={candidate.selected_count}")
    print(f"INDEX_TRANSFER_GAP_COUNT={len(gaps)}")
    for gap in gaps:
        print(f"INDEX_TRANSFER_GAP={gap}")

    candidate_ok = not lock_errors and candidate.clean and candidate.dry_run_passed
    if candidate_ok and not gaps:
        print("F17_CLEAN_CHECKOUT_PROOF=PASS")
        return 0
    if candidate_ok and gaps:
        print("F17_CLEAN_CHECKOUT_PROOF=BLOCKED_BY_INDEX")
        return 2
    print("F17_CLEAN_CHECKOUT_PROOF=FAIL")
    return 3


if __name__ == "__main__":
    raise SystemExit(main())
