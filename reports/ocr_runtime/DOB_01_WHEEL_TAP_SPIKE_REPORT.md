# DOB-01 — Wheel Tap Selection Spike Report

| Field | Value |
|-------|-------|
| **Mission** | DOB-01 — Wheel Tap Selection Spike |
| **Date** | 2026-07-08 |
| **Branch** | `spike/appium-skill` |
| **Scope** | Emulator only, DEV only, DOB picker only (no OCR, no camera) |
| **AVD** | `local_android_36` (API 36, arm64, 1080×2400, headless) |
| **Production keyword modified?** | **No** — `Select DOB Picker Value` untouched (used read-only for year/month) |

## Hypothesis

The 50ms adb swipe behaves as a fling and overshoots day 15 → 16. Alternative: scroll the
target value into the visible DOM, then tap the visible text element to select it.

## Method

`tests/investigation/dob_wheel_tap_spike.robot` (separate investigation test; does NOT modify
the production keyword):
1. `pm clear` → launch → drive to Profile (Landing → Consent).
2. Open DOB picker (tap `${PROFILE_DOB_CONTAINER}`).
3. Select Year=1992, Month=January via the existing `Select DOB Picker Value` (swipe) — read-only use.
4. Day wheel tap experiment:
   - Read current day from SeekBar `content-desc` (`"Day picker, <value>"`).
   - Detect target `15` via `xpath=//*[@resource-id="screenProfile_calendarDatePicker-dateScroll"]//android.widget.TextView[@text="15"]`.
   - If not visible: **slow drag** (400ms `adb shell input swipe`) toward target, re-detect.
   - If visible: `Click Element` on the `15` TextView, re-read `content-desc`.
5. Tap Done, read DOB field.
6. Capture before/after XML + screenshots; classify.

## Result: `TAP_SELECT_VISIBLE_BUT_NO_SELECTION`

The target `15` was brought into view and was genuinely visible, but **tapping its text node
did not select it.** The RN wheel picker does not respond to tap-to-select on a row.

### Experiment trace (from log)
```
day current=1 target=15
iter 0: not visible → slow drag 400ms → day=3
iter 1: not visible → slow drag 400ms → day=5
iter 2: not visible → slow drag 400ms → day=7
iter 3: not visible → slow drag 400ms → day=9
iter 4: not visible → slow drag 400ms → day=11
iter 5: not visible → slow drag 400ms → day=12
iter 6: not visible → slow drag 400ms → day=14
iter 7: target '15' visible — tapping text node
day after tap=14            ← tap did NOT select 15
DOB field after Done='14 Jan 1992'
CLASSIFICATION=TAP_SELECT_VISIBLE_BUT_NO_SELECTION  field_ok=False
```

### Evidence (before/after XML)
**`day_before_tap.xml`** (experiment start):
- SeekBar `content-desc="Day picker, 1"`, visible rows: `1, 2, 3` (15 not rendered).

**`day_after_tap.xml`** (after the tap):
- SeekBar `content-desc="Day picker, 14"` (unchanged by the tap).
- Visible rows: `12, 13, 14, 15, 16`.
- `14` TextView bounds `[140,1493][199,1573]` — at wheel center (selected).
- `15` TextView bounds `[146,1648][193,1712]` — directly below center, **visible and tappable**.
- Tapping `15` left the selection on `14` → tap-to-select does not work.

## Secondary Finding — Slow Drag Is Controllable

The 400ms drag moved the wheel **predictably ~2 rows per drag** (1→3→5→7→9→11→12→14),
with **no overshoot** beyond the target range. This contrasts sharply with the 50ms fling
(which overshoots 15→16). Implication: a slow-drag approach with finer geometry (smaller
swipe region for 1-row nudges) is the more promising path for precise landing — but the
final 1-row nudge (14→15) still needs a smaller-amplitude swipe than tested here.

## Conclusion

- **Tap-selection is ruled out** for this RN wheel picker. Do not implement `Click Element`
  on a visible row as a selection mechanism.
- The production `Select DOB Picker Value` was not modified (per mission rule).
- The 400ms slow drag is a candidate for a future DOB-reliability improvement (separate mission).

## Recommendation (for a future DOB-reliability mission, not this spike)

1. Replace the 50ms fling with a 400ms (or slower) drag for coarse positioning.
2. For the final 1-row nudge, use a very small-amplitude swipe (e.g., 0.45–0.55 of wheel
   height, ~300–500ms) and re-read `content-desc` until it matches.
3. Alternatively, request developer support for a `testID`/accessibility setter on each wheel
   (per `knowledge/profile/dob_picker.md` §8) — the picker rejects all direct input except swipes.

## Evidence Paths
- `reports/ocr_runtime/evidence/dob01/profile_before_picker.{png,xml}`
- `reports/ocr_runtime/evidence/dob01/picker_opened.{png,xml}`
- `reports/ocr_runtime/evidence/dob01/day_before_tap.{png,xml}`
- `reports/ocr_runtime/evidence/dob01/day_after_tap.{png,xml}`
- `reports/ocr_runtime/evidence/dob01/after_done.{png,xml}`
- `reports/ocr_runtime/evidence/dob01/classification.txt`
- Robot output: `reports/ocr_runtime/robot_dob01/{output.xml,log.html,report.html}`

## Validation
```bash
python3 -m robot -d reports/ocr_runtime/robot_dob01 -L TRACE tests/investigation/dob_wheel_tap_spike.robot
```
Result: 1 passed, 0 failed (spike completed; classification = `TAP_SELECT_VISIBLE_BUT_NO_SELECTION`).
