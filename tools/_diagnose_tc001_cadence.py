from __future__ import annotations

import os
import re
import subprocess
import time
from pathlib import Path

SERIAL = "emulator-5554"
PACKAGE = "com.bangkokbank.blue.dev"
ACTIVITY = "com.bangkokbank.blue.MainActivity"
DUMP_PATH = "/sdcard/etb_tc001_cadence.xml"

sdk_candidates = [
    os.environ.get("ANDROID_HOME", ""),
    os.environ.get("ANDROID_SDK_ROOT", ""),
    str(Path.home() / "Library/Android/sdk"),
]
adb = None
for root in sdk_candidates:
    candidate = Path(root) / "platform-tools" / "adb" if root else None
    if candidate and candidate.is_file():
        adb = str(candidate)
        break
if not adb:
    raise SystemExit("DIAG_ADB_NOT_FOUND")


def run(*args: str, timeout: float = 15.0) -> subprocess.CompletedProcess[str]:
    return subprocess.run([adb, "-s", SERIAL, *args], capture_output=True, text=True, timeout=timeout, check=False)


def shell(*args: str, timeout: float = 15.0) -> subprocess.CompletedProcess[str]:
    return run("shell", *args, timeout=timeout)


def foreground_target() -> bool:
    out = shell("dumpsys", "window", timeout=20).stdout
    match = re.search(r"mCurrentFocus=Window\{.*? u0 ([^ }]+)", out)
    component = match.group(1) if match else ""
    return component.startswith(PACKAGE + "/")


def fresh_dump() -> tuple[bool, str]:
    shell("rm", "-f", DUMP_PATH, timeout=5)
    dump = shell("uiautomator", "dump", "--compressed", DUMP_PATH, timeout=12)
    if dump.returncode != 0:
        return False, ""
    source = shell("cat", DUMP_PATH, timeout=12)
    if source.returncode != 0:
        return False, ""
    return True, source.stdout


def classify(source: str) -> str:
    if "screenLanding_skipButton" in source or "screenLanding_buttonReady" in source:
        return "LANDING"
    if "Transition_Screen_Logo_Icon" in source or "security-error-container" in source:
        return "STARTUP_TRANSITION"
    return "OTHER"


state = run("get-state").stdout.strip()
print(f"ADB_STATE={'PASS' if state == 'device' else 'FAIL'}")
if state != "device":
    raise SystemExit(1)

clear = shell("pm", "clear", PACKAGE, timeout=20)
clear_ok = clear.returncode == 0 and "success" in clear.stdout.lower()
print(f"PM_CLEAR={'PASS' if clear_ok else 'FAIL'}")
if not clear_ok:
    raise SystemExit(1)

launch = shell("am", "start", "-n", f"{PACKAGE}/{ACTIVITY}", timeout=15)
print(f"APP_START={'PASS' if launch.returncode == 0 else 'FAIL'}")
if launch.returncode != 0:
    raise SystemExit(1)

started = time.monotonic()
landing_seen = False
for target in range(5, 66, 5):
    remaining = target - (time.monotonic() - started)
    if remaining > 0:
        time.sleep(remaining)
    elapsed = int(round(time.monotonic() - started))
    dump_ok, source = fresh_dump()
    state_label = classify(source) if dump_ok else "NO_FRESH_DUMP"
    print(
        f"T+{elapsed:02d}s DUMP={'PASS' if dump_ok else 'FAIL'} "
        f"SOURCE={'YES' if bool(source.strip()) else 'NO'} "
        f"FOREGROUND={'TARGET' if foreground_target() else 'OTHER'} STATE={state_label}"
    )
    if state_label == "LANDING":
        landing_seen = True
        break

print(f"LANDING_SEEN={'YES' if landing_seen else 'NO'}")
raise SystemExit(0 if landing_seen else 1)
