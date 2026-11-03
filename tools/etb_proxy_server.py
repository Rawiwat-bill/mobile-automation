#!/usr/bin/env python3
"""Repo-managed forward proxy for ETB emulator networking.

The proxy only forwards HTTP and HTTPS CONNECT traffic. It does not terminate
TLS, inspect payloads, modify certificates, or persist request contents.
"""
from __future__ import annotations

import argparse
import asyncio
import itertools
import json
import hashlib
import os
import re
import signal
import shlex
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
TELEMETRY_DIR = ROOT / "reports" / "investigation" / "tc004_god002_tunnel_telemetry" / "private_local"
TELEMETRY_LOG = TELEMETRY_DIR / "tunnel_telemetry.jsonl"
ACTIVE_TUNNELS_FILE = TELEMETRY_DIR / "active_tunnels.json"
HOST = "127.0.0.1"
PORT = 8899
MAX_HEADER = 65536
HEADER_TIMEOUT = 5.0
CONNECT_TIMEOUT = 5.0
IDLE_TIMEOUT = 30.0
MAX_ACTIVITY_EVENTS = 1024
HOST_OVERRIDES = {"www-u.bangkokbank.com": "115.178.57.243"}
CLOSE_REASONS = frozenset({
    "CLIENT_EOF",
    "UPSTREAM_EOF",
    "IDLE_TIMEOUT_CLIENT_TO_UPSTREAM",
    "IDLE_TIMEOUT_UPSTREAM_TO_CLIENT",
    "CONNECTION_RESET",
    "CONNECT_FAILURE",
    "NORMAL_COMPLETION",
})
_HOST_RE = re.compile(r"^[A-Za-z0-9](?:[A-Za-z0-9.-]*[A-Za-z0-9])?$")
_TUNNEL_COUNTER = itertools.count(1)
_ACTIVE_TUNNELS: dict[int, dict[str, object]] = {}


def _utc_now() -> str:
    return datetime.now(timezone.utc).isoformat()


def _parse_iso(ts: str | None) -> float | None:
    if not ts or not isinstance(ts, str):
        return None
    try:
        return datetime.fromisoformat(ts.replace("Z", "+00:00")).timestamp()
    except ValueError:
        return None


def next_tunnel_id() -> int:
    return next(_TUNNEL_COUNTER)


def sanitize_target_host(raw_host: str) -> str:
    """Keep only a validated lowercase hostname; strip any userinfo, path, or query."""
    candidate = (raw_host or "").strip()
    candidate = re.sub(r"^[a-zA-Z][a-zA-Z0-9+.-]*://", "", candidate)
    candidate = candidate.split("/", 1)[0].split("?", 1)[0].split("#", 1)[0]
    if "@" in candidate:
        candidate = candidate.rsplit("@", 1)[-1]
    if ":" in candidate:
        candidate = candidate.rsplit(":", 1)[0]
    candidate = candidate.strip().lower()
    if not candidate or not _HOST_RE.fullmatch(candidate):
        return "REDACTED_HOST"
    return candidate


def new_tunnel_state(target_host: str, target_port: int, *, opened_at: str | None = None) -> dict[str, object]:
    tunnel_id = next_tunnel_id()
    state: dict[str, object] = {
        "schema": "bbl-etb-proxy-tunnel-telemetry/v1",
        "tunnel_id": tunnel_id,
        "target_host": sanitize_target_host(target_host),
        "target_port": int(target_port),
        "opened_at": opened_at or _utc_now(),
        "closed_at": None,
        "close_reason": None,
        "client_to_upstream_bytes": 0,
        "upstream_to_client_bytes": 0,
        "last_client_to_upstream_at": None,
        "last_upstream_to_client_at": None,
        "existed_across_confirm_pin_interval": None,
        "upstream_bytes_increased_after_terminal_request": None,
        "activity": [],
        "_closing": False,
        "_eof_directions": set(),
    }
    _ACTIVE_TUNNELS[tunnel_id] = state
    _persist_active_tunnels()
    return state


