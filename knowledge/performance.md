# Performance Knowledge

## Known Bottlenecks

### 1. Profile Next Button
- **Issue:** Appium tap gestures fail on React Native buttons; adb shell input tap required
- **Impact:** Adds ~500ms for coordinate calculation and adb execution
- **Status:** Accepted — no faster stable alternative

### 2. Citizen ID Input
- **Issue:** Appium `Input Text` does not reliably trigger RN onChange events
- **Workaround:** `Press Keycode` per digit via adb (≈13 keycodes for 13-digit ID)
- **Benchmarked strategies:** Input Text, Input Value, Press Keycodes, Adb Shell, Execute Script
- **Status:** Needs benchmark results to rank fastest stable option

### 3. DOB Input
- **Issue:** React Native TextInput for DOB does not respond to Appium text entry
- **Workaround:** Date Picker manipulation or direct field value setting
- **Benchmarked strategies:** Picker Calculated, Input Text, Adb Shell, Input Value
- **Status:** Needs benchmark results to rank fastest stable option

### 4. Mobile Number Input
- **Issue:** Same RN onChange issue as Citizen ID
- **Workaround:** Keycodes per digit
- **Benchmarked strategies:** Input Text, Input Value, Press Keycodes, Adb Shell, Execute Script
- **Status:** Needs benchmark results to rank fastest stable option

### 5. Consent Screen Scroll
- **Issue:** Full consent terms require scrolling; Appium swipe gestures unreliable on RN
- **Workaround:** adb shell swipe for scroll
- **Impact:** ~1-2s per scroll operation

## Optimization Rules

- No optimization without benchmark evidence
- Fixed long waits are replaced with event-based waits
- Excessive screenshots and repeated page source calls are avoided
- `Sleep` is never used
- Condition-based scrolling replaces fixed scroll loops

## Performance Baseline

- Explicit waits with reasonable timeouts (10-30s depending on network)
- Bounded loops with clear exit conditions
- Condition-based scrolling when possible
- Test execution suitable for CI/CD pipelines

## Internal Project Truth

This knowledge captures real performance findings from the project. External performance suggestions from skills are secondary. Benchmark results from the project's own benchmark suite are the authoritative data source.
