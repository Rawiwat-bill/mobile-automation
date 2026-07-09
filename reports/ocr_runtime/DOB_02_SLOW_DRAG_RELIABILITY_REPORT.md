# DOB-02 — Calibrated Slow Drag Reliability Report

| Field | Value |
|-------|-------|
| **Mission** | DOB-02 — Calibrated Slow Drag Reliability |
| **Date** | 2026-07-08 |
| **Branch** | `spike/appium-skill` |
| **Scope** | Emulator only, DEV only, DOB picker only (no OCR, no Consent) |
| **AVD** | `local_android_36` (API 36, arm64, 1080×2400, headless) |
| **Production keyword modified?** | **No** — `Select DOB Picker Value` untouched (separate investigation test only) |

## Summary

Calibrated a reliable DOB day-wheel swipe strategy. A **400ms slow drag** with **0.70→0.30
ratio** moves exactly **2 rows** (3/3 consistent) and **0.60→0.40** moves exactly **1 row**
(3/3 consistent). No content-desc lag observed (immediate read == settled read for all 18
measurements). A coarse+fine algorithm landed **exactly on day 15** producing **"15 Jan 1992"**
in **3/3 consecutive attempts**.

## Method

`tests/investigation/dob_slow_drag_reliability.robot` (does NOT modify production):
1. `pm clear` → drive to Profile → open DOB picker → set Year=1992, Month=January (existing swipe keyword, read-only).
2. **Calibration**: 6 geometries × 3 attempts each, 400ms drag. Per attempt: read before,
   swipe, read immediate, settle 0.3s, read settled, compute delta + lag.
3. **Auto-pick**: coarse = geometry with avg delta closest to 2; fine = closest to 1 (>0).
4. **Validation**: 3 attempts — reset to low, coarse until within 2, fine until exact 15, Done, verify field.

Geometries tested (finger up = toward higher values): `0.70|0.30, 0.60|0.40, 0.55|0.45,
0.52|0.48, 0.50|0.42, 0.58|0.50`.

## Calibration Results

| Geometry | deltas (3 attempts) | avg delta | lag | verdict |
|----------|:---:|:---:|:---:|---------|
| **0.70→0.30** | 2, 2, 2 | **2.0** | none | **reliable coarse (2 rows)** |
| **0.60→0.40** | 1, 1, 1 | **1.0** | none | **reliable 1-row nudge** |
| 0.55→0.45 | 0, 0, 1 | 0.33 | none | unreliable |
| 0.52→0.48 | 0, 0, 0 | 0.0 | none | no movement (too small) |
| 0.50→0.42 | 0, 0, 0 | 0.0 | none | no movement |
| 0.58→0.50 | 1, 1, 0 | 0.67 | none | mostly 1, not consistent |

- **content-desc lag: NONE.** `after_immediate == after_settled` for all 18 measurements. The
  SeekBar `content-desc` is stable immediately after the 400ms swipe (the ~0.1–0.3s Appium
  `Get Element Attribute` call is enough settle time).
- **Min safe sleep after swipe:** the read is stable with no added sleep; `SAFE_SLEEP=0.35s`
  was used in the algorithm and is more than sufficient (could be reduced to ~0.1s).
- Per-move elapsed: ~2.0s (swipe 0.4s + 2× Appium attribute read + sleep — Appium call
  overhead dominates, not the swipe).

## Algorithm Validation (3 consecutive attempts)

Auto-picked: **COARSE = 0.70|0.30** (2 rows), **FINE = 0.60|0.40** (1 row).

| Attempt | start | algo trace | landed | field | exact | elapsed |
|:---:|:---:|---|:---:|---|:---:|:---:|
| 1 | 3 | 5→7→9→11→13→14→15 | 15 | `15 Jan 1992` | ✅ | 12.115s |
| 2 | 3 | 5→7→9→11→13→14→15 | 15 | `15 Jan 1992` | ✅ | 12.208s |
| 3 | 2 | 4→6→8→10→12→14→15 | 15 | `15 Jan 1992` | ✅ | 12.209s |

