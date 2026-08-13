from __future__ import annotations

import tempfile
import unittest
import json
import socket
import ssl
from pathlib import Path
from unittest.mock import patch
from urllib.error import URLError

from libraries.cis_preparation import _clear_once, cleanup_cis_state, prepare_cis_state, probe_cis_transport


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
