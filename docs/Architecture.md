# Enterprise AI QA Platform Architecture

## Platform Layers

```
Layer 0: Principles
  docs/principles/engineering-principles.md
  → Rules that govern all other layers

Layer 1: Knowledge Layer (passive reference)
  knowledge/*.md                   — Topic knowledge
  knowledge/playbooks/*.md         — Step-by-step workflows
  knowledge/patterns/*.md          — Reusable structural patterns
  docs/decisions/ADR-*.md         — Architectural decisions
  → Passive reference material, not an active agent

Layer 2: External Skills (reference only)
  .agents/skills/*/SKILL.md       — General best practices from ecosystem
  → Secondary reference, overridden by internal knowledge

Layer 3: Internal Agents
  .agents/*.md                    — Agent instruction files
  AGENTS.md                       — Master agent policy
  → Active execution agents with defined capability boundaries

Layer 4: QA Runtime / Orchestrator
  .agents/qa-orchestrator.md      — Task classification, routing, supervision
  → Decision system governing agent selection, execution, and gates

Layer 5: Automation Framework
  tests/                          — Test suites
  resources/                      — Keywords, page objects, locators
  libraries/                      — Python helpers
  testdata/                       — YAML test data
  → Executable mobile automation code

Layer 6: Reporting / Evidence / CI-CD
  reports/                        — Robot output, investigation evidence
  → Results, artifacts, pipeline integration
```

### Layer Relationships

```
Principles (0)
    ↓ governs
Knowledge Layer (1) ─── overrides ───→ External Skills (2)
    ↓ informs
Internal Agents (3)
    ↓ routed by
QA Runtime / Orchestrator (4)
    ↓ executes
Automation Framework (5)
    ↓ produces
Reporting / Evidence / CI-CD (6)
```

## Project Structure

```
.
├── .agents/                          # Agent instruction files (Layer 3)
│   ├── qa-orchestrator.md            # Runtime orchestrator (Layer 4)
│   ├── appium-agent.md
│   ├── robotframework-agent.md
│   ├── locator-agent.md
│   ├── review-agent.md
│   ├── security-review-agent.md
│   ├── bug-agent.md
│   ├── performance-agent.md
│   ├── evidence-agent.md
│   └── experiment-agent.md
├── AGENTS.md                         # Master agent policy (Layers 3-4)
├── SKILLS.md                         # Skill inventory (Layer 2)
├── PROJECT_MATURITY.md               # Platform maturity assessment
├── docs/                             # Architecture and decisions
│   ├── Architecture.md               # This file
│   ├── principles/                   # Layer 0
│   │   └── engineering-principles.md
│   └── decisions/                    # Layer 1
│       └── ADR-*.md
├── knowledge/                        # Layer 1
│   ├── *.md                          # Topic knowledge
│   ├── playbooks/                    # Step-by-step workflows
│   └── patterns/                     # Reusable patterns
├── apps/                             # Application binaries (APK)
├── configs/                          # Device and environment configs
├── libraries/                        # Python library files
├── locators/                         # Element locators by platform
├── resources/                        # Keywords, page objects (Layer 5)
├── testdata/                         # YAML test data
├── tests/                            # Test suites (Layer 5)
└── reports/                          # Robot output, evidence (Layer 6)
```

## Agent System

The project uses a multi-agent orchestration system defined in `.agents/` (Layer 3).

### QA Orchestrator (Layer 4)
- Entry point for all automation tasks
- Classifies task type using signal-based classifier
- Selects internal agent + external skill per routing table
- Checks knowledge layer before loading skills
- Manages the approval flow through review and security gates
- Checks stop conditions at every gate
- Validates preconditions before execution

### Evidence Agent
- Captures screenshots + Appium XML before changes
- Captures after-state evidence for the failing interaction
- Compares manual success vs automation failure
- Stores evidence in `reports/investigation/<screen_name>/`

### Review Agent
- Reviews code before commit
- Checks locator quality, security, performance, git hygiene
- Cross-checks robot-expert and appium-skill rules
- Uses code-reviewer skill for review structure

### Experiment Agent
- Runs one experiment at a time
- Reverts failed or unproven experiments
- Reports results before next experiment
- Maintains isolated experiment state

### RobotFramework Agent
- Understands Robot Framework syntax and AppiumLibrary
- Follows Page Object conventions
- Validates with dryrun before execution
- Consults robot-expert skill and robotframework playbook

### Appium Agent
- Diagnoses Appium, device, emulator, and gesture issues
- Consults appium-skill and appium playbook
- Never guesses appPackage or appActivity

### Locator Agent
- Selects stable, maintainable locators
- Follows Android locator priority (resource-id > accessibility_id > text > XPath)
- Requires XML + screenshot evidence for new locators
- Consults locator playbook and locator pattern

### Security Review Agent
- Final security gate before commit
- Never loads external skills — internal rules only
- Checks PII, credentials, git hygiene, artifact safety

### Bug Agent
- Converts failures into classified defect reports
- Applies systematic-debugging Phase 1 before any fix
- Separates automation defect, app defect, environment, data, backend, device issues

### Performance Agent
- Identifies and resolves performance bottlenecks
- Uses benchmark framework for evidence-based optimization
- Checks React Native compatibility before recommending changes

## Knowledge Layer (Layer 1)

The Knowledge Layer is passive reference material. It is not an active agent. It consists of:

- **knowledge/*.md** — Topic knowledge (Appium, RF, locators, ADB, etc.)
- **knowledge/playbooks/*.md** — Step-by-step workflows for common tasks
- **knowledge/patterns/*.md** — Reusable structural patterns with anti-patterns
- **docs/decisions/ADR-*.md** — Architectural Decision Records

Agents consult the Knowledge Layer before loading external skills. Knowledge is updated only with confirmed evidence.

## Common Onboarding Flow

Flow shared by both NTB and ETB:

```
Landing
  │ Wait Until Landing Screen Is Displayed
  │ Tap Landing Ready Button
  ▼
Consent
  │ Wait Until Consent Screen Is Displayed
  │ Scroll Down Consent Terms (adb swipe)
  │ Tap Consent Accept Button
  ▼
Profile
  │ Wait Until Profile Screen Is Displayed
  │ Tap Citizen ID Container
  │ Enter Digits By Keycodes (citizen ID)
  │ Tap Blank Area to Blur
  │ Input Date Of Birth (picker)
  │ Tap Mobile Container
  │ Enter Digits By Keycodes (mobile number)
  │ Tap Blank Area to Blur
  │ Tap Profile Next (adb shell input tap)
  ▼
[Identity Validation Complete]
```

**Keyword:** `Complete Common Onboarding` in `resources/keywords/onboarding_common.resource`
- Takes `citizen_id`, `date_of_birth`, `mobile_number` as arguments
- Reusable by both NTB and ETB test suites

## NTB Flow

```
[Common Flow]
  │
  ▼
OCR (NTB only)
  │ Identity Verification
  ▼
Face Verification
  │
  ▼
PIN Setup
```

NTB-specific keywords: `resources/keywords/ntb_keywords.resource`
NTB test suite: `tests/android/ntb/ntb_flow.robot`
NTB test data: `testdata/onboarding/ntb.local.yaml` (local, gitignored)

## ETB Flow

```
[Common Flow]
  │
  ▼
ETB-specific flow (TBD)
```

ETB-specific keywords: `resources/keywords/etb_keywords.resource`
ETB test suite: `tests/android/etb/etb_flow.robot`
ETB test data: `testdata/onboarding/etb.local.yaml` (local, gitignored)

## Investigation Workflow

```
1. Identify flaky or failing interaction
2. Evidence Agent captures:
   - Screenshot of current screen
   - Appium XML page source
3. Manual interaction performed and evidence captured:
   - Manual success screenshots + XML
4. Compare manual vs automation:
   - Locator differences
   - Screen state differences
   - Timing differences
5. Hypothesis formation
6. One experiment at a time:
   - Code change
   - Run test
   - Report result
7. If resolved:
   - Document in knowledge/
   - Update locators/keywords
8. If not resolved:
   - Revert experiment
   - Document finding
   - Escalate if needed
```

## Evidence-First Rules

- Capture screenshot and Appium XML before changing Robot code for flaky mobile UI issues
- Capture after-state evidence for the failing interaction and compare it to the before-state
- When manual flow succeeds, compare manual success against automation failure before proposing a fix
- Use debug panel or logcat only when it helps explain the interaction gap
- Keep experiments isolated and reversible
- Create investigation report under `reports/investigation/<screen_name>/` for every investigation

## Approval Flow

```
1. Task assigned to agent
2. Agent inspects existing files
3. Identifies issue type (locator / code / device / security / review / defect)
4. Checks knowledge layer for relevant playbooks/patterns
5. Collects evidence if flaky
6. Proposes change
7. Review Agent validates:
   - Security review
   - Performance review
   - Locator quality
   - Code style
8. Runs dryrun validation
9. On approval: apply change
10. On rejection: revert and document
```

## Milestones

| Milestone | Description | Status |
|-----------|-------------|--------|
| M1 | Shared Onboarding Architecture | Done |
| M2 | Identity Validation (Profile Next) | Done |
| M3 | NTB OCR | Pending |
| M4 | Face Verification | Pending |
| M5 | PIN Setup | Pending |
| M6 | ETB Flow | Pending |
