#!/usr/bin/env python3
"""Fail-closed device readiness with an opt-in standalone startup observer.

The normal ETB runtime calls this module without ``--observe``. In that mode
the runner verifies device readiness only; Robot owns reset, launch, and the
authoritative startup-state observation.
"""
from __future__ import annotations

import argparse
import json
import re
import subprocess
import sys
import time
import urllib.request
from datetime import datetime, timezone
from pathlib import Path

PACKAGE = "com.bangkokbank.blue.dev"
ACTIVITY = "com.bangkokbank.blue.MainActivity"
EXPECTED_MANUFACTURER = "HUAWEI"
EXPECTED_MODEL = "MGA-LX3"
APPROVED_BUILD_IDENTITIES = {
    "DEV": ("1.14.0-debug-network-post-mmp-1-alpha-12-170-Unshield", "170"),
    "SIT": ("1.12.11-16-Unshield", "16"),
}
LANDING_MARKERS = ("screenLanding_skipButton", "screenLanding_buttonReady")
TERMS_MARKERS = ("Terms and Conditions", "termsAndConditions")
EXACT_ERROR_TEXT_MARKERS = (
    "Something went wrong on our side",
    "Please try again later",
    "Close app",
    "The app requires newer operating system",
)
EXACT_ERROR_CODE_PATTERN = re.compile(r"\b(?:RGI-\d+|AJI-001)\b")


def adb(serial: str, *args: str, timeout: float = 10, check: bool = True) -> str:
    result = subprocess.run(
        ["adb", "-s", serial, *args], capture_output=True, text=True, timeout=timeout
    )
    if check and result.returncode:
        raise RuntimeError((result.stderr or result.stdout).strip() or f"adb failed: {args}")
    return (result.stdout or "").replace("\r", "")


def prop(serial: str, name: str) -> str:
    return adb(serial, "shell", "getprop", name).strip()


