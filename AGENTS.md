# Mobile Automation Agent Instructions

## Enterprise Project Standard v2.0
This project follows Enterprise Mobile Banking Automation Standard v2.0.

Project context:
- Mobile Banking automation.
- Robot Framework with AppiumLibrary.
- Android first, with architecture that can support iOS where needed.
- Page Object style.
- Locators separated by platform and screen.
- Test data separated from test logic.

Quality standard:
- Code must be readable, minimal, maintainable, and reviewable.
- Changes must preserve framework architecture and existing useful patterns.
- No agent may rewrite the whole project without explicit approval.
- No agent may invent locators, test data, app package names, activities, credentials, OTPs, or user data.
- All changes must be scoped to the task and avoid unrelated refactors.

## Required Workflow
- Inspect existing files before editing.
- Identify whether the issue is locator, Robot code, Appium/device, security/data, review, or defect-report related.
- Reuse existing keywords before creating new ones.
- Reuse existing locators before creating new ones.
- Keep locators outside test files.
- Keep page keywords separated by screen.
- Prefer explicit waits and condition-based logic.
- Avoid `Sleep`.
- Make the smallest safe change.
- Run validation when possible.
- Do not run real device tests unless requested or clearly required.
- Perform security review before commit or handoff.

## Security Baseline
- Never commit real PII, citizen IDs, mobile numbers, account numbers, passwords, OTPs, tokens, certificates, keys, APKs, or production secrets.
- Local sensitive data must live in `.local.yaml`, `.env`, or another gitignored local file.
- Only example or masked test data may be committed.
- Mask sensitive values in logs, reports, screenshots, comments, and final responses.
- Check git hygiene before suggesting commit.
- Treat mobile banking automation as pen-test-auditable: every secret, log, fixture, and artifact must be defensible.

## Performance Baseline
- Avoid fixed long waits when event-based waits are possible.
- Avoid excessive screenshots, repeated page source dumps, and unnecessary Appium calls.
- Prefer waiting for stable screen state over retrying blind actions.
- Use bounded loops with clear exit conditions.
- Use condition-based scrolling when possible.
- Keep test execution suitable for CI/CD pipelines.

## Locator Baseline
- Android locator priority:
  1. Screen-specific `resource-id`.
  2. `accessibility_id` / `content-desc`.
  3. Stable text only when language-independent.
  4. Relative XPath only as a last resort.
- Reject coordinates as locators.
- Reject index XPath and absolute XPath.
- Reject generic ids such as `text`, `base-btn`, or `base-btn-container` when a better screen-specific locator exists.
- Reject language-dependent text when the app supports multiple languages.
- Reject dynamic locators without a fallback.
- If no stable locator exists, request developer support for `testID`, accessibility id, or stable screen-specific resource id.

## Test Data Baseline
- Do not invent test data.
- Do not hardcode test data inside test cases or page keywords.
- Do not store real banking data in Git.
- Keep local data in gitignored local files.
- Keep committed data as examples only and clearly non-real.
- Mask sensitive values when logging or reporting.

## Git Baseline
- Do not revert user changes unless explicitly requested.
- Do not modify unrelated files.
- Do not commit generated reports, screenshots, APKs, logs, or local data unless explicitly intended and safe.
- Before commit or handoff, verify changed files are expected.
- Security review is required before commit.

## Validation Baseline
- For Robot syntax and keyword validation, prefer:
  `python3 -m robot --dryrun tests/android/onboarding/ntb_onboarding.robot`
- For real mobile execution, run only when requested:
  `python3 -m robot -d reports tests/android/onboarding/ntb_onboarding.robot`
- When only agent instruction files change, do not run Robot tests.
- For agent-only updates, validate with:
  `ls -la .agents`
  `cat AGENTS.md`

## Final Response Format
Summary:
Agents Used:
Files Checked:
Files Changed:
Validation Command:
Validation Result:
Security Review:
Performance Review:
Risk / Note:
Next Recommended Action:
