# Locator Knowledge

## Android Locator Priority

1. Screen-specific `resource-id` (e.g., `com.bank.app:id/profile_citizen_id_input`)
2. `accessibility_id` / `content-desc` (when resource-id is not screen-specific)
3. Stable text (only when language-independent, e.g., numeric values)
4. Relative XPath (last resort, requires evidence)

## Evidence Requirements

Every new locator requires:
- Appium XML page source showing the element
- Screenshot confirming visual state
- Confirmation of uniqueness on the target screen

## Rejected Locator Patterns

- Absolute XPath (`/hierarchy/android.widget.FrameLayout/...`)
- Index-based XPath (`//android.widget.EditText[1]`)
- Generic resource-ids (`text`, `base-btn`, `base-btn-container`) with no screen context
- Coordinate-based locators
- Text-dependent locators when the app supports multiple languages
- Dynamic locators without a stable fallback (e.g., auto-generated resource-ids)

## Known Locator Findings

- `PROFILE_NEXT_BUTTON_CONTAINER` has `resource-id="base-btn"` — not screen-specific. Used via adb tap with bounds verification.
- `PROFILE_CITIZEN_ID_CONTAINER` — container element for focus management before keycodes.
- Date picker uses Android native DatePicker — accessed via direct field manipulation.

## Vendor Prefixes

Developer-provided test IDs or accessibility IDs are preferred over Appium-inferred locators. Request developer support when no stable screen-specific locator exists.

## Internal Project Truth

This knowledge overrides external appium-skill locator suggestions when the specific screen layout or app framework requires it. Locator evidence from the actual app always takes precedence over generic guidance.
