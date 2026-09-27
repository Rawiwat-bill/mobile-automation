from __future__ import annotations

import os
import re
import subprocess
import time
from pathlib import Path

SERIAL = "emulator-5554"
PACKAGE = "com.bangkokbank.blue.dev"
ACTIVITY = "com.bangkokbank.blue.MainActivity"
DURATION = 180
INTERVAL = 3
REMOTE_XML = "/sdcard/manual_etb_monitor.xml"

SDK_ROOTS = [
    os.environ.get("ANDROID_HOME", ""),
    os.environ.get("ANDROID_SDK_ROOT", ""),
    str(Path.home() / "Library/Android/sdk"),
]
ADB = ""
for root in SDK_ROOTS:
    candidate = Path(root) / "platform-tools" / "adb" if root else None
    if candidate and candidate.is_file():
        ADB = str(candidate)
        break
if not ADB:
    raise SystemExit("MONITOR_ADB_NOT_FOUND")


def adb(*args: str, timeout: float = 15.0) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        [ADB, "-s", SERIAL, *args],
        capture_output=True,
        text=True,
        timeout=timeout,
        check=False,
    )


def shell(*args: str, timeout: float = 15.0) -> subprocess.CompletedProcess[str]:
    return adb("shell", *args, timeout=timeout)


def foreground() -> str:
    out = shell("dumpsys", "window", timeout=20).stdout
    match = re.search(r"mCurrentFocus=Window\{.*? u0 ([^ }]+)", out)
    return match.group(1) if match else "UNKNOWN"


def fresh_source() -> tuple[bool, str]:
    shell("rm", "-f", REMOTE_XML)
    dump = shell("uiautomator", "dump", "--compressed", REMOTE_XML, timeout=12)
    if dump.returncode != 0:
        return False, ""
    cat = shell("cat", REMOTE_XML, timeout=12)
    if cat.returncode != 0:
        return False, ""
    return True, cat.stdout


def classify(source: str) -> str:
    if "screenLanding_skipButton" in source or "screenLanding_buttonReady" in source:
        return "LANDING"
    if "Transition_Screen_Logo_Icon" in source:
        return "STARTUP_TRANSITION"
    if "termsAndConditions" in source or "Terms and Conditions" in source:
        return "TERMS"
    if "consent" in source.lower():
        return "CONSENT_OR_RELATED"
    if re.search(r"\b(?:RGI-\d+|AJI-001)\b", source):
        return "KNOWN_ERROR"
    return "OTHER"


def ids(source: str) -> str:
    values: list[str] = []
    for value in re.findall(r'resource-id="([^"]+)"', source):
        if value and value not in values:
            values.append(value)
        if len(values) >= 10:
            break
    return ",".join(values) if values else "NONE"


state = adb("get-state").stdout.strip()
print(f"ADB_STATE={'PASS' if state == 'device' else 'FAIL'}", flush=True)
if state != "device":
    raise SystemExit(1)

launch = shell("am", "start", "-n", f"{PACKAGE}/{ACTIVITY}", timeout=20)
print(f"APP_START={'PASS' if launch.returncode == 0 else 'FAIL'}", flush=True)
if launch.returncode != 0:
    raise SystemExit(1)

print("MANUAL_MONITOR=READY", flush=True)
started = time.monotonic()
last_signature = None
while time.monotonic() - started <= DURATION:
    elapsed = int(time.monotonic() - started)
    component = foreground()
    ok, source = fresh_source()
    state_name = classify(source) if ok else "DUMP_FAILED"
    signature = (component, state_name, ids(source) if ok else "NONE")
    if signature != last_signature:
        print(
            f"T+{elapsed:03d}s FOREGROUND={component} DUMP={'PASS' if ok else 'FAIL'} STATE={state_name} IDS={signature[2]}",
            flush=True,
        )
        last_signature = signature
    time.sleep(INTERVAL)

print("MANUAL_MONITOR=DONE", flush=True)
