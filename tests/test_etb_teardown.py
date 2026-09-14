from __future__ import annotations

import io
import json
import os
import tempfile
import unittest
from contextlib import redirect_stdout
from pathlib import Path
from typing import Any, cast
from unittest.mock import patch
from urllib.error import HTTPError

import libraries.etb_teardown as teardown

_TEST_DELETE_URL = "https://example.invalid/cis/qa/profile/db"


class _Response:
    def __init__(self, status=204, body=b""):
        self.status = status
        self.body = body

    def __enter__(self):
        return self

    def __exit__(self, *args):
        return False

    def read(self):
        return self.body


def _not_found_error():
    body = json.dumps(
        {
            "httpStatus": "NOT_FOUND",
            "errorType": "CustomerProfileNotFoundException",
            "errorMessage": "This CI is not found in CIS DB",
        }
    ).encode("utf-8")
    return HTTPError(_TEST_DELETE_URL, 404, "not found", cast(Any, None), io.BytesIO(body))


class EtbTeardownContractTests(unittest.TestCase):
    def _run(self, responses):
        with tempfile.TemporaryDirectory() as directory:
            with patch.dict(os.environ, {"CIS_CLEAR_URL": _TEST_DELETE_URL}, clear=False):
                with patch.object(teardown, "_approved_load_yaml", return_value={"profile": {"citizen_id": "0" * 13}}):
                    with patch.object(teardown, "_open_default", return_value=unittest.mock.Mock(side_effect=responses)) as opener:
                        stdout = io.StringIO()
                        with redirect_stdout(stdout):
                            result = teardown.delete_etb_profile_after_success("approved-etb-path", directory)
            artifact = Path(directory, "etb_teardown_result.json").read_text(encoding="utf-8")
            transport = opener.return_value
            return result, artifact, stdout.getvalue(), transport

    def test_success_followed_by_expected_404_passes(self):
        result, artifact, _, transport = self._run([_Response(204), _not_found_error()])
        self.assertEqual(transport.call_count, 2)
        self.assertEqual(result["etb_teardown"], "PASS")
        self.assertEqual(result["profile_reusable"], "YES")
        self.assertEqual(result["cleanup_state"], "CLEANED_AND_VERIFIED")
        self.assertEqual(result["cleanup_classification"], "SUCCESS_THEN_EXPECTED_NOT_FOUND")
        self.assertEqual(result["second_response"], {"http_status": 404, "error_type": "CustomerProfileNotFoundException"})
        self.assertNotIn("This CI is not found in CIS DB", artifact)

    def test_expected_404_on_first_call_is_already_absent(self):
        result, _, _, transport = self._run([_not_found_error(), _not_found_error()])
        self.assertEqual(transport.call_count, 2)
        self.assertEqual(result["etb_teardown"], "PASS")
        self.assertEqual(result["profile_reusable"], "YES")
        self.assertEqual(result["cleanup_state"], "ALREADY_ABSENT")
        self.assertEqual(result["cleanup_classification"], "ALREADY_ABSENT_CONFIRMED")

    def test_unexpected_response_fails_and_stays_sanitized(self):
        result, artifact, stdout, transport = self._run([_Response(500, b"internal details"), _Response(204)])
        self.assertEqual(transport.call_count, 2)
        self.assertEqual(result["etb_teardown"], "FAIL")
        self.assertEqual(result["profile_reusable"], "UNKNOWN")
        self.assertEqual(result["cleanup_classification"], "UNEXPECTED_RESPONSE")
        self.assertNotIn("internal details", artifact)
        self.assertNotIn("internal details", stdout)

    def test_exactly_two_calls_maximum(self):
        result, _, _, transport = self._run([_Response(204), _not_found_error()])
        self.assertEqual(result["etb_teardown"], "PASS")
        self.assertEqual(transport.call_count, 2)

    def test_loader_request_headers_and_sensitive_value_redaction(self):
        synthetic_id = "0" * 13
        captured = {}

        def fake_transport(request, timeout):
            captured.setdefault("requests", []).append(request)
            return _Response(204)

        with tempfile.TemporaryDirectory() as directory:
            with patch.dict(os.environ, {"CIS_CLEAR_URL": _TEST_DELETE_URL}, clear=False):
                with patch.object(teardown, "_approved_load_yaml", return_value={"profile": {"citizen_id": synthetic_id}}) as loader:
                    with patch.object(teardown, "_open_default", return_value=fake_transport):
                        stdout = io.StringIO()
                        with redirect_stdout(stdout):
                            result = teardown.delete_etb_profile_after_success("approved-etb-path", directory)
            loader.assert_called_once_with("approved-etb-path")
            self.assertEqual(len(captured["requests"]), 2)
            request = captured["requests"][0]
            self.assertEqual(request.full_url, _TEST_DELETE_URL)
            self.assertEqual(request.method, "DELETE")
            self.assertEqual(request.headers["Accept"], "application/json")
            self.assertEqual(request.headers["Content-type"], "application/json")
            self.assertEqual(json.loads(request.data.decode("utf-8")), {"idNum": synthetic_id})
            artifact = Path(directory, "etb_teardown_result.json").read_text(encoding="utf-8")
            self.assertNotIn(synthetic_id, artifact)
            self.assertNotIn(synthetic_id, stdout.getvalue())
            self.assertEqual(result["etb_teardown"], "FAIL")

    def test_missing_runtime_endpoint_fails_without_transport(self):
        with tempfile.TemporaryDirectory() as directory:
            with patch.dict(os.environ, {}, clear=True):
                with patch.object(teardown, "_approved_load_yaml", return_value={"profile": {"citizen_id": "0" * 13}}):
                    with patch.object(teardown, "_open_default") as opener:
                        result = teardown.delete_etb_profile_after_success("approved-etb-path", directory)
            self.assertEqual(result["etb_teardown"], "FAIL")
            self.assertEqual(result["first_response"]["error_type"], "CIS_CLEAR_URL_REQUIRED")
            self.assertEqual(result["second_response"]["error_type"], "CIS_CLEAR_URL_REQUIRED")
            opener.assert_not_called()

    def test_sit_external_preparation_never_calls_transport(self):
        with tempfile.TemporaryDirectory() as directory:
            with patch.dict(os.environ, {"ETB_ENVIRONMENT": "SIT"}, clear=True):
                with patch.object(teardown, "_open_default") as opener:
                    result = teardown.delete_etb_profile_after_success("unused-local-profile", directory)
            self.assertEqual(result["etb_teardown"], "NOT_ATTEMPTED")
            self.assertEqual(result["cleanup_owner"], "EXTERNAL_TEAM")
            self.assertEqual(result["cleanup_allowed"], "FALSE")
            opener.assert_not_called()

    def test_etb_flow_uses_cis_preparation_and_mandatory_cleanup(self):
        suite = Path("tests/android/etb/etb_flow.robot").read_text(encoding="utf-8")
        self.assertIn("Prepare CIS State", suite)
        self.assertIn("Cleanup CIS State", suite)
        self.assertIn("FINALLY", suite)
        self.assertNotIn("Delete ETB Profile After Success", suite)


if __name__ == "__main__":
    unittest.main()
