# ADR-002: Use ADB Swipe for Consent Screen Scroll

## Status
Accepted

## Context
The Consent screen requires scrolling through the full terms text before the Accept button becomes enabled. Appium swipe gestures (W3C Actions, TouchAction, mobile: scroll) did not reliably trigger the React Native scroll view's onScroll handler, leaving the Accept button disabled.

## Decision
Use `adb shell input swipe` for scrolling the Consent screen terms.

Implementation:
```robot
Execute Adb Shell    input    swipe    ${start_x}    ${start_y}    ${end_x}    ${end_y}    ${duration_ms}
```

## Consequences
**Positive:**
- ADB swipe triggers RN scroll events reliably
- Works across device resolutions when coordinates are calculated dynamically
- No dependency on Appium gesture API

**Negative:**
- Requires Appium `--relaxed-security` for adb access
- Coordinate calculation required (element bounds + device resolution)
- Slower than an ideal native gesture (additional ~1-2s per scroll)

## Related
- `knowledge/adb.md` — ADB pattern reference
- `knowledge/appium.md` — React Native compatibility notes

## Compliance
- Coordinated-based scrolls must use element bounds, not hardcoded coordinates
- Review agent checks for coordinate hardcoding in scroll operations
