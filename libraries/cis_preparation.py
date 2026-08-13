"""Reusable, sanitized CIS preparation and cleanup component for ETB.

Each public operation performs exactly one CIS clear request. A 404 response
from the approved endpoint is treated as an already-clear, successful state.
Identity values are resolved from local test data and never returned or logged.
"""

from __future__ import annotations

import json
import hashlib
import os
import socket
import ssl
from pathlib import Path
from typing import Any
from urllib.error import HTTPError, URLError
from urllib.request import HTTPSHandler, Request, build_opener
from urllib.parse import urlsplit

from libraries.config_loader import load_yaml

CIS_CLEAR_URL = os.environ.get("CIS_CLEAR_URL", "")
_TIMEOUT_SECONDS = 30


def _transport_category(exc: BaseException) -> str:
    if isinstance(exc, socket.gaierror):
        return "DNS_RESOLUTION_FAILURE"
    if isinstance(exc, (socket.timeout, TimeoutError)):
        return "TIMEOUT"
    if isinstance(exc, ssl.SSLError):
        return "TLS_FAILURE"
    if isinstance(exc, ConnectionRefusedError):
        return "TCP_CONNECTION_FAILURE"
    if isinstance(exc, (ConnectionError, OSError)):
        return "CONNECTION_FAILURE"
    return "OTHER_TRANSPORT_FAILURE"


def probe_cis_transport() -> dict[str, Any]:
    """Check DNS, TCP, and TLS reachability without changing CIS state."""
    if not CIS_CLEAR_URL:
        return {"ready": "NO", "transport_category": "CIS_CLEAR_URL_REQUIRED"}
    endpoint = urlsplit(CIS_CLEAR_URL)
    hostname = endpoint.hostname
    port = endpoint.port or (443 if endpoint.scheme == "https" else 80)
    if not hostname:
        return {"ready": "NO", "transport_category": "OTHER_TRANSPORT_FAILURE"}
    try:
        addresses = socket.getaddrinfo(hostname, port, type=socket.SOCK_STREAM)
    except Exception as exc:
        return {"ready": "NO", "transport_category": _transport_category(exc)}
    if not addresses:
        return {"ready": "NO", "transport_category": "DNS_RESOLUTION_FAILURE"}
    try:
        with socket.create_connection((hostname, port), timeout=_TIMEOUT_SECONDS) as connection:
            if endpoint.scheme == "https":
                ca_bundle = os.environ.get("PDPA_CA_BUNDLE") or os.environ.get("SSL_CERT_FILE")
                context = ssl.create_default_context(cafile=ca_bundle) if ca_bundle else ssl.create_default_context()
                with context.wrap_socket(connection, server_hostname=hostname):
                    pass
    except Exception as exc:
        return {"ready": "NO", "transport_category": _transport_category(exc)}
    return {"ready": "YES", "transport_category": "READY"}
