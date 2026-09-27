#!/usr/bin/env python3
"""Repo-managed forward proxy for ETB emulator networking.

The proxy only forwards HTTP and HTTPS CONNECT traffic. It does not terminate
TLS, inspect payloads, modify certificates, or persist request contents.
"""
from __future__ import annotations

import argparse
import asyncio
import hashlib
import json
import os
import shlex
import signal
import socket
import subprocess
import sys
import time
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
RUNTIME_DIR = ROOT / "local" / "runtime"
RECEIPT = RUNTIME_DIR / "etb_proxy_state.json"
LOG = RUNTIME_DIR / "etb_proxy.log"
HOST = "127.0.0.1"
PORT = 8899
MAX_HEADER = 65536
HEADER_TIMEOUT = 5.0
CONNECT_TIMEOUT = 5.0
IDLE_TIMEOUT = 30.0


def receipt_payload(pid: int) -> dict[str, object]:
    return {
        "schema": "bbl-etb-forward-proxy/v1",
        "pid": int(pid),
        "host": HOST,
        "port": PORT,
        "source_sha256": hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),
        "started_at": datetime.now(timezone.utc).isoformat(),
    }


def write_receipt(pid: int) -> None:
    RUNTIME_DIR.mkdir(parents=True, exist_ok=True)
    tmp = RECEIPT.with_suffix(".json.tmp")
    tmp.write_text(json.dumps(receipt_payload(pid), indent=2, sort_keys=True) + "\n")
    tmp.replace(RECEIPT)


def pid_alive(pid: int) -> bool:
    try:
        os.kill(pid, 0)
    except (OSError, ProcessLookupError, PermissionError):
        return False
    return True


def listener_pids() -> set[int]:
    lsof = Path("/usr/sbin/lsof")
    if not lsof.is_file():
        return set()
    cp = subprocess.run(
        [str(lsof), "-nP", f"-iTCP:{PORT}", "-sTCP:LISTEN", "-t"],
        capture_output=True,
        text=True,
        timeout=5,
        check=False,
    )
    return {int(x) for x in cp.stdout.splitlines() if x.strip().isdigit()}


def process_command(pid: int) -> str:
    cp = subprocess.run(
        ["/bin/ps", "-p", str(pid), "-o", "command="],
        capture_output=True,
        text=True,
        timeout=5,
        check=False,
    )
    return (cp.stdout or "").strip()


def receipt_pid() -> int | None:
    try:
        data = json.loads(RECEIPT.read_text())
    except (OSError, json.JSONDecodeError):
        return None
    if data.get("schema") != "bbl-etb-forward-proxy/v1":
        return None
    pid = data.get("pid")
    return pid if isinstance(pid, int) and pid > 0 else None


def readiness() -> tuple[bool, str]:
    pids = listener_pids()
    if len(pids) != 1:
        return False, "PROXY_LISTENER_MISSING" if not pids else "PROXY_LISTENER_AMBIGUOUS"
    listener = next(iter(pids))
    try:
        receipt = json.loads(RECEIPT.read_text())
    except (OSError, json.JSONDecodeError):
        return False, "PROXY_RUNTIME_RECEIPT_UNAVAILABLE"
    if not isinstance(receipt, dict) or (
        receipt.get("host") != HOST or receipt.get("port") != PORT
        or receipt.get("source_sha256") != hashlib.sha256(Path(__file__).read_bytes()).hexdigest()
    ):
        return False, "PROXY_RUNTIME_RESTART_REQUIRED"
    owned = receipt_pid()
    if owned != listener or not pid_alive(listener):
        return False, "PROXY_LISTENER_UNMANAGED"
    command = process_command(listener)
    try:
        argv = shlex.split(command)
    except ValueError:
        return False, "PROXY_LISTENER_IDENTITY_MISMATCH"
    if str(Path(__file__).resolve()) not in argv or "--serve" not in argv:
        return False, "PROXY_LISTENER_IDENTITY_MISMATCH"
    try:
        with socket.create_connection(("127.0.0.1", PORT), timeout=2):
            pass
    except OSError:
        return False, "PROXY_TCP_UNAVAILABLE"
    return True, "READY"


async def pump(reader: asyncio.StreamReader, writer: asyncio.StreamWriter) -> None:
    try:
        while True:
            data = await asyncio.wait_for(reader.read(65536), timeout=IDLE_TIMEOUT)
            if not data:
                break
            writer.write(data)
            await asyncio.wait_for(writer.drain(), timeout=IDLE_TIMEOUT)
    except (asyncio.TimeoutError, ConnectionError, OSError):
        pass
    finally:
        try:
            writer.close()
        except Exception:
            pass


