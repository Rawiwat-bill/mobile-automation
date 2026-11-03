from __future__ import annotations

import os
import re
import subprocess
import time
from pathlib import Path

SERIAL = "emulator-5554"
PACKAGE = "com.bangkokbank.blue.dev"
ACTIVITY = "com.bangkokbank.blue.MainActivity"
REMOTE_XML = "/sdcard/etb_force_stop_repeat.xml"
POLL = 5
WINDOW = 90
ROUNDS = 3


def resolve_adb() -> str:
    candidates = []
    for key in ("ANDROID_HOME", "ANDROID_SDK_ROOT"):
        root = os.environ.get(key)
        if root:
            candidates.append(Path(root) / "platform-tools" / "adb")
    candidates.append(Path.home() / "Library" / "Android" / "sdk" / "platform-tools" / "adb")
    for candidate in candidates:
        if candidate.exists():
            return str(candidate)
    return "adb"

ADB = resolve_adb()


def adb(*args: str, timeout: float = 20.0) -> subprocess.CompletedProcess[str]:
    return subprocess.run([ADB, "-s", SERIAL, *args], capture_output=True, text=True, timeout=timeout, check=False)


def shell(*args: str, timeout: float = 20.0) -> subprocess.CompletedProcess[str]:
    return adb("shell", *args, timeout=timeout)


def foreground() -> str:
    out = shell("dumpsys", "window", timeout=20).stdout
    m = re.search(r"mCurrentFocus=Window\{.*? u0 ([^ }]+)", out)
    return m.group(1) if m else "UNKNOWN"


def fresh_source() -> tuple[bool, str]:
    shell("rm", "-f", REMOTE_XML)
    dump = shell("uiautomator", "dump", "--compressed", REMOTE_XML, timeout=15)
    if dump.returncode != 0:
        return False, ""
    cat = shell("cat", REMOTE_XML, timeout=15)
    if cat.returncode != 0:
        return False, ""
    return True, cat.stdout


def classify(source: str) -> str:
    if "screenLanding_skipButton" in source or "screenLanding_buttonReady" in source:
        return "LANDING"
    if "screenProfile_keyboardControllerScrollView" in source or "screenProfile_textInputDob-container" in source:
        return "PROFILE"
    if "Transition_Screen_Logo_Icon" in source:
        return "STARTUP_TRANSITION"
    if "termsAndConditions" in source or "Terms and Conditions" in source:
        return "TERMS"
    if re.search(r"\b(?:RGI-\d+|AJI-001)\b", source):
        return "KNOWN_ERROR"
    return "OTHER"


def observe(label: str) -> tuple[str, int | None]:
    started = time.monotonic()
    last = None
    terminal_at = None
    terminal_state = "NONE"
    while time.monotonic() - started <= WINDOW:
        elapsed = int(time.monotonic() - started)
        component = foreground()
        ok, source = fresh_source()
        state = classify(source) if ok else "DUMP_FAILED"
        sig = (component, state)
        if sig != last:
            print(f"{label} T+{elapsed:03d}s FOREGROUND={component} DUMP={'PASS' if ok else 'FAIL'} STATE={state}", flush=True)
            last = sig
        if state in {"LANDING", "PROFILE", "TERMS", "KNOWN_ERROR"}:
            terminal_at = elapsed
            terminal_state = state
            break
        time.sleep(POLL)
    print(f"{label}_RESULT STATE={terminal_state} T={terminal_at if terminal_at is not None else 'TIMEOUT'}", flush=True)
    return terminal_state, terminal_at


state = adb("get-state").stdout.strip()
print(f"ADB_STATE={'PASS' if state == 'device' else 'FAIL'}", flush=True)
if state != "device":
    raise SystemExit(1)

for index in range(1, ROUNDS + 1):
    stop = shell("am", "force-stop", PACKAGE, timeout=20)
    print(f"ROUND_{index}_FORCE_STOP={'PASS' if stop.returncode == 0 else 'FAIL'}", flush=True)
    if stop.returncode != 0:
        raise SystemExit(2)
    start = shell("am", "start", "-n", f"{PACKAGE}/{ACTIVITY}", timeout=20)
    print(f"ROUND_{index}_START={'PASS' if start.returncode == 0 else 'FAIL'}", flush=True)
    if start.returncode != 0:
        raise SystemExit(3)
    observe(f"ROUND_{index}")
