#!/usr/bin/env python3
"""Fail-fast ETB network/proxy gate for the selected DEV diagnostic target."""
from __future__ import annotations

import argparse
import json
import os
import re
import socket
import subprocess
import sys
import time
import zipfile
from pathlib import Path
from urllib.parse import urlsplit

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from libraries.android_adb import resolve_adb_executable

EXPECTED_PROXY = "10.0.2.2:8888"
MANAGED_PROXY = "10.0.2.2:8899"
CHARLES_EXECUTABLE = "/Applications/Charles.app/Contents/MacOS/Charles"


def selected_proxy() -> tuple[str, str]:
    mode = os.environ.get("ETB_NETWORK_PROXY_MODE", "CHARLES").strip().upper()
    if mode == "CHARLES":
        return mode, EXPECTED_PROXY
    if mode == "MANAGED":
        return mode, MANAGED_PROXY
    raise RuntimeError("ETB_NETWORK_PROXY_MODE_INVALID")


def managed_proxy_readiness(*, ensure: bool) -> tuple[bool, str]:
    command = [sys.executable, str(ROOT / "tools/etb_proxy_server.py"), "--ensure" if ensure else "--check"]
    result = subprocess.run(command, capture_output=True, text=True, timeout=15, check=False)
    return (result.returncode == 0, "READY" if result.returncode == 0 else "MANAGED_PROXY_NOT_READY")


def charles_readiness() -> tuple[bool, str]:
    """Validate the approved external proxy without starting or changing it."""
    port = int(EXPECTED_PROXY.rsplit(":", 1)[1])
    listeners = subprocess.run(
        ["/usr/sbin/lsof", "-nP", f"-iTCP:{port}", "-sTCP:LISTEN", "-t"],
        capture_output=True, text=True, timeout=5, check=False,
    )
    if listeners.returncode not in (0, 1):
        return False, "PROXY_LISTENER_CHECK_FAILED"
    pids = set(listeners.stdout.split())
    if not pids:
        return False, "PROXY_LISTENER_MISSING"
    if len(pids) != 1:
        return False, "PROXY_LISTENER_AMBIGUOUS"
    pid = pids.pop()
    if not pid.isdigit():
        return False, "PROXY_LISTENER_IDENTITY_MISMATCH"
    process = subprocess.run(
        ["/bin/ps", "-p", pid, "-o", "comm="],
        capture_output=True, text=True, timeout=5, check=False,
    )
    if process.returncode != 0 or process.stdout.strip() != CHARLES_EXECUTABLE:
        return False, "PROXY_LISTENER_IDENTITY_MISMATCH"
    try:
        with socket.create_connection(("127.0.0.1", port), timeout=2):
            pass
    except OSError:
        return False, "PROXY_TCP_UNAVAILABLE"
    return True, "READY"


def adb(serial: str, *args: str, timeout: int = 15) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        [resolve_adb_executable(), "-s", serial, *args],
        capture_output=True,
        text=True,
        timeout=timeout,
        check=False,
    )


def ensure_charles() -> tuple[bool, str]:
    """Open the approved app once if absent; never replace another listener."""
    ready, category = charles_readiness()
    if ready or category != "PROXY_LISTENER_MISSING":
        return ready, category
    result = subprocess.run(
        ["/usr/bin/open", "-a", str(Path(CHARLES_EXECUTABLE).parents[2])],
        capture_output=True, text=True, timeout=5, check=False,
    )
    if result.returncode:
        return False, "CHARLES_START_FAILED"
    deadline = time.monotonic() + 30
    while True:
        ready, category = charles_readiness()
        if ready or category != "PROXY_LISTENER_MISSING":
            return ready, category
        remaining = deadline - time.monotonic()
        if remaining <= 0:
            return False, "CHARLES_START_TIMEOUT"
        time.sleep(min(0.5, remaining))


def get_proxy(serial: str) -> str:
    result = adb(serial, "shell", "settings", "get", "global", "http_proxy")
    if result.returncode != 0:
        raise RuntimeError("ETB_PROXY_READ_FAILED")
    return (result.stdout or "").strip()


def set_proxy(serial: str, value: str) -> None:
    result = adb(serial, "shell", "settings", "put", "global", "http_proxy", value)
    if result.returncode != 0:
        raise RuntimeError("ETB_PROXY_SET_FAILED")


