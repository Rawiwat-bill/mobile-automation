"""Sanitized ETB test-profile teardown client.

The Robot-facing keyword accepts a testdata path, not the identity value. The
identity is resolved through the existing config_loader and never appears in
logs or result artifacts.
"""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any
from urllib.error import HTTPError, URLError
from urllib.request import Request, urlopen

from libraries.config_loader import load_yaml as _approved_load_yaml

_DELETE_URL = "https://blue-engagementservice-dev.azure.test.bbl/qahelper/api/v1/cis/qa/profile/db"
_TIMEOUT_SECONDS = 30
_EXPECTED_NOT_FOUND = {
    "http_status": 404,
    "httpStatus": "NOT_FOUND",
    "errorType": "CustomerProfileNotFoundException",
    "errorMessage": "This CI is not found in CIS DB",
}


def _write_result(output_dir: str, result: dict[str, Any]) -> dict[str, Any]:
    path = Path(output_dir) / "etb_teardown_result.json"
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(result, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    return result


def _resolve_id_num(testdata_path: str) -> str:
    data = _approved_load_yaml(testdata_path)
    try:
        id_num = data["profile"]["citizen_id"]
    except (KeyError, TypeError) as exc:
        raise ValueError("ETB testdata is missing profile.citizen_id") from exc
    if not isinstance(id_num, str) or not id_num:
        raise ValueError("ETB testdata profile.citizen_id must be a non-empty string")
    return id_num


def _parse_json_body(raw_body: bytes) -> dict[str, Any]:
    try:
        value = json.loads(raw_body.decode("utf-8"))
    except (UnicodeDecodeError, json.JSONDecodeError):
        return {}
    return value if isinstance(value, dict) else {}


def _delete_once(id_num: str) -> dict[str, Any]:
    payload = json.dumps({"idNum": id_num}).encode("utf-8")
    request = Request(
        _DELETE_URL,
        data=payload,
        headers={"accept": "application/json", "Content-Type": "application/json"},
        method="DELETE",
    )
    try:
        with urlopen(request, timeout=_TIMEOUT_SECONDS) as response:
            status = int(response.status)
            body = _parse_json_body(response.read())
            return {
                "http_status": status,
                "httpStatus": body.get("httpStatus"),
                "errorType": body.get("errorType"),
                "errorMessage": body.get("errorMessage"),
            }
    except HTTPError as exc:
        body = _parse_json_body(exc.read())
        return {
            "http_status": int(exc.code),
            "httpStatus": body.get("httpStatus"),
            "errorType": body.get("errorType"),
            "errorMessage": body.get("errorMessage"),
        }
    except (URLError, TimeoutError, OSError):
        return {
            "http_status": None,
            "httpStatus": None,
            "errorType": "TRANSPORT_ERROR",
            "errorMessage": None,
        }


def _is_expected_not_found(response: dict[str, Any]) -> bool:
    return all(response.get(key) == value for key, value in _EXPECTED_NOT_FOUND.items())


def _sanitized_response(response: dict[str, Any]) -> dict[str, Any]:
    return {
        "http_status": response.get("http_status"),
        "error_type": response.get("errorType"),
    }


def delete_etb_profile_after_success(testdata_path: str, output_dir: str) -> dict[str, Any]:
    """Delete and idempotently verify an ETB QA profile with at most two calls.

    The caller invokes this keyword only after the verified ETB success
    checkpoint. Raw request/response data remains local to this function and is
    never logged or written to the result artifact.
    """
    id_num = _resolve_id_num(testdata_path)
    first = _delete_once(id_num)
    second = _delete_once(id_num)
    first_expected_absent = _is_expected_not_found(first)
    second_expected_absent = _is_expected_not_found(second)
    first_success = first.get("http_status") is not None and 200 <= first["http_status"] < 300
    verified = (first_success and second_expected_absent) or (first_expected_absent and second_expected_absent)
    result = {
        "etb_teardown": "PASS" if verified else "FAIL",
        "profile_reusable": "YES" if verified else "UNKNOWN",
        "cleanup_state": "ALREADY_ABSENT" if first_expected_absent and verified else "CLEANED_AND_VERIFIED" if verified else "UNKNOWN",
        "cleanup_classification": "SUCCESS_THEN_EXPECTED_NOT_FOUND" if first_success and second_expected_absent else "ALREADY_ABSENT_CONFIRMED" if first_expected_absent and second_expected_absent else "UNEXPECTED_RESPONSE",
        "first_response": _sanitized_response(first),
        "second_response": _sanitized_response(second),
    }
    return _write_result(output_dir, result)
