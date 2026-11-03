from __future__ import annotations

import io
import tempfile
import unittest
from contextlib import redirect_stdout
from unittest.mock import patch
from pathlib import Path

from tools import cis_transport_status


class CisTransportStatusTests(unittest.TestCase):
    def test_local_env_is_loaded_but_explicit_environment_wins(self):
        with tempfile.TemporaryDirectory() as directory:
            env_file = Path(directory) / "etb.env"
            env_file.write_text(
                'CIS_CLEAR_URL="https://local.example.invalid/path"\n'
                'PDPA_CA_BUNDLE="/local/ca.pem"\n',
                encoding="utf-8",
            )
            result = cis_transport_status.effective_config(
                {
                    "CIS_CLEAR_URL": "https://explicit.example.invalid/path",
                    "PDPA_CA_BUNDLE": "/explicit/ca.pem",
                },
                env_file=env_file,
            )
        self.assertEqual(
            result["CIS_CLEAR_URL"],
            "https://explicit.example.invalid/path",
        )
        self.assertEqual(result["PDPA_CA_BUNDLE"], "/explicit/ca.pem")

    def test_payload_is_sanitized_to_ready_and_category_only(self):
        captured = {}

        def fake_probe(url, timeout, **kwargs):
            captured["url"] = url
            captured["timeout"] = timeout
            captured["ca_bundle"] = kwargs["ca_bundle"]
            return {
                "ready": "NO",
                "transport_category": "DNS_RESOLUTION_FAILURE",
                "sensitive": "must-not-propagate",
            }

        payload = cis_transport_status.probe_payload(
            {
                "CIS_CLEAR_URL": "https://internal.example.invalid/private",
                "PDPA_CA_BUNDLE": "/private/ca.pem",
            },
            probe_func=fake_probe,
        )

        self.assertEqual(
            payload,
            {
                "ready": "NO",
                "transport_category": "DNS_RESOLUTION_FAILURE",
            },
        )
        self.assertEqual(captured["timeout"], 30)
        self.assertEqual(captured["ca_bundle"], "/private/ca.pem")
        self.assertNotIn("url", payload)
        self.assertNotIn("sensitive", payload)

    def test_missing_url_remains_fail_closed(self):
        payload = cis_transport_status.probe_payload(
            {},
            probe_func=lambda *args, **kwargs: {
                "ready": "NO",
                "transport_category": "CIS_CLEAR_URL_REQUIRED",
            },
        )
        self.assertEqual(payload["ready"], "NO")
        self.assertEqual(payload["transport_category"], "CIS_CLEAR_URL_REQUIRED")


    def test_require_ready_returns_three_when_transport_is_closed(self):
        stdout = io.StringIO()
        with patch.object(
            cis_transport_status,
            "effective_config",
            return_value={},
        ), patch.object(
            cis_transport_status,
            "probe_payload",
            return_value={
                "ready": "NO",
                "transport_category": "DNS_RESOLUTION_FAILURE",
            },
        ), patch(
            "sys.argv",
            ["cis_transport_status.py", "--require-ready"],
        ), redirect_stdout(stdout):
            rc = cis_transport_status.main()

        self.assertEqual(rc, 3)
        self.assertIn('"ready": "NO"', stdout.getvalue())
        self.assertNotIn("http", stdout.getvalue())

    def test_require_ready_returns_zero_when_transport_is_ready(self):
        with patch.object(
            cis_transport_status,
            "effective_config",
            return_value={},
        ), patch.object(
            cis_transport_status,
            "probe_payload",
            return_value={
                "ready": "YES",
                "transport_category": "READY",
            },
        ), patch(
            "sys.argv",
            ["cis_transport_status.py", "--require-ready"],
        ):
            rc = cis_transport_status.main()

        self.assertEqual(rc, 0)


if __name__ == "__main__":
    unittest.main(verbosity=2)