def _write_result(output_dir: str, phase: str, result: dict[str, Any]) -> dict[str, Any]:
    path = Path(output_dir) / f"cis_{phase.lower()}_result.json"
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(result, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    return result


def _resolve_citizen_id(testdata_path: str, case_key: str) -> str:
    data = load_yaml(testdata_path)
    try:
        value = data["profile"]["citizen_id"] if "profile" in data else data["cases"][case_key]["profile"]["citizen_id"]
    except (KeyError, TypeError) as exc:
        raise ValueError("ETB case profile is missing profile.citizen_id") from exc
    if not isinstance(value, str) or not value:
        raise ValueError("ETB case profile.citizen_id must be a non-empty string")
    return value


def _parse_response(raw_body: bytes) -> dict[str, Any]:
    try:
        value = json.loads(raw_body.decode("utf-8"))
    except (UnicodeDecodeError, json.JSONDecodeError):
        return {}
    return value if isinstance(value, dict) else {}


def _response_metadata(http_status: int, headers: Any, raw_body: bytes) -> dict[str, Any]:
    body = _parse_response(raw_body)
    message_text = " ".join(str(body.get(key, "")) for key in ("errorType", "errorMessage", "message", "status")).lower()
    if "not found" in message_text or "not exist" in message_text:
        message_category = "PROFILE_NOT_FOUND"
    elif body.get("errorType"):
        message_category = "ERROR_TYPE_PRESENT"
    elif 200 <= http_status < 300:
        message_category = "SUCCESS_SIGNAL_PRESENT" if body else "EMPTY_SUCCESS_BODY"
    else:
        message_category = "HTTP_ERROR_BODY"
    business_result_code = next(
        (body.get(key) for key in ("resultCode", "code", "status", "httpStatus", "errorType") if body.get(key) is not None),
        None,
    )
    return {
        "http_status": http_status,
        "content_type": headers.get("Content-Type") if headers else None,
        "business_result_code": business_result_code,
        "message_category": message_category,
        "response_body_sha256": hashlib.sha256(raw_body).hexdigest() if raw_body else None,
        "response_structure": {key: type(value).__name__ for key, value in sorted(body.items())},
        "http_status_name": body.get("httpStatus"),
        "error_type": body.get("errorType"),
    }


def _open_default():
    ca_bundle = os.environ.get("PDPA_CA_BUNDLE") or os.environ.get("SSL_CERT_FILE")
    context = ssl.create_default_context(cafile=ca_bundle) if ca_bundle else ssl.create_default_context()
    return build_opener(HTTPSHandler(context=context)).open


def _clear_once(citizen_id: str) -> dict[str, Any]:
    if not CIS_CLEAR_URL:
        return {
            "http_status": None,
            "content_type": None,
            "business_result_code": None,
            "message_category": "CONFIGURATION_FAILURE",
            "response_body_sha256": None,
            "response_structure": None,
            "http_status_name": None,
            "error_type": "CIS_CLEAR_URL_REQUIRED",
        }
    request = Request(
        CIS_CLEAR_URL,
        data=json.dumps({"idNum": citizen_id}).encode("utf-8"),
        headers={"Accept": "application/json", "Content-Type": "application/json"},
        method="DELETE",
    )
    try:
        with _open_default()(request, timeout=_TIMEOUT_SECONDS) as response:
            return _response_metadata(int(response.status), response.headers, response.read())
    except HTTPError as exc:
        return _response_metadata(int(exc.code), exc.headers, exc.read())
    except (URLError, TimeoutError, OSError) as exc:
        return {
            "http_status": None,
            "content_type": None,
            "business_result_code": None,
            "message_category": "TRANSPORT_FAILURE",
            "response_body_sha256": None,
            "response_structure": None,
            "http_status_name": None,
            "error_type": "TRANSPORT_ERROR",
            "transport_category": _transport_category(exc.reason if isinstance(exc, URLError) and exc.reason else exc),
        }


def _clear_state(testdata_path: str, case_key: str, output_dir: str, phase: str) -> dict[str, Any]:
    citizen_id = _resolve_citizen_id(testdata_path, case_key)
    response = _clear_once(citizen_id)
    if response.get("http_status") == 200 and response.get("business_result_code") == "Success":
        normalized = "CLEARED"
    elif response.get("http_status") == 404 and response.get("message_category") == "PROFILE_NOT_FOUND":
        normalized = "ALREADY_CLEARED"
    else:
        normalized = "FAILED"
    result = {
        "phase": phase,
        "cis_clear": "PASS" if normalized in {"CLEARED", "ALREADY_CLEARED"} else "FAIL",
        "cis_clear_result": normalized,
        "cis_state_ready": "YES" if normalized in {"CLEARED", "ALREADY_CLEARED"} else "NO",
        "http_status": response.get("http_status"),
        "content_type": response.get("content_type"),
        "business_result_code": response.get("business_result_code"),
        "message_category": response.get("message_category"),
        "error_type": response.get("error_type"),
        "transport_category": response.get("transport_category"),
        "operation_count": 1,
        "profile_reusable": "YES" if normalized in {"CLEARED", "ALREADY_CLEARED"} else "UNKNOWN",
    }
    return _write_result(output_dir, phase, result)


def prepare_cis_state(testdata_path: str, case_key: str, output_dir: str) -> dict[str, Any]:
    """Clear CIS once before a testcase starts."""
    return _clear_state(testdata_path, case_key, output_dir, "PRE_TEST")


def cleanup_cis_state(testdata_path: str, case_key: str, output_dir: str) -> dict[str, Any]:
    """Clear CIS once after testcase evidence/result capture."""
    return _clear_state(testdata_path, case_key, output_dir, "POST_TEST")
