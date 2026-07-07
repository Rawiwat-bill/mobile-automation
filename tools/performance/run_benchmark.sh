#!/usr/bin/env bash
# Performance Observatory — Benchmark Runner
#
# Runs all benchmark suites, saves output under reports/benchmark-latest/,
# parses results, and compares with previous run if history exists.
#
# Usage:
#   bash tools/performance/run_benchmark.sh
#
# Requires: Appium server running, device connected, app installed.

set -uo pipefail

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
PROJECT_DIR="$(cd "$SCRIPT_DIR/../.." && pwd)"
TIMESTAMP=$(date +%Y%m%d_%H%M%S)
OUTPUT_DIR="$PROJECT_DIR/reports/benchmark-latest"
HISTORY_DIR="$PROJECT_DIR/reports/benchmark-history/$TIMESTAMP"
PERF_DIR="$PROJECT_DIR/reports/performance"

BENCHMARK_SUITES=(
    "tests/benchmark/landing_benchmark.robot"
    "tests/benchmark/consent_benchmark.robot"
    "tests/benchmark/profile_field_benchmark.robot"
)

echo "========================================"
echo " Performance Observatory — Run $TIMESTAMP"
echo "========================================"
echo ""

# Check for dryrun flag
if [ "${1:-}" = "--dryrun" ]; then
    echo "[RUNNER] Dryrun mode — validating syntax only."
    for suite in "${BENCHMARK_SUITES[@]}"; do
        echo "  python3 -m robot --dryrun $suite"
        python3 -m robot --dryrun "$PROJECT_DIR/$suite"
    done
    echo "[RUNNER] Dryrun complete."
    exit 0
fi

# Ensure output directory exists
mkdir -p "$OUTPUT_DIR"
mkdir -p "$HISTORY_DIR"
mkdir -p "$PERF_DIR/history"

# Save previous latest if exists (for comparison)
if [ -f "$PERF_DIR/latest.json" ]; then
    PREV_TIMESTAMP=$(date +%Y%m%d_%H%M%S)
    cp "$PERF_DIR/latest.json" "$PERF_DIR/history/$PREV_TIMESTAMP.json"
    echo "[RUNNER] Saved previous latest.json to history/$PREV_TIMESTAMP.json"
fi

# Run each benchmark suite, tracking pass/fail without aborting
EXIT_CODE=0
for suite in "${BENCHMARK_SUITES[@]}"; do
    suite_name=$(basename "$suite" .robot)
    echo "[RUNNER] Running: $suite_name"
    if python3 -m robot \
        -d "$OUTPUT_DIR" \
        --output "${suite_name}_output.xml" \
        --log "${suite_name}_log.html" \
        --report "${suite_name}_report.html" \
        "$PROJECT_DIR/$suite"; then
        echo "[RUNNER] Finished: $suite_name — PASS"
    else
        echo "[RUNNER] Finished: $suite_name — FAIL"
        EXIT_CODE=1
    fi
    echo ""
done

# Copy combined output for parser (use the last suite's output.xml as default source)
# The parser will scan all output files in the directory
echo "[RUNNER] All benchmarks complete. Parsing results..."

# Run parser
python3 "$SCRIPT_DIR/parse_benchmark.py" \
    --source "$OUTPUT_DIR/landing_benchmark_output.xml" \
    --outdir "$PERF_DIR"

# Run comparison if previous history exists
if ls "$PERF_DIR/history/"*.json >/dev/null 2>&1; then
    python3 "$SCRIPT_DIR/compare_benchmark.py" \
        --latest "$PERF_DIR/latest.json" \
        --history "$PERF_DIR/history/" \
        --outdir "$PERF_DIR"
else
    echo "[RUNNER] No previous history found — skipping comparison."
fi

echo ""
echo "========================================"
echo " Performance Observatory — Complete"
echo "========================================"
echo "  Output:   $OUTPUT_DIR/"
echo "  Summary:  $PERF_DIR/latest.md"
echo "  Data:     $PERF_DIR/latest.json"
echo "  Compare:  $PERF_DIR/comparison.md"
echo "  Overall:  $([ "$EXIT_CODE" -eq 0 ] && echo 'ALL PASS' || echo 'SOME FAILURES')"
echo "========================================"

exit "$EXIT_CODE"
