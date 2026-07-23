# Stage 1 Onboarding — Complete Automation Status

## Status: AUTOMATION VALIDATED — Backend save NOT YET CERTIFIED

## Complete Flow (193.61s baseline)

```
Landing → Consent → Profile → PDPA → SignUp → ScanCard → OCR → DOPA → OTP → Set PIN → Confirm PIN → [terminal]
```

## Screen-by-Screen Interaction Methods

| Screen | Marker | Input Method | Key Behavior |
|--------|--------|-------------|--------------|
| Landing | `screenLanding_buttonReady` | `Click Element` | Ready/Skip button |
| Consent | `xpath=//*[@text="Terms and Conditions"]` | State-based marker scroll | "I have read and understood" bottom marker |
| Profile | `Tell us about you` | `Input Text` (sendKeys) + adb tap Next | RN TextInput works with sendKeys |
| PDPA | `Personal data consent` | `Click Element` Accept | — |
| SignUp | `screenSignUp_letsStartButton` | `Click Element` | — |
| ScanCard | `screenScanCardIntro_buttonNext` | `Click Element` | — |
| OCR Camera | `RVCamera` | `Click Element` + adb tap fallback | `Capture ID Card Photo` handles RN gesture issue |
| DOPA | `screenDopaInformation` | `Input Text` (text XPath) + picker wheels | `@resource-id` XPath fails (package prefix). Text XPath works. |
| OTP | `screenVerifyMobileNumberOTP` | `Input Text` (sendKeys) | Single EditText, auto-submits after 6 digits |
| Set PIN | `screenPinInput_headerText` | `Click Element` × 6 keypad | Custom keypad, auto-submits after 6 digits |
| Confirm PIN | `Re-enter PIN to confirm` | `Click Element` × 6 keypad | Prefix `screenReEnterPinInput_keyPad` |

## Known Issues

1. **DOPA resource-id XPath**: `@resource-id="exact"` fails (accessibility tree stores full package ID). Use `contains()` or text-based XPath.
2. **OCR camera `Click Element`**: Doesn't trigger RN photo capture. `Capture ID Card Photo` keyword provides adb tap fallback.
3. **`Navigate Virtual Camera To Poster`**: Fails silently (no gRPC proto stubs). Harmless with imagefile camera mode.
4. **Backend intermittent**: AJI-001 ("Service is not available now") appears unpredictably. Not an automation issue.
5. **Post-Confirm-PIN backend error**: "App is not available now" after Confirm PIN — backend save fails intermittently.

## Test Data Structure (ntb.local.yaml)

```yaml
profile: { citizen_id, date_of_birth, mobile_number }
ocr: { thai/english names, dates, laser_code, mock_card_image }
dopa: { english names, document dates, laser parts }
otp: { code: "999999" }      # DEV mock
pin: { value: "123123" }     # DEV mock
environment: { customer_type, language }
```

## PIN Keypad Digit Mapping

Digit → Keypad Index: 0→10, 1→0, 2→1, 3→2, 4→3, 5→4, 6→5, 7→6, 8→7, 9→8

## Production Keywords

- `Complete Common Onboarding` — Landing through OCR camera capture
- `Complete Stage 1 Onboarding` — Landing through Confirm PIN (extends Common Onboarding)
- `Capture ID Card Photo` — adb tap fallback for OCR photo capture

## Production Test

`tests/android/onboarding/stage1_onboarding.robot` — calls `Complete Stage 1 Onboarding`, classifies terminal state.
