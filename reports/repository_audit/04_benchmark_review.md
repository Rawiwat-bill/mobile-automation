# 04 — Benchmark Review

> **IMPORTANT:** Benchmark is NOT temporary. It is reusable for regression,
> health checking, environment validation, runtime validation, and device
> qualification. Do NOT archive.

## Benchmark Inventory

### Tests (`tests/benchmark/`)

| File | Purpose | Strategies Compared |
|------|---------|---------------------|
| `profile_field_benchmark.robot` | Citizen ID / DOB / Mobile input strategies | input_text, input_value, press_keycodes, adb_shell, execute_script, picker_calculated |
| `consent_benchmark.robot` | Consent scroll strategies | (see consent_scroll_strategies.resource) |
| `landing_benchmark.robot` | Landing screen interaction | — |

### Resources (`resources/benchmark/`)

| File | Lines | Purpose |
|------|-------|---------|
| `benchmark_base.resource` | 152 | App lifecycle, isolated locators, permission handling |
| `benchmark_strategies.resource` | 301 | Strategy executors for Citizen ID, DOB, Mobile; baseline fillers; interaction helpers |
| `consent_scroll_strategies.resource` | — | Consent scroll strategy variants (Hardcoded Swipe, Dynamic Swipe, Scrollbar Drag) |

### Python (`resources/benchmark/`)

| File | Purpose |
|------|---------|
| `BenchmarkMetrics.py` | Metrics collection (Set Strategy, Set Result, Start/End Phase, Record Appium Action/ADB Call) |

---

## Findings

### Ponytail: "Benchmark duplicates production locators — shrink by importing"

**QA: Partially disagree.**

Benchmark isolates locators deliberately. Reasoning:
- Benchmark measures interaction strategies in isolation. If benchmark imports
  production locators and production locators change, benchmark results become
  non-comparable across time — defeating the measurement purpose.
- The `BENCHMARK_` prefix makes isolation explicit and traceable.
- **However:** the locators are currently identical copies. If they diverge, benchmark
  tests the wrong element.

**Recommendation:** Keep isolation pattern BUT add a consistency check:
```robotframework
# In benchmark_suite_setup
Benchmark Locators Should Match Production
    # Verifies BENCHMARK_DOB_INPUT xpath == PROFILE_DOB_INPUT xpath
    # Fails benchmark if production locators changed without updating benchmark
```
This preserves isolation while preventing silent divergence.

### Ponytail: "DOB picker logic duplicated — shrink to shared keyword"

**QA: Partially disagree.**

- Production `Select DOB Picker Value` has stability tracking (Record DOB Picker Attempt,
  Capture DOB Failure Evidence) baked in.
- Benchmark `Select Benchmark Picker Value` is a clean measurement version without
  stability overhead.
- Merging them would couple measurement to stability infrastructure, skewing benchmarks.

**Recommendation:** Keep separate, but extract the **pure algorithm** (swipe geometry
calculation, direction detection) into a shared helper that both call. Stability/measurement
wrappers stay in their respective layers.

### Agreed Findings

| # | Severity | Finding | Recommendation |
|---|----------|---------|----------------|
| 1 | High | `Allow Android Permission If Visible` duplicated | Benchmark imports from app_keywords; benchmark version adds `Record Appium Action` — wrap the shared keyword |
| 2 | High | `Landing Screen Should Be Visible` duplicated | Import from landing_screen_page |
| 3 | High | App package/activity hardcoded in benchmark_base | Import `${APP_PACKAGE}` from app_keywords |
| 4 | Medium | `month_map` / `month_indexes` duplicated 3x | Extract to shared date helper |
| 5 | Medium | `Enter Digits By Keycodes` in benchmark_strategies | Should be shared — production Citizen ID uses keycodes too |
| 6 | Medium | `Tap By Coordinates` / `Field Should Be Blurred` in benchmark | Generic helpers, should be shared |

### Code Smell

| # | Severity | Finding | Evidence |
|---|----------|---------|----------|
| 7 | Medium | `benchmark_strategies.resource` is 301 lines — largest file in repo | Mixed: 3 strategy groups + interaction helpers + baseline fillers | Split into `benchmark_citizen_strategies.resource`, `benchmark_dob_strategies.resource`, `benchmark_mobile_strategies.resource`, `benchmark_helpers.resource` |
| 8 | Low | `profile_field_benchmark.robot:24-26` hardcodes benchmark data, then overwrites in `Set Benchmark Data` | Dead variables — immediately replaced by YAML load |

---

## Benchmark Reuse Matrix

| Use Case | Benchmark Suite | How |
|----------|----------------|-----|
| Regression | profile_field_benchmark | Run after locator/keyword changes to detect perf regression |
| Health checking | consent_benchmark, landing_benchmark | Quick environment validation before full suite |
| Environment validation | All 3 | Run on new device/emulator to qualify interaction reliability |
| Runtime validation | profile_field_benchmark | Verify input strategies still work after app update |
| Device qualification | All 3 | Compare strategy results across devices |

## Recommendation

Benchmark framework is well-designed and reusable. Track it. The duplication is the
cost of measurement isolation — acceptable if a consistency check is added. C2 should:
1. Extract shared helpers (keycodes, tap, blur, month_map).
2. Add locator consistency check keyword.
3. Track `tests/benchmark/` and `resources/benchmark/` in git.
