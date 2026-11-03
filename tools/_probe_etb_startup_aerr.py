from __future__ import annotations

import os
import re
import subprocess
import time
import xml.etree.ElementTree as ET
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
    raise SystemExit("PROBE_ADB_NOT_FOUND")


def run(*args: str, timeout: float = 20.0) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        [adb, "-s", SERIAL, *args],
        capture_output=True,
        text=True,
        timeout=timeout,
        check=False,
    )


def shell(*args: str, timeout: float = 20.0) -> subprocess.CompletedProcess[str]:
    return run("shell", *args, timeout=timeout)


def foreground() -> str:
    out = shell("dumpsys", "window", timeout=20).stdout
    match = re.search(r"mCurrentFocus=Window\{.*? u0 ([^ }]+)", out)
    return match.group(1) if match else ""


def dump_source(name: str) -> str:
    remote = f"/sdcard/{name}.xml"
    shell("uiautomator", "dump", "--compressed", remote, timeout=12)
    return shell("cat", remote, timeout=12).stdout


def marker_list(source: str, component: str) -> list[str]:
    ids = set(re.findall(r'resource-id="([^"]+)"', source))
    found: list[str] = []
    if "android:id/aerr_close" in ids:
        found.append("AERR_CLOSE")
    if "android:id/aerr_wait" in ids:
        found.append("AERR_WAIT")
    if "screenLanding_skipButton" in source:
        found.append("LANDING_SKIP")
    if "screenLanding_buttonReady" in source:
        found.append("LANDING_READY")
    if component.startswith(PACKAGE + "/"):
        found.append("FOREGROUND_TARGET")
    return found or ["NONE"]


def observe(label: str) -> tuple[list[str], str]:
    component = foreground()
    source = dump_source(f"etb_5a_{label.lower()}")
    found = marker_list(source, component)
    packages: list[str] = []
    for value in re.findall(r'package="([^"]+)"', source):
        if value and value not in packages:
            packages.append(value)
    print(
        f"OBS_{label}=MARKERS:{','.join(found)} "
        f"FOREGROUND_TARGET:{'YES' if component.startswith(PACKAGE + '/') else 'NO'} "
        f"PACKAGES:{','.join(packages[:8]) if packages else 'NONE'}"
    )
    return found, source


def bounds_center(source: str, resource_id: str) -> tuple[int, int] | None:
    try:
        root = ET.fromstring(source)
    except ET.ParseError:
        return None
    for node in root.iter():
        if node.attrib.get("resource-id") != resource_id:
            continue
        match = re.fullmatch(r"\[(\d+),(\d+)\]\[(\d+),(\d+)\]", node.attrib.get("bounds", ""))
        if match:
            x1, y1, x2, y2 = (int(value) for value in match.groups())
            return ((x1 + x2) // 2, (y1 + y2) // 2)
    return None


state = run("get-state").stdout.strip()
print(f"ADB_STATE={'PASS' if state == 'device' else 'FAIL'}")
if state != "device":
    raise SystemExit(1)

observe("BEFORE_RESET")
force_stop = shell("am", "force-stop", PACKAGE)
print(f"FORCE_STOP={'PASS' if force_stop.returncode == 0 else 'FAIL'}")
if force_stop.returncode != 0:
    raise SystemExit(1)

clear = shell("pm", "clear", PACKAGE, timeout=25)
clear_ok = clear.returncode == 0 and "success" in clear.stdout.lower()
print(f"PM_CLEAR={'PASS' if clear_ok else 'FAIL'}")
if not clear_ok:
    raise SystemExit(1)

after_reset_markers, after_reset_source = observe("AFTER_RESET_BEFORE_DISMISS")
stale_aerr = "AERR_CLOSE" in after_reset_markers and "AERR_WAIT" in after_reset_markers
print(f"STALE_AERR_AFTER_RESET={'YES' if stale_aerr else 'NO'}")

if stale_aerr:
    center = bounds_center(after_reset_source, "android:id/aerr_close")
    print(f"AERR_CLOSE_BOUNDS={'FOUND' if center else 'NOT_FOUND'}")
    if center is None:
        raise SystemExit("STALE_AERR_CLOSE_BOUNDS_NOT_FOUND")
    tap = shell("input", "tap", str(center[0]), str(center[1]))
    print(f"AERR_CLOSE_TAP={'PASS' if tap.returncode == 0 else 'FAIL'}")
    if tap.returncode != 0:
        raise SystemExit(1)
    time.sleep(0.5)

after_dismiss_markers, _ = observe("AFTER_DISMISS_BEFORE_START")
still_aerr = "AERR_CLOSE" in after_dismiss_markers or "AERR_WAIT" in after_dismiss_markers
print(f"AERR_PRESENT_AFTER_DISMISS={'YES' if still_aerr else 'NO'}")
if still_aerr:
    raise SystemExit("STALE_AERR_DISMISSAL_FAILED")

launch_wall_epoch = time.time()
launch = shell("am", "start", "-n", f"{PACKAGE}/{ACTIVITY}")
launch_ok = launch.returncode == 0 and "Error" not in launch.stdout
print(f"APP_START={'PASS' if launch_ok else 'FAIL'}")
if not launch_ok:
    raise SystemExit(1)

last = 0.0
post_start_aerr = False
for index, elapsed in enumerate((0.1, 0.5, 1.0, 2.0, 5.0, 10.0), start=1):
    delay = elapsed - last
    if delay > 0:
        time.sleep(delay)
    last = elapsed
    component = foreground()
    source = dump_source(f"etb_5a_after_start_{index}")
    found = marker_list(source, component)
    if "AERR_CLOSE" in found or "AERR_WAIT" in found:
        post_start_aerr = True
    print(
        f"OBS_TPLUS_{elapsed:04.1f}=MARKERS:{','.join(found)} "
        f"FOREGROUND_TARGET:{'YES' if component.startswith(PACKAGE + '/') else 'NO'}"
    )
print(f"POST_START_AERR_SEEN={'YES' if post_start_aerr else 'NO'}")

system_log = run("logcat", "-d", "-v", "epoch", timeout=30)
signals: list[str] = []
if system_log.returncode == 0:
    signal = re.compile(r"ANR in |not responding|Input dispatching timed out|AppErrors|am_anr", re.I)
    for raw_line in system_log.stdout.splitlines():
        match = re.match(r"^(\d+(?:\.\d+)?)\s+", raw_line)
        if not match or float(match.group(1)) + 0.001 < launch_wall_epoch:
            continue
        if PACKAGE in raw_line and signal.search(raw_line):
            signals.append(re.sub(r"\s+", " ", raw_line.strip()))
            if len(signals) >= 20:
                break
print(f"POST_LAUNCH_ANR_SIGNAL_COUNT={len(signals)}")
for index, line in enumerate(signals, start=1):
    print(f"POST_LAUNCH_ANR_SIGNAL_{index:02d}={line}")

last_anr = shell("dumpsys", "activity", "lastanr", timeout=30)
print(f"POST_LAUNCH_LAST_ANR_FOR_TARGET={'YES' if PACKAGE in last_anr.stdout else 'NO'}")

cleanup = shell("am", "force-stop", PACKAGE)
print(f"FINAL_FORCE_STOP={'PASS' if cleanup.returncode == 0 else 'FAIL'}")