Coarse (2 rows) brings the wheel within 1 of target, then one fine nudge (1 row) lands exact.
Visual confirmation: `dob_field_final.xml` shows `screenProfile_textInputDob text="15 Jan 1992"`.

## Success Criteria

| # | Criterion | Status |
|---|-----------|--------|
| A | Reliable 1-row nudge measured, not assumed | **MET** — 0.60→0.40 = 1.0 avg, 3/3 consistent |
| B | Day wheel lands exactly on 15 | **MET** — 3/3 attempts |
| C | DOB field becomes exactly "15 Jan 1992" | **MET** — 3/3 attempts |
| D | Timing recorded | **MET** — ~2.0s/move, ~12.2s/attempt (incl. reset) |
| E | Production keyword unchanged unless approved | **MET** — no production code modified |

## Proposed Production Patch (NOT applied — awaiting explicit approval)

Replace the 50ms fling in `Select DOB Picker Value` (`resources/pages/onboarding/profile_screen_page.resource`)
with a calibrated 400ms two-phase drag:

```
diff > 2  → coarse: swipe 0.70→0.30 (ratio of wheel height), 400ms   # +2 rows
diff ≤ 2  → fine:   swipe 0.60→0.40 (or reversed for down), 400ms     # ±1 row
read SeekBar content-desc after each move (no lag → no extra sleep needed; 0.1–0.3s settle is safe)
bounded retries (≤ ~20)
```

Key changes vs current production keyword:
- **duration 50ms → 400ms** (fling → controlled drag; eliminates overshoot).
- **geometry**: use `0.70/0.30` (coarse) and `0.60/0.40` (fine) instead of the current
  `0.30–0.70` / `0.35–0.55` split.
- **no Sleep needed** for content-desc lag (none observed) — a small 0.1–0.3s settle is safe.
- Ratios are wheel-relative (SeekBar rect), so resolution-independent — should work on the
  720×1604 real device too, **but untested there** (emulator-only per mission scope).

## Risk / Note
- Validated on emulator only (1080×2400). Real device (720×1604) untested — ratios are
  wheel-relative so expected to transfer, but must be confirmed before claiming production reliability.
- The 50ms fling (current production) overshoots because it imparts momentum; the 400ms drag
  moves a deterministic number of rows. This is the root fix for the DOB-01 off-by-one (15→16).
- Per-move ~2s is dominated by Appium `Get Element Attribute` round-trips, not the swipe.
  Production could read less often (e.g., only after coarse phase) to speed up, but correctness
  first.

## Evidence
- `reports/ocr_runtime/evidence/dob02/calibration.csv` — 18 measurements (geometry, attempt, before, after_immediate, after_settled, delta, lag, elapsed)
- `reports/ocr_runtime/evidence/dob02/chosen.txt` — auto-picked coarse/fine + avg deltas
- `reports/ocr_runtime/evidence/dob02/validation.csv` — 3 attempts (landed_day, field_text, exact_match, elapsed)
- `reports/ocr_runtime/evidence/dob02/dob_field_final.{png,xml}` — visual confirmation (`text="15 Jan 1992"`)
- Robot output: `reports/ocr_runtime/robot_dob02/{output.xml,log.html,report.html}`

## Validation
```bash
python3 -m robot -d reports/ocr_runtime/robot_dob02 -L TRACE tests/investigation/dob_slow_drag_reliability.robot
```
Result: 1 passed, 0 failed. Classification: **calibrated slow-drag is reliable** (3/3 exact).

## Next Recommended Action
With explicit approval, apply the proposed patch to `Select DOB Picker Value` (400ms, 0.70/0.30
coarse + 0.60/0.40 fine), then validate on the **real device** (720×1604) and re-run the full
`emulator_revival` flow to confirm DOB = "15 Jan 1992" end-to-end (removing the OCR-03 DOB
off-by-one risk for the downstream OCR/DOPA path).
