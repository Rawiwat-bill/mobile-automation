# ADB Knowledge

## Prerequisites

Appium must start with `--relaxed-security` to enable `Execute Adb Shell`:
```bash
appium --relaxed-security
```

## Verified Patterns

### Tap
```robot
Execute Adb Shell    input    tap    ${x}    ${y}
```
Works for React Native buttons where Appium tap fails. Requires element bounds to calculate coordinates.

### Swipe
```robot
Execute Adb Shell    input    swipe    ${x1}    ${y1}    ${x2}    ${y2}    ${duration_ms}
```
Used for consent terms scrolling. Duration of 200-400ms is typically sufficient.

### Keycodes per digit
```robot
Execute Adb Shell    input    keyevent    ${KEYCODE_1}
```
Used for Citizen ID and Mobile Number input. Each digit is sent as a separate keyevent. This triggers proper RN onChange events unlike Appium `sendKeys()`.

### Text input
```robot
Execute Adb Shell    input    text    ${value}
```
Available but may not trigger RN onChange events reliably. Prefer keycodes per digit for numeric fields.

## Keycode Reference

| Digit/Action | Keycode |
|-------------|---------|
| 0 | 7 |
| 1 | 8 |
| 2 | 9 |
| 3 | 10 |
| 4 | 11 |
| 5 | 12 |
| 6 | 13 |
| 7 | 14 |
| 8 | 15 |
| 9 | 16 |
| Enter | 66 |
| Backspace | 67 |
| Delete | 112 |

## Constraints

- `adb shell` commands execute at the OS level, not within the app context
- Coordinates must be calculated based on element bounds, not hardcoded
- Screen resolution differences affect coordinate-based operations
- `input text` does not support special characters reliably via shell

## Security Note

`adb shell` commands can read device state (logs, installed packages, screen content). Never log the output of `adb shell` commands that may contain sensitive data. Mask or discard PII from adb output before logging.

## Internal Project Truth

ADB-level interaction is a documented strategy in this project, not a workaround to be eliminated. React Native's event handling model makes adb shell the most reliable interaction layer for certain components. This is accepted architecture.
