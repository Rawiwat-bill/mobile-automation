# Performance Pattern

## Problem
Test execution time grows as more flows are automated. Slow interactions (waits, gestures, screen transitions) compound across test suites. Without measurement, optimization is guesswork.

## Recommended Pattern
- Profile before optimizing: measure execution time with benchmark or Robot log.
- Compare strategies using the benchmark framework before changing production code.
- Use explicit condition-based waits instead of fixed `Sleep` delays.
- Prefer accessibility id / resource-id over XPath (XPath is slower).
- Use condition-based scrolling instead of fixed scroll loops.
- Minimize screenshots and page source dumps in test flow.
- For React Native input fields: benchmark keycodes vs Input Text vs adb shell.
- Accept known RN-related slowdowns (adb shell) when no faster stable alternative exists.

## Anti-Pattern
- Optimizing without benchmark evidence.
- Using `Sleep` for synchronization when condition-based waits work.
- Taking screenshots at every step "just in case."
- Repeating page source calls without caching.
- Using XPath when resource-id is available.

## Example
```robot
# Before: fixed wait
Sleep    5s
Click Element    ${PROFILE_NEXT_BUTTON}

# After: condition-based wait
Wait Until Element Is Visible    ${PROFILE_NEXT_BUTTON}    10s
Click Element    ${PROFILE_NEXT_BUTTON}
```

## When Not to Use
- For one-off debug scripts where speed doesn't matter.
- When the optimization introduces instability (slower but reliable > fast but flaky).
