"""Sanitized ETB runtime readiness evidence for bounded blocker handoff review."""

from __future__ import annotations

import json
import os
import re
from pathlib import Path

from robot.api.deco import keyword

from libraries.evidence_scope import resolve_scoped_output_dir

_ALLOWED_ENVIRONMENTS = frozenset({"DEV", "SIT", "DEV_MOCK"})
_ALLOWED_HANDOFF = frozenset({"PASS", "FAIL", "UNPROVEN"})
_SAFE_BUILD_IDENTITY = re.compile(r"^[A-Za-z0-9_.+\-]{1,160}$")
_SAFE_BLOCKER = re.compile(
    r"^(?:AJI-001|GOD-\d+|RGI-\d+|ENVIRONMENT_BACKEND_[A-Z0-9_]+)$"
)


def _scope_identity(output_dir: str) -> tuple[Path, str, str]:
    base = Path(output_dir)
    scoped = Path(resolve_scoped_output_dir(output_dir))
    try:
        relative = scoped.relative_to(base)
    except ValueError:
        return scoped, "UNPROVEN", "UNPROVEN"
    parts = relative.parts
    if len(parts) >= 3 and parts[-3] == "evidence":
        return scoped, parts[-2], parts[-1]
    return scoped, "UNPROVEN", "UNPROVEN"


def _cis_pre_test_state(scoped: Path) -> str:
    result_path = scoped / "cis_pre_test_result.json"
    if not result_path.is_file():
        return "UNPROVEN"
    try:
        payload = json.loads(result_path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError):
        return "UNPROVEN"
    if not isinstance(payload, dict):
        return "UNPROVEN"
    if (
        payload.get("cis_clear") == "PASS"
        and payload.get("cis_state_ready") == "YES"
        and payload.get("profile_reusable") == "YES"
    ):
        return "READY"
    return "NOT_READY"


def _environment() -> str:
    value = os.environ.get("ETB_ENVIRONMENT", "").strip().upper()
    return value if value in _ALLOWED_ENVIRONMENTS else "UNPROVEN"


def _build_identity() -> str:
    value = os.environ.get("ETB_BUILD_IDENTITY", "").strip()
    return value if _SAFE_BUILD_IDENTITY.fullmatch(value) else "UNPROVEN"


def _safe_blocker(value: str) -> str:
    normalized = str(value).strip().upper()
    return normalized if _SAFE_BLOCKER.fullmatch(normalized) else "UNPROVEN"


def _safe_handoff(value: str) -> str:
    normalized = str(value).strip().upper()
    return normalized if normalized in _ALLOWED_HANDOFF else "UNPROVEN"


def _boolean_label(value: object) -> str:
    if isinstance(value, str):
        resolved = value.strip().lower() in {"true", "1", "yes", "y"}
    else:
        resolved = bool(value)
    return "YES" if resolved else "NO"


@keyword("Persist ETB Readiness Summary")
def persist_etb_readiness_summary(
    output_dir: str,
    blocker_code: str = "AJI-001",
    profile_handoff: str = "UNPROVEN",
    dopa_reached: object = False,
) -> str:
    """Write one allowlisted, run/case-scoped readiness summary without PII/raw UI."""
    scoped, run_id, case_id = _scope_identity(output_dir)
    blocker = _safe_blocker(blocker_code)
    resume_condition = (
        "CONFIRM_BACKEND_HEALTH_THEN_RUN_ONE_FOCUSED_TC001"
        if blocker == "AJI-001"
        else "REVIEW_BLOCKER_PROVENANCE_BEFORE_RERUN"
    )
    payload = {
        "schema": "etb-readiness/v1",
        "artifact_classification": "SHAREABLE_SANITIZED",
        "run_id": run_id,
        "case_id": case_id,
        "environment": _environment(),
        "build_identity": _build_identity(),
        "cis_pre_test": _cis_pre_test_state(scoped),
        "profile_handoff": _safe_handoff(profile_handoff),
        "blocker_code": blocker,
        "dopa_reached": _boolean_label(dopa_reached),
        "backend_health": "UNPROVEN",
        "resume_condition": resume_condition,
    }
    target = scoped / "etb_readiness_summary.json"
    target.write_text(
        json.dumps(payload, indent=2, sort_keys=True, ensure_ascii=True) + "\n",
        encoding="utf-8",
    )
    return str(target)
