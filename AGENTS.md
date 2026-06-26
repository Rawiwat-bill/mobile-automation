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

## Enterprise Agent Runtime v1

### Overview
Enterprise Agent Runtime v1 is the decision system that governs how agents select, route, and execute work. It enforces skill integration, capability boundaries, quality gates, and stop conditions.

### Agent Capability Matrix

| Agent | Can Read Skills | Can Modify Code | Can Modify Locators | Can Modify Tests | Can Run Dryrun | Can Run Real Test | Can Approve Change | Needs Security Review |
|-------|:---:|:---:|:---:|:---:|:---:|:---:|:---:|:---:|
| qa-orchestrator | Yes | No* | No | No | No | No | No | N/A |
| robotframework-agent | Yes | Yes | No | Yes | Yes | No | No | Yes |
| appium-agent | Yes | Yes | No | No | No | No | No | Yes |
| locator-agent | Yes | No | Yes | No | No | No | No | Yes |
| review-agent | Yes | No | No | No | No | No | Yes | N/A |
| security-review-agent | No | No | No | No | No | No | Yes | N/A |
| bug-agent | Yes | No | No | No | No | No | No | Yes |
| performance-agent | Yes | No | No | No | No | No | No | Yes |

*qa-orchestrator may modify code only when explicitly required and authorized.

### Skill Routing Table

| Request Type | Route To | Required Skill |
|-------------|----------|----------------|
| Robot Framework code/questions | robotframework-agent | robot-expert |
| Appium / Mobile / Device / Gesture / Capabilities | appium-agent | appium-skill |
| Locator strategy | locator-agent | appium-skill |
| Bug / Failure / Flaky / Unexpected behavior | qa-orchestrator → systematic-debugging → specialist | systematic-debugging |
| Code Review / PR Review | review-agent | code-reviewer |
| Complex multi-agent workflow | qa-orchestrator | orchestration |
| Security / PII / Logs / Test Data | security-review-agent | internal banking rules only |
| Performance investigation | performance-agent | systematic-debugging, appium-skill, robot-expert |

### Execution Contract

Every agent MUST:
1. Read the relevant skill before starting domain work.
2. Inspect existing files before any modification.
3. Reuse existing keywords and locators before creating new ones.
4. Make the smallest safe change.
5. Validate with dryrun when Robot code changes.
6. Never invent locators, test data, package names, activities, credentials, OTPs, or user data.
7. Never modify files outside their Allowed Files scope.

### Validation Contract

- Robot code changes: `python3 -m robot --dryrun <test_path>`
- Agent-only changes: `find .agents -type f | sort` + `cat AGENTS.md`
- Locator changes: dryrun + evidence review
- Security-sensitive changes: security-review-agent approval required
- All changes: review-agent approval required before commit

### Stop Conditions

Stop and ask user when ANY of the following is true:

1. **Real PII may be exposed** — citizen ID, phone number, account, password, OTP, token, certificate, APK
2. **Test data is missing** — no example or local data file found for the required field
3. **Locator is not confirmed** — locator written without Appium XML or screenshot evidence
4. **More than 3 fixes failed** — architectural review needed; do not attempt fix #4
5. **App behavior contradicts assumptions** — manual flow succeeds but automation keeps failing without clear cause
6. **Required file is missing** — file expected by the task does not exist and cannot be inferred
7. **Running real test needs user approval** — real device or emulator test not explicitly requested
8. **Change requires modifying unrelated files** — expanding scope beyond the original task

### Escalation Rules

| Condition | Escalate To |
|-----------|-------------|
| Stop condition triggered | User (ask for decision) |
| Architecture question | User |
| Missing capability/knowledge | User |
| Requires app change (not automation) | User + developer team through bug report |
| Multi-team coordination needed | User |
| Security concern found | security-review-agent → User |

### Final Quality Gate

