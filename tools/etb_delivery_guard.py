from __future__ import annotations

import hashlib
import subprocess
from dataclasses import dataclass
from pathlib import Path, PurePosixPath
from typing import Iterable


@dataclass(frozen=True)
class Snapshot:
    branch: str
    head: str
    staged_count: int
    modified_count: int
    untracked_count: int
    staged_fingerprint: str
    worktree_fingerprint: str


@dataclass(frozen=True)
class AuditResult:
    safe: bool
    sensitive_count: int
    sensitive_paths: tuple[str, ...]


def _git_bytes(repo: Path, *args: str) -> bytes:
    completed = subprocess.run(
        ["git", *args],
        cwd=repo,
        check=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
    )
    return completed.stdout


def _git_text(repo: Path, *args: str) -> str:
    return _git_bytes(repo, *args).decode("utf-8", errors="surrogateescape").strip()


def _git_paths(repo: Path, *args: str) -> tuple[str, ...]:
    raw = _git_bytes(repo, *args)
    return tuple(
        part.decode("utf-8", errors="surrogateescape")
        for part in raw.split(b"\0")
        if part
    )


def _normalize_path(path: str) -> str:
    normalized = str(PurePosixPath(path.replace("\\", "/")))
    while normalized.startswith("./"):
        normalized = normalized[2:]
    return normalized


def is_sensitive_path(path: str) -> bool:
    normalized = _normalize_path(path)
    lower = normalized.lower()
    pure = PurePosixPath(normalized)
    name = pure.name.lower()
    parts = tuple(part.lower() for part in pure.parts)

    if "private_local" in parts:
        return True
    if lower == ".env" or name == ".env":
        return True
    if lower.startswith("reports/"):
        return True
    if lower.startswith("local/"):
        return True
    if lower.startswith(".runtime/"):
        return True
    if lower.endswith(".local.yaml") or lower.endswith(".secret.yaml"):
        return True
    if lower.startswith("testdata/onboarding/") and lower.endswith(".yaml"):
        if lower == "testdata/onboarding/etb_cases.yaml":
            return False
        if lower.endswith(".example.yaml"):
            return False
        return True
    if lower.startswith("apps/android/") and lower.endswith(".apk"):
        return True
    if name in {"output.xml", "log.html", "report.html"}:
        return True
    if lower.endswith(".log"):
        return True
    return False


def stable_fingerprint(records: Iterable[tuple[str, str, str]]) -> str:
    digest = hashlib.sha256()
    for status, path, content_digest in sorted(records):
        digest.update(status.encode("utf-8"))
        digest.update(b"\0")
        digest.update(_normalize_path(path).encode("utf-8", errors="surrogateescape"))
        digest.update(b"\0")
        digest.update(content_digest.encode("ascii", errors="strict"))
        digest.update(b"\n")
    return digest.hexdigest()


def _working_tree_digest(repo: Path, relative: str) -> str:
    target = repo / relative
    try:
        if target.is_symlink():
            payload = ("SYMLINK\0" + str(target.readlink())).encode("utf-8", errors="surrogateescape")
        elif target.is_file():
            payload = target.read_bytes()
        elif target.exists():
            payload = b"NON_REGULAR"
        else:
            payload = b"MISSING"
    except OSError:
        payload = b"UNREADABLE"
    return hashlib.sha256(payload).hexdigest()


def collect_snapshot(repo: Path) -> Snapshot:
    repo = Path(repo).resolve()
    head = _git_text(repo, "rev-parse", "HEAD")
    branch = _git_text(repo, "rev-parse", "--abbrev-ref", "HEAD")
    staged = set(_git_paths(repo, "diff", "--cached", "--name-only", "-z"))
    modified = set(_git_paths(repo, "diff", "--name-only", "-z"))
    untracked = set(_git_paths(repo, "ls-files", "--others", "--exclude-standard", "-z"))

    records: list[tuple[str, str, str]] = [
        ("H", "HEAD", hashlib.sha256(head.encode("ascii")).hexdigest()),
        ("B", "BRANCH", hashlib.sha256(branch.encode("utf-8")).hexdigest()),
    ]
    for relative in sorted(staged | modified | untracked):
        flags = "".join(
            flag
            for flag, collection in (("S", staged), ("M", modified), ("U", untracked))
            if relative in collection
        )
        records.append((flags, relative, _working_tree_digest(repo, relative)))

    staged_patch = _git_bytes(repo, "diff", "--cached", "--binary", "--no-ext-diff", "--no-color")
    return Snapshot(
        branch=branch,
        head=head,
        staged_count=len(staged),
        modified_count=len(modified),
        untracked_count=len(untracked),
        staged_fingerprint=hashlib.sha256(staged_patch).hexdigest(),
        worktree_fingerprint=stable_fingerprint(records),
    )


def audit_repository(repo: Path) -> AuditResult:
    repo = Path(repo).resolve()
    tracked = set(_git_paths(repo, "ls-files", "-z"))
    staged = set(_git_paths(repo, "diff", "--cached", "--name-only", "-z"))
    sensitive = tuple(sorted(path for path in (tracked | staged) if is_sensitive_path(path)))
    return AuditResult(
        safe=not sensitive,
        sensitive_count=len(sensitive),
        sensitive_paths=sensitive,
    )


def main() -> int:
    repo = Path(__file__).resolve().parents[1]
    snapshot = collect_snapshot(repo)
    audit = audit_repository(repo)
    dirty = snapshot.staged_count + snapshot.modified_count + snapshot.untracked_count > 0

    print(f"DELIVERY_GUARD={'PASS' if audit.safe else 'FAIL'}")
    print(f"BRANCH={snapshot.branch}")
    print(f"HEAD={snapshot.head}")
    print(f"STAGED_COUNT={snapshot.staged_count}")
    print(f"MODIFIED_COUNT={snapshot.modified_count}")
    print(f"UNTRACKED_COUNT={snapshot.untracked_count}")
    print(f"SENSITIVE_TRACKED_OR_STAGED_COUNT={audit.sensitive_count}")
    print(f"STAGED_FINGERPRINT={snapshot.staged_fingerprint}")
    print(f"WORKTREE_FINGERPRINT={snapshot.worktree_fingerprint}")
    print(f"CURRENT_WORKTREE_CLEAN={'NO' if dirty else 'YES'}")
    print("F17_CLEAN_CHECKOUT_PROOF=NOT_RUN")
    return 0 if audit.safe else 2


if __name__ == "__main__":
    raise SystemExit(main())