def _record_transfer(state: dict[str, object], direction: str, byte_count: int, *, at: str | None = None) -> None:
    if byte_count <= 0:
        return
    ts = at or _utc_now()
    if direction == "client_to_upstream":
        state["client_to_upstream_bytes"] = int(state.get("client_to_upstream_bytes", 0)) + int(byte_count)
        state["last_client_to_upstream_at"] = ts
    elif direction == "upstream_to_client":
        state["upstream_to_client_bytes"] = int(state.get("upstream_to_client_bytes", 0)) + int(byte_count)
        state["last_upstream_to_client_at"] = ts
    activity = state.get("activity")
    if isinstance(activity, list) and len(activity) < MAX_ACTIVITY_EVENTS:
        activity.append({
            "direction": direction,
            "at": ts,
            "bytes": int(byte_count),
        })
    _persist_active_tunnels()


def _finalize_direction(state: dict[str, object], outcome: str) -> None:
    if state.get("close_reason") is not None:
        return
    eof_dirs = state.get("_eof_directions")
    if outcome in ("CLIENT_EOF", "UPSTREAM_EOF") and isinstance(eof_dirs, set) and len(eof_dirs) >= 2:
        state["close_reason"] = "NORMAL_COMPLETION"
    else:
        state["close_reason"] = outcome if outcome in CLOSE_REASONS else "CONNECTION_RESET"
    state["_closing"] = True


def evaluate_tunnel_window(
    record: dict[str, object],
    *,
    confirm_pin_start: str | None = None,
    confirm_pin_end: str | None = None,
    terminal_request_at: str | None = None,
) -> dict[str, object]:
    """Compute interval and post-request byte correlation using sanitized timestamps only."""
    result = {k: v for k, v in record.items() if not str(k).startswith("_")}
    opened_ts = _parse_iso(str(result.get("opened_at") or ""))
    closed_ts = _parse_iso(str(result.get("closed_at") or ""))
    pin_start_ts = _parse_iso(confirm_pin_start)
    pin_end_ts = _parse_iso(confirm_pin_end)
    req_ts = _parse_iso(terminal_request_at)

    if opened_ts is not None and pin_start_ts is not None and pin_end_ts is not None:
        result["existed_across_confirm_pin_interval"] = bool(
            opened_ts <= pin_start_ts and (closed_ts is None or closed_ts >= pin_end_ts)
        )

    if req_ts is not None:
        activity = result.get("activity") if isinstance(result.get("activity"), list) else []
        c2u_after = 0
        u2c_after = 0
        prior_ts: float | None = opened_ts
        first_after_ts: float | None = None
        had_prior_activity = False
        for item in activity:
            if not isinstance(item, dict):
                continue
            ev_ts = _parse_iso(str(item.get("at") or ""))
            ev_bytes = int(item.get("bytes") or 0)
            ev_dir = item.get("direction")
            if ev_ts is None or ev_bytes <= 0:
                continue
            if ev_ts < req_ts:
                had_prior_activity = True
                if prior_ts is None or ev_ts > prior_ts:
                    prior_ts = ev_ts
            else:
                if first_after_ts is None or ev_ts < first_after_ts:
                    first_after_ts = ev_ts
                if ev_dir == "client_to_upstream":
                    c2u_after += ev_bytes
                elif ev_dir == "upstream_to_client":
                    u2c_after += ev_bytes
        if not activity:
            last_u2c_ts = _parse_iso(str(result.get("last_upstream_to_client_at") or ""))
            if last_u2c_ts is not None and last_u2c_ts >= req_ts and int(result.get("upstream_to_client_bytes") or 0) > 0:
                u2c_after = int(result.get("upstream_to_client_bytes") or 0)
        result["upstream_bytes_increased_after_terminal_request"] = u2c_after > 0
        result["client_to_upstream_bytes_after_request"] = c2u_after
        result["upstream_to_client_bytes_after_request"] = u2c_after
        result["tunnel_reuse"] = "REUSED" if (had_prior_activity or (opened_ts is not None and opened_ts < req_ts - 1.0)) else "NEW"
        if prior_ts is not None:
            ref_ts = first_after_ts if first_after_ts is not None else req_ts
            result["pre_request_idle_duration_seconds"] = round(max(0.0, ref_ts - prior_ts), 6)
    return result


