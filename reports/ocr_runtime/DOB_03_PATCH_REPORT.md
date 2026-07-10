# DOB-03 — Production DOB Picker Calibration Patch Report

| Field | Value |
|-------|-------|
| **Mission** | DOB-03 — Promote DOB-02 calibration into production |
| **Date** | 2026-07-08 |
| **Branch** | `spike/appium-skill` |
| **Scope** | DOB picker only (no OCR, no Consent, no Profile redesign) |
| **Production keyword modified?** | **Yes** — `Select DOB Picker Value` (minimal, calibrated) |

## Summary

Promoted the DOB-02 calibrated slow-drag into the production framework. The hardcoded swipe
geometry/duration inside `Select DOB Picker Value` was replaced with centralized, reusable
constants in `app_constants.resource`. Direction logic, bounded retry (25), failure capture,
and logging are all preserved. The fixed `Sleep 0.1s` is now configurable `DOB_SETTLE_TIME`.

**Live result:** `emulator_revival` PASS — DOB lands on **15 Jan 1992** (`Verify DOB Field Value`
PASS, no off-by-one), route reaches OCR Camera. The OCR-03 DOB off-by-one (15→16) is fixed.

## Constants Introduced

`resources/app/app_constants.resource`:
```robotframework
${DOB_DRAG_DURATION}        400      # ms — controlled drag (was 50ms fling that overshot)
${DOB_COARSE_START_RATIO}   0.70     # finger start for coarse (diff > 2) — moves ~2 rows
${DOB_COARSE_END_RATIO}     0.30     # finger end for coarse
${DOB_FINE_START_RATIO}     0.60     # finger start for fine (diff <= 2) — moves ~1 row
${DOB_FINE_END_RATIO}       0.40     # finger end for fine
${DOB_SETTLE_TIME}          0.3      # s — settle after swipe (replaces fixed Sleep 0.1s)
```

These are the exact values measured in DOB-02 (0.70→0.30 = 2 rows 3/3; 0.60→0.40 = 1 row 3/3;
no content-desc lag). Ratios are wheel-relative (SeekBar rect fraction) → resolution-independent.

## Before / After Diff

### `resources/app/app_constants.resource` (+7 lines)
```diff
 ${BLUR_AFTER_MOBILE_Y}      1600

+${DOB_DRAG_DURATION}        400
+${DOB_COARSE_START_RATIO}   0.70
+${DOB_COARSE_END_RATIO}     0.30
+${DOB_FINE_START_RATIO}     0.60
+${DOB_FINE_END_RATIO}       0.40
+${DOB_SETTLE_TIME}          0.3
+
 &{MONTH_MAP}        01=January ...
```

### `resources/pages/onboarding/profile_screen_page.resource` — `Select DOB Picker Value` (net -3 lines)
```diff
         ${diff}=    Evaluate    abs(int(${current_index}) - int(${target_index}))
-        ${duration}=    Set Variable    500
         IF    ${diff} <= 2
-            ${top_y}=    Evaluate    int(${picker_rect['y']} + (${picker_rect['height']} * 0.35))
-            ${bottom_y}=    Evaluate    int(${picker_rect['y']} + (${picker_rect['height']} * 0.55))
-            ${duration}=    Set Variable    50
+            ${top_y}=    Evaluate    int(${picker_rect['y']} + (${picker_rect['height']} * ${DOB_FINE_END_RATIO}))
+            ${bottom_y}=    Evaluate    int(${picker_rect['y']} + (${picker_rect['height']} * ${DOB_FINE_START_RATIO}))
         ELSE
-            ${top_y}=    Evaluate    int(${picker_rect['y']} + (${picker_rect['height']} * 0.30))
-            ${bottom_y}=    Evaluate    int(${picker_rect['y']} + (${picker_rect['height']} * 0.70))
-            ${duration}=    Set Variable    50
+            ${top_y}=    Evaluate    int(${picker_rect['y']} + (${picker_rect['height']} * ${DOB_COARSE_END_RATIO}))
+            ${bottom_y}=    Evaluate    int(${picker_rect['y']} + (${picker_rect['height']} * ${DOB_COARSE_START_RATIO}))
         END
         IF    '${direction}' == 'up'
-            Execute Adb Shell    input    swipe    ${center_x}    ${bottom_y}    ${center_x}    ${top_y}    ${duration}
+            Execute Adb Shell    input    swipe    ${center_x}    ${bottom_y}    ${center_x}    ${top_y}    ${DOB_DRAG_DURATION}
         ELSE
-            Execute Adb Shell    input    swipe    ${center_x}    ${top_y}    ${center_x}    ${bottom_y}    ${duration}
+            Execute Adb Shell    input    swipe    ${center_x}    ${top_y}    ${center_x}    ${bottom_y}    ${DOB_DRAG_DURATION}
         END
-        Sleep    0.1s
+        Sleep    ${DOB_SETTLE_TIME}s
```

