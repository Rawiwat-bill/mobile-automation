# Mobile Banking Automation Wiki

## 1. Project Overview

This project automates Android mobile-banking onboarding and registration flows using:

- Robot Framework
- AppiumLibrary
- Appium 3.x with UiAutomator2
- Android Emulator or approved Android device
- React Native application under test

The framework uses Page Object architecture, screen-specific locators, reusable business keywords, and separate test data.

Current supported scope:

- Platform: Android
- Primary environment: DEV
- Customer journeys: NTB and ETB onboarding coverage
- Execution: local emulator and approved real device, depending on the scenario
- iOS, UAT, and parallel execution are not currently configured

## 2. Business Journeys

### NTB — New To Bank

NTB represents a new customer onboarding journey:

1. Open the application and handle permissions.
2. Accept Terms and Conditions.
3. Enter Citizen ID, Date of Birth, and Mobile Number.
4. Provide PDPA consent.
5. Continue to Sign Up introduction.
6. Enter the ID-card scanning flow.
7. Continue to OCR and camera capture.
8. Continue to face verification and PIN setup where supported.

The OCR/camera portion requires a real device. The emulator camera does not provide a usable capture frame for the full NTB flow.

### ETB — Existing To Bank

ETB represents an existing Bangkok Bank customer registration or enrollment journey:

1. Open the application and switch to English.
2. Accept Terms and Conditions.
3. Enter Citizen ID, Date of Birth, and Mobile Number.
4. Submit with `NEXT`.
5. Perform CIS/customer-profile validation and backend handoff.
6. Continue through ETB-specific validation:
   - DOPA validation
   - Laser Code validation
   - Mobile OTP
   - PDPA consent, where applicable
   - Face-scan introduction
   - PIN setup and PIN confirmation
7. Reach Registration Complete or the expected RGI result.
8. Run approved idempotent cleanup after the test.

ETB execution depends on DEV backend availability, CIS readiness, approved local profiles, and the Google Play environment prerequisite.

## 3. ETB Regression Coverage

Canonical suite:

`tests/android/etb/etb_regression.robot`

The suite contains 13 cases:

| Cases | Business coverage |
|---|---|
| TC-ETB-001 | Positive registration success |
| TC-ETB-002 | Positive registration with PDPA Clause 6 |
| TC-ETB-003 to TC-ETB-004 | Product-selection variants and existing accounts |
| TC-ETB-005 to TC-ETB-006 | Mobile-number and Date-of-Birth mismatch RGI popups |
| TC-ETB-007 | Expired Citizen ID full-screen RGI |
| TC-ETB-008 to TC-ETB-011 | High-risk 3A, 3V, 3U, and 3B full-screen RGI |
| TC-ETB-012 | Low IAL full-screen RGI |
| TC-ETB-013 | Mule-warning full-screen RGI |

Available selections:

```bash
./run etb --dry-run
./run etb
./run etb TC-ETB-001
./run etb --tag smoke
./run etb --smoke
```

Do not run the full regression when a required external service is unavailable.

### Traceability

Full static traceability for TC-ETB-001..013 is maintained in:

- `configs/etb_traceability_full.json` — machine-readable registry
- `docs/standards/ETB_TRACEABILITY_MATRIX.md` — human-readable matrix
- `configs/etb_traceability_pilot.json` — retained historical pilot / immutable design-binding evidence
- `docs/standards/BBL_ETB_ACCEPTANCE_SNAPSHOT_2026-09-27.md` — current runtime acceptance state

Static traceability and runtime acceptance are separate dimensions. Do not infer a runtime pass percentage from static mapping completeness.

## 4. Repository Structure

```text
tests/
  Android business scenarios and suites
resources/keywords/
  Reusable business flow and orchestration keywords
resources/pages/
  Screen-specific page interaction keywords
locators/android/
  Android locators separated by screen
libraries/
  YAML loading, CIS/PDPA preparation, cleanup, evidence, and sanitization
testdata/
  Committed examples/contracts and gitignored local approved profiles
apps/android/
  Approved local APKs; do not commit new sensitive APKs without authorization
knowledge/
  Project patterns, playbooks, decisions, and operational truth
reports/
  Robot results and investigation evidence
tools/
  CI and operational scripts
run
  Main local runner
setup
  Local Python environment setup
```

## 5. Android Environments

### DEV

| Item | Value |
|---|---|
| AVD | `local_android_36` |
| Serial | `emulator-5554` |
| Image | Android 16 `google_apis_playstore` |
| APK | `apps/android/app-dev.apk` |
| Package | `com.bangkokbank.blue.dev` |
| Activity | `com.bangkokbank.blue.MainActivity` |

### SIT

| Item | Value |
|---|---|
| AVD | `Pixel_8` |
| Serial | `emulator-5556` |
| APK | `apps/android/app-sit-mmplot2.apk` |
| Package | `com.bangkokbank.blue.sit` |

Environment isolation is mandatory. The serials above are environment examples, not an execution-time authority. `DEVICE_UDID`, environment selection and target-guard validation are authoritative for each run. Install and run only against the intended target, and do not remove the competing environment from the wrong emulator.

## 6. Mandatory Readiness Gates

Before Android Sign Up or post-Sign Up continuation:

- Google Play Store must be installed, enabled, and launchable.
- Google Play services must be present and operational.
- The selected emulator image must support Google Play.
- AOSP or non-Play-Store images are not valid for this flow.
- The required DEV backend/CIS service must be available.
- Approved local test data must exist.
- Required VPN, endpoint, and approved CA configuration must be available.
- Appium must be running locally with the required security option.

