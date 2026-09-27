from __future__ import annotations

import os
import re
import subprocess
import time
from pathlib import Path

SERIAL = "emulator-5554"
PACKAGE = "com.bangkokbank.blue.dev"
ACTIVITY = "com.bangkokbank.blue.MainActivity"
SDK_CANDIDATES = [
    os.environ.get("ANDROID_HOME", ""),
    os.environ.get("ANDROID_SDK_ROOT", ""),
    str(Path.home() / "Library/Android/sdk"),
]

adb = None
for root in SDK_CANDIDATES:
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


def foreground() -> str:
    out = shell("dumpsys", "window", timeout=20).stdout
    match = re.search(r"mCurrentFocus=Window\{.*? u0 ([^ }]+)", out)
    return match.group(1) if match else "UNKNOWN"


def dump_source() -> str:
    shell("uiautomator", "dump", "--compressed", "/sdcard/etb_tc001_diag.xml", timeout=12)
    return shell("cat", "/sdcard/etb_tc001_diag.xml", timeout=12).stdout


def classify(source: str, component: str) -> list[str]:
    labels: list[str] = []
    markers = {
        "LANDING_SKIP": "screenLanding_skipButton",
        "LANDING_READY": "screenLanding_buttonReady",
        "LANDING_LANGUAGE": "screenLanding_languageSwitch",
        "PERMISSION_CONTROLLER": "permissioncontroller",
        "TERMS_TEXT": "Terms and Conditions",
        "TERMS_ID": "termsAndConditions",
        "KNOWN_AJI": "AJI-001",
        "KNOWN_RGI": "RGI-",
    }
    lower = source.lower()
    for label, marker in markers.items():
        haystack = lower if label == "PERMISSION_CONTROLLER" else source
        needle = marker.lower() if label == "PERMISSION_CONTROLLER" else marker
        if needle in haystack:
            labels.append(label)
    if component.startswith(PACKAGE + "/"):
        labels.append("FOREGROUND_TARGET")
    return labels


def resource_ids(source: str) -> str:
    values = []
    for value in re.findall(r'resource-id="([^"]+)"', source):
        if value and value not in values:
            values.append(value)
        if len(values) >= 12:
            break
    return ",".join(values) if values else "NONE"


state = run("get-state").stdout.strip()
print(f"ADB_STATE={'PASS' if state == 'device' else 'FAIL'}")
if state != "device":
    raise SystemExit(1)

clear = shell("pm", "clear", PACKAGE, timeout=20)
clear_ok = clear.returncode == 0 and "success" in clear.stdout.lower()
print(f"PM_CLEAR={'PASS' if clear_ok else 'FAIL'}")
if not clear_ok:
    raise SystemExit(1)

launch = shell("am", "start", "-n", f"{PACKAGE}/{ACTIVITY}")
print(f"APP_START={'PASS' if launch.returncode == 0 else 'FAIL'}")
if launch.returncode != 0:
    raise SystemExit(1)

last = 0
for elapsed in (1, 5, 15, 30, 45, 60, 75, 90):
    time.sleep(elapsed - last)
    last = elapsed
    component = foreground()
    source = dump_source()
    labels = classify(source, component)
    print(
        f"T+{elapsed:02d}s COMPONENT={component} "
        f"MARKERS={','.join(labels) if labels else 'NONE'} "
        f"IDS={resource_ids(source)} SOURCE_NONEMPTY={'YES' if bool(source.strip()) else 'NO'}"
    )
