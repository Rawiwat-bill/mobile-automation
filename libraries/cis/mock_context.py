"""Approved DEV_MOCK identity validation for CIS automation."""

from __future__ import annotations

import re
import subprocess
from collections.abc import Callable
from typing import Any

MOCK_ENVIRONMENT = "DEV_MOCK"
MOCK_SOURCE = "MOCK_BUILD_NOT_REQUIRED"
MOCK_UDID = "emulator-5558"
MOCK_AVD = "Pixel_10"
MOCK_PACKAGE = "com.bangkokbank.blue.dev"
MOCK_ACTIVITY = "com.bangkokbank.blue.MainActivity"
MOCK_VERSION_NAME = "1.13.0-alpha-93-146-Unshield"
MOCK_VERSION_CODE = "146"


def validate_mock_build_context(
    environment: str,
    readiness_source: str | None,
    device_udid: str | None,
    *,
    run_command: Callable[..., Any],
) -> None:
    """Reject mock CIS mode unless the exact approved local build is installed."""
    if environment.upper() != MOCK_ENVIRONMENT:
        raise ValueError("MOCK_CIS_INVALID_ENVIRONMENT")
    if readiness_source != MOCK_SOURCE:
        raise ValueError("MOCK_CIS_SOURCE_REQUIRED")
    if device_udid != MOCK_UDID:
        raise ValueError("MOCK_CIS_INVALID_DEVICE")

    def adb(*args: str) -> str:
        result = run_command(
            ["adb", "-s", MOCK_UDID, *args],
            check=True,
            capture_output=True,
            text=True,
            timeout=10,
        )
        return result.stdout.replace("\r", "")

    try:
        avd = adb("shell", "getprop", "ro.boot.qemu.avd_name").strip()
        package_path = adb("shell", "pm", "path", MOCK_PACKAGE).strip()
        package = adb("shell", "dumpsys", "package", MOCK_PACKAGE)
        activity = adb(
            "shell",
            "cmd",
            "package",
            "resolve-activity",
            "--brief",
            "-a",
            "android.intent.action.MAIN",
            "-c",
            "android.intent.category.LAUNCHER",
            MOCK_PACKAGE,
        ).strip().splitlines()[-1]
    except (OSError, subprocess.SubprocessError, IndexError) as exc:
        raise ValueError("MOCK_CIS_CONTEXT_UNAVAILABLE") from exc

    if not package_path.startswith("package:"):
        raise ValueError("MOCK_CIS_INVALID_PACKAGE")
    version_name = re.search(r"versionName=([^\s]+)", package)
    version_code = re.search(r"versionCode=([^\s]+)", package)
    if avd != MOCK_AVD:
        raise ValueError("MOCK_CIS_INVALID_AVD")
    if not version_name or version_name.group(1) != MOCK_VERSION_NAME:
        raise ValueError("MOCK_CIS_INVALID_VERSION_NAME")
    if not version_code or version_code.group(1) != MOCK_VERSION_CODE:
        raise ValueError("MOCK_CIS_INVALID_VERSION_CODE")
    if activity != f"{MOCK_PACKAGE}/{MOCK_ACTIVITY}":
        raise ValueError("MOCK_CIS_INVALID_ACTIVITY")
