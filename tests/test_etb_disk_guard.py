from __future__ import annotations

import io
from contextlib import redirect_stderr, redirect_stdout
from types import SimpleNamespace
import unittest
from unittest.mock import patch

from tools.runner import etb_runtime


class EtbDiskGuardTests(unittest.TestCase):
    def _run(self, free_gb: float, warn: str = "10", fail: str = "5"):
        usage = SimpleNamespace(free=int(free_gb * (1024 ** 3)))
        stdout = io.StringIO()
        stderr = io.StringIO()
        with patch.object(etb_runtime.shutil, "disk_usage", return_value=usage):
            with redirect_stdout(stdout), redirect_stderr(stderr):
                rc = etb_runtime.disk_guard("/synthetic", warn, fail)
        return rc, stdout.getvalue(), stderr.getvalue()

    def test_pass_at_or_above_warning_threshold(self):
        rc, out, err = self._run(12)
        self.assertEqual(rc, 0)
        self.assertIn("ETB_DISK_GUARD=PASS", out)
        self.assertEqual(err, "")

    def test_warn_between_fail_and_warning_thresholds(self):
        rc, out, err = self._run(7)
        self.assertEqual(rc, 0)
        self.assertIn("ETB_DISK_GUARD=WARN", out)
        self.assertEqual(err, "")

    def test_fail_below_fail_threshold(self):
        rc, out, err = self._run(4)
        self.assertEqual(rc, 3)
        self.assertEqual(out, "")
        self.assertIn("ETB_DISK_GUARD=FAIL", err)

    def test_invalid_threshold_order_is_closed(self):
        rc, out, err = self._run(20, warn="4", fail="5")
        self.assertEqual(rc, 2)
        self.assertEqual(out, "")
        self.assertIn("ETB_DISK_GUARD_INVALID_THRESHOLD", err)

    def test_runner_places_disk_gate_before_target_gate(self):
        source = (etb_runtime._PROJECT_ROOT / "tools/runner/etb_runner.sh").read_text(encoding="utf-8")
        self.assertLess(
            source.index("run_etb_disk_preflight"),
            source.index("run_etb_target_preflight"),
        )


if __name__ == "__main__":
    unittest.main(verbosity=2)
