# Locator Pattern

## Problem
Locators that are ambiguous, generic, or coupled to visual layout break when the app UI changes. Tests fail due to element not found, multiple matches, or stale references.

## Recommended Pattern
- Store locators in platform-specific resource files under `resources/locators/<platform>/<screen>.resource`.
- Use screen-specific `resource-id` where available.
- Use `accessibility_id` / `content-desc` as second priority.
- Use stable text only when language-independent.
- Use relative XPath only as a last resort.
- Naming convention: `${SCREEN}_${ELEMENT}` (e.g., `${PROFILE_CITIZEN_ID_INPUT}`).
- Document the source of evidence for each locator.

## Anti-Pattern
- Absolute XPath: `/hierarchy/android.widget.FrameLayout/...`
- Index XPath: `//android.widget.EditText[1]`
- Generic ids: `text`, `base-btn`, `base-btn-container`
- Hardcoded coordinates: `x=540, y=920`
- Language-dependent text: `"Citizen ID"` in a multilingual app
- Dynamic locators without fallback: auto-generated resource-ids

## Example
```robot
# resources/locators/android/onboarding/profile_screen_locators.resource
${PROFILE_CITIZEN_ID_INPUT}    accessibility_id=citizenIdInput
${PROFILE_CITIZEN_ID_CONTAINER}    resource-id=com.bank.app:id/citizenIdContainer
${PROFILE_NEXT_BUTTON_CONTAINER}    resource-id=base-btn
```

## When Not to Use
- When the element is a simple, stable Android framework widget with a known class (rare).
- For one-off investigation requiring visibility into dynamic elements.
