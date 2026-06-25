# Mobile Automation Architecture

## Project Layers

```
┌──────────────────────────────────────────────────┐
│  Test Suites (tests/)                            │
│  Business-flow test cases                        │
├──────────────────────────────────────────────────┤
│  Resource Keywords (resources/keywords/)          │
│  Cross-screen flow keywords                      │
├──────────────────────────────────────────────────┤
│  Page Keywords (resources/pages/)                 │
│  Screen-level page objects + interactions        │
├──────────────────────────────────────────────────┤
│  Locators (locators/)                             │
│  Element definitions by platform and screen      │
├──────────────────────────────────────────────────┤
│  Libraries (libraries/)                          │
│  Python helpers (config_loader, etc.)            │
├──────────────────────────────────────────────────┤
│  Test Data (testdata/)                           │
│  YAML data files separated by customer type      │
├──────────────────────────────────────────────────┤
│  Knowledge (knowledge/)                          │
│  Solved problems, architectural decisions        │
├──────────────────────────────────────────────────┤
│  Reports (reports/)                              │
│  Robot output, investigation evidence            │
└──────────────────────────────────────────────────┘
```

## Agent System

The project uses a multi-agent orchestration system defined in `.agents/`.

### QA Orchestrator
- Entry point for all automation tasks
- Delegates to specialized agents
- Manages the approval flow
- Validates preconditions before execution

### Evidence Agent
- Captures screenshots + Appium XML before changes
- Captures after-state evidence for the failing interaction
- Compares manual success vs automation failure
- Stores evidence in `reports/investigation/<screen_name>/`

### Review Agent
- Reviews code before commit
- Checks locator quality
- Validates security requirements
- Verifies git hygiene

### Experiment Agent
- Runs one experiment at a time
- Reverts failed or unproven experiments
- Maintains isolated experiment branches
- Reports results before next experiment

### RobotFramework Agent
- Understands Robot Framework syntax
- Knows AppiumLibrary keywords
- Follows Page Object conventions
- Validates with dryrun before execution

### Knowledge Agent
- Records solved problems in `knowledge/`
- Tracks architectural decisions
- Provides context for recurring issues

## Folder Structure

```
.
├── .agents/                          # Agent instruction files
├── AGENTS.md                         # Master agent instructions
├── apps/                             # Application binaries (APK)
├── configs/                          # Device and environment configs
│   ├── devices/
│   └── env/
├── docs/                             # Architecture and design docs
├── knowledge/                        # Solved problems documentation
├── libraries/                        # Python library files
├── locators/                         # Element locators by platform
│   └── android/
│       └── onboarding/
├── resources/
│   ├── app/                          # App session management
│   │   └── app_keywords.resource
│   ├── keywords/                     # Cross-screen flow keywords
│   │   ├── onboarding_common.resource
│   │   ├── ntb_keywords.resource
│   │   └── etb_keywords.resource
│   └── pages/                        # Screen-level page objects
│       └── onboarding/
├── testdata/                         # YAML test data
│   └── onboarding/
├── tests/                            # Test suites
│   └── android/
│       ├── common/                   # Shared flow tests
│       ├── ntb/                      # NTB-specific tests
│       ├── etb/                      # ETB-specific tests
│       └── onboarding/               # Legacy (backward compat)
└── reports/                          # Robot output + evidence
    └── investigation/
```

## Common Flow

Flow shared by both NTB and ETB:

```
Landing
  │ Wait Until Landing Screen Is Displayed
  │ Tap Landing Ready Button
  ▼
Consent
  │ Wait Until Consent Screen Is Displayed
  │ Scroll Down Consent Terms
  │ Tap Consent Accept Button
  ▼
Profile
  │ Wait Until Profile Screen Is Displayed
  │ Input Citizen ID (adb keycodes)
  │ Input Date Of Birth (picker)
  │ Input Mobile Number (adb keycodes)
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
4. Collects evidence if flaky
5. Proposes change
6. Review Agent validates:
   - Security review
   - Performance review
   - Locator quality
   - Code style
7. Runs dryrun validation
8. On approval: apply change
9. On rejection: revert and document
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
