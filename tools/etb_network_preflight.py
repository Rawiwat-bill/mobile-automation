#!/usr/bin/env python3
"""Fail-fast ETB network/proxy gate for the canonical Pixel 10 DEV emulator."""
from __future__ import annotations

import argparse
import importlib.util
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from libraries.android_adb import resolve_adb_executable

EXPECTED_SERIAL = "emulator-5556"
EXPECTED_PROXY = "10.0.2.2:8899"


def load_proxy_module():
    path = ROOT / "tools" / "etb_proxy_server.py"
    spec = importlib.util.spec_from_file_location("etb_proxy_server_runtime", path)
    if spec is None or spec.loader is None:
        raise RuntimeError("ETB_PROXY_MODULE_UNAVAILABLE")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def adb(serial: str, *args: str, timeout: int = 15) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        [resolve_adb_executable(), "-s", serial, *args],
        capture_output=True,
        text=True,
        timeout=timeout,
        check=False,
    )


def get_proxy(serial: str) -> str:
    result = adb(serial, "shell", "settings", "get", "global", "http_proxy")
    if result.returncode != 0:
        raise RuntimeError("ETB_PROXY_READ_FAILED")
    return (result.stdout or "").strip()


def set_proxy(serial: str, value: str) -> None:
    result = adb(serial, "shell", "settings", "put", "global", "http_proxy", value)
    if result.returncode != 0:
        raise RuntimeError("ETB_PROXY_SET_FAILED")


def enforce(serial: str, environment: str, execution_target: str) -> tuple[bool, str]:
    if not (
        serial == EXPECTED_SERIAL
        and environment.upper() == "DEV"
        and execution_target.upper() == "DIAGNOSTIC_CONTROL"
    ):
        return True, "NOT_APPLICABLE"

    state = adb(serial, "get-state")
    if state.returncode != 0 or (state.stdout or "").strip() != "device":
        return False, "ETB_PROXY_DEVICE_NOT_READY"

    observed = get_proxy(serial)
    if observed != EXPECTED_PROXY:
        return False, "ETB_PROXY_DEVICE_CONFIG_MISMATCH"

    proxy_module = load_proxy_module()
    ready, category = proxy_module.ensure()
    if not ready:
        return False, category

    ready, category = proxy_module.readiness()
    if not ready:
        return False, category
    return True, "LOCAL_READY"


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--serial", required=True)
    parser.add_argument("--environment", required=True)
    parser.add_argument("--execution-target", required=True)
    args = parser.parse_args()

    try:
        ready, category = enforce(args.serial, args.environment, args.execution_target)
    except (OSError, RuntimeError, subprocess.TimeoutExpired):
        ready, category = False, "ETB_PROXY_PREFLIGHT_ERROR"

    if not ready:
        print(f"ETB_NETWORK_GATE=CLOSED category={category}", file=sys.stderr)
        return 3
    if category == "NOT_APPLICABLE":
        print("ETB_NETWORK_GATE=NOT_APPLICABLE")
    else:
        print(
            "ETB_NETWORK_GATE=LOCAL_READY "
            f"serial={args.serial} proxy={EXPECTED_PROXY} host_listener=READY "
            "upstream=NOT_CHECKED service=NOT_CHECKED"
        )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
