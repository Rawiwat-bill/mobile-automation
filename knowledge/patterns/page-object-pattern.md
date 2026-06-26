# Page Object Pattern

## Problem
Test code becomes brittle and unreadable when UI interaction details (locators, gestures, waits) are mixed with business logic in test cases. Changes to the UI require changes in multiple tests.

## Recommended Pattern
- Each screen gets a resource file under `resources/pages/<feature>/<screen>_page.resource`.
- The page resource owns all screen-level keywords and interactions.
- Test files call page keywords, never locators or Appium keywords directly.
- Page keywords expose business-level actions (`Input Citizen ID`, `Tap Profile Next`), not element-level mechanics.

## Anti-Pattern
- Locators defined inside test cases.
- Multiple test cases duplicating the same tap/fill sequence.
- Test cases calling Appium keywords like `Click Element` directly.

## Example
```robot
# resources/pages/onboarding/profile_screen_page.resource
Input Citizen ID
    [Arguments]    ${citizen_id}
    Tap Profile Element Center    ${PROFILE_CITIZEN_ID_CONTAINER}
    Enter Digits By Keycodes    ${citizen_id}
    Tap Profile Blank Area    ${PROFILE_BLUR_AFTER_CITIZEN_Y}
    Wait Until Profile Fields Are Blurred

# tests/android/ntb/ntb_flow.robot
Complete Common Onboarding    ${data['profile']['citizen_id']}    ${data['profile']['date_of_birth']}    ${data['profile']['mobile_number']}
```

## When Not to Use
- For one-off debug or investigation scripts where readability is not a concern.
- When the interaction is truly unique and never reused (rare in mobile flows).
