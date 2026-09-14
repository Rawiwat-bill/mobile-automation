#!/usr/bin/env bash
# CI Health Check Runner — runs onboarding_health_check.robot and collects artifacts.
#
# Usage:
#   bash tools/ci/run_health_check.sh                    # full run
#   bash tools/ci/run_health_check.sh --dryrun           # syntax validation only
#
# Exit codes:
#   0 — all tests pass (or dryrun passes)
#   1 — any test fails (or dryrun fails)
#
# Environment overrides:
#   ROBOT_OPTIONS   extra flags passed to robot (e.g. "--variable APP:foo")
#   OUTPUT_DIR      output root (default: reports/ci-latest)

set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
PROJECT_DIR="$(cd "$SCRIPT_DIR/../.." && pwd)"
TIMESTAMP=$(date +%Y%m%d_%H%M%S)
OUTPUT_DIR="${OUTPUT_DIR:-$PROJECT_DIR/reports/ci-latest}"
ROBOT_OPTIONS="${ROBOT_OPTIONS:-}"
PYTHON_BIN="${PYTHON_BIN:-python3}"

HEALTH_CHECK_SUITE="$PROJECT_DIR/tests/android/onboarding/onboarding_health_check.robot"

echo "============================================"
echo " CI Health Check Runner — $TIMESTAMP"
echo "============================================"
echo ""

# --- Dryrun mode -----------------------------------------------------------
if [ "${1:-}" = "--dryrun" ]; then
    echo "[CI] Dryrun mode — validating syntax only."
    mkdir -p "$OUTPUT_DIR"
    if "$PYTHON_BIN" -m robot --dryrun --outputdir "$OUTPUT_DIR" "$HEALTH_CHECK_SUITE"; then
        rc=0
    else
        rc=$?
    fi
    if [ $rc -eq 0 ]; then
        echo "[CI] Dryrun PASSED"
    else
        echo "[CI] Dryrun FAILED"
    fi
    exit $rc
fi

# --- Prepare output directories --------------------------------------------
mkdir -p "$OUTPUT_DIR"

echo "[CI] Output directory: $OUTPUT_DIR"
echo "[CI] Suite: $HEALTH_CHECK_SUITE"
echo ""

# --- Run health check ------------------------------------------------------
if "$PYTHON_BIN" -m robot \
        --outputdir "$OUTPUT_DIR" \
        --output health_check_output.xml \
        --log health_check_log.html \
        --report health_check_report.html \
        $ROBOT_OPTIONS \
        "$HEALTH_CHECK_SUITE"; then
    rc=0
else
    rc=$?
fi

# --- Report artifacts ------------------------------------------------------
echo ""
echo "============================================"
echo " CI Health Check — Results"
echo "============================================"
if [ $rc -eq 0 ]; then
    echo "  Status: PASS"
else
    echo "  Status: FAIL (exit code $rc)"
fi
echo ""
echo "  Artifacts:"
echo "    Robot output:     $OUTPUT_DIR/health_check_output.xml"
echo "    Robot log:        $OUTPUT_DIR/health_check_log.html"
echo "    Robot report:     $OUTPUT_DIR/health_check_report.html"
echo ""

# Print sub-report paths if they exist
for sub in health_check api_logs stability; do
    subdir="$OUTPUT_DIR/$sub"
    if [ -d "$subdir" ]; then
        echo "    $sub/:            $subdir/"
        ls "$subdir"/*.md "$subdir"/*.json "$subdir"/*.log 2>/dev/null \
            | while IFS= read -r f; do echo "      - $f"; done
    else
        echo "    $sub/:            (not generated)"
    fi
done

echo ""
echo "============================================"
echo ""

exit $rc
