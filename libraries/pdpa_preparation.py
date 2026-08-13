"""Minimal PDPA Web Forms state-preparation adapter.

The adapter performs transport preparation only. A mobile test must verify that
PDPA is displayed after preparation; HTTP success is never treated as semantic
success.
"""

from __future__ import annotations

import os
import ssl
from html.parser import HTMLParser
from http.cookiejar import CookieJar
from typing import Any, Callable, Mapping
from urllib.error import HTTPError, URLError
from urllib.parse import urlencode, urljoin
from urllib.request import HTTPSHandler, HTTPCookieProcessor, Request, build_opener

from libraries.config_loader import load_yaml as _load_yaml

PDPA_FORM_PATH = "/PDPA_MB/frmIndex"
_FORM_STATE_NAMES = frozenset({"__VIEWSTATE", "__EVENTVALIDATION"})
Transport = Callable[[Request], Any]


class _FormParser(HTMLParser):
    def __init__(self) -> None:
        super().__init__()
        self.form_action = ""
        self.hidden_fields: dict[str, str] = {}
        self.submit_controls: list[dict[str, str]] = []
        self._in_form = False

    def handle_starttag(self, tag: str, attrs: list[tuple[str, str | None]]) -> None:
        values = {key: value or "" for key, value in attrs}
        if tag.lower() == "form":
            self._in_form = True
            self.form_action = values.get("action", "")
        elif self._in_form and tag.lower() == "input":
            name = values.get("name", "")
            input_type = values.get("type", "text").lower()
            if input_type == "hidden" and name:
                self.hidden_fields[name] = values.get("value", "")
            elif input_type in {"submit", "button"}:
                self.submit_controls.append(
                    {"name": name, "value": values.get("value", ""), "id": values.get("id", "")}
                )

    def handle_endtag(self, tag: str) -> None:
        if tag.lower() == "form":
            self._in_form = False


def _parse_form(html: str) -> tuple[str, dict[str, str], list[dict[str, str]]]:
    parser = _FormParser()
    parser.feed(html)
    parser.close()
    return parser.form_action, parser.hidden_fields, parser.submit_controls


def _sanitized_result(
    status: str,
    *,
    http_status: int | None = None,
    form_action: str | None = None,
    clear_control_name: str | None = None,
    post_field_names: list[str] | None = None,
    error: str | None = None,
) -> dict[str, Any]:
    return {
        "status": status,
        "http_status": http_status,
        "form_action": form_action,
        "clear_control_name": clear_control_name,
        "post_field_names": sorted(post_field_names or []),
        "post_count": 1 if status == "CLEAR_REQUEST_SUBMITTED" else 0,
        "semantic_verifiable": False,
        "error": error,
    }


def _open_default() -> Transport:
    # HTTPCookieProcessor preserves the ASP.NET session cookie between GET/POST.
    # urllib's default HTTPS context verifies certificates; no insecure mode is used.
    # PDPA_CA_BUNDLE selects the approved project CA when the system/default store
    # does not contain the internal DEV issuing CA.
    ca_bundle = os.environ.get("PDPA_CA_BUNDLE") or os.environ.get("SSL_CERT_FILE")
    context = ssl.create_default_context(cafile=ca_bundle) if ca_bundle else ssl.create_default_context()
    return build_opener(HTTPCookieProcessor(CookieJar()), HTTPSHandler(context=context)).open


def _read_response(response: Any) -> tuple[int, str]:
    status = int(getattr(response, "status", getattr(response, "code", 0)))
    body = response.read()
    if isinstance(body, bytes):
        body = body.decode("utf-8", errors="replace")
    return status, body


