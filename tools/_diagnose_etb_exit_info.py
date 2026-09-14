from __future__ import annotations

import os
import re
import subprocess
from pathlib import Path

SERIAL = "emulator-5554"
PACKAGE = "com.bangkokbank.blue.dev"
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


def run(*args: str, timeout: float = 20.0) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        [adb, "-s", SERIAL, *args],
        capture_output=True,
        text=True,
        timeout=timeout,
        check=False,
    )


state = run("get-state")
state_value = state.stdout.strip()
print(f"ADB_STATE={'PASS' if state_value == 'device' else 'FAIL'}")
if state_value != "device":
    raise SystemExit(1)

pid = run("shell", "pidof", PACKAGE).stdout.strip()
print(f"CURRENT_PID={'PRESENT' if pid else 'EMPTY'}")

exit_info = run("shell", "dumpsys", "activity", "exit-info", PACKAGE, timeout=30)
if exit_info.returncode != 0:
    print("EXIT_INFO=UNAVAILABLE")
else:
    patterns = re.compile(
        r"ApplicationExitInfo|timestamp=|reason=|subReason=|status=|importance=|"
        r"description=|processName=|packageUid=|realUid=|pss=|rss=|traceFile="
    )
    lines = []
    for raw_line in exit_info.stdout.splitlines():
        line = raw_line.strip()
        if patterns.search(line):
            line = re.sub(r"traceFile=.*", "traceFile=[REDACTED_PATH]", line)
            lines.append(line)
            if len(lines) >= 80:
                break
    print(f"EXIT_INFO_MATCH_COUNT={len(lines)}")
    for index, line in enumerate(lines, start=1):
        print(f"EXIT_INFO_{index:02d}={line}")

last_anr = run("shell", "dumpsys", "activity", "lastanr", timeout=30)
if last_anr.returncode != 0 or not last_anr.stdout.strip():
    print("LAST_ANR=UNAVAILABLE")
else:
    anr_pattern = re.compile(
        r"ANR in |PID:|Reason:|ErrorId:|Frozen:|Load:|CPU usage from|"
        r"Process uptime:|Cmd line:|Subject:"
    )
    anr_lines = []
    for raw_line in last_anr.stdout.splitlines():
        line = raw_line.strip()
        if anr_pattern.search(line):
            anr_lines.append(line)
            if len(anr_lines) >= 40:
                break
    print(f"LAST_ANR_MATCH_COUNT={len(anr_lines)}")
    for index, line in enumerate(anr_lines, start=1):
        print(f"LAST_ANR_{index:02d}={line}")

system_log = run(
    "logcat",
    "-d",
    "-v",
    "threadtime",
    "ActivityManager:E",
    "ActivityTaskManager:E",
    "AndroidRuntime:E",
    "WindowManager:E",
    "*:S",
    timeout=30,
)
log_lines = []
if system_log.returncode == 0:
    signal = re.compile(r"ANR in |not responding|Input dispatching timed out|AppErrors", re.I)
    for raw_line in system_log.stdout.splitlines():
        if PACKAGE in raw_line and signal.search(raw_line):
            log_lines.append(raw_line.strip())
            if len(log_lines) >= 40:
                break
print(f"SYSTEM_ANR_LOG_MATCH_COUNT={len(log_lines)}")
for index, line in enumerate(log_lines, start=1):
    print(f"SYSTEM_ANR_LOG_{index:02d}={line}")
