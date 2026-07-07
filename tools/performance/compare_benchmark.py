#!/usr/bin/env python3
"""
Performance Observatory — Benchmark Comparator

Compares current latest.json with the most recent previous history entry.
Generates reports/performance/comparison.md with improvements/regressions.

Usage:
  python3 tools/performance/compare_benchmark.py
      [--latest reports/performance/latest.json]
      [--history reports/performance/history/]
      [--outdir reports/performance]
"""

import argparse
import glob
import json
import os
import sys
from datetime import datetime, timezone

PERF_DIR = "reports/performance"
HISTORY_DIR = os.path.join(PERF_DIR, "history")


def load_json(path):
    with open(path) as f:
        return json.load(f)


def find_previous_history(history_dir):
    files = sorted(glob.glob(os.path.join(history_dir, "*.json")))
    if len(files) < 2:
        return None
    return files[-2]


def build_lookup(records):
    """Build {(field, strategy): record} dict."""
    lookup = {}
    for r in records:
        key = (r.get("field", ""), r.get("strategy", ""))
        lookup[key] = r
    return lookup


def pct_change(old_val, new_val):
    if old_val == 0:
        return None
    return round((new_val - old_val) / old_val * 100, 1)


def write_comparison(current, previous, out_path):
    cur_records = current.get("records", [])
    prev_records = previous.get("records", [])

    cur_lookup = build_lookup(cur_records)
    prev_lookup = build_lookup(prev_records)

    all_keys = set(cur_lookup.keys()) | set(prev_lookup.keys())

    improvements = []
    regressions = []
    unchanged = []
    new_entries = []
    removed_entries = []

    for key in sorted(all_keys):
        field, strategy = key
        cur = cur_lookup.get(key)
        prev = prev_lookup.get(key)

        if cur and not prev:
            new_entries.append(cur)
            continue
        if prev and not cur:
            removed_entries.append(prev)
            continue

        old_total = float(prev.get("total", 0))
        new_total = float(cur.get("total", 0))
        delta = pct_change(old_total, new_total)
        if delta is None:
            continue
        entry = {
            "field": field,
            "strategy": strategy,
            "old_total": old_total,
            "new_total": new_total,
            "delta_pct": delta,
            "old_result": prev.get("result", ""),
            "new_result": cur.get("result", ""),
        }
        if new_total < old_total:
            improvements.append(entry)
        elif new_total > old_total:
            regressions.append(entry)
        else:
            unchanged.append(entry)

    improvements.sort(key=lambda x: x["delta_pct"])
    regressions.sort(key=lambda x: x["delta_pct"], reverse=True)

    lines = []
    lines.append("# Performance Observatory — Benchmark Comparison\n")
    lines.append(f"Generated: {datetime.now(timezone.utc).isoformat()}\n")
    cur_time = current.get("generated_at", "unknown")
    prev_time = previous.get("generated_at", "unknown")
    lines.append(f"- **Previous run:** {prev_time}\n")
    lines.append(f"- **Current run:** {cur_time}\n")
    lines.append(f"- **Strategies compared:** {len(all_keys)}\n")
    lines.append(f"- **New strategies:** {len(new_entries)}\n")
    lines.append(f"- **Removed strategies:** {len(removed_entries)}\n")
    lines.append("---\n")

    if improvements:
        lines.append("\n## ✅ Improvements (faster)\n")
        lines.append("| Field | Strategy | Before (s) | After (s) | Change |\n")
        lines.append("|-------|----------|------------|-----------|--------|\n")
        for e in improvements:
            lines.append(
                f"| {e['field']} | `{e['strategy']}` "
                f"| {e['old_total']} | {e['new_total']} "
                f"| {e['delta_pct']}% |\n"
            )

    if regressions:
        lines.append("\n## 🔴 Regressions (slower)\n")
        lines.append("| Field | Strategy | Before (s) | After (s) | Change |\n")
        lines.append("|-------|----------|------------|-----------|--------|\n")
        for e in regressions:
            lines.append(
                f"| {e['field']} | `{e['strategy']}` "
                f"| {e['old_total']} | {e['new_total']} "
                f"| +{e['delta_pct']}% |\n"
            )

    if new_entries:
        lines.append("\n## 🆕 New Strategies\n")
        lines.append("| Field | Strategy | Result | Total (s) |\n")
        lines.append("|-------|----------|--------|-----------|\n")
        for e in new_entries:
            lines.append(f"| {e.get('field', '')} | `{e.get('strategy', '')}` | {e.get('result', '')} | {e.get('total', '')} |\n")

    if not improvements and not regressions and not new_entries and not removed_entries:
        lines.append("\n*No changes detected between runs.*\n")

    lines.append("\n---\n")
    lines.append("Run `python3 tools/performance/parse_benchmark.py` after each benchmark to refresh.\n")

    os.makedirs(os.path.dirname(out_path), exist_ok=True)
    with open(out_path, "w") as f:
        f.writelines(lines)
    return out_path


def main():
    parser = argparse.ArgumentParser(
        description="Compare current benchmark results with previous run."
    )
    parser.add_argument(
        "--latest",
        default=os.path.join(PERF_DIR, "latest.json"),
        help="Current benchmark JSON (default: reports/performance/latest.json)",
    )
    parser.add_argument(
        "--history",
        default=HISTORY_DIR,
        help="History directory (default: reports/performance/history/)",
    )
    parser.add_argument(
        "--outdir",
        default=PERF_DIR,
        help=f"Output directory (default: {PERF_DIR})",
    )
    args = parser.parse_args()

    if not os.path.isfile(args.latest):
        print(f"[ERROR] Latest results not found: {args.latest}")
        print("[ERROR] Run parse_benchmark.py first.")
        sys.exit(1)

    previous = find_previous_history(args.history)
    if previous is None:
        print("[COMPARE] No previous history found. Nothing to compare.")
        print("[COMPARE] Run parse_benchmark.py at least twice to enable comparison.")
        sys.exit(0)

    current_data = load_json(args.latest)
    previous_data = load_json(previous)

    out_path = os.path.join(args.outdir, "comparison.md")
    write_comparison(current_data, previous_data, out_path)
    print(f"[COMPARE] → {out_path}")
    print("[COMPARE] Done.")


if __name__ == "__main__":
    main()
