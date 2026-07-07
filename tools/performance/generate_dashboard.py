#!/usr/bin/env python3
"""
QA Observatory — Benchmark Dashboard Generator

Transforms benchmark data from reports/performance/ into an engineering
dashboard at reports/benchmark/dashboard.md.

Sections:
  - Overall benchmark health
  - Latest benchmark summary
  - Average execution time per phase
  - Strategy comparison
  - Improvement vs baseline
  - Trend (last N runs)
  - ADB/Appium call statistics
  - Experiment references
  - Decision references
  - Known risks
  - Recommended next actions

Usage:
  python3 tools/performance/generate_dashboard.py
      [--latest reports/performance/latest.json]
      [--history reports/performance/history/]
      [--experiments docs/experiments/]
      [--decisions docs/decisions/]
      [--output reports/benchmark/dashboard.md]
"""

import argparse
import glob
import json
import os
import re
import sys
from collections import defaultdict
from datetime import datetime, timezone

PERF_DIR = "reports/performance"
HISTORY_DIR = os.path.join(PERF_DIR, "history")
EXPERIMENTS_DIR = "docs/experiments"
DECISIONS_DIR = "docs/decisions"
OUTPUT_PATH = "reports/benchmark/dashboard.md"


def load_json(path):
    with open(path) as f:
        return json.load(f)


def load_markdown_frontmatter(path, section=None):
    """Read a markdown file and return its lines for basic parsing."""
    if not os.path.isfile(path):
        return []
    with open(path) as f:
        return f.readlines()


def find_history_files(history_dir):
    files = sorted(glob.glob(os.path.join(history_dir, "*.json")))
    result = []
    for fpath in files:
        try:
            data = load_json(fpath)
            if data.get("total_records", 0) > 0:
                ts = os.path.splitext(os.path.basename(fpath))[0]
                result.append({"path": fpath, "timestamp": ts, "data": data})
        except (json.JSONDecodeError, OSError):
            continue
    return result


def extract_strategy_label(strategy):
    return strategy.replace("_", " ").title()


# ─── Dashboard Section Builders ─────────────────────────────────────────────


def build_header(latest, total_history_files):
    lines = []
    lines.append("# QA Observatory — Benchmark Dashboard\n")
    lines.append(f"**Generated:** {datetime.now(timezone.utc).isoformat()}\n")
    lines.append(f"**Source:** `{latest.get('generated_at', 'unknown')}`\n")
    lines.append(f"**Records in latest:** {latest.get('total_records', 0)}\n")
    lines.append(f"**History files with data:** {total_history_files}\n")
    lines.append("---\n")
    return lines


def build_health(latest, history):
    records = latest.get("records", [])
    total = len(records)
    passed = sum(1 for r in records if r.get("result") == "PASS")
    failed = total - passed
    fields = set(r.get("field", "") for r in records)

    lines = []
    lines.append("\n## Overall Benchmark Health\n")
    lines.append(f"| Metric | Value |\n")
    lines.append(f"|--------|-------|\n")
    lines.append(f"| Total strategies tracked | {total} |\n")
    lines.append(f"| Passing | {passed} |\n")
    lines.append(f"| Failing | {failed} |\n")
    lines.append(f"| Pass rate | {100.0 if total == 0 else round(passed/total*100, 1)}% |\n")
    lines.append(f"| Fields covered | {', '.join(sorted(fields)) if fields else 'none'} |\n")
    lines.append(f"| History data points | {sum(h['data']['total_records'] for h in history)} |\n")
    lines.append(f"| History snapshots | {len(history)} |\n")

    if failed > 0:
        lines.append("\n### Failing Strategies\n")
        for r in records:
            if r.get("result") != "PASS":
                lines.append(f"- `{r.get('strategy', '?')}` ({r.get('field', '?')}) — {r.get('result')}\n")
    lines.append("")
    return lines


