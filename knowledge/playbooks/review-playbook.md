# Review Playbook

## When to Use
- Before any commit (required by Final Quality Gate)
- Reviewing a PR or code change
- Checking locator quality
- Validating security and performance of a change
- Verifying git hygiene

## Inputs Required
- List of changed files (`git status`, `git diff --staged`)
- Purpose of the change (from task description)
- Existing test output if available

## Evidence Required
- `git diff` or `git diff --staged` output
- For flaky fixes: screenshots + XML evidence + manual comparison
- Dryrun output if Robot code changed
- Security review output if data/log/config/git involved

## Step-by-Step Workflow
1. Determine review target (local changes or remote PR).
2. For local changes: run `git status`, `git diff --staged`, `git diff`.
3. Identify which files are changed and categorize them.
4. For each changed file, check:
   - Does the change match the stated purpose?
   - Are the changes minimal and scoped?
5. Apply the Must Reject checklist:
   - Weak locator when stable locator exists?
   - `Sleep` used?
   - Hardcoded sensitive data?
   - Duplicated keywords?
   - Locator inside a test case?
   - Test data inside test logic?
   - Excessive screenshots?
   - Fixed long waits?
   - Broad refactors unrelated to change?
   - Generated artifacts staged?
   - Changes without evidence for flaky fixes?
6. Verify validation was run (dryrun, benchmark, or test execution).
7. If Robot/Appium code changed: cross-check against robot-expert and appium-skill rules.
8. If change involves data/logs/config/git: require security review.
9. Provide structured feedback: Critical, Improvements, Nitpicks.
10. Approve or request changes.

## Validation
- Confirm validation command was run and passed.
- Confirm security review was completed for changes involving data, logs, config, or git.
- If approving: confirm all Must Reject items have been checked.

## Output Format
Summary:
Issues Found:
Required Fix:
Optional Improvement:
Files Checked:
Files Changed:
Validation Command:
Validation Result:
Security Review:
Risk / Note:

## Stop Conditions
- **Evidence missing for flaky fix** — do not approve without screenshots/XML.
- **Manual success not compared** — stop, require comparison.
- **Security review not done** — stop, require security review before approval.
- **Validation not run** — stop, require validation.
- **Experiment not reverted** — stop, require reversion of disproven experiments.
