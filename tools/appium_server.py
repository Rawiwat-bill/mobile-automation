#!/usr/bin/env python3
"""Launch, ensure, and validate the repo-managed Appium server.

IRIS/package runners may sandbox HOME to the project root and omit Android SDK
variables. Appium resolves installed drivers from APPIUM_HOME/HOME and
UiAutomator2 resolves ADB from ANDROID_HOME/ANDROID_SDK_ROOT. This launcher
restores those account-level runtime variables and records a local runtime
receipt.

ETB uses --ensure: reuse a healthy managed listener, or start one detached only
when port 4723 is free. An unknown listener is never killed or adopted.
"""
from __future__ import annotations

import argparse
import json
import os
import pwd
import shutil
import signal
import subprocess
import time
import urllib.request
from datetime import datetime, timezone
from pathlib import Path
from typing import Mapping

PROJECT_ROOT = Path(__file__).resolve().parents[1]
RUNTIME_DIR = PROJECT_ROOT / "local" / "runtime"
RUNTIME_RECEIPT = RUNTIME_DIR / "appium_server_state.json"
RUNTIME_LOG = RUNTIME_DIR / "appium_server.log"
STATUS_URL = "http://127.0.0.1:4723/status"


def account_home() -> Path:
    try:
        return Path(pwd.getpwuid(os.getuid()).pw_dir)
    except (KeyError, OSError):
        return Path.home()


def resolve_android_sdk_root(
    env: Mapping[str, str],
    *,
    home: Path,
) -> Path:
    candidates: list[Path] = []
    for key in ("ANDROID_SDK_ROOT", "ANDROID_HOME"):
        value = env.get(key, "").strip()
        if value:
            candidates.append(Path(value))

    candidates.extend(
        (
            home / "Library" / "Android" / "sdk",
            home / "Android" / "Sdk",
            home / "Android" / "sdk",
        )
    )

    for candidate in candidates:
        adb = candidate / "platform-tools" / ("adb.exe" if os.name == "nt" else "adb")
        if adb.is_file():
            return candidate
    raise FileNotFoundError("ANDROID_SDK_ROOT_NOT_FOUND")


def build_environment(
    base: Mapping[str, str] | None = None,
    *,
    home: Path | None = None,
    sdk_root: Path | None = None,
) -> dict[str, str]:
    env = dict(os.environ if base is None else base)
    resolved_home = home if home is not None else account_home()
    resolved_sdk = (
        sdk_root
        if sdk_root is not None
        else resolve_android_sdk_root(env, home=resolved_home)
    )

    env["HOME"] = str(resolved_home)
    env["APPIUM_HOME"] = str(resolved_home / ".appium")
    env["ANDROID_HOME"] = str(resolved_sdk)
    env["ANDROID_SDK_ROOT"] = str(resolved_sdk)
    return env


def build_argv(appium: str, *, inspector: bool = False) -> list[str]:
    argv = [
        appium,
        "--address",
        "127.0.0.1",
        "--allow-insecure=uiautomator2:adb_shell",
    ]
    if inspector:
        argv.extend(["--use-plugins=inspector", "--allow-cors"])
    return argv


def runtime_receipt_payload(
    env: Mapping[str, str],
    *,
    pid: int | None = None,
) -> dict[str, object]:
    return {
        "schema": "bbl-appium-runtime/v1",
        "pid": int(os.getpid() if pid is None else pid),
        "appium_home": str(env["APPIUM_HOME"]),
        "android_sdk_root": str(env["ANDROID_SDK_ROOT"]),
        "started_at": datetime.now(timezone.utc).isoformat(),
    }


def receipt_matches_environment(payload: object, env: Mapping[str, str]) -> bool:
    if not isinstance(payload, dict) or payload.get("schema") != "bbl-appium-runtime/v1":
        return False
    pid = payload.get("pid")
    if not isinstance(pid, int) or pid <= 0:
        return False
    return (
        payload.get("appium_home") == env.get("APPIUM_HOME")
        and payload.get("android_sdk_root") == env.get("ANDROID_SDK_ROOT")
    )


def write_runtime_receipt(
    env: Mapping[str, str],
    path: Path = RUNTIME_RECEIPT,
    *,
    pid: int | None = None,
) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    temporary = path.with_suffix(path.suffix + ".tmp")
    temporary.write_text(
        json.dumps(runtime_receipt_payload(env, pid=pid), sort_keys=True, indent=2) + "\n",
        encoding="utf-8",
    )
    temporary.replace(path)


def _pid_alive(pid: int) -> bool:
    try:
        os.kill(pid, 0)
    except (ProcessLookupError, PermissionError, OSError):
        return False
    return True


def _listener_pids(port: int = 4723) -> set[int]:
    lsof = Path("/usr/sbin/lsof")
    if not lsof.is_file():
        return set()
    result = subprocess.run(
        [str(lsof), "-nP", f"-iTCP:{port}", "-sTCP:LISTEN", "-t"],
        capture_output=True,
        text=True,
        timeout=5,
        check=False,
    )
    return {
        int(line.strip())
        for line in result.stdout.splitlines()
        if line.strip().isdigit()
    }


def _listener_pid(port: int = 4723) -> int | None:
    pids = _listener_pids(port)
    if len(pids) != 1:
        return None
    return next(iter(pids))


