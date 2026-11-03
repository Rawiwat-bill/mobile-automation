"""Shared Android ADB executable resolution.

Keeps every automation layer on the same physical ADB binary even when HOME/PATH
are sandboxed by a package runner. Resolution is read-only and fail-closed.
"""
from __future__ import annotations

import os
import shutil
import sys
from pathlib import Path

try:
    import pwd
except ImportError:  # Windows
    pwd = None


def resolve_adb_executable() -> str:
    candidates: list[Path] = []

    for sdk_root in (
        os.environ.get("ANDROID_HOME", ""),
        os.environ.get("ANDROID_SDK_ROOT", ""),
    ):
        if sdk_root:
            root = Path(sdk_root)
            candidates.append(root / "platform-tools" / "adb")
            candidates.append(root / "platform-tools" / "adb.exe")

    if sys.platform == "darwin":
        account_home = _account_home()
        if account_home is not None:
            candidates.append(
                account_home / "Library" / "Android" / "sdk" / "platform-tools" / "adb"
            )
    elif os.name == "nt":
        local_app_data = os.environ.get("LOCALAPPDATA", "")
        if local_app_data:
            candidates.append(
                Path(local_app_data) / "Android" / "Sdk" / "platform-tools" / "adb.exe"
            )
        user_profile = os.environ.get("USERPROFILE", "")
        if user_profile:
            candidates.append(
                Path(user_profile)
                / "AppData"
                / "Local"
                / "Android"
                / "Sdk"
                / "platform-tools"
                / "adb.exe"
            )
    else:
        account_home = _account_home()
        if account_home is not None:
            candidates.extend(
                (
                    account_home / "Android" / "Sdk" / "platform-tools" / "adb",
                    account_home / "Android" / "sdk" / "platform-tools" / "adb",
                )
            )

    for candidate in candidates:
        if candidate.is_file() and os.access(candidate, os.X_OK):
            return str(candidate)

    found = shutil.which("adb")
    if found:
        return found
    raise FileNotFoundError("adb executable not found")


def _account_home() -> Path | None:
    if pwd is not None:
        try:
            return Path(pwd.getpwuid(os.getuid()).pw_dir)
        except (KeyError, OSError):
            pass

    for variable in ("USERPROFILE", "HOME"):
        value = os.environ.get(variable, "")
        if value:
            return Path(value)
    return None
