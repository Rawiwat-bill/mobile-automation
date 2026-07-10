# OCR-01 — Emulator Boundary

## Boundary Statement

The Android emulator is usable for the DEV OCR route **up to the OCR Camera screen only**.
OCR capture (`Take Photo`) is **not possible** on the emulator because the virtual camera
produces no frames (0-FPS). A real device is required for the capture step and any
post-capture classification.

## Why 0-FPS

The app's OCR camera surface (`RVCamera`) expects a live camera feed. The emulator's camera
scene renderer does not deliver frames to the RN camera surface in this app configuration, so
the capture button never produces an image — the app either hangs on the camera screen or
never enables capture. This was confirmed during prior emulator revival work
(`tests/health/emulator_revival.robot` reaches the camera and deliberately stops).

## What the Emulator CAN Do (DEV OCR)

| Step | Emulator |
|------|:--------:|
| pm clear / install / launch | OK |
| Landing → Consent → Profile → PDPA → SignUp | OK |
| ScanCardIntro → OCR Camera (view + Take Photo locator visible) | OK |
| Assert camera screen reached | OK |
| Capture / OCR result | BLOCKED |

## Emulator Boundary Test

`tests/health/emulator_revival.robot` — `Emulator Fresh State To OCR Camera`:
- `pm clear` → launch → drive onboarding → reach OCR Camera → assert
  `${ID_CARD_CAMERA_VIEW}` and `${ID_CARD_TAKE_PHOTO}` are visible → **stop**.
- `Process Camera Screen` records `SHARED` decision: "Emulator reached OCR camera screen and
  stopped before capture."
- No `Tap Take Photo` is attempted (would hang / produce nothing).

## Real-Device Complement

`tests/investigation/dev_ocr_real_device.robot` continues past the emulator boundary:
OCR Camera → `Tap Take Photo` → `Classify OCR Result` → stop before OTP.

## Rule

> Emulator may be used only until the OCR Camera boundary. Capture and post-capture
> classification require a real device.