Current NTB/Sign Up blocker status:

```text
ENVIRONMENT_PREREQUISITE: GOOGLE_PLAY_REQUIRED
GOOGLE_PLAY_PREREQUISITE: CONFIRMED
CURRENT_BLOCKER: REQUIRED_SERVICE_UNAVAILABLE
AUTOMATION_STATUS: BLOCKED_BEFORE_POST_SIGN_UP_CONTINUATION
ROOT_CAUSE_CATEGORY: EXTERNAL_SERVICE_AVAILABILITY
READY_TO_CONTINUE: NO
```

When this blocker is active:

- Stop at the current boundary.
- Do not repeatedly rerun Sign Up.
- Do not modify locators, test logic, application data, network settings, or emulator configuration as a workaround.
- Do not run the full regression suite.
- Resume only after the service owner confirms restoration.

## 7. Installation and Execution

### Prerequisites

Install Python, Node.js, JDK 17, Android SDK Platform-Tools, Android Emulator, and Appium UiAutomator2. Then run:

```bash
./setup
npm install -g appium@3.5.0
appium driver install uiautomator2@7.6.1
```

### Start Appium

Use the project-managed, least-privilege launcher:

```bash
pnpm appium
```

The default launcher binds to `127.0.0.1` and enables only `--allow-insecure=uiautomator2:adb_shell`. Do not use `--relaxed-security` as the default. Inspector/CORS is opt-in through:

```bash
pnpm appium:inspector
```

### Verify the device

```bash
adb devices -l
adb -s emulator-5554 shell getprop sys.boot_completed
adb -s emulator-5554 shell pm list packages | grep com.bangkokbank.blue.dev
```

### Install the DEV app

```bash
adb -s emulator-5554 install -r apps/android/app-dev.apk
```

Verify package version and launcher activity before execution.

### Prepare local runtime data

Approved local files are required and must remain outside Git:

```text
testdata/onboarding/etb_cases.local.yaml
testdata/onboarding/ntb.local.yaml
local/env/etb.env
local/certs/cis-ca-bundle.pem
```

Never print or commit customer data, Citizen IDs, mobile numbers, accounts, passwords, OTPs, tokens, certificates, or unmasked logs.

## 8. Validation Levels

### Dry run

Use dry run to validate Robot syntax and ETB selection without starting a mobile session:

```bash
./run etb --dry-run
```

### Smallest affected testcase

After an external blocker is confirmed restored:

1. Verify Google Play Store and Google Play services.
2. Run only the smallest affected Sign Up testcase once.
3. Continue from the earliest unverified post-Sign Up boundary.
4. Capture sanitized logs only if the flow fails again.

### Full regression

Only run after readiness gates pass:

```bash
./run etb
```

Results are written to:

```text
reports/run-etb/
```

Primary artifacts include `report.html`, `log.html`, and `output.xml`.

## 9. Investigation Rules

For flaky or unexpected mobile behavior:

1. Capture screenshot and Appium XML before changing code.
2. Capture after-state evidence.
3. Compare manual success with automation failure.
4. Identify whether the issue is environment, service, app, locator, or automation.
5. Run one experiment at a time.
6. Revert failed or unproven experiments.
7. Record the result under `reports/investigation/<screen_name>/`.

A service-unavailable response after Sign Up is an environment/service gate unless evidence proves otherwise. It must not automatically be treated as an Appium or locator defect.

## 10. Architecture Rules

- Test cases describe business behavior.
- Page resources own screen interaction.
- Locators remain outside test cases.
- Test data remains outside test logic.
- Prefer explicit condition-based waits over fixed sleeps.
- Reuse existing keywords and locators before creating new ones.
- Use coordinates only for evidence-backed ADB interaction, never as locator definitions.
- Keep Appium bound to `127.0.0.1`.

## 11. Security and Evidence Handling

Never commit:

- Real customer data or PII
- Citizen IDs, phone numbers, account numbers, passwords, or OTPs
- Tokens, certificates, private keys, or production secrets
- Unapproved APKs
- Raw screenshots, XML, logs, or reports containing sensitive data

Mask sensitive values before sharing evidence. Use the project’s sanitization and redaction utilities where available.

No commit, push, PR, merge, or release approval is part of normal test execution.

## 12. Key Documentation

- `docs/standards/ETB_TRACEABILITY_MATRIX.md` — full static TC001–TC013 traceability and current runtime bindings
- `configs/etb_traceability_full.json` — machine-readable full traceability registry
- `docs/standards/BBL_ETB_ACCEPTANCE_SNAPSHOT_2026-09-27.md` — accepted/open runtime cases
- `docs/standards/BBL_REMEDIATION_CHECKLIST.md` — remediation Block B/C/D status

- Project setup and business runbook: `README.md`
- Architecture and coverage overview: `AUTOMATION_OVERVIEW.md`
- Project structure and standards: `AGENTS.md`
- Android/ADB patterns: `knowledge/adb.md`
- Test strategy and readiness rules: `knowledge/test-strategy.md`
- Current NTB/Sign Up blocker receipt: `reports/investigation/ntb_signup_readiness/2026-08-29_blocker_receipt.md`
- ETB canonical suite: `tests/android/etb/etb_regression.robot`

## 13. Ownership and Escalation

| Situation | Escalation |
|---|---|
| Required service unavailable | Service/backend owner |
| Backend or CIS readiness failure | Automation/backend owner |
| App behavior differs from expected business flow | Application/development team |
| Locator or UI interaction issue with evidence | Automation team |
| PII, secrets, or unsafe evidence exposure | Security owner immediately |
| Architecture or scope decision | Project owner |