async def handle(client_r: asyncio.StreamReader, client_w: asyncio.StreamWriter) -> None:
    upstream_w: asyncio.StreamWriter | None = None
    try:
        header = await asyncio.wait_for(client_r.readuntil(b"\r\n\r\n"), timeout=HEADER_TIMEOUT)
        if len(header) > MAX_HEADER:
            return
        first = header.split(b"\r\n", 1)[0].decode("latin1", "replace")
        parts = first.split()
        if len(parts) < 3:
            return
        method, target, version = parts[:3]
        if method.upper() == "CONNECT":
            if ":" not in target:
                return
            host, port_text = target.rsplit(":", 1)
            port = int(port_text)
            if not 1 <= port <= 65535 or not host or "@" in host:
                raise ValueError("INVALID_PROXY_TARGET")
            upstream_r, upstream_w = await asyncio.wait_for(
                asyncio.open_connection(host, port), timeout=CONNECT_TIMEOUT
            )
            client_w.write(b"HTTP/1.1 200 Connection Established\r\n\r\n")
            await asyncio.wait_for(client_w.drain(), timeout=IDLE_TIMEOUT)
            await asyncio.gather(pump(client_r, upstream_w), pump(upstream_r, client_w))
            return

        import re
        match = re.match(r"^http://([^/:]+)(?::(\d+))?(/.*)?$", target)
        if not match:
            return
        host = match.group(1)
        port = int(match.group(2) or 80)
        path = match.group(3) or "/"
        if not 1 <= port <= 65535:
            raise ValueError("INVALID_PROXY_TARGET")
        upstream_r, upstream_w = await asyncio.wait_for(
            asyncio.open_connection(host, port), timeout=CONNECT_TIMEOUT
        )
        lines = header.split(b"\r\n")
        lines[0] = f"{method} {path} {version}".encode("latin1")
        lines = [line for line in lines if not line.lower().startswith(b"proxy-connection:")]
        upstream_w.write(b"\r\n".join(lines))
        await asyncio.wait_for(upstream_w.drain(), timeout=IDLE_TIMEOUT)
        await asyncio.gather(pump(client_r, upstream_w), pump(upstream_r, client_w))
    except (asyncio.TimeoutError, asyncio.LimitOverrunError, asyncio.IncompleteReadError,
            ConnectionError, OSError, ValueError):
        try:
            client_w.write(b"HTTP/1.1 502 Bad Gateway\r\nContent-Length: 0\r\n\r\n")
            await asyncio.wait_for(client_w.drain(), timeout=IDLE_TIMEOUT)
        except Exception:
            pass
    finally:
        try:
            if upstream_w is not None:
                upstream_w.close()
        except Exception:
            pass
        try:
            client_w.close()
        except Exception:
            pass


async def serve() -> None:
    server = await asyncio.start_server(handle, HOST, PORT, limit=MAX_HEADER)
    write_receipt(os.getpid())
    async with server:
        await server.serve_forever()


def ensure() -> tuple[bool, str]:
    ready, category = readiness()
    if ready:
        return True, "READY"
    pids = listener_pids()
    if pids:
        return False, category if category == "PROXY_RUNTIME_RESTART_REQUIRED" else "PROXY_UNMANAGED_LISTENER"
    RUNTIME_DIR.mkdir(parents=True, exist_ok=True)
    with LOG.open("ab") as handle:
        process = subprocess.Popen(
            [sys.executable, os.fspath(Path(__file__).resolve()), "--serve"],
            cwd=str(ROOT),
            stdout=handle,
            stderr=subprocess.STDOUT,
            start_new_session=True,
            close_fds=True,
        )
    deadline = time.monotonic() + 10
    while time.monotonic() < deadline:
        if process.poll() is not None:
            return False, "PROXY_MANAGED_START_EXITED"
        ready, category = readiness()
        if ready:
            return True, "STARTED"
        time.sleep(0.2)
    try:
        os.killpg(process.pid, signal.SIGTERM)
    except OSError:
        pass
    return False, f"PROXY_MANAGED_START_TIMEOUT_{category}"


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--serve", action="store_true")
    parser.add_argument("--check", action="store_true")
    parser.add_argument("--ensure", action="store_true")
    args = parser.parse_args()
    if sum((args.serve, args.check, args.ensure)) != 1:
        raise SystemExit("PROXY_MODE_REQUIRED")
    if args.serve:
        asyncio.run(serve())
        return 0
    if args.check:
        ready, category = readiness()
    else:
        ready, category = ensure()
    if not ready:
        print(f"ETB_PROXY_READY=NO category={category}", file=sys.stderr)
        return 3
    mode = "CHECK" if args.check else category
    print(f"ETB_PROXY_READY=YES host=10.0.2.2 port={PORT} mode={mode}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