## What Is Preserved

| Aspect | Status |
|--------|--------|
| Direction logic (up: bottom→top; down: top→bottom) | Preserved |
| Bounded retry (25) | Preserved |
| Failure capture (`Record DOB Failure` + `Capture DOB Failure Evidence` + `Fail`) | Preserved |
| Logging (`Record DOB Picker Attempt`) | Preserved |
| Settle wait | Preserved — now configurable `DOB_SETTLE_TIME` (was fixed `0.1s`) |
| Dead `${duration}=500` default (always overridden) | Removed (was never used) |

## Validation

### Dryrun (android, benchmark, health, regression)
```bash
python3 -m robot --dryrun --outputdir /tmp/dob03_dryrun tests/android tests/benchmark tests/health tests/preparation tests/regression
```
Result: **33/33 PASS** — no regression.

### Live emulator (end-to-end)
```bash
python3 -m robot -d reports/ocr_runtime/robot_dob03 -L TRACE tests/health/emulator_revival.robot
```
Result: **1 PASS** — `Emulator Fresh State To OCR Camera` reached OCR Camera.

DOB correctness (from `reports/ocr_runtime/robot_dob03/output.xml`):
- `Input Date Of Birth` → **PASS**
- `Verify DOB Field Value` → **PASS** (field contains day=15 + year=1992 → `"15 Jan 1992"`)
- No "Could not select" failure, no mismatch.

Per-screen: landing → consent → **cnd (Profile, DOB=15 Jan 1992)** → pdpa → ocr_intro → camera, all PASS.

### Real device (task 7)
**Not run** — no real device connected (`adb devices` = emulator-5554 only). Real-device DOB
validation deferred (ratios are wheel-relative so expected to transfer, but unmeasured on 720×1604).

## Success Criteria

| # | Criterion | Status |
|---|-----------|--------|
| 1 | Patch applied | MET |
| 2 | Constants centralized in `app_constants.resource` | MET |
| 3 | No hardcoded geometry in `Select DOB Picker Value` | MET |
| 4 | DOB exact (15 Jan 1992) | MET — `Verify DOB Field Value` PASS |
| 5 | Regression green | MET — 33/33 dryrun + live emulator_revival PASS |

## Remaining Risk

1. **Year wheel large-gap unvalidated.** The calibration was measured on the DAY wheel (1–31).
   The same constants now govern the YEAR wheel (~100+ values). At 2 rows/coarse, a large year
   gap (>~50 rows) would exceed the 25-retry bound. The testdata year (1992) is within range
   (validated live). Risk: a test requiring a year far from the picker default (e.g., 1950)
   could exhaust retries. Mitigation: raise the bound or add a faster long-distance coarse
   (uncalibrated — would need its own DOB-02-style measurement first).
2. **Real device unvalidated.** Ratios are wheel-relative (SeekBar fraction), so expected to
   transfer to 720×1604, but not measured. Must confirm before claiming cross-device reliability.
3. **Month wheel** uses the same constants; 12-value range is small, low risk, but also not
   separately measured.
4. **Settle time 0.3s** — DOB-02 showed no content-desc lag (immediate == settled). 0.3s is
   conservative; could be reduced to speed up, but kept safe.

## Files Changed
- `resources/app/app_constants.resource` (+7 lines — 6 DOB constants)
- `resources/pages/onboarding/profile_screen_page.resource` (`Select DOB Picker Value` — net -3 lines)

No other files modified. No OCR/Consent/Profile-locator changes.

## Next Recommended Action
Validate the calibrated DOB on the **real device** (720×1604) once one is connected — run a
focused DOB-only check (do not continue to OCR, per task 7). If a year-wheel stress test is
needed (far-from-default year), run a separate calibration for a long-distance coarse geometry.
