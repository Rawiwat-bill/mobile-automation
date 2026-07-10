# OCR-02 — Emulator Boundary Validation

> **Scope:** DEV only, emulator only. Validate the fresh-state route reaches the OCR Camera boundary.

## Run

| Field | Value |
|-------|-------|
| **Test** | `tests/health/emulator_revival.robot` |
| **AVD** | `local_android_36` (google_apis, arm64-v8a, API 36, 1080×2400) |
| **Boot** | headless, `-no-snapshot-load -no-boot-anim -gpu swiftshader_indirect`; `boot_completed=1` in ~19s |
| **Device serial** | `emulator-5554` |
| **Appium** | running, `--relaxed-security --allow-insecure get_server_logs,adb_shell` |
| **Command** | `python3 -m robot -d reports/ocr_runtime/robot -L TRACE tests/health/emulator_revival.robot` |
| **Result** | **FAIL** — `CND/Profile did not transition on emulator.` |

## Outcome: BLOCKED at Profile/CND (did NOT reach OCR Camera)

The emulator route did **not** reach the OCR Camera boundary. It stalled at the Profile/CND
screen. The OCR Camera 0-FPS boundary was therefore **not validated** this run — the blocker is
upstream of the camera.

## Exact Blocker (evidence-based)

| Item | Evidence |
|------|----------|
| **Screen** | `screenProfile_` marker present in page source → **Profile/CND** |
| **Activity** | `com.bangkokbank.blue.dev/com.bangkokbank.blue.MainActivity` (RN single-activity, still on Profile route) |
| **Failing keyword** | `Input CND Data With Masked Logs` → **False**; `Tap Profile Next` → **False** (`cnd/result.md`) |
| **DOB field** | `screenProfile_textInputDob` `text="16 Jan 1992"` (filled; testdata DOB is `15-01-1992` — observed off-by-one, recorded as evidence, not diagnosed) |
| **Mobile field** | `screenProfile_textInputMobileNumber` shows placeholder `Enter 10-digit mobile number` → **empty** |
| **Next button** | `screenProfile_buttonNext`, `enabled="true"`, `clickable="true"`, bounds `[59,2125][1021,2268]` — enabled in hierarchy, but adb input tap did not transition |
| **Assertion that failed** | `Should Be True ${page_result}` in `Process CND Screen` (`emulator_revival.robot:129`) |

This matches the prior-session `reports/investigation/emulator_revival/REPORT.md` (2026-07-07
17:30): *"The flow did not transition past CND/Profile on the emulator. DOB input and the next
navigation step did not complete the branch."* → **reproducible**, not a flake.

## Reproducibility

| Run | Date | Reached | Blocker |
|-----|------|---------|---------|
| Prior | 2026-07-07 15:42–17:30 | Landing, Consent, CND | CND/Profile transition |
| OCR-02 (this) | 2026-07-07 22:44 | Landing, Consent, CND | CND/Profile transition |

## Evidence Captured

### Test-captured (test's own evidence dir)
- `reports/investigation/emulator_revival/evidence/landing.png` (+ `_activity.txt`)
- `reports/investigation/emulator_revival/evidence/consent_before.png`, `consent_after_scroll.png`, `consent_after_accept.png` (+ activity)
- `reports/investigation/emulator_revival/evidence/cnd_before.png`, `cnd_after.png` (+ activity)
- `reports/investigation/emulator_revival/cnd/result.md` (locator/keyword/page results)

### OCR-02 focused evidence (proper page source)
- `reports/ocr_runtime/evidence/ocr02/profile_page_source.xml` (31 KB, non-compressed uiautomator dump)
- `reports/ocr_runtime/evidence/ocr02/profile_blocked.png`
- `reports/ocr_runtime/evidence/ocr02/profile_activity.txt`

### Robot output
- `reports/ocr_runtime/robot/output.xml`
- `reports/ocr_runtime/robot/log.html`
- `reports/ocr_runtime/robot/report.html`

## Evidence-Method Finding (not fixed — out of scope)

The test's `Capture Screen Evidence` keyword uses `adb shell uiautomator dump --compressed
/sdcard/window_dump.xml`. On this AVD (API 36) the dump writes **no file** → `cat` returns
`/sdcard/window_dump.xml: No such file or directory` (all test-captured `*.xml` are 55 bytes
containing that error). A non-compressed dump to `/data/local/tmp/` succeeds (31 KB). Appium
`Get Source` (used by `onboarding_branch_decision.robot`) is the more reliable method.

**Not fixed** — mission rules: do not modify OCR capture code / minimal changes / no broad
investigation. Flagged for a focused evidence-capture fix later.

## Emulator Boundary (OCR Camera 0-FPS)

**Not reached this run.** The expected 0-FPS camera boundary remains as documented in
`04_emulator_boundary.md` (from OCR-01). It cannot be re-validated until the Profile/CND
blocker is unblocked on the emulator.

## Stop Decision

Per mission task 4: blocker identified at exact screen (Profile/CND), evidence captured,
investigation **not** broadened, no fix attempted. The emulator is left running
(`emulator-5554`) for inspection.

## Next Action (recommended)

A **focused** Profile-on-emulator unblock mission (separate from OCR-02):
- Root-cause: (a) mobile number not entering, (b) DOB picker off-by-one, (c) `Tap Profile Next`
  adb tap not transitioning on 1080×2400 despite enabled button.
- Compare against the real-device Profile path (which works via the same shared keywords).
- Re-run OCR-02 once Profile transitions on emulator.
