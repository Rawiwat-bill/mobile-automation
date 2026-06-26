# Locator Playbook

## When to Use
- Adding a new locator for an element on a screen
- Replacing an unstable or generic locator
- Investigating a locator-related test failure
- Reviewing locator quality

## Inputs Required
- Screen name (e.g., `profile`, `consent`, `landing`)
- Element description (e.g., "Citizen ID input field", "Next button")
- Platform (Android / iOS)
- Appium XML page source of the target screen
- Screenshot of the target screen

## Evidence Required
- Appium XML showing the target element with attributes
- Screenshot confirming visual state and context
- Confirmation that the locator is unique on the screen

## Step-by-Step Workflow
1. Identify the screen and element from the task description.
2. Locate the existing locator resource file at `resources/locators/<platform>/<screen>.resource`.
3. Inspect existing locators in the file for reusable patterns.
4. Capture Appium XML page source from a running session.
5. Search the XML for the target element using attribute values.
6. Apply Android locator priority:
   - Screen-specific `resource-id` → best
   - `accessibility_id` / `content-desc` → second
   - Stable language-independent text → third
   - Relative XPath → last resort
7. Verify uniqueness: confirm no other element on the screen matches the same locator.
8. Name the locator: `${SCREEN}_${ELEMENT}` (e.g., `${PROFILE_CITIZEN_ID_INPUT}`).
9. Add the locator to the appropriate resource file.
10. Add the resource import to the page keyword file if not already present.
11. Update or create the corresponding page keyword that uses the locator.

## Validation
- Run `python3 -m robot --dryrun <test_path>` to verify syntax.
- Run a focused test to confirm the locator resolves correctly.
- If locator is for a new screen, run the full flow test.

## Output Format
Screen:
Element:
Recommended Locator:
Alternative Locator:
Reason:
Risk:
Confidence:
Dev Support Needed:

## Stop Conditions
- **No evidence** — stop if locator is written without Appium XML or screenshot.
- **No stable locator found** — stop and request developer support for testID/accessibility id.
- **Locator conflicts with existing** — stop and verify intended element.
- **Unmodifiable file** — stop if locator change requires modifying a test file (not allowed).
