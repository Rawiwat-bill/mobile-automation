#!/usr/bin/env python3
"""
Performance Observatory — Benchmark Parser

Reads Robot Framework output.xml or log.txt from a benchmark run,
extracts BENCHMARK| structured lines, and generates:
  - reports/performance/latest.json      (JSON summary)
  - reports/performance/latest.md        (Markdown summary)
  - reports/performance/history/<ts>.json (timestamped archive)

Usage:
  python3 tools/performance/parse_benchmark.py \
      --source reports/benchmark/output.xml \
      [--outdir reports/performance]

If --source is omitted, scans reports/benchmark*/output.xml for the
newest output.xml.
"""

import argparse
import glob
import json
import os
import re
import sys
from datetime import datetime, timezone
from xml.etree import ElementTree

BENCHMARK_DIR = "reports/benchmark"
PERF_DIR = "reports/performance"
HISTORY_DIR = os.path.join(PERF_DIR, "history")
BENCHMARK_PATTERN_NEW = re.compile(
    r"(?:\[?BENCHMARK\]?\|)(?P<name>[^|]+)\|(?P<field>[^|]*)\|(?P<strategy>[^|]*)\|"
    r"(?P<result>[^|]*)\|(?P<total>[^|]*)\|(?P<wait>[^|]*)\|"
    r"(?P<scroll>[^|]*)\|(?P<appium>[^|]*)\|(?P<adb>[^|]*)\|"
    r"(?P<screenshots>[^|]*)\|(?P<retries>[^|]*)"
)


def find_newest_xml():
    candidates = glob.glob(f"{BENCHMARK_DIR}*/output.xml") + glob.glob(f"{BENCHMARK_DIR}/output.xml")
    if not candidates:
        print(f"[ERROR] No output.xml found under {BENCHMARK_DIR}*/")
        sys.exit(1)
    return max(candidates, key=os.path.getmtime)


def parse_output_xml(path):
    """Yield BENCHMARK| or [BENCHMARK]| lines from Robot output.xml msg elements."""
    tree = ElementTree.parse(path)
    root = tree.getroot()
    for msg in root.iter("msg"):
        text = msg.text or ""
        for line in text.splitlines():
            line = line.strip()
            if line.startswith("BENCHMARK|") or line.startswith("[BENCHMARK]|"):
                yield line


def parse_line(line):
    m = BENCHMARK_PATTERN_NEW.match(line)
    if not m:
        return None
    d = m.groupdict()
    # Convert numeric fields
    for key in ("total", "wait", "scroll"):
        try:
            d[key] = float(d[key])
        except (ValueError, TypeError):
            d[key] = 0.0
    for key in ("appium", "adb", "screenshots", "retries"):
        try:
            d[key] = int(d[key])
        except (ValueError, TypeError):
            d[key] = 0
    return d


def summarize(records):
    """Build a structured summary from parsed records."""
    fields = {}
    for r in records:
        field = r["field"]
        if field not in fields:
            fields[field] = {"strategies": [], "fastest": None, "slowest": None}
        fields[field]["strategies"].append(r)
    for field, info in fields.items():
        passed = [s for s in info["strategies"] if s["result"] == "PASS"]
        if passed:
            passed.sort(key=lambda x: x["total"])
            info["fastest"] = passed[0]
            info["slowest"] = passed[-1]
            info["ranked"] = passed
        else:
            info["ranked"] = []
    return {
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "source": "benchmark_output",
        "total_records": len(records),
        "records": records,
        "fields": fields,
    }


def write_json(summary, path):
    os.makedirs(os.path.dirname(path), exist_ok=True)
    # Remove large nested dicts from JSON output (keep in records)
    summary_export = {
        "generated_at": summary["generated_at"],
        "source": summary["source"],
        "total_records": summary["total_records"],
        "records": summary["records"],
    }
    with open(path, "w") as f:
        json.dump(summary_export, f, indent=2)