def validate_target_identity(
    serial: str,
    execution_target: str,
    environment: str,
    package: str,
    activity: str,
    competing_package: str,
) -> dict:
    """Read-only, fail-closed guard before ETB backend or package preparation.

    Serial/AVD policy follows AGENTS.md. DEV_MOCK retains the isolated target
    already required by cis_preparation.validate_mock_build_context; its exact
    build/source validation still runs separately before preparation.

    Runtime requires an already-installed, identifiable target application.
    Missing/unknown builds require a separate approved provisioning operation;
    this guard never installs, removes, wakes, resets, or launches anything.
    """
    def require(condition: bool, reason: str) -> None:
        if not condition:
            raise ValueError("TARGET_GUARD_" + reason)

    require(isinstance(serial, str) and bool(re.fullmatch(r"[A-Za-z0-9][A-Za-z0-9_.:-]{0,199}", serial)), "SERIAL_REQUIRED_OR_INVALID")
    require(environment in {"DEV", "SIT", "DEV_MOCK"}, "ENVIRONMENT_INVALID")
    require(execution_target in {"REAL", "DIAGNOSTIC_CONTROL"}, "EXECUTION_TARGET_INVALID")
    expected_package = "com.bangkokbank.blue.sit" if environment == "SIT" else "com.bangkokbank.blue.dev"
    expected_competing = "com.bangkokbank.blue.dev" if environment == "SIT" else "com.bangkokbank.blue.sit"
    require(package == expected_package and competing_package == expected_competing, "PACKAGE_POLICY_MISMATCH")
    require(activity == "com.bangkokbank.blue.MainActivity", "ACTIVITY_POLICY_MISMATCH")
    emulator_targets = {
        "DEV": ("emulator-5554", "local_android_36"),
        "SIT": ("emulator-5556", "Pixel_8"),
        "DEV_MOCK": ("emulator-5558", "Pixel_10"),
    }
    if execution_target == "DIAGNOSTIC_CONTROL":
        expected_serial, expected_avd = emulator_targets[environment]
        require(serial == expected_serial, "ENVIRONMENT_SERIAL_MISMATCH")
    else:
        require(not serial.startswith("emulator-") and environment != "DEV_MOCK", "REAL_TARGET_MISMATCH")

    try:
        require(adb(serial, "get-state").strip() == "device", "DEVICE_NOT_READY")
        require(prop(serial, "sys.boot_completed") == "1", "BOOT_NOT_COMPLETE")
        qemu = prop(serial, "ro.kernel.qemu")
        if execution_target == "DIAGNOSTIC_CONTROL":
            require(qemu == "1", "EMULATOR_IDENTITY_MISMATCH")
            require(prop(serial, "ro.boot.qemu.avd_name") == expected_avd, "AVD_MISMATCH")
        else:
            require(qemu in {"0", ""}, "REAL_TARGET_MISMATCH")
            require(prop(serial, "ro.product.manufacturer").upper() == EXPECTED_MANUFACTURER, "MANUFACTURER_MISMATCH")
            require(prop(serial, "ro.product.model").upper() == EXPECTED_MODEL, "MODEL_MISMATCH")
        require(adb(serial, "shell", "pm", "path", package).strip().startswith("package:"), "TARGET_PACKAGE_MISSING")
        app_info = adb(serial, "shell", "dumpsys", "package", package)
        version_code = re.search(r"\bversionCode=(\d+)", app_info)
        version_name = re.search(r"\bversionName=([^\s]+)", app_info)
        require(bool(version_code and version_name) and version_name.group(1).lower() not in {"null", "unknown"}, "BUILD_UNIDENTIFIED")
        assert version_code is not None and version_name is not None
        approved_identity = APPROVED_BUILD_IDENTITIES.get(environment)
        if approved_identity is not None:
            require(
                (version_name.group(1), version_code.group(1)) == approved_identity,
                "BUILD_APPROVAL_MISMATCH",
            )
        resolved = adb(
            serial, "shell", "cmd", "package", "resolve-activity", "--brief",
            "-a", "android.intent.action.MAIN", "-c", "android.intent.category.LAUNCHER", package,
        ).strip().splitlines()
        require(bool(resolved) and resolved[-1] == f"{package}/{activity}", "LAUNCHER_MISMATCH")
    except (OSError, subprocess.SubprocessError, RuntimeError):
        # Never echo raw command output, serials, or transport exception data.
        raise ValueError("TARGET_GUARD_OBSERVATION_FAILED") from None
    return {
        "target_identity": "PASS",
        "environment": environment,
        "execution_target": execution_target,
        "package": package,
        "activity": activity,
        "build_identified": True,
        "build_approval": "PASS" if environment in APPROVED_BUILD_IDENTITIES else "DELEGATED_TO_ENVIRONMENT_VALIDATOR",
        "operation_count": 0,
    }


def foreground(serial: str) -> str:
    text = adb(serial, "shell", "dumpsys", "window", check=False)
    match = re.search(r"mCurrentFocus=Window\{.*? u0 ([^ }]+)", text)
    return match.group(1) if match else ""


def ui_dump(serial: str, destination: Path) -> str:
    adb(serial, "shell", "uiautomator", "dump", "/data/local/tmp/hermes_startup.xml", check=False)
    xml = adb(serial, "shell", "cat", "/data/local/tmp/hermes_startup.xml", check=False)
    destination.write_text(xml, encoding="utf-8")
    return xml


def has_exact_application_error(source: str) -> bool:
    """Return true only for an explicit application error message or code."""
    return any(marker in source for marker in EXACT_ERROR_TEXT_MARKERS) or bool(EXACT_ERROR_CODE_PATTERN.search(source))


def keyguard_inactive(serial: str) -> bool:
    power = adb(serial, "shell", "dumpsys", "power", check=False)
    policy = adb(serial, "shell", "dumpsys", "window", "policy", check=False)
    awake = "mWakefulness=Awake" in power or "mWakefulness=Dozing" in power
    restricted = re.search(r"mInputRestricted=(true|false)", policy)
    showing = re.search(r"mShowingLockscreen=(true|false)", policy)
    return awake and (not restricted or restricted.group(1) == "false") and (not showing or showing.group(1) == "false")


