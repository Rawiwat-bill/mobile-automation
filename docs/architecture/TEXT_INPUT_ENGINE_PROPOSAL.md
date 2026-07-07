# Text Input Engine — Architecture Proposal

## Problem

The project currently uses a single mechanism — `Enter Digits By Keycodes` (`Press Keycode` per digit) — for all text entry. This is:
1. **Slower**: 13 Appium calls for a 13-digit CID vs 1 call for `Input Text`
2. **Historically inaccurate**: The keycode approach was adopted because of a misunderstanding — RN gesture issues with the Next button were incorrectly attributed to text input
3. **Not extensible**: Future fields (Name, Email, Address) use alphanumeric input, not digits. Keycodes cannot handle alphabetic characters in a portable way

## Proposed Architecture

```
┌─────────────────────────────────────────────────────┐
│                 TextInput Engine                      │
│  (Appium Input Text — single sendKeys() call)        │
│                                                       │
│  Input Text Into Field                                │
│  ├─ Focus field                                       │
│  ├─ Input Text (full value, single call)              │
│  ├─ Hide Keyboard (if needed)                         │
│  └─ Verify via Get Text (normalized)                  │
├─────────────────────────────────────────────────────┤
│  Supports:                                            │
│  ├─ Numeric (Citizen ID, Mobile, PIN*)                │
│  ├─ Alphanumeric (Name, Email, Address*)              │
│  └─ Formatted (auto-dash, auto-slash*)               │
└─────────────────────────────────────────────────────┘
         │
         ├──▶ Citizen ID    (migrated from keycodes)
         ├──▶ Mobile Number (migrated from keycodes)
         ├──▶ Name*         (new — alphanumeric)
         ├──▶ Email*        (new — alphanumeric with @)
         ├──▶ Address*      (new — mixed)
         └──▶ ...           (future TextInput fields)

┌─────────────────────────────────────────────────────┐
│                Wheel Picker Engine                     │
│  (adb shell input swipe + center text detection)      │
│                                                       │
│  Swipe To Value                                       │
│  ├─ Read center text                                   │
│  ├─ Calculate direction and steps                      │
│  ├─ Execute Adb Shell input swipe                     │
│  └─ Verify center text                                 │
├─────────────────────────────────────────────────────┤
│  Currently:                                           │
│  └── DOB (Day, Month, Year)                          │
│  Future:                                              │
│  ├── Province / District / Sub-district               │
│  ├── Occupation                                        │
│  └── Any wheel picker                                 │
└─────────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────┐
│                 Gesture Engine                         │
│  (adb shell input tap / adb shell input swipe)        │
│                                                       │
│  Tap Element Via Adb                                  │
│  ├─ Get element rect                                   │
│  ├─ Calculate center coordinates                       │
│  └─ Execute Adb Shell input tap                       │
│                                                       │
│  Swipe Scroll Via Adb                                 │
│  ├─ Get scroll container bounds                       │
│  ├─ Calculate start/end coordinates                    │
│  └─ Execute Adb Shell input swipe                     │
├─────────────────────────────────────────────────────┤
│  Currently:                                           │
│  ├── Profile Next button                              │
│  ├── Consent screen scroll                            │
│  ├── DOB picker scroll                                │
│  └── Any RN TouchableOpacity/WheelPicker              │
└─────────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────┐
│                 OTP Engine* (Future)                   │
│  (Per-character input — may need keycodes)            │
│                                                       │
│  Enter OTP Digit                                      │
│  ├─ Focus field                                        │
│  ├─ Input single character                             │
│  ├─ Auto-advance to next field                        │
│  └─ Verify via text attribute                         │
├─────────────────────────────────────────────────────┤
│  Future:                                              │
│  └── OTP / PIN / Passcode                            │
└─────────────────────────────────────────────────────┘
```

## Key Principles

1. **Single responsibility**: TextInput Engine handles only `TextInput` fields. Gesture handling (taps, swipes) belongs in Gesture Engine. Picker interaction belongs in Picker Engine.

2. **`Input Text` for TextInput, `adb` for gestures**: React Native `TextInput` components accept standard Appium `Input Text` (sendKeys). React Native `TouchableOpacity`/`onPress`/`WheelPicker` components require `adb shell` level interaction. These are independent.

3. **Verification via `Get Text`**: After input, verify the field value by reading the `text` attribute via `Get Text` with non-digit normalization for comparison. Page source XML is the source of truth; `Get Element Attribute` is the reliable accessor.

4. **IME handling**: When a field requires keyboard dismissal (e.g., Mobile Number's Done action), use `Hide Keyboard` instead of `Press Keycode 66`. This avoids keycode dependency while achieving the same effect.

## Engine Keyword Design (Reference Only — Not Implemented)

```robot
Input Text Into Field
    [Arguments]    ${field_locator}    ${value}    ${verify}=${TRUE}
    Click Element    ${field_locator}
    Clear Text    ${field_locator}
    Input Text    ${field_locator}    ${value}
    IF    ${verify}
        ${actual}=    Get Text    ${field_locator}
        ${normalized_actual}=    Replace String Using Regexp    ${actual}    [^0-9a-zA-Z]    ${EMPTY}
        ${normalized_expected}=    Replace String Using Regexp    ${value}    [^0-9a-zA-Z]    ${EMPTY}
        Should Be Equal As Strings    ${normalized_actual}    ${normalized_expected}
    END
    Run Keyword And Ignore Error    Hide Keyboard
```

## Migration Path

| Step | Action | Sprint |
|:----:|--------|--------|
| 1 | Make `Input Citizen ID` use `Input Text` instead of `Enter Digits By Keycodes` | Sprint 2.11 |
| 2 | Simplify `Input Mobile Number` — remove keycode path, keep only `Input Text` + `Hide Keyboard` | Sprint 2.11 |
| 3 | Dryrun + real device validation | Sprint 2.11 |
| 4 | Update knowledge files | Sprint 2.11 |
| 5 | Update `docs/Architecture.md` | Sprint 2.11 |
| 6 | Remove or deprecate `Enter Digits By Keycodes` from production keywords (keep in benchmark) | Sprint 2.12 |

## Engine Decision Guide

New field appears on screen → ask:

```
Is it a TextInput (accepts keyboard text)?
   YES → Use TextInput Engine (Input Text)
   NO  → Is it a Wheel Picker?
            YES → Use Picker Engine (adb swipe)
            NO  → Is it a Button / Scroll / Gesture component?
                     YES → Use Gesture Engine (adb tap/swipe)
                     NO  → Investigate (new component type)
```

## What This Replaces

| Engine | Replaces | Removes |
|--------|----------|---------|
| TextInput Engine | `Enter Digits By Keycodes` for CID, Mobile | 13 `Press Keycode` calls per CID session |
| TextInput Engine | `Enter Mobile Number By Keycodes` wrapper | Redundant keyword |
| TextInput Engine | Keycode fallback path in `Input Mobile Number` | 2-branch logic (keycodes vs Input Text) |

## What This Does NOT Replace

| Component | Engine | Reason |
|-----------|--------|--------|
| Next button | Gesture Engine | RN `TouchableOpacity` requires `adb shell input tap` |
| DOB picker | Picker Engine | RN `WheelPicker` requires `adb shell input swipe` |
| Consent scroll | Gesture Engine | RN `ScrollView` requires `adb shell input swipe` |
| OTP / PIN (future) | OTP Engine (TBD) | May require per-character input |