def build_latest_summary(latest):
    records = latest.get("records", [])
    if not records:
        return ["\n## Latest Benchmark Summary\n\n*No data.*\n"]

    lines = []
    lines.append("\n## Latest Benchmark Summary\n")
    lines.append(f"Run: {latest.get('generated_at', 'unknown')}\n")
    lines.append("\n")
    lines.append("| Rank | Field | Strategy | Result | Total (s) | Scroll (s) | Wait (s) | Appium | ADB | Scrnshts | Retries |\n")
    lines.append("|------|-------|----------|--------|-----------|------------|----------|--------|-----|----------|--------|\n")

    sorted_records = sorted(records, key=lambda r: r.get("total", 0))
    for rank, rec in enumerate(sorted_records, 1):
        lines.append(
            f"| {rank} | {rec.get('field', '')} | `{rec.get('strategy', '')}` "
            f"| {rec.get('result', '')} | {rec.get('total', 0)} "
            f"| {rec.get('scroll', 0)} | {rec.get('wait', 0)} "
            f"| {rec.get('appium', 0)} | {rec.get('adb', 0)} "
            f"| {rec.get('screenshots', 0)} | {rec.get('retries', 0)} |\n"
        )
    lines.append("")
    return lines


def build_phase_averages(latest):
    records = latest.get("records", [])
    if not records:
        return ["\n## Average Execution Time Per Phase\n\n*No data.*\n"]

    lines = []
    lines.append("\n## Average Execution Time Per Phase\n")
    lines.append("Phases are derived from metric breakdown per record.\n")
    lines.append("\n")
    lines.append("| Metric | Average (s) | Min (s) | Max (s) | Total (s) |\n")
    lines.append("|--------|:-----------:|:-------:|:-------:|:---------:|\n")

    metrics = [
        ("total", "Total execution"),
        ("scroll", "Scroll operations"),
        ("wait", "Explicit waits"),
    ]
    for key, label in metrics:
        vals = [r.get(key, 0) for r in records]
        avg = sum(vals) / len(vals) if vals else 0
        mn = min(vals) if vals else 0
        mx = max(vals) if vals else 0
        total = sum(vals)
        lines.append(f"| {label} | {avg:.3f} | {mn:.3f} | {mx:.3f} | {total:.3f} |\n")

    non_io_vals = [
        r.get("total", 0) - r.get("scroll", 0) - r.get("wait", 0) for r in records
    ]
    avg_io = sum(non_io_vals) / len(non_io_vals) if non_io_vals else 0
    mn_io = min(non_io_vals) if non_io_vals else 0
    mx_io = max(non_io_vals) if non_io_vals else 0
    lines.append(
        f"| Navigation + interaction | {avg_io:.3f} | {mn_io:.3f} | {mx_io:.3f} "
        f"| {sum(non_io_vals):.3f} |\n"
    )
    lines.append("\n*Note: Phase-level timing from Robot Framework output.xml is not yet\n"
                  "extracted by the parser. Averages here are from aggregate record metrics.*\n")
    lines.append("")
    return lines


def build_strategy_comparison(latest):
    records = latest.get("records", [])
    if not records:
        return ["\n## Strategy Comparison\n\n*No data.*\n"]

    fields = defaultdict(list)
    for r in records:
        fields[r.get("field", "unknown")].append(r)

    lines = []
    lines.append("\n## Strategy Comparison\n")

    for field in sorted(fields):
        strategies = fields[field]
        strategies.sort(key=lambda r: r.get("total", 0))
        baseline = strategies[0] if strategies else None

        lines.append(f"\n### {field.replace('_', ' ').title()}\n")
        lines.append("| Rank | Strategy | Total (s) | Scroll (s) | vs Fastest | ADB Calls |\n")
        lines.append("|------|----------|-----------|------------|------------|-----------|\n")

        for rank, rec in enumerate(strategies, 1):
            fastest_total = baseline.get("total", 0) if baseline else 0
            gap = rec.get("total", 0) - fastest_total if fastest_total > 0 else 0
            gap_label = f"+{gap:.1f}s" if gap > 0.01 else "baseline"
            lines.append(
                f"| {rank} | `{rec.get('strategy', '')}` "
                f"| {rec.get('total', 0)} | {rec.get('scroll', 0)} "
                f"| {gap_label} | {rec.get('adb', 0)} |\n"
            )

        rank1 = strategies[0] if len(strategies) > 0 else None
        rank2 = strategies[-1] if len(strategies) > 1 else None
        if rank1 and rank2 and rank2.get("total", 0) > 0:
            improvement = (1 - rank1.get("total", 0) / rank2.get("total", 0)) * 100
            lines.append(
                f"\n**Spread:** {improvement:.1f}% improvement from "
                f"`{rank2.get('strategy', '?')}` → `{rank1.get('strategy', '?')}`\n"
            )
    lines.append("")
    return lines


