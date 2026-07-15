# Scroll Pattern

## Problem
React Native scroll views do not reliably respond to Appium swipe gestures (W3C Actions, TouchAction, mobile: scroll). The scroll content does not advance, leaving buttons and content inaccessible.

## Recommended Pattern
Use `adb shell input swipe` for scrolling React Native scroll containers.

```robot
Execute Adb Shell    input    swipe    ${start_x}    ${start_y}    ${end_x}    ${end_y}    ${duration_ms}
```

Where coordinates are calculated from element bounds or screen dimensions, not hardcoded.

## Anti-Pattern
- Appium `swipe` or `Scroll` gestures on React Native scroll views.
- Hardcoded scroll coordinates that assume a specific screen resolution.
- Fixed scroll loops without checking if the target element is visible.
- `Sleep` between scroll operations.

## Example
```robot
Scroll Down Consent Terms
    ${start_x}=    Evaluate    int(${SCREEN_WIDTH} / 2)
    ${start_y}=    Evaluate    int(${SCREEN_HEIGHT} * 0.7)
    ${end_y}=    Evaluate    int(${SCREEN_HEIGHT} * 0.3)
    Execute Adb Shell    input    swipe    ${start_x}    ${start_y}    ${start_x}    ${end_y}    300
```

## When Not to Use
- When the app uses a native Android scroll view that responds to Appium swipe gestures.
- When `mobile: scrollGesture` (Appium 2.0+) is verified to work on the target component.

## State-Based Bottom Detection (Consent Screen)

For consent/terms screens with a scrollable WebView, detect the bottom via a virtualized native `TextView` marker rather than blind swipe count.

**Marker:** "I have read and understood" text appears as `android.widget.TextView` only when scrolled to the bottom (virtualized — absent until rendered into view).

**Production implementation:** `Scroll Down Consent Terms With Big Fling` in `scroll_keywords.resource`.
**Observed result:** marker appears at swipe 4 (20/20 runs, σ=0.0, max 10 swipes).
**Stall fallback:** hash-based page-source comparison (2 consecutive unchanged → `CONSENT_SCROLL_STALLED`).
**Important:** The Accept button's `enabled` attribute is `true` at all scroll positions — it is NOT a valid bottom signal.
