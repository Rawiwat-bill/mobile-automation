from __future__ import annotations

import tempfile
import unittest
import json
import os
import socket
import ssl
import subprocess
from pathlib import Path
from unittest.mock import patch
from urllib.error import URLError

from libraries.cis_preparation import (
    _clear_once,
    cleanup_cis_state,
    prepare_cis_state,
    probe_cis_transport,
    validate_mock_build_context,
    verify_external_cis_readiness,
)


class _Response:
    status = 200
    headers = {"Content-Type": "application/json"}

    def __enter__(self):
        return self

    def __exit__(self, *args):
        return False

    def read(self):
        return b'{"status":"Success"}'


class CisPreparationTests(unittest.TestCase):
    def setUp(self) -> None:
        self.tempdir = tempfile.TemporaryDirectory(prefix="cis-preparation-")
        self.data = Path(self.tempdir.name) / "cases.yaml"
        self.data.write_text(
            "cases:\n  etb_tc_001:\n    profile:\n      citizen_id: MASKED_ID\n",
            encoding="utf-8",
        )

    def tearDown(self) -> None:
        self.tempdir.cleanup()

    def _mock_adb_run(self, command, **kwargs):
        if command[-3:] == ["shell", "getprop", "ro.boot.qemu.avd_name"]:
            stdout = "Pixel_10\n"
        elif command[-3:] == ["pm", "path", "com.bangkokbank.blue.dev"]:
            stdout = "package:/data/app/mock/base.apk\n"
        elif command[-3:] == ["dumpsys", "package", "com.bangkokbank.blue.dev"]:
            stdout = "versionName=1.13.0-alpha-93-146-Unshield versionCode=146\n"
        elif "resolve-activity" in command:
            stdout = "com.bangkokbank.blue.dev/com.bangkokbank.blue.MainActivity\n"
        else:
            raise AssertionError(command)
        return subprocess.CompletedProcess(command, 0, stdout=stdout, stderr="")

    def test_exact_mock_context_is_not_applicable_and_makes_no_http_call(self) -> None:
        with patch.dict(os.environ, {
            "ETB_ENVIRONMENT": "DEV_MOCK",
            "CIS_READINESS_SOURCE": "MOCK_BUILD_NOT_REQUIRED",
            "DEVICE_UDID": "emulator-5558",
        }, clear=True), patch("libraries.cis_preparation.subprocess.run", side_effect=self._mock_adb_run), patch(
            "libraries.cis_preparation._clear_once"
        ) as clear:
            result = prepare_cis_state("does-not-exist.yaml", "etb_tc_001", self.tempdir.name)
        clear.assert_not_called()
        self.assertEqual(result["cis_clear"], "NOT_APPLICABLE")
        self.assertEqual(result["cis_state_ready"], "NOT_REQUIRED")
        self.assertEqual(result["message_category"], "APPROVED_MOCK_BUILD")
        self.assertEqual(result["http_status"], "NOT_ATTEMPTED")
        self.assertEqual(result["transport_category"], "NOT_ATTEMPTED")
        self.assertEqual(result["operation_count"], 0)

    def test_mock_context_rejects_wrong_version(self) -> None:
        def wrong_version(command, **kwargs):
            result = self._mock_adb_run(command, **kwargs)
            if command[-3:] == ["dumpsys", "package", "com.bangkokbank.blue.dev"]:
                result.stdout = "versionName=canonical-dev versionCode=144\n"
            return result

        with patch.dict(os.environ, {
            "ETB_ENVIRONMENT": "DEV_MOCK",
            "CIS_READINESS_SOURCE": "MOCK_BUILD_NOT_REQUIRED",
            "DEVICE_UDID": "emulator-5558",
        }, clear=True), patch("libraries.cis_preparation.subprocess.run", side_effect=wrong_version):
            with self.assertRaisesRegex(ValueError, "MOCK_CIS_INVALID_VERSION_NAME"):
                validate_mock_build_context()

    def test_mock_context_rejects_wrong_package(self) -> None:
        def missing_package(command, **kwargs):
            if command[-3:] == ["pm", "path", "com.bangkokbank.blue.dev"]:
                return subprocess.CompletedProcess(command, 0, stdout="", stderr="")
            return self._mock_adb_run(command, **kwargs)

        with patch.dict(os.environ, {
            "ETB_ENVIRONMENT": "DEV_MOCK",
            "CIS_READINESS_SOURCE": "MOCK_BUILD_NOT_REQUIRED",
            "DEVICE_UDID": "emulator-5558",
        }, clear=True), patch("libraries.cis_preparation.subprocess.run", side_effect=missing_package):
            with self.assertRaisesRegex(ValueError, "MOCK_CIS_INVALID_PACKAGE"):
                validate_mock_build_context()

    def test_mock_context_rejects_wrong_device(self) -> None:
        with patch.dict(os.environ, {
            "ETB_ENVIRONMENT": "DEV_MOCK",
            "CIS_READINESS_SOURCE": "MOCK_BUILD_NOT_REQUIRED",
            "DEVICE_UDID": "emulator-5554",
        }, clear=True):
            with self.assertRaisesRegex(ValueError, "MOCK_CIS_INVALID_DEVICE"):
                validate_mock_build_context()

    def test_mock_context_rejects_missing_source(self) -> None:
        with patch.dict(os.environ, {
            "ETB_ENVIRONMENT": "DEV_MOCK",
            "DEVICE_UDID": "emulator-5558",
        }, clear=True):
            with self.assertRaisesRegex(ValueError, "MOCK_CIS_SOURCE_REQUIRED"):
                validate_mock_build_context()

    def test_200_normalizes_to_cleared_and_makes_one_call(self) -> None:
        response = {
            "http_status": 200,
            "content_type": "application/json",
            "business_result_code": "Success",
            "message_category": "SUCCESS_SIGNAL_PRESENT",
            "error_type": None,
        }
        with patch("libraries.cis_preparation._clear_once", return_value=response) as clear:
            result = prepare_cis_state(str(self.data), "etb_tc_001", self.tempdir.name)
        clear.assert_called_once()
        self.assertEqual(result["cis_clear"], "PASS")
        self.assertEqual(result["cis_clear_result"], "CLEARED")
        self.assertEqual(result["cis_state_ready"], "YES")
        self.assertEqual(result["operation_count"], 1)
        self.assertNotIn("MASKED_ID", repr(result))
        self.assertEqual((Path(self.tempdir.name) / "cis_pre_test_result.json").is_file(), True)

    def test_approved_profile_name_resolves_without_filesystem_path(self) -> None:
        response = {
            "http_status": 200,
            "content_type": "application/json",
            "business_result_code": "Success",
            "message_category": "SUCCESS_SIGNAL_PRESENT",
            "error_type": None,
        }
        synthetic_profile = {"profile": {"citizen_id": "SYNTHETIC_CIS_ID"}}
        with patch(
            "libraries.cis_preparation._load_profile", return_value=synthetic_profile
        ) as load_profile, patch(
            "libraries.cis_preparation._clear_once", return_value=response
        ) as clear:
            result = prepare_cis_state("etb", "", self.tempdir.name)
        load_profile.assert_called_once_with("etb")
        clear.assert_called_once_with("SYNTHETIC_CIS_ID")
        self.assertEqual(result["cis_clear"], "PASS")
        self.assertEqual(result["cis_clear_result"], "CLEARED")

    def test_proven_profile_not_found_404_normalizes_to_already_cleared(self) -> None:
        response = {
            "http_status": 404,
            "business_result_code": "NOT_FOUND",
            "message_category": "PROFILE_NOT_FOUND",
            "error_type": "CustomerProfileNotFoundException",
        }
        with patch("libraries.cis_preparation._clear_once", return_value=response) as clear:
            result = cleanup_cis_state(str(self.data), "etb_tc_001", self.tempdir.name)
        clear.assert_called_once()
        self.assertEqual(result["cis_clear"], "PASS")
        self.assertEqual(result["cis_clear_result"], "ALREADY_CLEARED")
        self.assertEqual(result["cis_state_ready"], "YES")
        self.assertEqual(result["phase"], "POST_TEST")

    def test_500_normalizes_to_failed(self) -> None:
        response = {
            "http_status": 500,
            "business_result_code": "INTERNAL_SERVER_ERROR",
            "message_category": "HTTP_ERROR_BODY",
            "error_type": "InternalServerError",
        }
        with patch("libraries.cis_preparation._clear_once", return_value=response) as clear:
            result = prepare_cis_state(str(self.data), "etb_tc_001", self.tempdir.name)
        clear.assert_called_once()
        self.assertEqual(result["cis_clear"], "FAIL")
        self.assertEqual(result["cis_clear_result"], "FAILED")
        self.assertEqual(result["cis_state_ready"], "NO")

    def test_transport_error_normalizes_to_failed(self) -> None:
        response = {
            "http_status": None,
            "business_result_code": None,
            "message_category": "TRANSPORT_FAILURE",
            "error_type": "TRANSPORT_ERROR",
            "transport_category": "TIMEOUT",
        }
        with patch("libraries.cis_preparation._clear_once", return_value=response) as clear:
            result = prepare_cis_state(str(self.data), "etb_tc_001", self.tempdir.name)
        clear.assert_called_once()
        self.assertEqual(result["cis_clear_result"], "FAILED")
        self.assertEqual(result["transport_category"], "TIMEOUT")
        self.assertNotIn("MASKED_ID", repr(result))

    def test_transport_probe_classifies_dns_failure(self) -> None:
        with patch("libraries.cis_preparation.CIS_CLEAR_URL", "https://example.invalid/cis-clear"), patch(
            "libraries.cis_preparation.socket.getaddrinfo", side_effect=socket.gaierror("no host")
        ):
            result = probe_cis_transport()
        self.assertEqual(result, {"ready": "NO", "transport_category": "DNS_RESOLUTION_FAILURE"})

    def test_transport_probe_classifies_tls_failure(self) -> None:
        class FakeConnection:
            def __enter__(self):
                return self

            def __exit__(self, *args):
                return False

        class FakeContext:
            def wrap_socket(self, connection, server_hostname):
                raise ssl.SSLError("bad tls")

        with patch("libraries.cis_preparation.CIS_CLEAR_URL", "https://example.invalid/cis-clear"), patch(
            "libraries.cis_preparation.socket.getaddrinfo", return_value=[("family", "type", "proto", "", ("host", 443))]
        ), patch(
            "libraries.cis_preparation.socket.create_connection", return_value=FakeConnection()
        ), patch("libraries.cis_preparation.ssl.create_default_context", return_value=FakeContext()):
            result = probe_cis_transport()
        self.assertEqual(result, {"ready": "NO", "transport_category": "TLS_FAILURE"})

    def test_clear_request_classifies_transport_failure(self) -> None:
        def unavailable_request(request, timeout):
            raise URLError(socket.timeout("timed out"))

        with patch(
            "libraries.cis_preparation.CIS_CLEAR_URL", "https://example.invalid/cis-clear"
        ), patch("libraries.cis_preparation._open_default", return_value=unavailable_request):
            result = _clear_once("MASKED_ID")
        self.assertEqual(result["message_category"], "TRANSPORT_FAILURE")
        self.assertEqual(result["error_type"], "TRANSPORT_ERROR")
        self.assertEqual(result["transport_category"], "TIMEOUT")
        self.assertNotIn("MASKED_ID", repr(result))

    def test_external_readiness_scopes_a_valid_selected_case(self) -> None:
        self.data.write_text(
            "cases:\n"
            "  etb_tc_001:\n"
            "    tc_id: TC-ETB-001\n"
            "    profile:\n"
            "      citizen_id: MASKED_ID_001\n"
            "  etb_tc_003:\n"
            "    tc_id: TC-ETB-003\n"
            "    profile:\n"
            "      citizen_id: MASKED_ID_003\n",
            encoding="utf-8",
        )
        result = verify_external_cis_readiness(
            str(self.data), self.tempdir.name, "TC-ETB-003"
        )
        self.assertEqual(result["selected_testcase"], "TC-ETB-003")
        self.assertEqual(len(result["profiles"]), 1)
        self.assertEqual(result["all_required_cis_ready"], "NO")
        self.assertEqual(result["full_runtime_gate"], "CLOSED")
        self.assertEqual(result["gate_decision"], "SIT_CIS_EXTERNAL_CONFIRMATION_REQUIRED")

    def test_external_readiness_rejects_missing_selected_case(self) -> None:
        with self.assertRaisesRegex(ValueError, "not present"):
            verify_external_cis_readiness(str(self.data), self.tempdir.name, "TC-ETB-003")

    def _write_selected_cases(self) -> None:
        self.data.write_text(
            "cases:\n"
            "  etb_tc_003:\n"
            "    tc_id: TC-ETB-003\n"
            "    profile:\n"
            "      citizen_id: MASKED_ID_003\n"
            "  etb_tc_004:\n"
            "    tc_id: TC-ETB-004\n"
            "    profile:\n"
            "      citizen_id: MASKED_ID_004\n",
            encoding="utf-8",
        )

    def test_exact_tc003_receipt_opens_only_tc003_gate(self) -> None:
        self._write_selected_cases()
        with patch.dict(os.environ, {
            "CIS_READINESS_SOURCE": "EXTERNAL_TEAM_CONFIRMATION",
            "CIS_READY": "EXTERNALLY_CONFIRMED",
        }, clear=False):
            result = verify_external_cis_readiness(str(self.data), self.tempdir.name, "TC-ETB-003")
        self.assertEqual(result["cis_readiness_status"], "EXTERNALLY_CONFIRMED")
        self.assertEqual(result["read_only_cis_verification_capability"], "EXTERNAL_TEAM_CONFIRMATION")
        self.assertEqual(result["selected_testcase"], "TC-ETB-003")
        self.assertEqual(result["all_required_cis_ready"], "YES")
        self.assertEqual(result["full_runtime_gate"], "OPEN")
        self.assertFalse((Path(self.tempdir.name) / "cis_readiness_result.json").exists())

    def test_missing_receipt_remains_closed(self) -> None:
        self._write_selected_cases()
        with patch.dict(os.environ, {}, clear=True):
            result = verify_external_cis_readiness(str(self.data), self.tempdir.name, "TC-ETB-003")
        self.assertEqual(result["gate_decision"], "SIT_CIS_EXTERNAL_CONFIRMATION_REQUIRED")
        self.assertEqual(result["all_required_cis_ready"], "NO")
        self.assertEqual(result["full_runtime_gate"], "CLOSED")

    def test_tc004_receipt_mismatch_remains_closed(self) -> None:
        self._write_selected_cases()
        with patch.dict(os.environ, {"CIS_READINESS_SOURCE": "EXTERNAL_TEAM_CONFIRMATION"}, clear=False):
            result = verify_external_cis_readiness(str(self.data), self.tempdir.name, "TC-ETB-004")
        self.assertEqual(result["gate_decision"], "SIT_CIS_EXTERNAL_CONFIRMATION_REQUIRED")
        self.assertEqual(result["full_runtime_gate"], "CLOSED")

    def test_wildcard_and_generic_receipts_remain_closed(self) -> None:
        self._write_selected_cases()
        for receipt in (("*", "YES"), ("EXTERNAL_TEAM_CONFIRMATION", "TRUE"), ("EXTERNAL_TEAM_CONFIRMATION", "TC-ETB-003,TC-ETB-004")):
            with self.subTest(receipt=receipt), patch.dict(os.environ, {"CIS_READINESS_SOURCE": receipt[0], "CIS_READY": receipt[1]}, clear=False):
                result = verify_external_cis_readiness(str(self.data), self.tempdir.name, "TC-ETB-003")
            self.assertEqual(result["full_runtime_gate"], "CLOSED")

    def test_sit_preparation_and_cleanup_make_zero_cis_mutation_calls(self) -> None:
        self._write_selected_cases()
        with patch.dict(
            os.environ,
            {"ETB_ENVIRONMENT": "SIT", "CIS_READINESS_SOURCE": "EXTERNAL_TEAM_CONFIRMATION", "CIS_READY": "EXTERNALLY_CONFIRMED"},
            clear=False,
        ), patch("libraries.cis_preparation._clear_once") as clear:
            preparation = prepare_cis_state(str(self.data), "etb_tc_003", self.tempdir.name)
            cleanup = cleanup_cis_state(str(self.data), "etb_tc_003", self.tempdir.name)
        clear.assert_not_called()
        self.assertEqual(preparation["cis_state_ready"], "EXTERNALLY_CONFIRMED")
        self.assertEqual(preparation["operation_count"], 0)
        self.assertEqual(cleanup["operation_count"], 0)
        self.assertFalse((Path(self.tempdir.name) / "cis_pre_test_result.json").exists())

    def test_dev_behavior_remains_mutating_and_unchanged(self) -> None:
        response = {
            "http_status": 200,
            "business_result_code": "Success",
            "message_category": "SUCCESS_SIGNAL_PRESENT",
            "error_type": None,
        }
        with patch.dict(os.environ, {"ETB_ENVIRONMENT": "DEV"}, clear=False), patch(
            "libraries.cis_preparation._clear_once", return_value=response
        ) as clear:
            result = prepare_cis_state(str(self.data), "etb_tc_001", self.tempdir.name)
        clear.assert_called_once()
        self.assertEqual(result["cis_clear"], "PASS")
        self.assertEqual(result["cis_state_ready"], "YES")

    def test_request_matches_approved_contract(self) -> None:
        requests = []

        def open_request(request, timeout):
            requests.append((request, timeout))
            return _Response()

        with patch(
            "libraries.cis_preparation.CIS_CLEAR_URL", "https://example.invalid/cis-clear"
        ), patch("libraries.cis_preparation._open_default", return_value=open_request):
            result = _clear_once("MASKED_ID")
        self.assertEqual(result["http_status"], 200)
        self.assertEqual(len(requests), 1)
        request, timeout = requests[0]
        self.assertEqual(request.get_method(), "DELETE")
        self.assertEqual(request.full_url, "https://example.invalid/cis-clear")
        self.assertEqual(request.get_header("Accept"), "application/json")
        self.assertEqual(request.get_header("Content-type"), "application/json")
        self.assertEqual(json.loads(request.data.decode("utf-8")), {"idNum": "MASKED_ID"})
        self.assertEqual(timeout, 30)
        self.assertNotIn("MASKED_ID", repr(result))


if __name__ == "__main__":
    unittest.main()