def build_improvement_vs_baseline(latest):
    records = latest.get("records", [])
    if not records:
        return ["\n## Improvement vs Baseline\n\n*No data.*\n"]

    lines = []
    lines.append("\n## Improvement vs Baseline\n")
    lines.append("Baseline is the strategy named `hardcoded` within each field.\n")
    lines.append("\n")

    fields = defaultdict(list)
    for r in records:
        fields[r.get("field", "unknown")].append(r)

    found_any = False
    for field in sorted(fields):
        strategies = fields[field]
        baseline_rec = next((r for r in strategies if r.get("strategy") == "hardcoded"), None)
        if not baseline_rec:
            # Use slowest as pseudo-baseline
            strategies.sort(key=lambda r: r.get("total", 0))
            baseline_rec = strategies[-1] if strategies else None
        if not baseline_rec:
            continue

        baseline_time = baseline_rec.get("total", 0)
        if baseline_time == 0:
            continue

        lines.append(f"\n### {field.replace('_', ' ').title()}\n")
        lines.append("| Strategy | Total (s) | vs Baseline | Scroll (s) | vs Baseline |\n")
        lines.append("|----------|-----------|-------------|------------|-------------|\n")

        baseline_scroll = baseline_rec.get("scroll", 0)
        for rec in sorted(strategies, key=lambda r: r.get("total", 0)):
            total_vs = rec.get("total", 0) - baseline_time
            total_pct = (total_vs / baseline_time) * 100
            scroll_vs = rec.get("scroll", 0) - baseline_scroll
            scroll_pct = (scroll_vs / baseline_scroll * 100) if baseline_scroll > 0 else 0

            total_label = "baseline"
            if total_vs < -0.01:
                total_label = f"{total_vs:.1f}s ({total_pct:.0f}%)"
            elif total_vs > 0.01:
                total_label = f"+{total_vs:.1f}s (+{total_pct:.0f}%)"

            scroll_label = "baseline"
            if scroll_vs < -0.01:
                scroll_label = f"{scroll_vs:.1f}s ({scroll_pct:.0f}%)"
            elif scroll_vs > 0.01:
                scroll_label = f"+{scroll_vs:.1f}s (+{scroll_pct:.0f}%)"

            lines.append(
                f"| `{rec.get('strategy', '')}` "
                f"| {rec.get('total', 0)} | {total_label} "
                f"| {rec.get('scroll', 0)} | {scroll_label} |\n"
            )
        found_any = True

    if not found_any:
        lines.append("*No baseline strategy found in current data.*\n")
    lines.append("")
    return lines


