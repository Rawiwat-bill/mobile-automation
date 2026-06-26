# Security Pattern

## Problem
Mobile banking automation code can accidentally expose customer data through logs, screenshots, reports, or committed test data. This creates pen-test audit failures and compliance risk.

## Recommended Pattern
- Never commit real PII to any file in the repository.
- Mask sensitive values in logs: `[MASKED_CITIZEN_ID]`, `[MASKED_PHONE]`.
- Keep sensitive data in gitignored local files (`*.local.yaml`, `.env`).
- Committed test data must be clearly non-real example data.
- Check staged files before every commit (`git status`, `git diff --staged`).
- Screenshots must not contain customer data, OTPs, tokens, or account numbers.
- Security review is required before every commit.

## Anti-Pattern
- Committing real-looking citizen IDs or phone numbers in example YAML files.
- Logging raw `adb shell` output that contains device data.
- Committing screenshots without checking for visible customer data.
- Storing passwords or tokens in Robot files or agent instructions.
- Skipping security review for "small" changes.

## Example
```robot
# Good: masked logging
Log    Citizen ID entered: [MASKED_CITIZEN_ID]

# Bad: exposed logging
Log    Citizen ID entered: ${citizen_id}
```

## When Not to Use
- When explicitly asked to store test data for a specific environment (use gitignored local file).
- When documenting a bug with evidence (mask before including in report).