def check_runtime_readiness(
    *,
    receipt_path: Path = RUNTIME_RECEIPT,
    status_url: str = STATUS_URL,
) -> tuple[bool, str]:
    try:
        env = build_environment()
    except FileNotFoundError:
        return False, "ANDROID_SDK_ROOT_NOT_FOUND"

    driver = Path(env["APPIUM_HOME"]) / "node_modules" / "appium-uiautomator2-driver"
    if not driver.is_dir():
        return False, "UIAUTOMATOR2_DRIVER_NOT_FOUND"

    try:
        payload = json.loads(receipt_path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError):
        return False, "APPIUM_RUNTIME_RECEIPT_UNAVAILABLE"
    if not receipt_matches_environment(payload, env):
        return False, "APPIUM_RUNTIME_RECEIPT_MISMATCH"

    pid = int(payload["pid"])
    if not _pid_alive(pid):
        return False, "APPIUM_RUNTIME_PID_NOT_ALIVE"

    listener_pids = _listener_pids()
    if not listener_pids:
        return False, "APPIUM_RUNTIME_LISTENER_MISSING"
    if len(listener_pids) > 1:
        return False, "APPIUM_RUNTIME_LISTENER_AMBIGUOUS"
    if listener_pids and pid not in listener_pids:
        return False, "APPIUM_RUNTIME_LISTENER_MISMATCH"

    try:
        with urllib.request.urlopen(status_url, timeout=3) as response:
            body = json.loads(response.read().decode("utf-8"))
            ready = (
                response.status == 200
                and isinstance(body, dict)
                and isinstance(body.get("value"), dict)
                and body["value"].get("ready") is True
            )
    except (OSError, ValueError, json.JSONDecodeError):
        return False, "APPIUM_STATUS_UNAVAILABLE"
    if not ready:
        return False, "APPIUM_STATUS_NOT_READY"
    return True, "READY"


def _terminate_owned_process_group(pid: int) -> None:
    if not _pid_alive(pid):
        return
    try:
        pgid = os.getpgid(pid)
    except OSError:
        return
    if pgid != pid:
        return
    try:
        os.killpg(pgid, signal.SIGTERM)
    except (ProcessLookupError, PermissionError, OSError):
        return


def ensure_runtime_readiness(
    *,
    startup_timeout: float = 15.0,
) -> tuple[bool, str]:
    ready, category = check_runtime_readiness()
    if ready:
        return True, "READY"

    listeners = _listener_pids()
    if listeners:
        return False, "APPIUM_UNMANAGED_LISTENER"

    try:
        env = build_environment()
    except FileNotFoundError:
        return False, "ANDROID_SDK_ROOT_NOT_FOUND"

    driver = Path(env["APPIUM_HOME"]) / "node_modules" / "appium-uiautomator2-driver"
    if not driver.is_dir():
        return False, "UIAUTOMATOR2_DRIVER_NOT_FOUND"

    executable = shutil.which("appium")
    if not executable:
        return False, "APPIUM_EXECUTABLE_NOT_FOUND"

    RUNTIME_DIR.mkdir(parents=True, exist_ok=True)
    with RUNTIME_LOG.open("ab") as handle:
        process = subprocess.Popen(
            build_argv(executable),
            cwd=str(PROJECT_ROOT),
            env=env,
            stdout=handle,
            stderr=subprocess.STDOUT,
            start_new_session=True,
            close_fds=True,
        )
    write_runtime_receipt(env, pid=process.pid)

    deadline = time.monotonic() + float(startup_timeout)
    last_category = category
    while time.monotonic() < deadline:
        if process.poll() is not None:
            return False, "APPIUM_MANAGED_START_EXITED"
        ready, last_category = check_runtime_readiness()
        if ready:
            return True, "STARTED"
        time.sleep(0.25)

    _terminate_owned_process_group(process.pid)
    return False, f"APPIUM_MANAGED_START_TIMEOUT_{last_category}"


def reconcile_runtime_readiness() -> tuple[bool, str]:
    """Compatibility entry point; only reuse an already proven owned runtime.

    Command-line resemblance cannot establish process environment/ownership.
    ensure_runtime_readiness refuses existing unknown listeners without writing
    or deleting their receipts, terminating them, or adopting them.
    """
    return ensure_runtime_readiness()


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--inspector", action="store_true")
    parser.add_argument("--check", action="store_true")
    parser.add_argument("--ensure", action="store_true")
    parser.add_argument("--reconcile", action="store_true")
    args = parser.parse_args()

    if sum((args.check, args.ensure, args.reconcile)) > 1:
        raise SystemExit("APPIUM_MODE_CONFLICT")

    if args.check:
        ready, category = check_runtime_readiness()
        if not ready:
            print(f"APPIUM_RUNTIME_READY=NO category={category}", file=os.sys.stderr)
            return 3
        print("APPIUM_RUNTIME_READY=YES driver=uiautomator2 sdk=READY receipt=PASS mode=CHECK")
        return 0

    if args.ensure:
        ready, category = ensure_runtime_readiness()
        if not ready:
            print(f"APPIUM_RUNTIME_READY=NO category={category}", file=os.sys.stderr)
            return 3
        print(
            "APPIUM_RUNTIME_READY=YES "
            f"driver=uiautomator2 sdk=READY receipt=PASS mode={category}"
        )
        return 0

    if args.reconcile:
        ready, category = reconcile_runtime_readiness()
        if not ready:
            print(f"APPIUM_RUNTIME_READY=NO category={category}", file=os.sys.stderr)
            return 3
        print(
            "APPIUM_RUNTIME_READY=YES "
            f"driver=uiautomator2 sdk=READY receipt=PASS mode={category}"
        )
        return 0

    executable = shutil.which("appium")
    if not executable:
        raise SystemExit("APPIUM_EXECUTABLE_NOT_FOUND")

    try:
        env = build_environment()
    except FileNotFoundError as exc:
        raise SystemExit(str(exc)) from None

    write_runtime_receipt(env)
    os.execve(executable, build_argv(executable, inspector=args.inspector), env)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
