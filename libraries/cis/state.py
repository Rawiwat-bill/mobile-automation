"""Pure CIS state-result normalization helpers."""

from __future__ import annotations

from typing import Any

MOCK_ENVIRONMENT = "DEV_MOCK"


def mock_result(phase: str) -> dict[str, Any]:
    return {
        "phase": phase,
        "cis_mode": MOCK_ENVIRONMENT,
        "cis_clear": "NOT_APPLICABLE",
        "cis_clear_result": "NOT_REQUIRED",
        "cis_state_ready": "NOT_REQUIRED",
        "message_category": "APPROVED_MOCK_BUILD",
        "http_status": "NOT_ATTEMPTED",
        "transport_category": "NOT_ATTEMPTED",
        "operation_count": 0,
    }


def normalize_clear_response(
    phase: str,
    response: dict[str, Any],
) -> dict[str, Any]:
    """Normalize one CIS clear response into the public lifecycle result shape."""
    if (
        response.get("http_status") == 200
        and response.get("business_result_code") == "Success"
    ):
        normalized = "CLEARED"
    elif (
        response.get("http_status") == 404
        and response.get("message_category") == "PROFILE_NOT_FOUND"
    ):
        normalized = "ALREADY_CLEARED"
    else:
        normalized = "FAILED"

    succeeded = normalized in {"CLEARED", "ALREADY_CLEARED"}
    return {
        "phase": phase,
        "cis_clear": "PASS" if succeeded else "FAIL",
        "cis_clear_result": normalized,
        "cis_state_ready": "YES" if succeeded else "NO",
        "http_status": response.get("http_status"),
        "content_type": response.get("content_type"),
        "business_result_code": response.get("business_result_code"),
        "message_category": response.get("message_category"),
        "error_type": response.get("error_type"),
        "transport_category": response.get("transport_category"),
        "operation_count": 1,
        "profile_reusable": "YES" if succeeded else "UNKNOWN",
    }


def external_preparation_result(
    readiness_status: str,
    *,
    sit_mode: str,
) -> dict[str, Any]:
    return {
        "phase": "PRE_TEST",
        "cis_mode": sit_mode,
        "cis_clear_allowed": "FALSE",
        "cis_clear": "NOT_AUTHORIZED",
        "cis_state_ready": readiness_status,
        "cis_readiness_status": readiness_status,
        "readiness": readiness_status,
        "operation_count": 0,
        "preparation_owner": "EXTERNAL_TEAM",
    }


def external_cleanup_result(*, sit_mode: str) -> dict[str, Any]:
    return {
        "phase": "POST_TEST",
        "cis_mode": sit_mode,
        "cis_clear_allowed": "FALSE",
        "cis_clear": "NOT_ATTEMPTED",
        "post_cis_cleanup_owner": "EXTERNAL_TEAM",
        "post_cis_cleanup_required": "YES",
        "operation_count": 0,
    }