def write_markdown(summary, path):
    os.makedirs(os.path.dirname(path), exist_ok=True)
    lines = []
    lines.append("# Performance Observatory — Latest Benchmark Results\n")
    lines.append(f"Generated: {summary['generated_at']}\n")
    lines.append(f"Total measurement records: {summary['total_records']}\n")
    lines.append("---\n")

    for field, info in sorted(summary["fields"].items()):
        lines.append(f"\n## {field.replace('_', ' ').title()}\n")
        if not info["ranked"]:
            lines.append("*No passing strategies.*\n")
            continue
        fastest = info["fastest"]
        lines.append(f"- **Fastest:** `{fastest['strategy']}` — {fastest['total']}s\n")
        if info["slowest"]:
            slowest = info["slowest"]
            lines.append(f"- **Slowest:** `{slowest['strategy']}` — {slowest['total']}s\n")
        lines.append(f"\n### Ranked (fastest → slowest)\n")
        lines.append("| Rank | Strategy | Result | Total (s) | Wait (s) | Scroll (s) | Appium | ADB | Scrnshts | Retries |\n")
        lines.append("|------|----------|--------|-----------|----------|------------|--------|-----|----------|--------|\n")
        for rank, rec in enumerate(info["ranked"], 1):
            lines.append(
                f"| {rank} | `{rec['strategy']}` | {rec['result']} "
                f"| {rec['total']} | {rec['wait']} | {rec['scroll']} "
                f"| {rec['appium']} | {rec['adb']} "
                f"| {rec['screenshots']} | {rec['retries']} |\n"
            )

    lines.append("\n---\n")
    latest_url = "reports/performance/latest.json"
    lines.append(f"Raw data: [{latest_url}]({latest_url})\n")
    comparison_url = "reports/performance/comparison.md"
    lines.append(f"Compare with previous run: `python3 tools/performance/compare_benchmark.py` → [{comparison_url}]({comparison_url})\n")

    with open(path, "w") as f:
        f.writelines(lines)


def write_history(summary):
    ts = datetime.now(timezone.utc).strftime("%Y%m%d_%H%M%S")
    path = os.path.join(HISTORY_DIR, f"{ts}.json")
    os.makedirs(HISTORY_DIR, exist_ok=True)
    with open(path, "w") as f:
        json.dump(summary, f, indent=2)
    return path


def main():
    parser = argparse.ArgumentParser(
        description="Parse benchmark output.xml and generate performance summaries."
    )
    parser.add_argument(
        "--source",
        default=None,
        help="Path to Robot output.xml (default: newest under reports/benchmark*/)",
    )
    parser.add_argument(
        "--outdir",
        default=PERF_DIR,
        help=f"Output directory (default: {PERF_DIR})",
    )
    args = parser.parse_args()

    source = args.source or find_newest_xml()
    if not os.path.isfile(source):
        print(f"[ERROR] Source not found: {source}")
        sys.exit(1)

    print(f"[PARSE] Reading: {source}")
    raw_lines = list(parse_output_xml(source))
    if not raw_lines:
        print(f"[WARN] No BENCHMARK| lines found in {source}")
        print(f"[WARN] Generating empty summary.")
        summary = summarize([])
    else:
        records = []
        for line in raw_lines:
            rec = parse_line(line)
            if rec:
                records.append(rec)
        print(f"[PARSE] Found {len(records)} benchmark records")
        summary = summarize(records)

    latest_json = os.path.join(args.outdir, "latest.json")
    latest_md = os.path.join(args.outdir, "latest.md")
    write_json(summary, latest_json)
    write_markdown(summary, latest_md)
    history_path = write_history(summary)
    print(f"[PARSE] → {latest_json}")
    print(f"[PARSE] → {latest_md}")
    print(f"[PARSE] → {history_path}")
    print("[PARSE] Done.")


if __name__ == "__main__":
    main()