def sanitized_tunnel_record(state: dict[str, object]) -> dict[str, object]:
    evaluated = evaluate_tunnel_window(
        state,
        confirm_pin_start=os.environ.get("ETB_TELEMETRY_CONFIRM_PIN_START"),
        confirm_pin_end=os.environ.get("ETB_TELEMETRY_CONFIRM_PIN_END"),
        terminal_request_at=os.environ.get("ETB_TELEMETRY_TERMINAL_REQUEST_AT"),
    )
    allowed_keys = (
        "schema",
        "tunnel_id",
        "target_host",
        "target_port",
        "opened_at",
        "closed_at",
        "close_reason",
        "client_to_upstream_bytes",
        "upstream_to_client_bytes",
        "last_client_to_upstream_at",
        "last_upstream_to_client_at",
        "existed_across_confirm_pin_interval",
        "upstream_bytes_increased_after_terminal_request",
        "client_to_upstream_bytes_after_request",
        "upstream_to_client_bytes_after_request",
        "tunnel_reuse",
        "pre_request_idle_duration_seconds",
        "activity",
    )
    return {k: evaluated[k] for k in allowed_keys if k in evaluated}


def _persist_active_tunnels() -> None:
    try:
        ACTIVE_TUNNELS_FILE.parent.mkdir(parents=True, exist_ok=True)
        payload = [sanitized_tunnel_record(s) for s in _ACTIVE_TUNNELS.values()]
        tmp = ACTIVE_TUNNELS_FILE.with_suffix(".json.tmp")
        tmp.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n")
        tmp.replace(ACTIVE_TUNNELS_FILE)
    except OSError:
        pass


def finalize_tunnel_state(state: dict[str, object], *, close_reason: str | None = None, closed_at: str | None = None) -> dict[str, object]:
    if close_reason is not None and state.get("close_reason") is None:
        state["close_reason"] = close_reason if close_reason in CLOSE_REASONS else "CONNECTION_RESET"
    if state.get("close_reason") is None:
        state["close_reason"] = "NORMAL_COMPLETION"
    if state.get("closed_at") is None:
        state["closed_at"] = closed_at or _utc_now()
    tunnel_id = state.get("tunnel_id")
    if isinstance(tunnel_id, int):
        _ACTIVE_TUNNELS.pop(tunnel_id, None)
    record = sanitized_tunnel_record(state)
    try:
        TELEMETRY_LOG.parent.mkdir(parents=True, exist_ok=True)
        with TELEMETRY_LOG.open("a", encoding="utf-8") as handle:
            handle.write(json.dumps(record, sort_keys=True) + "\n")
    except OSError:
        pass
    _persist_active_tunnels()
    return record


def upstream_host(host: str) -> str:
    """Use the approved DEV bootstrap address while preserving TLS SNI."""
    return HOST_OVERRIDES.get(host.lower(), host)


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
        receipt.get("host") != HOST or receipt.get("port") != PORT or
        receipt.get("source_sha256") != hashlib.sha256(Path(__file__).read_bytes()).hexdigest()
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
    # Exact module path, not an arbitrary process whose command contains a name.
    if str(Path(__file__).resolve()) not in argv or "--serve" not in argv:
        return False, "PROXY_LISTENER_IDENTITY_MISMATCH"
    try:
        with socket.create_connection(("127.0.0.1", PORT), timeout=2):
            pass
    except OSError:
        return False, "PROXY_TCP_UNAVAILABLE"
    return True, "READY"


