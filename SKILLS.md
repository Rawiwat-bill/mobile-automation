# Installed Skills Inventory — Enterprise Agent Runtime v1

## Skill List

| # | Skill | Location | Owner Agent | Purpose |
|---|-------|----------|-------------|---------|
| 1 | appium-skill | `.agents/skills/appium-skill/` | appium-agent | Appium automation best practices, locator strategy, gestures, capabilities, cloud testing |
| 2 | robot-expert | `.agents/skills/robot-expert/` | robotframework-agent | Robot Framework conventions, file structure, keyword patterns, test organization |
| 3 | code-reviewer | `.agents/skills/code-reviewer/` | review-agent | Code review workflow, correctness, maintainability, security, readability checks |
| 4 | orchestration | `.agents/skills/orchestration/` | qa-orchestrator | Multi-agent coordination, task dispatch, messaging, DAG workflows |
| 5 | systematic-debugging | `.agents/skills/systematic-debugging/` | bug-agent, performance-agent | Root cause investigation, evidence-first debugging, hypothesis testing |

## Skill Purpose

### appium-skill
- Appium server setup and capabilities (UiAutomator2, XCUITest)
- Locator strategy priority and selection
- Gesture implementation (W3C Actions API)
- Cloud testing (TestMu, LambdaTest)
- Device interaction patterns

### robot-expert
- Robot Framework file structure and organization
- Keyword naming conventions and patterns
- Variable usage patterns
- Tags system
- Database and messaging test patterns

### code-reviewer
- PR review workflow (remote and local)
- Correctness, maintainability, readability, efficiency, security, edge cases, testability
- Structured feedback (Critical, Improvements, Nitpicks)

### orchestration
- Multi-agent task dispatch and coordination
- DAG-based task dependencies
- Worker completion tracking and escalation
- Inter-agent messaging

### systematic-debugging
- Root cause investigation (Phase 1-4)
- Evidence gathering before fixes
- Hypothesis testing
- Condition-based waiting patterns

## When To Use Each Skill

| Skill | Use When | Do Not Use When |
|-------|----------|-----------------|
| appium-skill | Diagnosing Appium sessions, selecting locators, evaluating gestures, configuring caps | App business logic, test data, production code, security review |
| robot-expert | Writing/refactoring keywords, organizing test files, applying RF best practices | Mobile device behavior, Appium gestures, security review |
| code-reviewer | Reviewing PRs, evaluating code quality before commit | Investigating flaky tests, debugging failures, feature design |
| orchestration | Coordinating multi-agent work with task dependencies | Single-agent tasks, simple sequential operations |
| systematic-debugging | Any bug, test failure, flaky test, unexpected behavior — before proposing any fix | Fully diagnosed issues, pure feature development |

## Skill Priority Rules

1. **Internal project rules > external skill advice.** AGENTS.md and project conventions always win.
2. **Playbooks and patterns > skills.** If a playbook or pattern exists for the task, it takes priority over external skill recommendations.
3. **Security overrides everything.** No skill recommendation may bypass security baseline rules.
4. **No fix without root cause.** systematic-debugging must complete Phase 1 before any fix is proposed.
5. **Evidence over assumptions.** Skills provide general guidance; project evidence (screenshots, XML, logs) confirms applicability.
6. **Skill scope is bounded.** Each skill only applies to its owner agent's domain.

## Internal Rules Override Policy

- If a skill suggests a pattern that conflicts with AGENTS.md, locator baseline, security baseline, or project architecture, the project rule wins.
- If a skill suggests a generic approach that does not match the existing codebase patterns, adapt or discard the suggestion.
- If a skill suggests using `Sleep`, a fixed loop, or a weak locator when a better option exists, follow project baselines instead.

## Mobile Banking Security Override Policy

- No skill recommendation may cause:
  - Real PII, citizen ID, phone number, account number, password, OTP, or token exposure
  - Committing sensitive data to Git
  - Logging or screenshotting customer data
  - Using production secrets in test code
- Security-review-agent is the final gate. No skill output bypasses it.
- External skills are advisory; internal mobile banking security rules are mandatory and take precedence in all cases.