1. review-agent reviews every change before commit.
2. security-review-agent reviews every change involving data, logs, config, or git.
3. No fix is allowed for failures until systematic-debugging root cause investigation (Phase 1) is complete.
4. External skills are reference material — internal project rules override all suggestions.
5. Stop conditions are checked at every gate. If any is true, execution stops and user is asked.

## Knowledge Layer Policy

### Overview
Enterprise Knowledge Layer v1 provides a project-level knowledge base at `knowledge/`, engineering principles at `docs/principles/`, and architectural decisions at `docs/decisions/`. This is the project's primary truth source.

### Knowledge Hierarchy

```
1. knowledge/playbooks/*.md     — Executable workflows (highest priority)
2. knowledge/patterns/*.md      — Reusable structural patterns
3. knowledge/*.md               — Project knowledge
4. docs/principles/*.md         — Engineering principles
5. docs/decisions/ADR-*.md     — Architectural decisions
6. .agents/skills/*/SKILL.md   — External skills (reference only)
```

Internal project knowledge always overrides external skill suggestions. The knowledge layer is authoritative.

### Playbook and Pattern Policy

- Agents MUST consult the relevant playbook when the task matches a playbook's "When to use" criteria.
- Agents MUST consult the relevant pattern when the task structure matches a pattern's described problem.
- Playbooks take precedence over knowledge files when both address the same topic.
- Patterns take precedence over ad-hoc solutions when the problem matches a known pattern.
- If no playbook or pattern applies, follow general knowledge and then external skills.
- Playbooks and patterns are passive reference material — they do not execute actions or replace agent judgment.

### Agent Knowledge Rules

1. **Check knowledge first.** Before loading an external skill, check `knowledge/` for relevant project knowledge.
2. **Knowledge overrides skills.** If `knowledge/<topic>.md` exists and conflicts with an external skill, the knowledge file wins.
3. **Update with evidence only.** Agents may update knowledge files only when the new information is confirmed by evidence (screenshots, XML, logs, benchmark results).
4. **Do not invent knowledge.** Do not add speculative or unverified information to knowledge files. Every claim must be traceable to evidence.
5. **Security knowledge is absolute.** `knowledge/banking-security.md` overrides ALL external skill security recommendations.
6. **ADR updates require review.** Changes to `docs/decisions/ADR-*.md` require review-agent approval.

### Knowledge File Scope

| File | Owner Agent | Purpose |
|------|-------------|---------|
| `knowledge/appium.md` | appium-agent | Appium patterns, RN compatibility, known limitations |
| `knowledge/robotframework.md` | robotframework-agent | RF structure, naming, conventions, anti-patterns |
| `knowledge/locator.md` | locator-agent | Locator priority, evidence requirements, rejected patterns |
| `knowledge/performance.md` | performance-agent | Known bottlenecks, benchmark results, optimization rules |
| `knowledge/ocr.md` | robotframework-agent | OCR step knowledge (Milestone 3) |
| `knowledge/facescan.md` | robotframework-agent | Face verification knowledge (Milestone 4) |
| `knowledge/api.md` | robotframework-agent | API testing knowledge |
| `knowledge/adb.md` | appium-agent | ADB patterns, keycode reference, security notes |
| `knowledge/benchmark.md` | performance-agent | Benchmark framework, strategies, classification |
| `knowledge/banking-security.md` | security-review-agent | Non-negotiable security rules |
| `knowledge/test-strategy.md` | qa-orchestrator | Test organization, data model, environment |
| `knowledge/playbooks/*.md` | All agents | Executable workflows for common tasks |
| `knowledge/patterns/*.md` | All agents | Reusable structural patterns |

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

## Playbook and Pattern Consultation
- Before work: check if a playbook or pattern matches the task.
- During work: follow the playbook workflow if applicable; apply the pattern if the problem matches.
- After work: note which playbook/pattern was used in the final response.

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
Playbook/Pattern Used:
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
