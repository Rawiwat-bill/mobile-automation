from __future__ import annotations
import subprocess
import sys
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
PY = Path(sys.executable)

unit_modules = [
    "tests/test_mobile_review_task3.py",
    "tests/test_mobile_review_task4.py",
    "tests/test_mobile_review_task5.py",
    "tests/test_mobile_review_task7.py",
    "tests/test_startup_state.py",
    "tests/test_f05_landing_transition.py",
    "tests/test_etb_dopa_boundary.py",
    "tests/test_etb_artifact_security.py",
    "tests/test_etb_teardown.py",
]

print("FOCUSED_UNIT_START", flush=True)
unit = subprocess.run([str(PY), "-m", "unittest", "-v", *unit_modules], cwd=ROOT)
if unit.returncode:
    raise SystemExit(unit.returncode)
print("FOCUSED_UNIT=PASS", flush=True)

suites = [
    "tests/android/etb/etb_regression.robot",
    "tests/android/ntb/ntb_flow.robot",
    "tests/android/onboarding/stage1_onboarding.robot",
    "tests/android/onboarding/onboarding_health_check.robot",
]
with tempfile.TemporaryDirectory(prefix="bbl-mobile-review-dryrun-") as base:
    for index, suite in enumerate(suites, 1):
        out = Path(base) / str(index)
        cmd = [str(PY), "-m", "robot", "--dryrun", "--console", "none", "--outputdir", str(out), str(ROOT / suite)]
        result = subprocess.run(cmd, cwd=ROOT, capture_output=True, text=True)
        print(f"DRYRUN {suite}={'PASS' if result.returncode == 0 else 'FAIL'}", flush=True)
        if result.returncode:
            print(result.stdout[-2000:])
            print(result.stderr[-2000:], file=sys.stderr)
            raise SystemExit(result.returncode)
print("FOCUSED_DRYRUN=PASS_4_OF_4", flush=True)
