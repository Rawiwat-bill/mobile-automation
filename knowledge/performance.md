# Performance Knowledge

## Known Bottlenecks

### 1. Profile Next Button
- **Issue:** Appium tap gestures fail on React Native buttons; adb shell input tap required
- **Impact:** Adds ~500ms for coordinate calculation and adb execution
- **Status:** Accepted — no faster stable alternative

### 2. Citizen ID Input
- **Issue:** Resolved. Appium `Input Text` triggers RN `onChangeText` reliably (verified Sprint 2.10.3 — byte-identical to manual typing)
- **Production method:** `Input Text Field` — single `sendKeys()` call via `Profile Screen Page.Input Citizen ID`
- **Benchmarked strategies:** Input Text, Input Value, Press Keycodes, Adb Shell, Execute Script (benchmark still tests all strategies for comparison)
- **Status:** Production path migrated to `Input Text` (Sprint 2.11). Benchmark results pending for strategy ranking.

### 3. DOB Input
- **Issue:** React Native TextInput for DOB does not respond to Appium text entry
- **Workaround:** Date Picker manipulation or direct field value setting
- **Benchmarked strategies:** Picker Calculated, Input Text, Adb Shell, Input Value
- **Status:** Needs benchmark results to rank fastest stable option

### 4. Mobile Number Input
- **Issue:** Resolved. Same as Citizen ID — Appium `Input Text` works reliably
- **Production method:** `Input Text Field` — single `sendKeys()` call via `Profile Screen Page.Input Mobile Number`
- **Benchmarked strategies:** Input Text, Input Value, Press Keycodes, Adb Shell, Execute Script
- **Status:** Production path migrated to `Input Text` (Sprint 2.11).

### 5. Consent Screen Scroll
- **Issue:** Full consent terms require scrolling; Appium swipe gestures unreliable on RN
- **Workaround:** adb shell swipe for scroll
- **Impact:** ~1-2s per scroll operation

## Optimization Rules

1. **No optimization without benchmark evidence.** Every production change must include a before/after comparison in `reports/performance/comparison.md`.
2. Fixed long waits are replaced with event-based waits.
3. Excessive screenshots and repeated page source calls are avoided.
4. `Sleep` is never used.
5. Condition-based scrolling replaces fixed scroll loops.

## Performance Baseline

- Explicit waits with reasonable timeouts (10-30s depending on network)
- Bounded loops with clear exit conditions
- Condition-based scrolling when possible
- Test execution suitable for CI/CD pipelines

## Performance Observatory

The Performance Observatory at `tools/performance/` provides automated processing of benchmark output:

| Tool | Purpose |
|------|---------|
| `tools/performance/run_benchmark.sh` | Run all benchmarks, parse, compare |
| `tools/performance/parse_benchmark.py` | Extract BENCHMARK\| lines → JSON/Markdown |
| `tools/performance/compare_benchmark.py` | Compare latest vs previous → improvements/regressions |

### Workflow for Optimization

1. **Baseline:** Run `bash tools/performance/run_benchmark.sh` before any change.
2. **Review:** Read `reports/performance/latest.md` for current rankings.
3. **Change:** Implement the optimization in production code.
4. **Measure:** Run `bash tools/performance/run_benchmark.sh` again.
5. **Compare:** Read `reports/performance/comparison.md` to confirm improvement.
6. **Commit:** Only commit if benchmark evidence shows improvement without stability regression.

Storage: `reports/performance/latest.json`, `reports/performance/history/<timestamp>.json`

## Internal Project Truth

This knowledge captures real performance findings from the project. External performance suggestions from skills are secondary. Benchmark results from the project's own benchmark suite are the authoritative data source.
