"""Shared run/case evidence scoping for ETB runtime artifacts."""

from __future__ import annotations

import os
import re
from datetime import datetime, timezone
from pathlib import Path

from robot.api.deco import keyword, not_keyword
from robot.libraries.BuiltIn import BuiltIn

_SAFE_SEGMENT = re.compile(r"[^A-Za-z0-9_.-]+")
_CASE_ID = re.compile(r"\bTC-ETB-\d{3}\b")
_FALLBACK_RUN_ID = (
    datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%S%fZ") + f"-p{os.getpid()}"
)


def _safe_segment(value: str, fallback: str) -> str:
    normalized = _SAFE_SEGMENT.sub("_", value.strip()).strip("._-")
    return normalized or fallback


def _robot_case_id() -> str:
    try:
        test_name = str(BuiltIn().get_variable_value("${TEST NAME}") or "")
    except Exception:
        return ""
    match = _CASE_ID.search(test_name)
    return match.group(0) if match else ""


def _runtime_scope(run_id: str = "", case_id: str = "") -> tuple[str, str] | None:
    resolved_run = run_id or os.environ.get("ETB_RUN_ID", "")
    resolved_case = case_id or os.environ.get("ETB_CASE_ID", "") or _robot_case_id()
    if not resolved_run and not resolved_case:
        return None
    if not resolved_run:
        resolved_run = _FALLBACK_RUN_ID
    if not resolved_case:
        resolved_case = "CASE_UNSCOPED"
    return (
        _safe_segment(resolved_run, "RUN_UNSCOPED"),
        _safe_segment(resolved_case, "CASE_UNSCOPED"),
    )


@not_keyword
def resolve_scoped_output_dir(
    output_dir: str,
    run_id: str = "",
    case_id: str = "",
) -> str:
    """Return output root or output/evidence/<run>/<case> when context exists."""
    base = Path(output_dir)
    scope = _runtime_scope(run_id, case_id)
    target = base if scope is None else base / "evidence" / scope[0] / scope[1]
    target.mkdir(parents=True, exist_ok=True)
    return str(target)


@not_keyword
def resolve_private_evidence_dir(
    output_dir: str,
    run_id: str = "",
    case_id: str = "",
) -> str:
    """Return the private-local directory inside the resolved run/case scope."""
    target = Path(resolve_scoped_output_dir(output_dir, run_id, case_id)) / "private_local"
    target.mkdir(parents=True, exist_ok=True)
    return str(target)


@keyword("Resolve Private Evidence Dir")
def resolve_private_evidence_dir_for_robot(
    output_dir: str,
    run_id: str = "",
    case_id: str = "",
) -> str:
    """Robot keyword wrapper around the internal Python resolver."""
    return resolve_private_evidence_dir(output_dir, run_id, case_id)
