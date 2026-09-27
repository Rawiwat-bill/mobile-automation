"""Environment-aware, sanitized CIS preparation component for ETB.

DEV retains the existing clear lifecycle. SIT is external-preparation mode:
this module never sends a CIS mutation there. Identity values are resolved from
local test data and are never returned or logged.
"""

from __future__ import annotations

import os
import socket
import ssl
import subprocess
from pathlib import Path
from typing import Any

from libraries.cis import evidence as cis_evidence
from libraries.cis import mock_context as cis_mock
from libraries.cis import readiness as cis_readiness
from libraries.cis import state as cis_state
from libraries.cis import transport as cis_transport
from libraries.config_loader import load_profile as _load_profile
from libraries.config_loader import load_yaml

CIS_CLEAR_URL = os.environ.get("CIS_CLEAR_URL", "")
_TIMEOUT_SECONDS = 30
_PROFILE_NAMES = frozenset({"etb", "ntb_ilove", "ntb_somjai", "ilove", "somjai"})
_SIT_MODE = cis_readiness.SIT_MODE
_STATEFUL_CASE_NUMBERS = cis_readiness.STATEFUL_CASE_NUMBERS
_CIS_READINESS_VERIFIED = cis_readiness.READINESS_VERIFIED
_CIS_READINESS_EXTERNALLY_CONFIRMED = cis_readiness.READINESS_EXTERNALLY_CONFIRMED
_CIS_READINESS_NOT_READY = cis_readiness.READINESS_NOT_READY
_CIS_READINESS_UNKNOWN = cis_readiness.READINESS_UNKNOWN
_MOCK_ENVIRONMENT = cis_mock.MOCK_ENVIRONMENT
_MOCK_SOURCE = cis_mock.MOCK_SOURCE
_MOCK_UDID = cis_mock.MOCK_UDID
_MOCK_AVD = cis_mock.MOCK_AVD
_MOCK_PACKAGE = cis_mock.MOCK_PACKAGE
_MOCK_ACTIVITY = cis_mock.MOCK_ACTIVITY
_MOCK_VERSION_NAME = cis_mock.MOCK_VERSION_NAME
_MOCK_VERSION_CODE = cis_mock.MOCK_VERSION_CODE


def _cis_mode() -> str:
    if os.environ.get("CIS_MODE"):
        return os.environ["CIS_MODE"].upper()
    if os.environ.get("ETB_ENVIRONMENT", "DEV").upper() == "SIT":
        return _SIT_MODE
    return "AUTOMATION"


def validate_mock_build_context() -> None:
    """Reject mock CIS mode unless the approved local build is installed."""
    cis_mock.validate_mock_build_context(
        os.environ.get("ETB_ENVIRONMENT", ""),
        os.environ.get("CIS_READINESS_SOURCE"),
        os.environ.get("DEVICE_UDID"),
        run_command=subprocess.run,
    )


def _mock_cis_result(phase: str) -> dict[str, Any]:
    return cis_state.mock_result(phase)


def _cis_readiness_status() -> str:
    """Resolve non-mutating SIT readiness metadata into an explicit state."""
    return cis_readiness.readiness_status(
        os.environ.get("CIS_READINESS_SOURCE"),
        os.environ.get("CIS_READY"),
    )


def _selected_case_testcase_id(testdata_path: str, case_key: str) -> str | None:
    """Resolve a case key to its non-sensitive testcase ID without logging data."""
    try:
        case = _load_cases(testdata_path).get(case_key, {})
    except (OSError, TypeError, ValueError):
        return None
    testcase_id = case.get("tc_id")
    return testcase_id if isinstance(testcase_id, str) else None


def _transport_category(exc: BaseException) -> str:
    return cis_transport.transport_category(exc)

def probe_cis_transport() -> dict[str, Any]:
    """Check DNS, TCP, and TLS reachability without changing CIS state."""
    ca_bundle = os.environ.get("PDPA_CA_BUNDLE") or os.environ.get("SSL_CERT_FILE")
    return cis_transport.probe(
        CIS_CLEAR_URL,
        _TIMEOUT_SECONDS,
        ca_bundle=ca_bundle,
        getaddrinfo=socket.getaddrinfo,
        create_connection=socket.create_connection,
        create_default_context=ssl.create_default_context,
    )

