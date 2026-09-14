"""Environment-aware, sanitized CIS preparation component for ETB.

DEV retains the existing clear lifecycle. SIT is external-preparation mode:
this module never sends a CIS mutation there. Identity values are resolved from
local test data and are never returned or logged.
"""

from __future__ import annotations

import json
import hashlib
import os
import re
import socket
import ssl
import subprocess
from pathlib import Path
from typing import Any
from urllib.error import HTTPError, URLError
from urllib.request import HTTPSHandler, Request, build_opener
from urllib.parse import urlsplit

from libraries.config_loader import load_profile as _load_profile
from libraries.config_loader import load_yaml
from libraries.evidence_scope import resolve_scoped_output_dir

CIS_CLEAR_URL = os.environ.get("CIS_CLEAR_URL", "")
_TIMEOUT_SECONDS = 30
_PROFILE_NAMES = frozenset({"etb", "ntb_ilove", "ntb_somjai", "ilove", "somjai"})
_SIT_MODE = "EXTERNAL_PREPARED"
_STATEFUL_CASE_NUMBERS = frozenset({1, 2, 3, 4})
_CIS_READINESS_VERIFIED = "VERIFIED"
_CIS_READINESS_EXTERNALLY_CONFIRMED = "EXTERNALLY_CONFIRMED"
_CIS_READINESS_NOT_READY = "NOT_READY"
_CIS_READINESS_UNKNOWN = "UNKNOWN"
_MOCK_ENVIRONMENT = "DEV_MOCK"
_MOCK_SOURCE = "MOCK_BUILD_NOT_REQUIRED"
_MOCK_UDID = "emulator-5558"
_MOCK_AVD = "Pixel_10"
_MOCK_PACKAGE = "com.bangkokbank.blue.dev"
_MOCK_ACTIVITY = "com.bangkokbank.blue.MainActivity"
_MOCK_VERSION_NAME = "1.13.0-alpha-93-146-Unshield"
_MOCK_VERSION_CODE = "146"


def _cis_mode() -> str:
    if os.environ.get("CIS_MODE"):
        return os.environ["CIS_MODE"].upper()
    if os.environ.get("ETB_ENVIRONMENT", "DEV").upper() == "SIT":
        return _SIT_MODE
    return "AUTOMATION"


def validate_mock_build_context() -> None:
    """Reject mock CIS mode unless the approved local build is installed."""
    if os.environ.get("ETB_ENVIRONMENT", "").upper() != _MOCK_ENVIRONMENT:
        raise ValueError("MOCK_CIS_INVALID_ENVIRONMENT")
    if os.environ.get("CIS_READINESS_SOURCE") != _MOCK_SOURCE:
        raise ValueError("MOCK_CIS_SOURCE_REQUIRED")
    if os.environ.get("DEVICE_UDID") != _MOCK_UDID:
        raise ValueError("MOCK_CIS_INVALID_DEVICE")

    def adb(*args: str) -> str:
        result = subprocess.run(
            ["adb", "-s", _MOCK_UDID, *args],
            check=True,
            capture_output=True,
            text=True,
            timeout=10,
        )
        return result.stdout.replace("\r", "")

    try:
        avd = adb("shell", "getprop", "ro.boot.qemu.avd_name").strip()
        package_path = adb("shell", "pm", "path", _MOCK_PACKAGE).strip()
        package = adb("shell", "dumpsys", "package", _MOCK_PACKAGE)
        activity = adb(
            "shell", "cmd", "package", "resolve-activity", "--brief",
            "-a", "android.intent.action.MAIN", "-c", "android.intent.category.LAUNCHER",
            _MOCK_PACKAGE,
        ).strip().splitlines()[-1]
    except (OSError, subprocess.SubprocessError, IndexError) as exc:
        raise ValueError("MOCK_CIS_CONTEXT_UNAVAILABLE") from exc

    if not package_path.startswith("package:"):
        raise ValueError("MOCK_CIS_INVALID_PACKAGE")
    version_name = re.search(r"versionName=([^\s]+)", package)
    version_code = re.search(r"versionCode=([^\s]+)", package)
    if avd != _MOCK_AVD:
        raise ValueError("MOCK_CIS_INVALID_AVD")
    if not version_name or version_name.group(1) != _MOCK_VERSION_NAME:
        raise ValueError("MOCK_CIS_INVALID_VERSION_NAME")
    if not version_code or version_code.group(1) != _MOCK_VERSION_CODE:
        raise ValueError("MOCK_CIS_INVALID_VERSION_CODE")
    if activity != f"{_MOCK_PACKAGE}/{_MOCK_ACTIVITY}":
        raise ValueError("MOCK_CIS_INVALID_ACTIVITY")