def appium_ready(url: str) -> bool:
    try:
        with urllib.request.urlopen(url.rstrip("/") + "/status", timeout=5) as response:
            body = json.loads(response.read().decode("utf-8"))
            return response.status == 200 and body.get("value", {}).get("ready") is True
    except Exception:
        return False


def readiness(serial: str, report_dir: Path, appium_url: str, package: str, activity: str) -> dict:
    report_dir = report_dir / "private_local"
    report_dir.mkdir(parents=True, exist_ok=True)
    checks: dict[str, str] = {}
    try:
        checks["ADB_RESPONSIVE"] = "YES" if adb(serial, "get-state").strip() == "device" else "NO"
    except Exception:
        checks["ADB_RESPONSIVE"] = "NO"
    devices = subprocess.run(["adb", "devices"], capture_output=True, text=True, check=False).stdout
    checks["DEVICE_CONNECTED"] = "YES" if re.search(rf"^{re.escape(serial)}\s+device\b", devices, re.M) else "NO"
    manufacturer = prop(serial, "ro.product.manufacturer") if checks["ADB_RESPONSIVE"] == "YES" else ""
    model = prop(serial, "ro.product.model") if checks["ADB_RESPONSIVE"] == "YES" else ""
    checks["DEVICE_REAL"] = "YES" if manufacturer.upper() == EXPECTED_MANUFACTURER and model.upper() == EXPECTED_MODEL else "NO"
    # Readiness is observational: leave a locked/asleep device unchanged.
    checks["DEVICE_UNLOCKED"] = "YES" if keyguard_inactive(serial) else "NO"
    checks["SCREEN_AWAKE"] = "YES" if checks["DEVICE_UNLOCKED"] == "YES" else "NO"
    checks["KEYGUARD_INACTIVE"] = checks["DEVICE_UNLOCKED"]
    checks["APPIUM_READY"] = "YES" if appium_ready(appium_url) else "NO"
    checks["TARGET_PACKAGE_INSTALLED"] = "YES" if adb(serial, "shell", "pm", "path", package, check=False).startswith("package:") else "NO"
    resolved = adb(serial, "shell", "cmd", "package", "resolve-activity", "--brief", "-a", "android.intent.action.MAIN", "-c", "android.intent.category.LAUNCHER", package, check=False).strip().splitlines()
    resolved_activity = resolved[-1] if resolved else ""
    checks["TARGET_ACTIVITY_RESOLVED"] = "YES" if resolved_activity == f"{package}/{activity}" else "NO"
    stay_on = adb(serial, "shell", "settings", "get", "global", "stay_on_while_plugged_in", check=False).strip()
    checks["STAY_ON_WHILE_PLUGGED_IN"] = "YES" if stay_on.isdigit() and int(stay_on) > 0 else "NO"
    app_info = adb(serial, "shell", "dumpsys", "package", package, check=False)
    version_code = re.search(r"versionCode=(\d+)", app_info)
    version_name = re.search(r"versionName=([^\s]+)", app_info)
    result = {
        "artifact_classification": "PRIVATE_LOCAL",
        "timestamp_utc": datetime.now(timezone.utc).isoformat(),
        "serial": serial,
        "manufacturer": manufacturer,
        "model": model,
        "android": prop(serial, "ro.build.version.release") if manufacturer else "",
        "api": prop(serial, "ro.build.version.sdk") if manufacturer else "",
        "package": package,
        "activity": activity,
        "resolved_activity": resolved_activity,
        "version_name": version_name.group(1) if version_name else "UNKNOWN",
        "version_code": version_code.group(1) if version_code else "UNKNOWN",
        "checks": checks,
    }
    (report_dir / "device_preflight.json").write_text(json.dumps(result, indent=2) + "\n", encoding="utf-8")
    failed = [name for name, value in checks.items() if value != "YES"]
    if failed:
        print("REAL_DEVICE_PREFLIGHT=FAIL " + ",".join(failed), file=sys.stderr)
        return result
    print("REAL_DEVICE_PREFLIGHT=PASS")
    print("readiness=" + " ".join(f"{k}={v}" for k, v in checks.items()))
    return result


