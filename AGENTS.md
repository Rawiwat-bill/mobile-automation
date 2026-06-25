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
- For flaky mobile UI issues, collect evidence before code changes: screenshot, Appium XML, and logs when useful.
- When manual success differs from automation failure, compare manual success vs automation failure before changing code.
- Run one experiment at a time and revert any failed or unproven experiment before the next one.
- Create an investigation report under `reports/investigation/<screen_name>/` for every investigation.
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
- Prefer full Appium XML and screenshot evidence over copied attributes alone when validating a locator.
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
- Mask citizen IDs as `[MASKED_CITIZEN_ID]` and phone numbers as `[MASKED_PHONE]`.

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

## Evidence-First Mobile Workflow
- Capture screenshot and Appium XML before changing Robot code for flaky mobile UI issues.
- Capture after-state evidence for the failing interaction and compare it to the before-state.
- When manual flow succeeds, compare manual success against automation failure before proposing a fix.
- Use debug panel or logcat only when it helps explain the interaction gap.
- Keep experiments isolated and reversible.

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

## Project Milestones

### Milestone 1 — Shared Onboarding Architecture
- Landing, Consent, Profile extracted to common flow
- NTB and ETB test suites separated
- Common keyword: `Complete Common Onboarding`
- Architecture documented in `docs/Architecture.md`
- Backward compatibility preserved

### Milestone 2 — Identity Validation (Profile Next)
- Profile Next blocker diagnosed and resolved
- Root cause: React Native gesture handling incompatible with Appium touch events
- Fix: `adb shell input tap` via `Execute Adb Shell` with Appium `--relaxed-security`
- Citizens ID input converted to adb keycodes for proper RN events
- Documented in `knowledge/profile/next_button.md`
- Identity validation suite at `tests/android/common/identity_validation.robot`

### Milestone 3 — NTB OCR
- TBD

### Milestone 4 — Face Verification
- TBD

### Milestone 5 — PIN Setup
- TBD

### Milestone 6 — ETB Flow
- TBD