def _mock_cis_result(phase: str) -> dict[str, Any]:
    return {
        "phase": phase,
        "cis_mode": _MOCK_ENVIRONMENT,
        "cis_clear": "NOT_APPLICABLE",
        "cis_clear_result": "NOT_REQUIRED",
        "cis_state_ready": "NOT_REQUIRED",
        "message_category": "APPROVED_MOCK_BUILD",
        "http_status": "NOT_ATTEMPTED",
        "transport_category": "NOT_ATTEMPTED",
        "operation_count": 0,
    }


def _cis_readiness_status() -> str:
    """Resolve non-mutating SIT readiness metadata into an explicit state."""
    source = os.environ.get("CIS_READINESS_SOURCE")
    if source == "EXTERNAL_TEAM_CONFIRMATION":
        if os.environ.get("CIS_READY") == "EXTERNALLY_CONFIRMED":
            return _CIS_READINESS_EXTERNALLY_CONFIRMED
        return _CIS_READINESS_NOT_READY
    return _CIS_READINESS_UNKNOWN


def _selected_case_testcase_id(testdata_path: str, case_key: str) -> str | None:
    """Resolve a case key to its non-sensitive testcase ID without logging data."""
    try:
        case = _load_cases(testdata_path).get(case_key, {})
    except (OSError, TypeError, ValueError):
        return None
    testcase_id = case.get("tc_id")
    return testcase_id if isinstance(testcase_id, str) else None


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
    path = Path(resolve_scoped_output_dir(output_dir)) / f"cis_{phase.lower()}_result.json"
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(result, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    return result


def _load_cases(testdata_path: str) -> dict[str, Any]:
    data = load_yaml(testdata_path)
    cases = data.get("cases")
    if not isinstance(cases, dict):
        raise ValueError("ETB case profiles must contain cases")
    return cases


def _load_contract_cases(testdata_path: str) -> dict[str, Any]:
    """Load non-sensitive case boundaries alongside local-only profiles."""
    configured = os.environ.get("CIS_CASE_CONTRACT")
    candidate = Path(configured) if configured else Path(testdata_path).with_name("etb_cases.yaml")
    if not candidate.is_file():
        return {}
    return _load_cases(str(candidate))


def _case_number(tc_id: str) -> int | None:
    try:
        return int(tc_id.rsplit("-", 1)[1])
    except (IndexError, ValueError):
        return None


def _dependency_class(tc_id: str, case: dict[str, Any]) -> tuple[str, str]:
    """Classify CIS dependency from the case boundary, not profile reuse."""
    if _case_number(tc_id) in _STATEFUL_CASE_NUMBERS:
        return "STATEFUL_PROFILE_REQUIRED", "YES"
    terminal_state = str(case.get("terminal_state", "")).lower()
    if terminal_state in {"popup closed", "app closed"}:
        return "NEGATIVE_FLOW_REUSABLE_PROFILE", "NO"
    return "NEGATIVE_FLOW_REUSABLE_PROFILE", "UNKNOWN"


def audit_cis_profiles(
    testdata_path: str,
    output_dir: str,
    selected_case_id: str | None = None,
) -> dict[str, Any]:
    """Write a sanitized CIS matrix separating stateful and negative flows."""
    cases = _load_cases(testdata_path)
    contract_cases = _load_contract_cases(testdata_path)
    ordered = sorted(
        ((str(case.get("tc_id", "")), key, case) for key, case in cases.items()),
        key=lambda item: item[0],
    )
    if selected_case_id is not None:
        ordered = [item for item in ordered if item[0] == selected_case_id]
        if not ordered:
            raise ValueError(f"Selected ETB testcase is not present in CIS case data: {selected_case_id}")
    groups: dict[str, str] = {}
    aliases: dict[str, list[str]] = {}
    case_metadata: dict[str, dict[str, str]] = {}
    for tc_id, case_key, case in ordered:
        identity = case.get("profile", {}).get("citizen_id")
        if not isinstance(identity, str) or not identity:
            raise ValueError(f"Missing local CIS identity for {tc_id or 'case'}")
        group = groups.setdefault(identity, f"PROFILE_GROUP_{len(groups) + 1:02d}")
        aliases.setdefault(group, []).append(tc_id)
        dependency_case = contract_cases.get(case_key, case)
        dependency_class, persistent_mutation = _dependency_class(tc_id, dependency_case)
        case_metadata[tc_id] = {
            "cis_dependency": dependency_class,
            "persistent_mutation": persistent_mutation,
        }
    matrix = {tc_id: groups[case["profile"]["citizen_id"]] for tc_id, _, case in ordered}
    shared = {group: testcases for group, testcases in aliases.items() if len(testcases) > 1}
    stateful_groups = sorted({matrix[tc_id] for tc_id, metadata in case_metadata.items() if metadata["cis_dependency"] == "STATEFUL_PROFILE_REQUIRED"})
    negative_groups = sorted({matrix[tc_id] for tc_id, metadata in case_metadata.items() if metadata["cis_dependency"] == "NEGATIVE_FLOW_REUSABLE_PROFILE"})
    shared_profile_safe = {
        group: "YES" if all(case_metadata[tc_id]["persistent_mutation"] == "NO" for tc_id in testcases) else "NO"
        for group, testcases in shared.items()
    }
    one_pass_compatible = all(value == "YES" for value in shared_profile_safe.values())
    result = {
        "total_cases": len(matrix),
        "unique_profile_groups": len(aliases),
        "shared_profile_groups": len(shared),
        "testcase_to_profile_group": matrix,
        "shared_groups": shared,
        "case_dependencies": {tc_id: {"profile_group": matrix[tc_id], **metadata} for tc_id, metadata in case_metadata.items()},
        "shared_profile_safe_for_reuse": shared_profile_safe,
        "stateful_profile_groups": stateful_groups,
        "negative_reusable_profile_groups": negative_groups,
        "one_pass_external_preparation_compatible": "YES" if one_pass_compatible else "NO",
        "external_preparation_required": "YES",
        "external_cis_profile_count": len(stateful_groups),
        "tc002_readiness": {
            "cis_preparation": "EXTERNAL_TEAM_REQUIRED",
            "pdpa_preparation": "APPROVED_SHARED_ADAPTER_READY",
            "tc002_runtime": "READY_AFTER_EXTERNAL_CIS_CONFIRMATION",
        },
        "pdpa_preparation_policy": {
            "owner": "AUTOMATION",
            "environment_scope": "DEV_AND_SIT",
            "adapter_status": "APPROVED_SHARED_ADAPTER_READY",
        },
    }
    output = Path(output_dir)
    output.mkdir(parents=True, exist_ok=True)
    (output / "cis_profile_dependency_matrix.json").write_text(json.dumps(result, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    preparation = {
        "external_cis_preparation_required": "YES",
        "profiles": [
            {
                "testcase_id": tc_id,
                "profile_group": group,
                "required_action": "CLEAR_CIS" if case_metadata[tc_id]["cis_dependency"] == "STATEFUL_PROFILE_REQUIRED" else "REUSE_NEGATIVE_FLOW_PROFILE",
                "cis_dependency": case_metadata[tc_id]["cis_dependency"],
                "persistent_mutation": case_metadata[tc_id]["persistent_mutation"],
            }
            for tc_id, group in matrix.items()
        ],
        "shared_profile_warning": shared,
        "shared_profile_safe_for_reuse": shared_profile_safe,
        "cleanup_owner": "EXTERNAL_TEAM",
    }
    (output / "external_cis_preparation_manifest.json").write_text(json.dumps(preparation, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    post_manifest = {
        "post_run_external_cis_cleanup_required": "YES",
        "profiles": [
            {"testcase_id": tc_id, "profile_group": group}
            for tc_id, group in matrix.items()
            if case_metadata[tc_id]["cis_dependency"] == "STATEFUL_PROFILE_REQUIRED"
        ],
        "cleanup_owner": "EXTERNAL_TEAM",
    }
    (output / "external_cis_post_run_cleanup_manifest.json").write_text(json.dumps(post_manifest, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    return result


def verify_external_cis_readiness(
    testdata_path: str,
    output_dir: str,
    selected_case_id: str | None = None,
) -> dict[str, Any]:
    """Evaluate SIT readiness metadata without reading or mutating CIS state."""
    matrix = audit_cis_profiles(testdata_path, output_dir, selected_case_id)
    required_groups = matrix["stateful_profile_groups"]
    readiness_status = _cis_readiness_status()
    runtime_allowed = readiness_status in {
        _CIS_READINESS_VERIFIED,
        _CIS_READINESS_EXTERNALLY_CONFIRMED,
    }
    result = {
        "cis_mode": _SIT_MODE,
        "cis_readiness_status": readiness_status,
        "read_only_cis_verification_capability": "EXTERNAL_TEAM_CONFIRMATION" if readiness_status == _CIS_READINESS_EXTERNALLY_CONFIRMED else "NOT_CONFIGURED",
        "gate_decision": "EXTERNAL_TEAM_CONFIRMATION_ACCEPTED" if runtime_allowed else "SIT_CIS_EXTERNAL_CONFIRMATION_REQUIRED",
        "selected_testcase": selected_case_id or "ALL_ETB_CASES",
        "profiles": [
            {"profile_group": group, "cis_ready": readiness_status}
            for group in required_groups
        ],
        "negative_reusable_profile_groups": matrix["negative_reusable_profile_groups"],
        "all_required_cis_ready": "YES" if runtime_allowed else ("NO" if required_groups else "YES"),
        "full_runtime_gate": "OPEN" if runtime_allowed else "CLOSED",
    }
    if not runtime_allowed:
        Path(output_dir, "cis_readiness_result.json").write_text(json.dumps(result, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    return result


def _resolve_citizen_id(testdata_path: str, case_key: str) -> str:
    data = _load_profile(testdata_path) if testdata_path in _PROFILE_NAMES else load_yaml(testdata_path)
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
    """Prepare CIS for one testcase without mutating SIT."""
    if os.environ.get("ETB_ENVIRONMENT", "").upper() == _MOCK_ENVIRONMENT:
        validate_mock_build_context()
        return _write_result(output_dir, "PRE_TEST", _mock_cis_result("PRE_TEST"))
    if _cis_mode() == _SIT_MODE:
        readiness_status = _cis_readiness_status()
        result = {
            "phase": "PRE_TEST", "cis_mode": _SIT_MODE, "cis_clear_allowed": "FALSE",
            "cis_clear": "NOT_AUTHORIZED", "cis_state_ready": readiness_status,
            "cis_readiness_status": readiness_status, "readiness": readiness_status,
            "operation_count": 0,
            "preparation_owner": "EXTERNAL_TEAM",
        }
        # Do not persist owner-provided readiness metadata in a runtime report.
        return result if readiness_status == _CIS_READINESS_EXTERNALLY_CONFIRMED else _write_result(output_dir, "PRE_TEST", result)
    return _clear_state(testdata_path, case_key, output_dir, "PRE_TEST")


def cleanup_cis_state(testdata_path: str, case_key: str, output_dir: str) -> dict[str, Any]:
    """Clean up CIS in DEV; record external ownership in SIT."""
    if os.environ.get("ETB_ENVIRONMENT", "").upper() == _MOCK_ENVIRONMENT:
        validate_mock_build_context()
        return _write_result(output_dir, "POST_TEST", _mock_cis_result("POST_TEST"))
    if _cis_mode() == _SIT_MODE:
        return _write_result(output_dir, "POST_TEST", {
            "phase": "POST_TEST", "cis_mode": _SIT_MODE, "cis_clear_allowed": "FALSE",
            "cis_clear": "NOT_ATTEMPTED", "post_cis_cleanup_owner": "EXTERNAL_TEAM",
            "post_cis_cleanup_required": "YES", "operation_count": 0,
        })
    return _clear_state(testdata_path, case_key, output_dir, "POST_TEST")
