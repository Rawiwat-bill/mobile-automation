"""Schema validation for the read-only AIOS Query Engine contract."""

from __future__ import annotations

from collections.abc import Mapping
from typing import Any

ANSWER_KEYS = frozenset({"repository_answer_exists", "confidence", "answer_source", "existing_answer"})
GAP_KEYS = frozenset({"repository_answer_exists", "knowledge_gap", "missing_evidence_required"})
KNOWLEDGE_GAPS = frozenset(
    {
        "NONE",
        "PARTIAL",
        "REQUIRES_RUNTIME",
        "REQUIRES_EXTERNAL_INFORMATION",
        "UNKNOWN",
    }
)
CONFIDENCE = frozenset({"HIGH", "MEDIUM", "LOW"})


def validate_response(response: Mapping[str, Any]) -> dict[str, Any]:
    """Validate and return a copy of exactly one public response shape."""
    if not isinstance(response, Mapping):
        raise ValueError("AIOS_QUERY_RESPONSE_NOT_OBJECT")

    exists = response.get("repository_answer_exists")
    if not isinstance(exists, bool):
        raise ValueError("AIOS_QUERY_REPOSITORY_ANSWER_FLAG_INVALID")

    expected = ANSWER_KEYS if exists else GAP_KEYS
    if set(response) != expected:
        raise ValueError("AIOS_QUERY_RESPONSE_SCHEMA_INVALID")

    if exists:
        if response["confidence"] not in CONFIDENCE:
            raise ValueError("AIOS_QUERY_CONFIDENCE_INVALID")
        if not isinstance(response["answer_source"], list) or not all(
            isinstance(item, str) and item for item in response["answer_source"]
        ):
            raise ValueError("AIOS_QUERY_ANSWER_SOURCE_INVALID")
        if not isinstance(response["existing_answer"], str) or not response["existing_answer"].strip():
            raise ValueError("AIOS_QUERY_EXISTING_ANSWER_INVALID")
    else:
        if response["knowledge_gap"] not in KNOWLEDGE_GAPS:
            raise ValueError("AIOS_QUERY_KNOWLEDGE_GAP_INVALID")
        if not isinstance(response["missing_evidence_required"], str) or not response[
            "missing_evidence_required"
        ].strip():
            raise ValueError("AIOS_QUERY_MISSING_EVIDENCE_INVALID")

    return dict(response)
