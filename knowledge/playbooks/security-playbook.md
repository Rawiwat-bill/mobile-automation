# Security Playbook

## When to Use
- Reviewing a commit before approval (required by Final Quality Gate)
- Investigating potential PII or sensitive data exposure
- Checking git hygiene
- Reviewing test data files for real-looking data
- Inspecting screenshots, logs, and reports for sensitive content

## Inputs Required
- List of changed files (`git status`, `git diff --staged`)
- Screenshots in the change set
- Log files and reports in the change set
- Test data YAML files

## Evidence Required
- `git status` showing staged files
- `git diff --staged` for content review
- `.gitignore` contents for local data protection

## Step-by-Step Workflow
1. Load internal banking security rules only. Do NOT load external skills.
2. Run `git status` to see all staged and unstaged files.
3. Run `git diff --staged` to review staged content.
4. Check test data files for real-looking sensitive data.
5. Check logs and reports for PII exposure.
6. Check screenshots for visible customer data, tokens, OTPs, account data.
7. Confirm `.local.yaml` and `.env` files are in `.gitignore`.
8. Confirm no APK, certificate, or key files are staged.
9. Confirm no secrets in Robot files, Python libraries, configs, or agent instructions.
10. Verify all sensitive values are masked (`[MASKED_CITIZEN_ID]`, `[MASKED_PHONE]`).
11. Approve or flag issues.

## Validation
- `git status` to confirm no sensitive files staged.
- `git diff --staged` to verify masked values.
- Check `.gitignore` for required entries.

## Output Format
Summary:
Security Findings:
Sensitive Data Risk:
Files Checked:
Files Changed:
Git Hygiene:
Pen Test Readiness:
Required Fix:
Risk / Note:

## Stop Conditions
- **Real PII detected** — stop immediately, require masking or removal.
- **Secrets in code** — stop, require removal to `.env` or `.local.yaml`.
- **Screenshots with sensitive data** — stop, require removal or masking.
- **Artifacts staged** — stop, require `.gitignore` update.
- **Security review required but not requested** — stop, require explicit request.