def build_trend(latest, history, max_runs=10):
    lines = []
    lines.append("\n## Trend (Last N Runs)\n")

    # Build per-field per-strategy time series from history + latest
    all_snapshots = []

    for h in history:
        ts = h["timestamp"]
        dt = datetime.strptime(ts, "%Y%m%d_%H%M%S").replace(tzinfo=timezone.utc)
        for rec in h["data"].get("records", []):
            all_snapshots.append({
                "ts": dt,
                "field": rec.get("field", ""),
                "strategy": rec.get("strategy", ""),
                "total": rec.get("total", 0),
                "scroll": rec.get("scroll", 0),
            })

    # Add latest
    latest_ts = latest.get("generated_at", "")
    try:
        dt_latest = datetime.fromisoformat(latest_ts)
        if dt_latest.tzinfo is None:
            dt_latest = dt_latest.replace(tzinfo=timezone.utc)
    except (ValueError, TypeError):
        dt_latest = datetime.now(timezone.utc)
    for rec in latest.get("records", []):
        all_snapshots.append({
            "ts": dt_latest,
            "field": rec.get("field", ""),
            "strategy": rec.get("strategy", ""),
            "total": rec.get("total", 0),
            "scroll": rec.get("scroll", 0),
        })

    # Remove duplicate timestamps within 60s (same run)
    all_snapshots.sort(key=lambda x: (x["field"], x["strategy"], x["ts"]))
    deduped = []
    for s in all_snapshots:
        if deduped and deduped[-1]["field"] == s["field"] and deduped[-1]["strategy"] == s["strategy"]:
            delta = (s["ts"] - deduped[-1]["ts"]).total_seconds()
            if delta < 60:
                continue
        deduped.append(s)
    all_snapshots = deduped

    # Group by field+strategy
    series = defaultdict(list)
    for s in all_snapshots:
        key = (s["field"], s["strategy"])
        series[key].append(s)

    if not series:
        lines.append("*No trend data available — only one time point.*\n")
        lines.append("")
        return lines

    lines.append("\nEach row is one benchmark snapshot.\n")
    lines.append("\n")

    for key in sorted(series):
        field, strategy = key
        points = series[key][-max_runs:]
        lines.append(f"\n### {field.replace('_', ' ').title()} — `{strategy}`\n")
        lines.append("| Run # | Timestamp | Total (s) | Scroll (s) |\n")
        lines.append("|-------|-----------|-----------|------------|\n")
        for i, p in enumerate(points, 1):
            ts_str = p["ts"].strftime("%m/%d %H:%M")
            lines.append(
                f"| {i} | {ts_str} | {p['total']} | {p['scroll']} |\n"
            )

        if len(points) >= 2:
            first, last = points[0], points[-1]
            total_delta = last["total"] - first["total"]
            scroll_delta = last["scroll"] - first["scroll"]
            lines.append(
                f"\n  **Δ total:** {total_delta:+.1f}s — "
                f"{'improving' if total_delta < 0 else 'regressing' if total_delta > 0 else 'stable'}\n"
            )
            lines.append(
                f"  **Δ scroll:** {scroll_delta:+.1f}s — "
                f"{'improving' if scroll_delta < 0 else 'regressing' if scroll_delta > 0 else 'stable'}\n"
            )
        else:
            lines.append("\n  *(Single data point — trend requires ≥2 runs)*\n")

    lines.append("")
    return lines


def build_adb_appium_stats(latest):
    records = latest.get("records", [])
    if not records:
        return ["\n## ADB/Appium Call Statistics\n\n*No data.*\n"]

    lines = []
    lines.append("\n## ADB/Appium Call Statistics\n")

    total_adb = sum(r.get("adb", 0) for r in records)
    total_appium = sum(r.get("appium", 0) for r in records)
    total_screenshots = sum(r.get("screenshots", 0) for r in records)

    lines.append("| Metric | Total | Average | Min | Max |\n")
    lines.append("|--------|:-----:|:-------:|:---:|:---:|\n")

    for key, label in [("adb", "ADB calls"), ("appium", "Appium actions"),
                        ("screenshots", "Screenshots"), ("retries", "Retries")]:
        vals = [r.get(key, 0) for r in records]
        lines.append(
            f"| {label} | {sum(vals)} | {sum(vals)/len(vals):.1f} "
            f"| {min(vals)} | {max(vals)} |\n"
        )

    lines.append("\n### ADB/Appium Ratio\n")
    if total_appium > 0:
        ratio = total_adb / total_appium
        lines.append(f"Overall ADB per Appium action: {ratio:.2f}\n")
        lines.append("Lower is better — ADB bypasses Appium's gesture engine.\n")
    lines.append("")
    return lines


