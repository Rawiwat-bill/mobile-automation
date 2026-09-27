from __future__ import annotations

import contextlib
import importlib.util
import io
import json
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
RUNTIME_PATH = ROOT / "tools" / "runner" / "etb_runtime.py"
PREFLIGHT_PATH = ROOT / "tools" / "runner" / "etb_preflight.sh"
TARGET_GUARD_PATH = ROOT / "tools" / "real_device_preflight.py"

SPEC = importlib.util.spec_from_file_location("etb_runtime_provenance", RUNTIME_PATH)
assert SPEC and SPEC.loader
RUNTIME = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(RUNTIME)

BUILD_IDENTITY = "1.14.0-debug-network-post-mmp-1-alpha-24-191-Unshield:191"


class ETBRunProvenanceTests(unittest.TestCase):
    def test_target_build_identity_requires_proven_target(self):
        out = io.StringIO()
        payload = json.dumps(
            {
                "target_identity": "PASS",
                "build_identified": True,
                "build_identity": BUILD_IDENTITY,
            }
        )
        with contextlib.redirect_stdout(out):
            status = RUNTIME.target_build_identity(payload)
        self.assertEqual(status, 0)
        self.assertEqual(out.getvalue().strip(), BUILD_IDENTITY)

    def test_target_build_identity_rejects_unproven_payload(self):
        err = io.StringIO()
        with contextlib.redirect_stderr(err):
            status = RUNTIME.target_build_identity(
                json.dumps(
                    {
                        "target_identity": "FAIL",
                        "build_identified": True,
                        "build_identity": BUILD_IDENTITY,
                    }
                )
            )
        self.assertEqual(status, 3)
        self.assertIn("UNPROVEN", err.getvalue())

    def test_record_build_identity_updates_existing_run_manifest(self):
        with tempfile.TemporaryDirectory(prefix="bbl-etb-provenance-") as directory:
            manifest = Path(directory) / "run_manifest.json"
            manifest.write_text(
                json.dumps(
                    {
                        "schema": "bbl-etb-run-manifest/v1",
                        "runtime": {
                            "environment": "DEV",
                            "execution_target": "DIAGNOSTIC_CONTROL",
                            "build_identity": "UNPROVEN",
                        },
                    }
                ),
                encoding="utf-8",
            )
            with contextlib.redirect_stdout(io.StringIO()):
                status = RUNTIME.record_run_build_identity(str(manifest), BUILD_IDENTITY)
            payload = json.loads(manifest.read_text(encoding="utf-8"))
        self.assertEqual(status, 0)
        self.assertEqual(payload["runtime"]["build_identity"], BUILD_IDENTITY)

    def test_preflight_persists_identity_only_after_target_guard_passes(self):
        source = PREFLIGHT_PATH.read_text(encoding="utf-8")
        guard = source.index("TARGET_GUARD=PASS")
        extract = source.index("target-build-identity")
        persist = source.index("record-build-identity")
        cis_boundary = source.index("run_etb_cis_preflight()")
        self.assertLess(guard, extract)
        self.assertLess(extract, persist)
        self.assertLess(persist, cis_boundary)
        self.assertIn('export ETB_BUILD_IDENTITY="$build_identity"', source)

    def test_target_guard_returns_sanitized_proven_identity(self):
        source = TARGET_GUARD_PATH.read_text(encoding="utf-8")
        self.assertIn(
            '"build_identity": f"{version_name.group(1)}:{version_code.group(1)}"',
            source,
        )


if __name__ == "__main__":
    unittest.main(verbosity=2)
