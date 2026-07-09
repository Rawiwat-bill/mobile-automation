# OCR-01 — Fresh-State OCR Route (DEV)

## Route

```
pm clear com.bangkokbank.blue.dev
→ launch app
→ Landing
→ Consent
→ Profile (CND: citizen_id, DOB, mobile)
→ PDPA
→ SignUp (Let's start)
→ ScanCardIntro (Next)
→ OCR Camera
→ [real device only] Take Photo (one capture)
→ classify result
→ STOP before OTP
```

## Step → Keyword → Locator → Proven By

| # | Step | Page Keyword | Locator | Proven By |
|---|------|--------------|---------|-----------|
| 0 | Clear app data | `Clear App Data For Fresh Run` | `adb shell pm clear` | branch_decision:61 |
| 0 | Launch | `Open Installed App On Real Device` | appPackage/Activity | branch_decision:66 |
| 1 | Landing | `Tap Landing Ready Button` | `${LANDING_READY_BUTTON}` | emulator_revival:96 |
| 2 | Consent (real dev) | `Pass Consent Screen Reliably` | adb swipe + `${CONSENT_ACCEPT_BUTTON}` | branch_decision:119 |
| 3 | Profile | `Input Citizen ID` / `Input Date Of Birth` / `Input Mobile Number` | profile locators (adb keycodes) | profile_screen_page.resource; Milestone 2 |
| 3b | Profile Next | `Tap Profile Next` | `${PROFILE_NEXT_BUTTON_CONTAINER}` via `Execute Adb Shell` | profile_screen_page.resource:168 |
| 4 | PDPA | `Tap PDPA Consent Accept Button` | `${PDPA_ACCEPT_BUTTON}` | emulator_revival:142 |
| 5 | SignUp | `Tap Sign Up Lets Start Button` | `${SIGN_UP_LETS_START}` | emulator_revival:151 |
| 6 | ScanCardIntro | `Tap Scan Card Intro Next` | `${SCAN_CARD_INTRO_NEXT}` | emulator_revival:156 |
| 7 | OCR Camera | `Wait Until ID Card Camera Capture Screen Is Displayed` | `${ID_CARD_CAMERA_VIEW}` (RVCamera) | emulator_revival:164 |
| 8 | Capture | `Tap Take Photo` | `${ID_CARD_TAKE_PHOTO}` (accessibility_id=Take photo) | id_card_camera_capture_page.resource |
| 9 | Classify | `Classify OCR Result` | DOPA / RGI- / GOD- / error / retake | NEW (dev_ocr_real_device.robot) |

## Test Data (DEV)

`testdata/onboarding/ntb.local.yaml` (gitignored, local):
- `profile.citizen_id` → `[MASKED_CITIZEN_ID]`
- `profile.date_of_birth` → `[MASKED_DOB]`
- `profile.mobile_number` → `[MASKED_PHONE]`
- `ocr.*` → thai/en names, DOB, issue/expiry, laser code, `mock_card_image: apps/android/mock/ntb_id_card.png` (EXISTS, 2.6 MB)

**No rename/sanitize performed** — mission explicitly defers sanitization; data is DEV-scoped and correct for OCR research. `ntb.example.yaml` is the committed example copy.

## Two Device Variants

### Emulator variant (boundary)
- Drives steps 0–7, **stops at OCR Camera** (step 7).
- `tests/health/emulator_revival.robot` — `Process Camera Screen` asserts camera view + Take Photo locator visible, then stops.
- No capture: emulator camera is 0-FPS (see `04_emulator_boundary.md`).

### Real-device variant (full)
- Drives steps 0–9, captures once, classifies, stops before OTP.
- `tests/investigation/dev_ocr_real_device.robot` — dryrun PASS, live run pending connected device.

## Validation
- Dryrun (new): `python3 -m robot --dryrun tests/investigation/dev_ocr_real_device.robot` → 1 passed.
- Dryrun (regression, no break): 33/33 still pass.