def _write_result(
    output_dir: str,
    phase: str,
    result: dict[str, Any],
) -> dict[str, Any]:
    return cis_evidence.write_lifecycle_result(output_dir, phase, result)


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
    return cis_readiness.case_number(tc_id)


def _dependency_class(tc_id: str, case: dict[str, Any]) -> tuple[str, str]:
    return cis_readiness.dependency_class(tc_id, case)


def audit_cis_profiles(
    testdata_path: str,
    output_dir: str,
    selected_case_id: str | None = None,
) -> dict[str, Any]:
    """Write sanitized CIS profile-dependency evidence from pure readiness policy."""
    cases = _load_cases(testdata_path)
    contract_cases = _load_contract_cases(testdata_path)
    result, preparation, post_manifest = cis_readiness.build_profile_audit(
        cases,
        contract_cases,
        selected_case_id,
    )
    cis_evidence.write_profile_audit(
        output_dir,
        result,
        preparation,
        post_manifest,
    )
    return result


def verify_external_cis_readiness(
    testdata_path: str,
    output_dir: str,
    selected_case_id: str | None = None,
) -> dict[str, Any]:
    """Evaluate SIT readiness metadata without reading or mutating CIS state."""
    matrix = audit_cis_profiles(testdata_path, output_dir, selected_case_id)
    result = cis_readiness.build_external_readiness(
        matrix,
        _cis_readiness_status(),
        selected_case_id,
    )
    if result["full_runtime_gate"] != "OPEN":
        cis_evidence.write_readiness_result(output_dir, result)
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
    return cis_transport.parse_response(raw_body)

def _response_metadata(http_status: int, headers: Any, raw_body: bytes) -> dict[str, Any]:
    return cis_transport.response_metadata(http_status, headers, raw_body)

def _open_default():
    ca_bundle = os.environ.get("PDPA_CA_BUNDLE") or os.environ.get("SSL_CERT_FILE")
    return cis_transport.open_default(
        ca_bundle=ca_bundle,
        create_default_context=ssl.create_default_context,
    )

def _clear_once(citizen_id: str) -> dict[str, Any]:
    return cis_transport.clear_once(
        citizen_id,
        url=CIS_CLEAR_URL,
        timeout_seconds=_TIMEOUT_SECONDS,
        opener=_open_default(),
        classify_transport=_transport_category,
    )

def _clear_state(
    testdata_path: str,
    case_key: str,
    output_dir: str,
    phase: str,
) -> dict[str, Any]:
    citizen_id = _resolve_citizen_id(testdata_path, case_key)
    response = _clear_once(citizen_id)
    result = cis_state.normalize_clear_response(phase, response)
    return _write_result(output_dir, phase, result)


def prepare_cis_state(
    testdata_path: str,
    case_key: str,
    output_dir: str,
) -> dict[str, Any]:
    """Prepare CIS for one testcase without mutating SIT."""
    if os.environ.get("ETB_ENVIRONMENT", "").upper() == _MOCK_ENVIRONMENT:
        validate_mock_build_context()
        return _write_result(output_dir, "PRE_TEST", _mock_cis_result("PRE_TEST"))
    if _cis_mode() == _SIT_MODE:
        readiness_status = _cis_readiness_status()
        result = cis_state.external_preparation_result(
            readiness_status,
            sit_mode=_SIT_MODE,
        )
        # Do not persist owner-provided readiness metadata in a runtime report.
        return (
            result
            if readiness_status == _CIS_READINESS_EXTERNALLY_CONFIRMED
            else _write_result(output_dir, "PRE_TEST", result)
        )
    return _clear_state(testdata_path, case_key, output_dir, "PRE_TEST")


def cleanup_cis_state(
    testdata_path: str,
    case_key: str,
    output_dir: str,
) -> dict[str, Any]:
    """Clean up CIS in DEV; record external ownership in SIT."""
    if os.environ.get("ETB_ENVIRONMENT", "").upper() == _MOCK_ENVIRONMENT:
        validate_mock_build_context()
        return _write_result(output_dir, "POST_TEST", _mock_cis_result("POST_TEST"))
    if _cis_mode() == _SIT_MODE:
        return _write_result(
            output_dir,
            "POST_TEST",
            cis_state.external_cleanup_result(sit_mode=_SIT_MODE),
        )
    return _clear_state(testdata_path, case_key, output_dir, "POST_TEST")
