from __future__ import annotations

import importlib.util
import os
import re
import subprocess
from pathlib import Path

ADB_PATH: Path | None = None
for android_sdk_root in (
    os.environ.get("ANDROID_HOME", ""),
    os.environ.get("ANDROID_SDK_ROOT", ""),
    str(Path.home() / "Library/Android/sdk"),
):
    candidate = Path(android_sdk_root) / "platform-tools" / "adb" if android_sdk_root else None
    if candidate and candidate.is_file():
        ADB_PATH = candidate
        os.environ["PATH"] = f"{candidate.parent}{os.pathsep}{os.environ.get('PATH', '')}"
        break
if ADB_PATH is None:
    raise SystemExit("DIAG_ADB_NOT_FOUND")

source = Path(__file__).with_name("real_device_preflight.py")
spec = importlib.util.spec_from_file_location("guard_under_diagnosis", source)
if spec is None or spec.loader is None:
    raise SystemExit("DIAGNOSTIC_IMPORT=FAIL")
guard = importlib.util.module_from_spec(spec)
spec.loader.exec_module(guard)

SERIAL = "emulator-5554"
PACKAGE = "com.bangkokbank.blue.dev"
ACTIVITY = "com.bangkokbank.blue.MainActivity"


def check(name, callback, predicate=lambda value: True):
    try:
        value = callback()
        ok = bool(predicate(value))
        print(f"{name}={'PASS' if ok else 'FAIL'}")
        return ok
    except Exception as exc:
        print(f"{name}=ERROR:{type(exc).__name__}")
        return False


def serial_status() -> str:
    result = subprocess.run(
        [str(ADB_PATH), "devices"], capture_output=True, text=True, timeout=10, check=False
    )
    if result.returncode:
        return "ADB_ERROR"
    for line in result.stdout.replace("\r", "").splitlines()[1:]:
        fields = line.split()
        if fields and fields[0] == SERIAL:
            status = fields[1].upper() if len(fields) > 1 else "UNKNOWN"
            if status == "DEVICE":
                return "DEVICE"
            if status == "OFFLINE":
                return "OFFLINE"
            if status == "UNAUTHORIZED":
                return "UNAUTHORIZED"
            return "OTHER"
    return "MISSING"


status = serial_status()
print(f"ADB_SERIAL_STATUS={status}")
results = [status == "DEVICE"]
results.append(check("ADB_STATE", lambda: guard.adb(SERIAL, "get-state").strip(), lambda v: v == "device"))
results.append(check("BOOT", lambda: guard.prop(SERIAL, "sys.boot_completed"), lambda v: v == "1"))
results.append(check("QEMU", lambda: guard.prop(SERIAL, "ro.kernel.qemu"), lambda v: v == "1"))
results.append(check("AVD_PROP", lambda: guard.prop(SERIAL, "ro.boot.qemu.avd_name"), lambda v: v == "local_android_36"))
results.append(check("PACKAGE_PATH", lambda: guard.adb(SERIAL, "shell", "pm", "path", PACKAGE), lambda v: v.strip().startswith("package:")))
results.append(check("PACKAGE_INFO", lambda: guard.adb(SERIAL, "shell", "dumpsys", "package", PACKAGE, timeout=30), lambda v: bool(re.search(r"versionCode=170\b", v) and re.search(r"versionName=1\.14\.0-debug-network-post-mmp-1-alpha-12-170-Unshield\b", v))))
results.append(check("LAUNCHER", lambda: guard.adb(SERIAL, "shell", "cmd", "package", "resolve-activity", "--brief", "-a", "android.intent.action.MAIN", "-c", "android.intent.category.LAUNCHER", PACKAGE, timeout=30), lambda v: v.strip().splitlines()[-1:] == [f"{PACKAGE}/{ACTIVITY}"]))
raise SystemExit(0 if all(results) else 1)
