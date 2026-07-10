# OCR-02 — Emulator Boundary Validation Report

| Field | Value |
|-------|-------|
| **Mission** | OCR-02 — Emulator OCR Boundary Validation |
| **Date** | 2026-07-07 |
| **Branch** | `spike/appium-skill` |
| **Scope** | DEV only, emulator only (no real device, no SIT/UAT, no Frida, no APK patch) |
| **Test** | `tests/health/emulator_revival.robot` (unmodified) |

## Summary

Ran `emulator_revival.robot` live on the `local_android_36` AVD (API 36, arm64, 1080×2400,
headless). The fresh-state route **did not reach the OCR Camera boundary**. It stalled at the
**Profile/CND screen**: `Input CND Data With Masked Logs` and `Tap Profile Next` both returned
False. This is the **same blocker** documented in the prior-session
`reports/investigation/emulator_revival/REPORT.md` (2026-07-07 17:30) — reproducible, not a
flake. Per mission task 4, the exact blocker was identified, evidence captured, and
investigation was **not** broadened.

The OCR Camera 0-FPS boundary could therefore not be re-validated this run (blocker is upstream).
`Take Photo` was never tapped (correct — emulator capture remains real-device only).

## Success Criteria

| # | Criterion | Status |
|---|-----------|--------|
| A | Emulator reaches OCR Camera and stops | **NOT MET** — blocked at Profile/CND |
| B | If not, exact blocker is identified | **MET** — Profile/CND; `Tap Profile Next` non-transition; mobile field empty, DOB filled (off-by-one observed), Next enabled in hierarchy |

## Exact Blocker

- **Screen**: Profile/CND (`screenProfile_` marker).
- **Activity**: `com.bangkokbank.blue.dev/.MainActivity` (RN, did not navigate).
- **Failing step**: `Process CND Screen` → `Should Be True ${page_result}` failed (`emulator_revival.robot:129`).
- `cnd/result.md`: Locator=True, Keyword (CND input)=False, Page Object (Tap Next)=False.
- **Next button**: `screenProfile_buttonNext`, `enabled="true"`, bounds `[59,2125][1021,2268]` — enabled but adb input tap did not transition.
- **Fields**: DOB `text="16 Jan 1992"` (filled; testdata `15-01-1992`); mobile shows placeholder (empty).

## Agents Used
- qa-orchestrator (execution + evidence only; no code changes authorized or made).

## Files Checked
- `tests/health/emulator_revival.robot` (re-read before run)
- `reports/investigation/emulator_revival/REPORT.md` (prior-session finding)
- `reports/investigation/emulator_revival/evidence/*` + `cnd/result.md`
- Live page source / activity (captured this run)

## Files Changed
**None.** No code modified (mission: do not modify OCR capture code; minimal changes; no broad
investigation). The test was run unmodified.

## Validation Command
```bash
python3 -m robot -d reports/ocr_runtime/robot -L TRACE tests/health/emulator_revival.robot
```

## Validation Result
- **1 test, 0 passed, 1 failed** — `CND/Profile did not transition on emulator.`
- Robot output: `reports/ocr_runtime/robot/{output.xml,log.html,report.html}`.

## Evidence
- Test evidence: `reports/investigation/emulator_revival/evidence/{landing,consent_*,cnd_*}.png` + `_activity.txt` + `cnd/result.md`
- OCR-02 focused: `reports/ocr_runtime/evidence/ocr02/{profile_page_source.xml, profile_blocked.png, profile_activity.txt}`
- Emulator left running: `emulator-5554` (for inspection; kill when done).

## Security Review
- Emulator only; no real device; no PII added.
- `ntb.local.yaml` not modified (mission: do not change testdata); values not echoed in this report.
- No APK patch, no Frida, no SIT/UAT.

## Performance Review
- Emulator boot ~19s; test run to failure ~2 min (install 227 MB APK + pm clear + drive to CND).
- No new waits introduced (no code changes).

## Risk / Note
- **Primary risk:** the emulator route is not yet stable to the OCR Camera boundary. The
  Profile/CND blocker prevents CI/CD emulator coverage of the OCR path until unblocked.
- The blocker is the same class as Milestone 2 (RN touch vs Appium/adb) but on the emulator's
  1080×2400 surface; the shared `Tap Profile Next` (adb input tap) works on the 720×1604 real
  device but did not transition here.
- Evidence-method gap: the test's `uiautomator dump --compressed /sdcard/` fails on API 36 (all
  test `*.xml` are 55-byte error stubs). Non-compressed `/data/local/tmp/` dump works. Not fixed
  (out of scope) — flagged for later.
- No broad root-cause performed, per mission rules.

## Playbook / Pattern Used
- `knowledge/playbooks/debugging-playbook.md` — consulted for evidence-first stance; broad
  root-cause explicitly deferred per mission task 4 ("do not investigate broadly").
- `knowledge/patterns/page-object-pattern.md` — confirmed the failing step routes through shared
  page keywords (`Tap Profile Next`).

## Next Recommended Action
Focused **Profile-on-emulator unblock** mission (separate from OCR-02):
1. Root-cause mobile-number entry failure, DOB picker off-by-one, and `Tap Profile Next`
   non-transition on 1080×2400 (compare vs real-device path).
2. Fix the test's `Capture Screen Evidence` XML method (non-compressed dump or Appium `Get Source`).
3. Re-run OCR-02 to validate the OCR Camera boundary.

## Deliverables
- `reports/ocr_runtime/06_emulator_boundary_validation.md` — detailed validation + evidence
- `reports/ocr_runtime/OCR_02_EMULATOR_BOUNDARY_REPORT.md` — this file
