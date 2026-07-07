# Benchmark Knowledge

## Status

**Recovered** — Sprint 1.1. The benchmark framework was previously deleted from disk.
Original output logs remain at `reports/benchmark/` through `reports/benchmark5/`.
The framework has been rebuilt with expanded capabilities.

**Observatory** — Sprint 1.2. Performance Observatory tooling added for parsing,
comparison, and historical tracking.

## Benchmark Framework

### Files

| File | Purpose |
|------|---------|
| `resources/benchmark/BenchmarkMetrics.py` | Python metrics collector — tracks timing, counts, phases |
| `resources/benchmark/benchmark_base.resource` | Shared keywords: app navigation, screen detection, benchmark lifecycle |
| `resources/benchmark/benchmark_strategies.resource` | Strategy executors per field, baseline fillers |
| `tests/benchmark/profile_field_benchmark.robot` | Citizen ID (5), DOB (4), Mobile Number (5) strategy comparisons |
| `tests/benchmark/consent_benchmark.robot` | Consent scroll strategy benchmark (hardcoded vs dynamic) |
| `tests/benchmark/landing_benchmark.robot` | Landing detection and navigation benchmarks |

### Architecture

```
tests/benchmark/
├── profile_field_benchmark.robot    # Field-level strategy comparison
├── consent_benchmark.robot           # Consent scroll efficiency
└── landing_benchmark.robot           # Landing detection timing

resources/benchmark/
├── BenchmarkMetrics.py               # Python metrics collector
├── benchmark_base.resource           # App lifecycle, navigation, metrics keywords
└── benchmark_strategies.resource     # Strategy executors per field
```

### Metrics Collected

Each benchmark run records:

| Metric | Source | Description |
|--------|--------|-------------|
| Execution Time | Python `time.time()` | Total elapsed seconds per strategy |
| Phase Times | Phase start/end markers | Per-phase breakdown (open_app, navigate, strategy, blur) |
| Wait Time | Accumulated via `Record Wait` | Time spent in explicit waits and navigation |
| Scroll Time | Accumulated via `Record Scroll` | Time spent in scroll operations |
| Appium Actions | Count via `Record Appium Action` | Every AppiumLibrary call `Click`, `Tap`, `Input`, etc. |
| ADB Calls | Count via `Record ADB Call` | Every `Execute Adb Shell` call |
| Screenshots | Count via `Record Screenshot` | Every `Capture Page Screenshot` call |
| Retries | Count via `Record Retry` | Every `Wait Until Keyword Succeeds` retry |
| Pass/Fail | Benchmark result | PASS, FAIL_STRATEGY, BLOCKED_ENV |

### Supported Screens

- Landing (detection strategies, ready button timing)
- Consent (scroll strategies, accept timing)
- Profile (Citizen ID, DOB, Mobile Number input strategies)
- OCR (future — placeholder structure)
- FaceScan (future — placeholder structure)

## Approach

Each benchmark iteration:
1. Opens app → Landing → Consent → Profile
2. Applies one strategy to the field under test
3. Fills remaining fields with baseline strategy
4. Records timing, action counts, and result
5. Closes app
6. Logs structured `BENCHMARK|` result line

Clean app restart for each strategy.
All benchmark code is isolated from production keywords and locators.

## Strategies by Field

### Citizen ID (5 strategies)
- Input Text (`Input Text Into Current Element`)
- Input Value (`Input Value` — Appium native set)
- Press Keycodes (`Press Keycode` per digit — current production)
- Adb Shell (`Execute Adb Shell input text`)
- Execute Script (`Execute Script` — JS injection)

### DOB (4 strategies)
- Picker Calculated (scroll picker wheels by step count — current production)
- Input Text (`Clear Text` + `Input Text`)
- Adb Shell (`Execute Adb Shell input text`)
- Input Value (`Input Value` — Appium native set)

### Mobile Number (5 strategies)
- Input Text (`Input Text Into Current Element`)
- Input Value (`Input Value` — Appium native set)
- Press Keycodes (`Press Keycode` per digit — current production)
- Adb Shell (`Execute Adb Shell input text`)
- Execute Script (`Execute Script` — JS injection)

## Classification

- **PASS:** Strategy completed, field validated, navigation confirmed
- **FAIL_STRATEGY:** Strategy executed but field validation or navigation failed
- **BLOCKED_ENV:** Failed before strategy execution (navigation, permission, device)

## Ranking

Valid (PASS) strategies only. Ranked fastest to slowest per field.
Update this file with benchmark results after each run.

## Performance Observatory

### Tools

| Tool | Purpose |
|------|---------|
| `tools/performance/parse_benchmark.py` | Parse Robot output.xml → JSON + Markdown summaries |
| `tools/performance/compare_benchmark.py` | Compare latest vs previous run → improvement/regression report |
| `tools/performance/run_benchmark.sh` | Run all benchmarks, parse, compare in one command |

### Output Structure

```
reports/performance/
├── latest.json          # Current benchmark data (JSON)
├── latest.md            # Current benchmark summary (Markdown)
├── comparison.md        # Comparison with previous run (Markdown)
└── history/             # Timestamped historical snapshots
    ├── 20260101_120000.json
    └── 20260102_120000.json
```

### Running

```bash
# Full pipeline (run + parse + compare)
bash tools/performance/run_benchmark.sh

# Parse only (from existing output)
python3 tools/performance/parse_benchmark.py \
    --source reports/benchmark-latest/profile_field_benchmark_output.xml

# Compare only (after at least 2 parse runs)
python3 tools/performance/compare_benchmark.py

# Dryrun validation
bash tools/performance/run_benchmark.sh --dryrun

# Individual benchmark
python3 -m robot -d reports/benchmark tests/benchmark/profile_field_benchmark.robot
```

### Reading Results

`reports/performance/latest.md` shows:
- Per-field ranking (fastest → slowest)
- Execution time, wait time, scroll time
- Appium action count, ADB call count
- Screenshot count, retry count

`reports/performance/comparison.md` shows:
- Improvements (faster strategies, green)
- Regressions (slower strategies, red)
- New/removed strategies

## Benchmark Line Format

Each benchmark logs a pipe-delimited line captured by the parser:
```
BENCHMARK|name|field|strategy|result|total|wait|scroll|appium|adb|screenshots|retries
```

Example:
```
BENCHMARK|Citizen ID Strategy Comparison|citizen_id|press_keycodes|PASS|18.234|2.100|0.000|28|1|0|0
```

## Internal Project Truth

Benchmark results are the authoritative data source for strategy selection. External skill suggestions about interaction patterns are secondary to measured results from the project's own benchmark suite. Do not change production strategy without benchmark evidence.

**Rule: No performance optimization without benchmark evidence.** Every optimization must include a before/after comparison in `reports/performance/comparison.md`.

The benchmark framework is isolated from production code. No benchmark keywords import or depend on production page keywords or locators. This ensures benchmark changes never affect test execution.
