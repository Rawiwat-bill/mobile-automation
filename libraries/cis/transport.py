"""Pure CIS transport and HTTP-response normalization helpers."""

from __future__ import annotations

import hashlib
import json
import socket
import ssl
from typing import Any, Callable
from urllib.error import HTTPError, URLError
from urllib.parse import urlsplit
from urllib.request import HTTPSHandler, Request, build_opener


def transport_category(exc: BaseException) -> str:
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


def probe(
    url: str,
    timeout_seconds: int,
    *,
    ca_bundle: str | None,
    getaddrinfo: Callable[..., Any],
    create_connection: Callable[..., Any],
    create_default_context: Callable[..., Any],
) -> dict[str, Any]:
    """Check DNS, TCP, and TLS reachability without changing CIS state."""
    if not url:
        return {"ready": "NO", "transport_category": "CIS_CLEAR_URL_REQUIRED"}
    endpoint = urlsplit(url)
    hostname = endpoint.hostname
    port = endpoint.port or (443 if endpoint.scheme == "https" else 80)
    if not hostname:
        return {"ready": "NO", "transport_category": "OTHER_TRANSPORT_FAILURE"}
    try:
        addresses = getaddrinfo(hostname, port, type=socket.SOCK_STREAM)
    except Exception as exc:
        return {"ready": "NO", "transport_category": transport_category(exc)}
    if not addresses:
        return {"ready": "NO", "transport_category": "DNS_RESOLUTION_FAILURE"}
    try:
        with create_connection((hostname, port), timeout=timeout_seconds) as connection:
            if endpoint.scheme == "https":
                context = (
                    create_default_context(cafile=ca_bundle)
                    if ca_bundle
                    else create_default_context()
                )
                with context.wrap_socket(connection, server_hostname=hostname):
                    pass
    except Exception as exc:
        return {"ready": "NO", "transport_category": transport_category(exc)}
    return {"ready": "YES", "transport_category": "READY"}


def parse_response(raw_body: bytes) -> dict[str, Any]:
    try:
        value = json.loads(raw_body.decode("utf-8"))
    except (UnicodeDecodeError, json.JSONDecodeError):
        return {}
    return value if isinstance(value, dict) else {}


def response_metadata(http_status: int, headers: Any, raw_body: bytes) -> dict[str, Any]:
    body = parse_response(raw_body)
    message_text = " ".join(
        str(body.get(key, ""))
        for key in ("errorType", "errorMessage", "message", "status")
    ).lower()
    if "not found" in message_text or "not exist" in message_text:
        message_category = "PROFILE_NOT_FOUND"
    elif body.get("errorType"):
        message_category = "ERROR_TYPE_PRESENT"
    elif 200 <= http_status < 300:
        message_category = "SUCCESS_SIGNAL_PRESENT" if body else "EMPTY_SUCCESS_BODY"
    else:
        message_category = "HTTP_ERROR_BODY"
    business_result_code = next(
        (
            body.get(key)
            for key in ("resultCode", "code", "status", "httpStatus", "errorType")
            if body.get(key) is not None
        ),
        None,
    )
    return {
        "http_status": http_status,
        "content_type": headers.get("Content-Type") if headers else None,
        "business_result_code": business_result_code,
        "message_category": message_category,
        "response_body_sha256": hashlib.sha256(raw_body).hexdigest() if raw_body else None,
        "response_structure": {
            key: type(value).__name__ for key, value in sorted(body.items())
        },
        "http_status_name": body.get("httpStatus"),
        "error_type": body.get("errorType"),
    }


def open_default(
    *,
    ca_bundle: str | None,
    create_default_context: Callable[..., Any],
):
    context = (
        create_default_context(cafile=ca_bundle)
        if ca_bundle
        else create_default_context()
    )
    return build_opener(HTTPSHandler(context=context)).open


def clear_once(
    citizen_id: str,
    *,
    url: str,
    timeout_seconds: int,
    opener: Callable[..., Any],
    classify_transport: Callable[[BaseException], str],
) -> dict[str, Any]:
    if not url:
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
        url,
        data=json.dumps({"idNum": citizen_id}).encode("utf-8"),
        headers={"Accept": "application/json", "Content-Type": "application/json"},
        method="DELETE",
    )
    try:
        with opener(request, timeout=timeout_seconds) as response:
            return response_metadata(int(response.status), response.headers, response.read())
    except HTTPError as exc:
        return response_metadata(int(exc.code), exc.headers, exc.read())
    except (URLError, TimeoutError, OSError) as exc:
        cause = exc.reason if isinstance(exc, URLError) and exc.reason else exc
        return {
            "http_status": None,
            "content_type": None,
            "business_result_code": None,
            "message_category": "TRANSPORT_FAILURE",
            "response_body_sha256": None,
            "response_structure": None,
            "http_status_name": None,
            "error_type": "TRANSPORT_ERROR",
            "transport_category": classify_transport(cause),
        }
