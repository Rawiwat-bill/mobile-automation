# Wait Pattern

## Problem
Fixed waits (`Sleep`) introduce unnecessary delays in test execution and fail when timing varies between devices, network conditions, or app states. Tests become slow and flaky.

## Recommended Pattern
Always use explicit, condition-based waits:

```robot
# Wait for an element to be visible before interacting
Wait Until Element Is Visible    ${LOCATOR}    timeout=30s

# Wait for a condition to be true
Wait Until Keyword Succeeds    5x    2s    Element Should Be Visible    ${LOCATOR}

# Wait for screen transition
Wait Until Page Does Not Contain Element    ${CURRENT_SCREEN_LOCATOR}
Wait Until Page Contains Element    ${NEXT_SCREEN_LOCATOR}
```

Use bounded loops with clear exit conditions for scrolling or repeated actions.

## Anti-Pattern
- `Sleep    5s` — fixed delay that is either too short (flaky) or too long (slow).
- `Sleep    1s` after every action — accumulates unnecessary delay across a test.
- `Wait Until Element Is Visible` with no timeout argument.
- Fixed wait loops without checking success condition.

## Example
```robot
# Good: explicit wait
Wait Until Element Is Visible    ${PROFILE_CITIZEN_ID_INPUT}    15s

# Bad: fixed wait
Sleep    5s
Click Element    ${PROFILE_CITIZEN_ID_INPUT}
```

## When Not to Use
- When the action inherently requires a fixed delay (e.g., animation duration, network round trip with no visible indicator). Document the reason if `Sleep` is unavoidable.
