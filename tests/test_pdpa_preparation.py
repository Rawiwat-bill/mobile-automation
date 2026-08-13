from __future__ import annotations

import unittest
import tempfile
from urllib.error import URLError
from urllib.parse import parse_qs
from urllib.request import Request
from pathlib import Path

from libraries.pdpa_preparation import prepare_pdpa_state, prepare_pdpa_state_from_profile


FORM_HTML = """
<html><body>
<form action="/PDPA_MB/frmIndex" method="post">
<input type="hidden" name="__VIEWSTATE" value="masked-view-state" />
<input type="hidden" name="__EVENTVALIDATION" value="masked-event-validation" />
<input type="hidden" name="__VIEWSTATEGENERATOR" value="masked-generator" />
<input type="submit" name="btnClear" value="Clear" />
</form>
</body></html>
"""


class _Response:
    def __init__(self, status: int, body: str = "") -> None:
        self.status = status
        self._body = body.encode("utf-8")

    def read(self) -> bytes:
        return self._body


class _Transport:
    def __init__(self, responses: list[_Response | Exception]) -> None:
        self.responses = iter(responses)
        self.requests: list[Request] = []

    def __call__(self, request: Request) -> _Response:
        self.requests.append(request)
        response = next(self.responses)
        if isinstance(response, Exception):
            raise response
        return response


class PdpaPreparationTests(unittest.TestCase):
    def test_extracts_hidden_state_and_builds_clear_post(self) -> None:
        transport = _Transport([_Response(200, FORM_HTML), _Response(200, "<html></html>")])
        result = prepare_pdpa_state(
            "CI",
            {"citizenId": "MASKED_ID"},
            base_url="https://example.test",
            opener=transport,
        )
        self.assertEqual(result["status"], "CLEAR_REQUEST_SUBMITTED")
        self.assertEqual(result["post_count"], 1)
        self.assertEqual(result["clear_control_name"], "btnClear")
        self.assertNotIn("MASKED_ID", repr(result))
        self.assertEqual(len(transport.requests), 2)
        payload = parse_qs(transport.requests[1].data.decode("utf-8"))
        self.assertEqual(payload["__VIEWSTATE"], ["masked-view-state"])
        self.assertEqual(payload["__EVENTVALIDATION"], ["masked-event-validation"])
        self.assertEqual(payload["documentType"], ["CI"])
        self.assertEqual(payload["citizenId"], ["MASKED_ID"])
        self.assertEqual(payload["btnClear"], ["Clear"])

    def test_missing_viewstate_is_invalid_and_does_not_post(self) -> None:
        transport = _Transport([_Response(200, '<form><input type="hidden" name="__EVENTVALIDATION" value="x"></form>')])
        result = prepare_pdpa_state("CI", {"citizenId": "MASKED_ID"}, base_url="https://example.test", opener=transport)
        self.assertEqual(result["status"], "FORM_STATE_INVALID")
        self.assertEqual(len(transport.requests), 1)

    def test_missing_eventvalidation_is_invalid(self) -> None:
        html = '<form><input type="hidden" name="__VIEWSTATE" value="x"><input type="submit" name="btnClear" value="Clear"></form>'
        transport = _Transport([_Response(200, html)])
        result = prepare_pdpa_state("CI", {"citizenId": "MASKED_ID"}, base_url="https://example.test", opener=transport)
        self.assertEqual(result["status"], "FORM_STATE_INVALID")

    def test_missing_clear_control_is_invalid(self) -> None:
        html = '<form><input type="hidden" name="__VIEWSTATE" value="x"><input type="hidden" name="__EVENTVALIDATION" value="y"></form>'
        transport = _Transport([_Response(200, html)])
        result = prepare_pdpa_state("CI", {"citizenId": "MASKED_ID"}, base_url="https://example.test", opener=transport)
        self.assertEqual(result["status"], "FORM_STATE_INVALID")

    def test_form_action_is_resolved(self) -> None:
        html = FORM_HTML.replace('/PDPA_MB/frmIndex', '/PDPA_MB/submit')
        transport = _Transport([_Response(200, html), _Response(200, "ok")])
        result = prepare_pdpa_state("CI", {"citizenId": "MASKED_ID"}, base_url="https://example.test", opener=transport)
        self.assertEqual(result["status"], "CLEAR_REQUEST_SUBMITTED")
        self.assertEqual(transport.requests[1].full_url, "https://example.test/PDPA_MB/submit")

    def test_transport_failure_is_sanitized(self) -> None:
        transport = _Transport([URLError("connection details must not escape")])
        result = prepare_pdpa_state("CI", {"citizenId": "MASKED_ID"}, base_url="https://example.test", opener=transport)
        self.assertEqual(result["status"], "CLEAR_TRANSPORT_FAILED")
        self.assertNotIn("connection details", repr(result))
        self.assertNotIn("MASKED_ID", repr(result))

    def test_http_failure_is_not_semantic_success(self) -> None:
        transport = _Transport([_Response(200, FORM_HTML), _Response(503, "failure")])
        result = prepare_pdpa_state("CI", {"citizenId": "MASKED_ID"}, base_url="https://example.test", opener=transport)
        self.assertEqual(result["status"], "CLEAR_TRANSPORT_FAILED")
        self.assertEqual(result["http_status"], 503)
        self.assertFalse(result["semantic_verifiable"])

    def test_requires_host_and_identity_mapping(self) -> None:
        self.assertEqual(prepare_pdpa_state("CI", {"citizenId": "MASKED_ID"})["status"], "FORM_STATE_INVALID")
        self.assertEqual(prepare_pdpa_state("CI", "MASKED_ID", base_url="https://example.test")["status"], "FORM_STATE_INVALID")

    def test_profile_wrapper_uses_approved_field_contract(self) -> None:
        transport = _Transport([_Response(200, FORM_HTML), _Response(200, "ok")])
        with tempfile.TemporaryDirectory(prefix="pdpa-profile-") as directory:
            path = Path(directory) / "cases.yaml"
            path.write_text(
                "cases:\n  etb_tc_002:\n    profile:\n      citizen_id: MASKED_ID\n",
                encoding="utf-8",
            )
            result = prepare_pdpa_state_from_profile(
                str(path),
                "etb_tc_002",
                base_url="https://example.test",
                opener=transport,
            )
        self.assertEqual(result["status"], "CLEAR_REQUEST_SUBMITTED")
        payload = parse_qs(transport.requests[1].data.decode("utf-8"))
        self.assertEqual(payload["ddlIdType"], ["CI"])
        self.assertEqual(payload["btnClear"], ["Clear"])
        self.assertNotIn("MASKED_ID", repr(result))


if __name__ == "__main__":
    unittest.main()