def build_experiment_references():
    lines = []
    lines.append("\n## Experiment References\n")

    exp_dir = EXPERIMENTS_DIR
    if not os.path.isdir(exp_dir):
        lines.append("*No experiment files found.*\n")
        lines.append("")
        return lines

    exp_files = sorted(glob.glob(os.path.join(exp_dir, "*.md")))
    if not exp_files:
        lines.append("*No experiment files found.*\n")
        lines.append("")
        return lines

    for fpath in exp_files:
        basename = os.path.basename(fpath)
        content = load_markdown_frontmatter(fpath)
        status_line = ""
        finding_lines = []
        in_findings = False
        for line in content:
            stripped = line.strip()
            if stripped.startswith("## Status"):
                status_line = content[content.index(line) + 1].strip() if content.index(line) + 1 < len(content) else ""
            if stripped.startswith("## Conclusion"):
                in_findings = True
            elif stripped.startswith("## ") and in_findings:
                break
            elif in_findings and stripped and not stripped.startswith("#"):
                finding_lines.append(stripped)

        lines.append(f"- **{basename}** — Status: {status_line or 'unknown'}\n")
        if finding_lines:
            for fl in finding_lines[:3]:
                lines.append(f"  - {fl}\n")
        lines.append(f"  - Path: `{fpath}`\n")

    lines.append("")
    return lines


def build_decision_references():
    lines = []
    lines.append("\n## Decision References\n")

    dec_dir = DECISIONS_DIR
    if not os.path.isdir(dec_dir):
        lines.append("*No decision files found.*\n")
        lines.append("")
        return lines

    # Collect DEC- files (experiment decisions) and ADR files
    dec_files = sorted(glob.glob(os.path.join(dec_dir, "DEC-*.md")))
    adr_files = sorted(glob.glob(os.path.join(dec_dir, "ADR-*.md")))

    if not dec_files and not adr_files:
        lines.append("*No decision files found.*\n")
        lines.append("")
        return lines

    if dec_files:
        lines.append("\n### Experiment Decisions\n")
        for fpath in dec_files:
            basename = os.path.basename(fpath)
            content = load_markdown_frontmatter(fpath)
            status = ""
            for line in content:
                if line.strip().startswith("## Status"):
                    idx = content.index(line)
                    if idx + 1 < len(content):
                        status = content[idx + 1].strip()
                    break
            lines.append(f"- **{basename}** — {status}\n")
            lines.append(f"  - Path: `{fpath}`\n")

    if adr_files:
        lines.append("\n### Architectural Decisions\n")
        for fpath in adr_files:
            basename = os.path.basename(fpath)
            content = load_markdown_frontmatter(fpath)
            status = ""
            context = ""
            for i, line in enumerate(content):
                stripped = line.strip()
                if stripped.startswith("## Status") and i + 1 < len(content):
                    status = content[i + 1].strip()
                if stripped.startswith("## Context") or stripped.startswith("## Decision"):
                    for j in range(i + 1, min(i + 4, len(content))):
                        ctx = content[j].strip()
                        if ctx and not ctx.startswith("#"):
                            context = ctx[:120]
                            break
            lines.append(f"- **{basename}** — {status}\n")
            if context:
                lines.append(f"  - {context}…\n")
            lines.append(f"  - Path: `{fpath}`\n")

    lines.append("")
    return lines


def build_known_risks():
    lines = []
    lines.append("\n## Known Risks\n")
    lines.append("*No decision records with risk data found.*\n")
    lines.append("")
    return lines


