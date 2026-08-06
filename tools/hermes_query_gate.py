"""Hermes pre-action query boundary.

This module makes the mandatory pre-investigation contract explicit without
owning lifecycle, making decisions, or executing any engineering action.
"""

from __future__ import annotations

from pathlib import Path
from typing import Any

from .aios_query import query
from .aios_query_schema import validate_response


ALLOWED_ACTION_KINDS = frozenset({
    "INVESTIGATION",
    "EVIDENCE_COLLECTION",
    "REPOSITORY_SEARCH",
    "RUNTIME_ATTEMPT",
})


def query_before_action(
    mission: str,
    question: str,
    action_kind: str,
    *,
    root: Path | None = None,
) -> dict[str, Any]:
    """Query repository knowledge before a Hermes-owned action.

    The returned value is exactly the Query Engine public response. Hermes
    decides whether to proceed; this boundary never approves, blocks, or
    executes the requested action.
    """
    normalized_action = action_kind.strip().upper()
    if normalized_action not in ALLOWED_ACTION_KINDS:
        raise ValueError("AIOS_QUERY_ACTION_KIND_INVALID")
    return validate_response(query(mission, question, root=root))