def prepare_pdpa_state(
    document_type: str,
    identity: Mapping[str, str],
    target_state: str = "CLEARED",
    *,
    base_url: str | None = None,
    identity_field: str | None = None,
    document_type_field: str = "documentType",
    clear_control_name: str | None = None,
    form_path: str = PDPA_FORM_PATH,
    opener: Transport | None = None,
) -> dict[str, Any]:
    """Submit one Clear request using fresh ASP.NET form state.

    ``identity`` is a mapping of the field name to the local-only identity
    value. Values are used only in the in-memory request payload and are never
    returned, logged, or written to disk.
    """
    if target_state != "CLEARED":
        return _sanitized_result("FORM_STATE_INVALID", error="unsupported_target_state")
    if not isinstance(identity, Mapping) or not identity or any(not isinstance(k, str) or not k for k in identity):
        return _sanitized_result("FORM_STATE_INVALID", error="identity_field_mapping_required")
    if identity_field is not None and identity_field not in identity:
        return _sanitized_result("FORM_STATE_INVALID", error="identity_field_missing")
    if not document_type or not document_type_field:
        return _sanitized_result("FORM_STATE_INVALID", error="document_type_required")

    base = base_url or os.environ.get("PDPA_BASE_URL", "")
    if not base:
        return _sanitized_result("FORM_STATE_INVALID", error="PDPA_BASE_URL_required")
    form_url = urljoin(base.rstrip("/") + "/", form_path.lstrip("/"))
    transport = opener or _open_default()

    try:
        get_request = Request(form_url, headers={"Accept": "text/html"}, method="GET")
        get_response = transport(get_request)
        get_status, html = _read_response(get_response)
    except (HTTPError, URLError, TimeoutError, OSError):
        return _sanitized_result("CLEAR_TRANSPORT_FAILED")
    if not 200 <= get_status < 300:
        return _sanitized_result("CLEAR_TRANSPORT_FAILED", http_status=get_status)

    action, hidden_fields, submit_controls = _parse_form(html)
    if not _FORM_STATE_NAMES.issubset(hidden_fields):
        return _sanitized_result("FORM_STATE_INVALID", http_status=get_status)
    if not action:
        return _sanitized_result("FORM_STATE_INVALID", http_status=get_status)

    clear = next(
        (
            control
            for control in submit_controls
            if (control["name"] == clear_control_name)
            or ("clear" in control["name"].lower() + " " + control["value"].lower() + " " + control["id"].lower())
        ),
        None,
    )
    if clear is None or not clear["name"]:
        return _sanitized_result("FORM_STATE_INVALID", http_status=get_status)

    fields = dict(hidden_fields)
    fields.update(identity)
    fields[document_type_field] = document_type
    fields[clear["name"]] = clear["value"]
    post_url = urljoin(form_url, action)
    post_request = Request(
        post_url,
        data=urlencode(fields).encode("utf-8"),
        headers={"Accept": "text/html", "Content-Type": "application/x-www-form-urlencoded"},
        method="POST",
    )
    try:
        post_response = transport(post_request)
        post_status, _ = _read_response(post_response)
    except (HTTPError, URLError, TimeoutError, OSError):
        return _sanitized_result("CLEAR_TRANSPORT_FAILED", http_status=get_status, form_action=action, clear_control_name=clear["name"])
    if not 200 <= post_status < 300:
        return _sanitized_result("CLEAR_TRANSPORT_FAILED", http_status=post_status, form_action=action, clear_control_name=clear["name"])
    return _sanitized_result(
        "CLEAR_REQUEST_SUBMITTED",
        http_status=post_status,
        form_action=action,
        clear_control_name=clear["name"],
        post_field_names=list(fields),
    )


def prepare_pdpa_state_from_profile(
    testdata_path: str,
    case_key: str,
    document_type: str = "CI",
    *,
    base_url: str | None = None,
    opener: Transport | None = None,
) -> dict[str, Any]:
    """Resolve one local-only case profile and submit its PDPA Clear request.

    The profile value is never returned or logged. This wrapper keeps identity
    resolution outside Robot argument logging while preserving the generic
    transport function for unit tests and other callers.
    """
    try:
        data = _load_yaml(testdata_path)
        profile = data["cases"][case_key]["profile"]
        identity = {"txtIdNo": profile["citizen_id"]}
    except (KeyError, TypeError, OSError, ValueError):
        return _sanitized_result("FORM_STATE_INVALID", error="local_profile_invalid")
    return prepare_pdpa_state(
        document_type,
        identity,
        base_url=base_url,
        document_type_field="ddlIdType",
        clear_control_name="btnClear",
        opener=opener,
    )
