#!/usr/bin/env python3
"""Sanitized, read-only CIS transport readiness probe for ETB DEV."""
from __future__ import annotations

import argparse
import json
import os
import shlex
import socket
import ssl
import sys
from pathlib import Path
from typing import Mapping

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from libraries.cis import transport as cis_transport


_KEYS = ("CIS_CLEAR_URL", "PDPA_CA_BUNDLE", "SSL_CERT_FILE")


def load_simple_env(path: Path) -> dict[str, str]:
    values: dict[str, str] = {}
    if not path.is_file():
        return values
    for raw in path.read_text(encoding="utf-8", errors="ignore").splitlines():
        line = raw.strip()
        if not line or line.startswith("#"):
            continue
        if line.startswith("export "):
            line = line[7:].strip()
        if "=" not in line:
            continue
        key, value = line.split("=", 1)
        key = key.strip()
        if key not in _KEYS:
            continue
        try:
            parts = shlex.split(value, posix=True)
        except ValueError:
            continue
        if len(parts) == 1:
            values[key] = parts[0]
        elif not value.strip():
            values[key] = ""
    return values


def effective_config(
    base: Mapping[str, str] | None = None,
    *,
    env_file: Path | None = None,
) -> dict[str, str]:
    base_values = dict(os.environ if base is None else base)
    path = env_file if env_file is not None else ROOT / "local/env/etb.env"
    values = load_simple_env(path)
    # Match runner precedence: explicitly exported caller values override local defaults.
    for key in _KEYS:
        if key in base_values:
            values[key] = base_values[key]
    return values


def probe_payload(
    config: Mapping[str, str],
    *,
    probe_func=cis_transport.probe,
) -> dict[str, str]:
    url = config.get("CIS_CLEAR_URL", "")
    ca_bundle = config.get("PDPA_CA_BUNDLE") or config.get("SSL_CERT_FILE")
    result = probe_func(
        url,
        30,
        ca_bundle=ca_bundle,
        getaddrinfo=socket.getaddrinfo,
        create_connection=socket.create_connection,
        create_default_context=ssl.create_default_context,
    )
    return {
        "ready": str(result.get("ready") or "NO"),
        "transport_category": str(result.get("transport_category") or "OTHER_TRANSPORT_FAILURE"),
    }


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--require-ready", action="store_true")
    args = parser.parse_args()

    payload = probe_payload(effective_config())
    print("ETB_CIS_TRANSPORT_STATUS=" + json.dumps(payload, sort_keys=True))
    if args.require_ready and payload["ready"] != "YES":
        return 3
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
