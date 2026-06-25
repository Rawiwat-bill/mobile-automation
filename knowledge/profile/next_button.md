# Profile Next Button — Solved

## Problem
Profile fields populate successfully, but the onboarding flow does not hand off after tapping `Next` from the Profile screen when automation uses Appium `Click Element` or `Tap`.

## Symptoms
- All 3 fields (Citizen ID, DOB, Mobile Number) fill and blur correctly
- Next button is visible, enabled, and bounds-verified
- Appium `Click Element`, coordinate `Tap`, W3C tap, and native tap all fail to trigger handoff
- Manual tap succeeds and reaches `Service is not available now` (AJI-001)
- Automation remains on Profile screen after attempting tap

## Evidence
- Investigation report: `reports/investigation/profile/profile_next_investigation_report.md`
- XML captures at: `reports/investigation/profile/profile_after_next.xml`
- Manual success evidence at: `reports/investigation/profile/manual_success/`

## Root Cause
The app uses React Native gesture handling that does not respond correctly to Appium-generated touch events (`Click Element`, `Tap`). The React Native `TouchableOpacity`/`onPress` handler requires OS-level touch input, which `adb shell input tap` provides.

The form data entry method also matters: using `Press Keycode` (adb keycodes) for Citizen ID and Mobile Number triggers proper React Native `onChange` events, unlike `Input Text` which uses `element.sendKeys()`.

## Working Fix

### Required Appium startup
```bash
appium --relaxed-security
```
Without `--relaxed-security`, `Execute Adb Shell` is blocked by Appium's security policy.

### Robot keyword used
```robot
Tap Profile Next Using Adb
    ${element_rect}=    Get Element Rect    ${PROFILE_NEXT_BUTTON_CONTAINER}
    ${center_x}=    Evaluate    int(${element_rect['x']} + (${element_rect['width']} / 2))
    ${center_y}=    Evaluate    int(${element_rect['y']} + (${element_rect['height']} / 2))
    Execute Adb Shell    input    tap    ${center_x}    ${center_y}
```

Fallback to Appium `Tap` is included in `Tap Profile Next Button` if adb tap does not navigate.

### Data entry changes
- `Input Citizen ID` uses `Enter Digits By Keycodes` (adb `Press Keycode` per digit) instead of Appium `Input Text`
- `Enter Mobile Number By Keycodes` refactored to share `Enter Digits By Keycodes`

## Validation Result
```
Landing → Consent → Profile → adb tap Next → navigated away from Profile → Service is not available now
```
- `Execute Adb Shell` → PASS
- `Wait Until Page Does Not Contain Element ${PROFILE_TITLE_TEXT}` → PASS (Profile disappeared)
- `Wait Until Page Contains Element "Service is not available now"` → PASS

## Note
`AJI-001` (Service is not available now) is the destination/environment issue (dev backend not reachable), not a Profile handoff failure. The handoff itself succeeded.

## Rejected Experiments
- `Click Element` on inner `base-btn`
- Appium coordinate tap at verified center point
- W3C/action tap
- Native center tap
- Outer container `click`/`tap`
- All of the above without `--relaxed-security` (adb blocked)

## Privacy
No real Citizen ID or phone numbers are included in this file or in the investigation report.
