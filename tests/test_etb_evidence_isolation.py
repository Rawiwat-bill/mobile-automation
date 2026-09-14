from __future__ import annotations

import hashlib
import json
import os
import subprocess
import sys
import tempfile
import unittest
import xml.etree.ElementTree as ET
from pathlib import Path
from unittest.mock import patch

from libraries.product_selection_evidence import capture_product_selection_evidence

ROOT = Path(__file__).resolve().parents[1]
TARGETS = (
    "run",
    "libraries/failure_evidence.py",
    "libraries/visual_timeline.py",
    "libraries/product_selection_evidence.py",
    "libraries/profile_exit_evidence.py",
    "libraries/adb_device.py",
    "libraries/cis_preparation.py",
    "resources/app/app_keywords.resource",
    "resources/pages/etb/mobile_otp_page.resource",
    "resources/pages/common_onboarding/terms_and_conditions_page.resource",
    "resources/pages/onboarding/profile_screen_page.resource",
    "tests/test_etb_artifact_security.py",
    "package.json",
)


def _read(relative: str) -> str:
    return (ROOT / relative).read_text(encoding="utf-8")


def _sha(relative: str) -> str:
    return hashlib.sha256((ROOT / relative).read_bytes()).hexdigest()


def _product_source(index: int) -> str:
    return (
        "<hierarchy>"
        '<node resource-id="screenProductSelection_textTitle" visible-to-user="true" />'
        f'<node resource-id="screenProductSelection_flatListCardsTouchableOpacity_{index}" '
        'visible-to-user="true" enabled="true" />'
        f'<node resource-id="screenProductSelection_flatListCardsCheckBox_{index}" '
        'visible-to-user="true" enabled="true" checked="false" selected="false" />'
        '<node resource-id="screenProductSelection_buttonConfirm" visible-to-user="true" />'
        "</hierarchy>"
    )


class ETBEvidenceIsolationTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        for relative in TARGETS:
            print(f"SHA256 {relative} {_sha(relative)}")

    def test_product_evidence_survives_two_cases_and_two_runs(self) -> None:
        with tempfile.TemporaryDirectory(prefix="etb-evidence-isolation-") as temp:
            output = Path(temp)
            expected: list[tuple[Path, int]] = []
            for run_id, case_id, index in (
                ("RUN-A", "TC-ETB-001", 0),
                ("RUN-A", "TC-ETB-002", 1),
                ("RUN-B", "TC-ETB-001", 2),
            ):
                with patch.dict(
                    os.environ,
                    {"ETB_RUN_ID": run_id, "ETB_CASE_ID": case_id},
                    clear=False,
                ):
                    capture_product_selection_evidence(
                        _product_source(index), "", str(output)
                    )
                expected.append(
                    (
                        output
                        / "evidence"
                        / run_id
                        / case_id
                        / "private_local"
                        / "product_selection_runtime.json",
                        index,
                    )
                )

            for path, index in expected:
                self.assertTrue(path.is_file(), f"missing isolated evidence: {path}")
                payload = json.loads(path.read_text(encoding="utf-8"))
                self.assertIn(
                    f"screenProductSelection_flatListCardsTouchableOpacity_{index}",
                    payload["visible_product_row_resource_ids"],
                )

            self.assertFalse(
                (output / "private_local" / "product_selection_runtime.json").exists(),
                "legacy shared evidence path must not be used once run/case scope is available",
            )

    def test_python_runtime_writers_use_shared_scope_resolver(self) -> None:
        for relative in (
            "libraries/failure_evidence.py",
            "libraries/visual_timeline.py",
            "libraries/product_selection_evidence.py",
            "libraries/profile_exit_evidence.py",
            "libraries/adb_device.py",
        ):
            with self.subTest(relative=relative):
                text = _read(relative)
                self.assertTrue("evidence_scope" in text, f"{relative}: shared scope import missing")
                self.assertTrue(
                    "resolve_private_evidence_dir" in text,
                    f"{relative}: private evidence resolver missing",
                )

        cis = _read("libraries/cis_preparation.py")
        self.assertTrue("evidence_scope" in cis, "cis_preparation: shared scope import missing")
        self.assertTrue(
            "resolve_scoped_output_dir" in cis,
            "cis_preparation: scoped output resolver missing",
        )

    def test_robot_direct_private_writers_use_scoped_directory(self) -> None:
        for relative in (
            "resources/app/app_keywords.resource",
            "resources/pages/etb/mobile_otp_page.resource",
            "resources/pages/common_onboarding/terms_and_conditions_page.resource",
        ):
            with self.subTest(relative=relative):
                text = _read(relative)
                self.assertTrue("evidence_scope.py" in text, f"{relative}: evidence scope library missing")
                self.assertTrue(
                    "Resolve Private Evidence Dir" in text,
                    f"{relative}: scoped Robot evidence keyword missing",
                )
                self.assertFalse(
                    "${OUTPUT DIR}/private_local" in text,
                    f"{relative}: legacy shared private_local path remains",
                )

    def test_runner_exports_one_run_id_before_runtime(self) -> None:
        text = _read("run")
        self.assertTrue("ETB_RUN_ID" in text, "runner: ETB_RUN_ID missing")
        self.assertTrue("export ETB_RUN_ID" in text, "runner: ETB_RUN_ID is not exported")

    def test_etb_robot_dryrun_after_scoping(self) -> None:
        with tempfile.TemporaryDirectory(prefix="etb-evidence-dryrun-") as temp:
            result = subprocess.run(
                [
                    sys.executable,
                    "-m",
                    "robot",
                    "--dryrun",
                    "--console",
                    "none",
                    "--outputdir",
                    temp,
                    str(ROOT / "tests/android/etb/etb_regression.robot"),
                ],
                cwd=ROOT,
                capture_output=True,
                text=True,
                check=False,
            )
            if result.returncode:
                errors: list[str] = []
                output_xml = Path(temp) / "output.xml"
                if output_xml.is_file():
                    root = ET.parse(output_xml).getroot()
                    errors = [
                        (message.text or "").strip()
                        for message in root.iter("msg")
                        if message.get("level") in {"ERROR", "FAIL"}
                        and (message.text or "").strip()
                    ]
                details = "\n".join(errors[-20:]) or (result.stderr.strip() or result.stdout.strip())
                self.fail(f"ETB Robot dry-run failed ({result.returncode}):\n{details}")


if __name__ == "__main__":
    unittest.main(verbosity=2)
