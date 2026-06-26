# Debugging Playbook

## When to Use
- A test fails unexpectedly
- A flaky test passes sometimes but not consistently
- Manual flow succeeds but automation flow fails
- A new error or exception appears in test output

## Inputs Required
- Robot output log (output.xml or log.html)
- Screenshot of failure state
- Appium XML page source at failure point
- Description of expected vs actual behavior

## Evidence Required
- Robot log showing the first failing keyword
- Screenshot at failure point
- Appium XML at failure point
- If manual success exists: screenshots + XML of manual success

## Step-by-Step Workflow
1. Read the Robot output log. Identify the first failing keyword.
2. Examine the error message and stack trace.
3. Check the failure screenshot. Does the screen look correct?
4. Check the Appium XML. Is the target element present? Is it visible? Enabled?
5. Compare with a known-good run if available.
6. If manual success exists, perform the manual flow and capture screenshots + XML.
7. Compare manual vs automation:
   - Is the element in a different state?
   - Is a different element visible?
   - Is the timing different (loading, animation)?
8. Classify the failure:
   - Automation defect (keyword, locator, logic)
   - App defect (crash, UI bug, missing element)
   - Environment issue (device, Appium, network, VPN)
   - Test data issue (invalid, expired, missing data)
   - Backend issue (API failure, service unavailable)
   - Device issue (OS, screen size, permissions)
9. If root cause is found, document it.
10. If root cause is not found after systematic investigation, escalate.

## Validation
- Verify failure is reproducible with same inputs.
- If fix is proposed: confirm by running the test with the fix.
- If not reproducible after 3 attempts: classify as environment/flaky, document.

## Output Format
Title:
Environment:
Device:
Precondition:
Steps:
Expected Result:
Actual Result:
Evidence:
Failure Classification:
Root Cause:
Recommended Next Action:

## Stop Conditions
- **Root cause not found** — stop, do not suggest fixes without understanding.
- **Evidence incomplete** — stop, collect screenshots, XML, logs first.
- **3+ fix attempts failed** — stop, architectural review needed.
- **App behavior contradicts automation assumptions** — stop, compare manual vs automated flow.
- **Requires app change** — stop, route to developer team through bug report.