def observe_startup(serial: str, report_dir: Path, timeout: float, interval: float) -> int:
    report_dir = report_dir / "private_local"
    report_dir.mkdir(parents=True, exist_ok=True)
    adb(serial, "shell", "am", "force-stop", PACKAGE)
    started_at = time.monotonic()
    adb(serial, "shell", "am", "start", "-n", f"{PACKAGE}/{ACTIVITY}")
    timeline = []
    terminal = {"LANDING", "PERMISSION_DIALOG", "TERMS", "KNOWN_ERROR"}
    while True:
        elapsed = round(time.monotonic() - started_at, 3)
        snapshot = report_dir / "startup_last.xml"
        xml = ui_dump(serial, snapshot)
        fg = foreground(serial)
        if any(marker in xml for marker in LANDING_MARKERS):
            state = "LANDING"
        elif "permissioncontroller" in xml or "GrantPermissionsActivity" in fg:
            state = "PERMISSION_DIALOG"
        elif any(marker in xml for marker in TERMS_MARKERS):
            state = "TERMS"
        elif has_exact_application_error(xml):
            state = "KNOWN_ERROR"
        elif PACKAGE in fg:
            state = "STARTUP_TRANSITION"
        elif not fg or "launcher" in fg.lower():
            state = "APP_INITIALIZING"
        else:
            state = "UNKNOWN"
        if not timeline or timeline[-1]["state"] != state:
            timeline.append({"state": state, "elapsed_seconds": elapsed, "foreground": fg})
            print(f"STARTUP_STATE={state} elapsed={elapsed:.3f}s")
        if state in terminal or elapsed >= timeout:
            break
        time.sleep(interval)
    subprocess.run(
        ["adb", "-s", serial, "exec-out", "screencap", "-p"],
        stdout=(report_dir / "startup_terminal.png").open("wb"),
        check=False,
        timeout=10,
    )
    (report_dir / "startup_terminal.window.txt").write_text(
        adb(serial, "shell", "dumpsys", "window", check=False), encoding="utf-8"
    )
    result = {"serial": serial, "package": PACKAGE, "activity": ACTIVITY, "timeout_seconds": timeout, "poll_interval_seconds": interval, "terminal_state": timeline[-1]["state"], "timeline": timeline}
    (report_dir / "startup_timeline.json").write_text(json.dumps(result, indent=2) + "\n", encoding="utf-8")
    if timeline[-1]["state"] not in terminal:
        print(f"STARTUP_OBSERVER=FAIL terminal_state={timeline[-1]['state']} timeout={timeout}s", file=sys.stderr)
        return 4
    print(f"STARTUP_OBSERVER={timeline[-1]['state']} first_business_screen={timeline[-1]['state']}")
    return 0 if timeline[-1]["state"] != "KNOWN_ERROR" else 5


def main() -> int:
    global PACKAGE, ACTIVITY
    parser = argparse.ArgumentParser()
    parser.add_argument("--serial", required=True)
    parser.add_argument("--report-dir", required=True, type=Path)
    parser.add_argument("--observe", action="store_true")
    parser.add_argument("--appium-url", default="http://127.0.0.1:4723")
    parser.add_argument("--package", default=PACKAGE)
    parser.add_argument("--activity", default=ACTIVITY)
    parser.add_argument("--timeout", type=float, default=45)
    parser.add_argument("--interval", type=float, default=1)
    args = parser.parse_args()
    PACKAGE = args.package
    ACTIVITY = args.activity
    result = readiness(args.serial, args.report_dir, args.appium_url, PACKAGE, ACTIVITY)
    if any(v != "YES" for v in result["checks"].values()):
        return 3
    return observe_startup(args.serial, args.report_dir, args.timeout, args.interval) if args.observe else 0


if __name__ == "__main__":
    sys.exit(main())