def build_recommendations(latest, history):
    records = latest.get("records", [])
    lines = []
    lines.append("\n## Recommended Next Actions\n")

    recommendations = []

    # Check if history is sparse
    if len(history) < 2:
        recommendations.append(
            "🔴 Run benchmarks again to establish trend data. "
            "Only {} snapshot(s) with data exist.".format(len(history))
        )

    # Check if scrollbar drag is fastest but not promoted
    for r in records:
        if "scrollbar" in r.get("strategy", "") and r.get("result") == "PASS":
            recommendations.append(
                "🟡 Scrollbar drag (`{}`) is the fastest consent strategy at {:.1f}s. "
                "Review for production promotion.".format(
                    r["strategy"], r["total"]
                )
            )
            break

    # Check for fields with only 1 strategy
    fields = defaultdict(list)
    for r in records:
        fields[r.get("field", "")].append(r)
    for field, strs in fields.items():
        if len(strs) <= 1:
            recommendations.append(
                "🟡 Field `{}` has only {} strategy. "
                "Add more strategies for comparison.".format(field, len(strs))
            )

    # Check for strategies with high ADB count
    for r in records:
        adb = r.get("adb", 0)
        if adb > 5:
            recommendations.append(
                "🟡 `{}` ({}) uses {} ADB calls. "
                "Consider scrollbar drag or dynamic swipe to reduce.".format(
                    r.get("strategy", "?"), r.get("field", "?"), adb
                )
            )

    # Check pass rate
    if records:
        passed = sum(1 for r in records if r.get("result") == "PASS")
        if passed < len(records):
            recommendations.append(
                "🔴 {}/{} strategies are failing. Investigate failures.".format(
                    len(records) - passed, len(records)
                )
            )

    if not recommendations:
        recommendations.append("✅ No immediate issues detected.")

    for rec in recommendations:
        lines.append(f"- {rec}\n")

    lines.append("")
    return lines


def build_footer():
    lines = []
    lines.append("---\n")
    lines.append("Generated by `tools/performance/generate_dashboard.py`\n")
    lines.append(
        "Raw data: `reports/performance/latest.json` | "
        "History: `reports/performance/history/`\n"
    )
    lines.append("")
    return lines


# ─── Main ───────────────────────────────────────────────────────────────────


def main():
    parser = argparse.ArgumentParser(
        description="Generate QA Observatory engineering dashboard from benchmark data."
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
        "--experiments",
        default=EXPERIMENTS_DIR,
        help="Experiments directory (default: docs/experiments/)",
    )
    parser.add_argument(
        "--decisions",
        default=DECISIONS_DIR,
        help="Decisions directory (default: docs/decisions/)",
    )
    parser.add_argument(
        "--output",
        default=OUTPUT_PATH,
        help="Dashboard output path (default: reports/benchmark/dashboard.md)",
    )
    args = parser.parse_args()

    # Load data
    if not os.path.isfile(args.latest):
        print(f"[DASHBOARD] ERROR: Latest data not found: {args.latest}")
        print("[DASHBOARD] Run parse_benchmark.py first.")
        sys.exit(1)

    latest = load_json(args.latest)
    history = find_history_files(args.history)
    print(f"[DASHBOARD] Loaded latest: {latest.get('total_records', 0)} records")
    print(f"[DASHBOARD] Loaded history: {len(history)} snapshots with data")

    # Build dashboard
    sections = [
        build_header(latest, len(history)),
        build_health(latest, history),
        build_latest_summary(latest),
        build_phase_averages(latest),
        build_strategy_comparison(latest),
        build_improvement_vs_baseline(latest),
        build_trend(latest, history),
        build_adb_appium_stats(latest),
        build_experiment_references(),
        build_decision_references(),
        build_known_risks(),
        build_recommendations(latest, history),
        build_footer(),
    ]

    os.makedirs(os.path.dirname(args.output), exist_ok=True)
    with open(args.output, "w") as f:
        for section in sections:
            f.writelines(section)

    print(f"[DASHBOARD] → {args.output}")
    print("[DASHBOARD] Done.")


if __name__ == "__main__":
    main()