async def pump(
    reader: asyncio.StreamReader,
    writer: asyncio.StreamWriter,
    direction: str = "client_to_upstream",
    state: dict[str, object] | None = None,
) -> str:
    outcome = "NORMAL_COMPLETION"
    try:
        while True:
            data = await asyncio.wait_for(reader.read(65536), timeout=IDLE_TIMEOUT)
            if not data:
                outcome = "CLIENT_EOF" if direction == "client_to_upstream" else "UPSTREAM_EOF"
                if state is not None and not state.get("_closing"):
                    eof_dirs = state.get("_eof_directions")
                    if isinstance(eof_dirs, set):
                        eof_dirs.add(direction)
                    await asyncio.sleep(0)
                break
            if state is not None:
                _record_transfer(state, direction, len(data))
            writer.write(data)
            await asyncio.wait_for(writer.drain(), timeout=IDLE_TIMEOUT)
    except asyncio.TimeoutError:
        outcome = (
            "IDLE_TIMEOUT_CLIENT_TO_UPSTREAM"
            if direction == "client_to_upstream"
            else "IDLE_TIMEOUT_UPSTREAM_TO_CLIENT"
        )
    except (ConnectionError, OSError):
        outcome = "CONNECTION_RESET"
    finally:
        if state is not None:
            _finalize_direction(state, outcome)
        try:
            writer.close()
        except Exception:
            pass
    return outcome


async def handle(client_r: asyncio.StreamReader, client_w: asyncio.StreamWriter) -> None:
    upstream_w: asyncio.StreamWriter | None = None
    tunnel_state: dict[str, object] | None = None
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
            tunnel_state = new_tunnel_state(host, port)
            upstream_r, upstream_w = await asyncio.wait_for(
                asyncio.open_connection(upstream_host(host), port), timeout=CONNECT_TIMEOUT
            )
            client_w.write(b"HTTP/1.1 200 Connection Established\r\n\r\n")
            await asyncio.wait_for(client_w.drain(), timeout=IDLE_TIMEOUT)
            await asyncio.gather(
                pump(client_r, upstream_w, "client_to_upstream", tunnel_state),
                pump(upstream_r, client_w, "upstream_to_client", tunnel_state),
            )
            return

        # Absolute-form HTTP request. Resolve on the host so VPN/corporate DNS
        # stays authoritative for the emulator.
        match = re.match(r"^http://([^/:]+)(?::(\d+))?(/.*)?$", target)
        if not match:
            return
        host = match.group(1)
        port = int(match.group(2) or 80)
        path = match.group(3) or "/"
        if not 1 <= port <= 65535:
            raise ValueError("INVALID_PROXY_TARGET")
        tunnel_state = new_tunnel_state(host, port)
        upstream_r, upstream_w = await asyncio.wait_for(
            asyncio.open_connection(upstream_host(host), port), timeout=CONNECT_TIMEOUT
        )
        lines = header.split(b"\r\n")
        lines[0] = f"{method} {path} {version}".encode("latin1")
        lines = [line for line in lines if not line.lower().startswith(b"proxy-connection:")]
        forwarded = b"\r\n".join(lines)
        _record_transfer(tunnel_state, "client_to_upstream", len(forwarded))
        upstream_w.write(forwarded)
        await asyncio.wait_for(upstream_w.drain(), timeout=IDLE_TIMEOUT)
        await asyncio.gather(
            pump(client_r, upstream_w, "client_to_upstream", tunnel_state),
            pump(upstream_r, client_w, "upstream_to_client", tunnel_state),
        )
    except (asyncio.TimeoutError, asyncio.LimitOverrunError, asyncio.IncompleteReadError, ConnectionError, OSError, ValueError):
        if tunnel_state is not None and tunnel_state.get("close_reason") is None:
            tunnel_state["close_reason"] = "CONNECT_FAILURE"
        try:
            client_w.write(b"HTTP/1.1 502 Bad Gateway\r\nContent-Length: 0\r\n\r\n")
            await asyncio.wait_for(client_w.drain(), timeout=IDLE_TIMEOUT)
        except Exception:
            pass
    finally:
        if tunnel_state is not None:
            finalize_tunnel_state(tunnel_state)
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
    import sys
    raise SystemExit(main())