def _configured_dev_hosts() -> list[str] | None:
    """Read the HTTPS hosts used by startup and the DEV backend from the APK."""
    try:
        with zipfile.ZipFile(ROOT / "apps/android/app-dev.apk") as apk:
            names = set(apk.namelist())
            if "assets/EnvironmentConfig.json" in names:
                config = json.loads(apk.read("assets/EnvironmentConfig.json"))
                hosts = []
                for key in ("API_BASE_URL", "IMAGE_BASE_URL"):
                    value = config.get(key)
                    if value is None and key == "IMAGE_BASE_URL":
                        continue
                    if not isinstance(value, str):
                        return None
                    url = urlsplit(value)
                    host = url.hostname
                    if url.scheme != "https" or not host or not re.fullmatch(r"[A-Za-z0-9](?:[A-Za-z0-9.-]*[A-Za-z0-9])?", host):
                        return None
                    hosts.append(host)
                return hosts or None
            if "classes.dex" in names:
                dex = apk.read("classes.dex")
                hosts = []
                for raw in re.findall(rb"https://([A-Za-z0-9.-]+(?:\.tosulmara\.com|\.bangkokbank\.com))(?=/|\x00)", dex):
                    host = raw.decode("ascii", "ignore")
                    if re.fullmatch(r"[A-Za-z0-9](?:[A-Za-z0-9.-]*[A-Za-z0-9])?", host) and host not in hosts:
                        hosts.append(host)
                return hosts or None
            return None
    except (OSError, ValueError, KeyError, TypeError, zipfile.BadZipFile):
        return None


def native_dns_readiness(serial: str) -> tuple[bool, str]:
    """Check device DNS independently of Charles resolving names on the host."""
    hosts = _configured_dev_hosts()
    if not hosts:
        return False, "DEV_BACKEND_CONFIG_INVALID"
    for host in hosts:
        try:
            result = adb(serial, "shell", "timeout", "5", "ping", "-c", "1", "-W", "1", host, timeout=8)
        except subprocess.TimeoutExpired:
            return False, "DEV_BACKEND_DNS_UNAVAILABLE"
        # Cloud endpoints may reject ICMP; the resolved address is the DNS evidence.
        if not re.search(r"(?m)^PING [^\n]*\([0-9a-fA-F:.]+\)", result.stdout or ""):
            return False, "DEV_BACKEND_DNS_UNAVAILABLE"
    return True, "READY"


def enforce(serial: str, environment: str, execution_target: str, *, ensure_proxy: bool = False) -> tuple[bool, str]:
    if not (
        environment.upper() == "DEV"
        and execution_target.upper() == "DIAGNOSTIC_CONTROL"
    ):
        return True, "NOT_APPLICABLE"

    state = adb(serial, "get-state")
    if state.returncode != 0 or (state.stdout or "").strip() != "device":
        return False, "ETB_PROXY_DEVICE_NOT_READY"

    mode, expected_proxy = selected_proxy()
    observed = get_proxy(serial)
    if observed != expected_proxy:
        return False, "ETB_PROXY_DEVICE_CONFIG_MISMATCH"

    if mode == "MANAGED":
        ready, category = managed_proxy_readiness(ensure=ensure_proxy)
    else:
        ready, category = ensure_charles() if ensure_proxy else charles_readiness()
    if not ready:
        return False, category
    if mode == "MANAGED":
        return True, "LOCAL_READY"
    ready, category = native_dns_readiness(serial)
    if not ready:
        return False, category
    return True, "LOCAL_READY"


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--serial", required=True)
    parser.add_argument("--environment", required=True)
    parser.add_argument("--execution-target", required=True)
    parser.add_argument("--ensure-charles", action="store_true")
    args = parser.parse_args()

    try:
        ready, category = enforce(args.serial, args.environment, args.execution_target, ensure_proxy=args.ensure_charles)
    except (OSError, RuntimeError, subprocess.TimeoutExpired):
        ready, category = False, "ETB_PROXY_PREFLIGHT_ERROR"

    if not ready:
        print(f"ETB_NETWORK_GATE=CLOSED category={category}", file=sys.stderr)
        return 3
    if category == "NOT_APPLICABLE":
        print("ETB_NETWORK_GATE=NOT_APPLICABLE")
    else:
        mode, expected_proxy = selected_proxy()
        native_dns = "PROXY_RESOLVED" if mode == "MANAGED" else "READY"
        print(
            "ETB_NETWORK_GATE=LOCAL_READY "
            f"serial={args.serial} proxy={expected_proxy} host_listener=READY native_dns={native_dns} "
            "upstream=NOT_CHECKED service=NOT_CHECKED"
        )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
