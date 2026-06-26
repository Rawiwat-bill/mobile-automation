# Test Strategy Knowledge

## Test Types

### 1. Functional Flow Tests
File: `tests/android/ntb/ntb_flow.robot`, `tests/android/etb/etb_flow.robot`
- End-to-end onboarding flow
- Validates navigation, field input, data persistence
- Separate suites for NTB and ETB customer types

### 2. Identity Validation Tests
File: `tests/android/common/identity_validation.robot`
- Profile Next navigation
- Field interaction strategies
- Cross-field validation

### 3. Benchmark Tests
File: `tests/benchmark/profile_field_benchmark.robot`
- Strategy comparison for Citizen ID, DOB, Mobile Number
- Execution time measurement
- Stability classification

## Test Data Separation

- Customer-specific data in `testdata/onboarding/<type>.example.yaml` (committed)
- Local overrides in `testdata/onboarding/<type>.local.yaml` (gitignored)
- Data loaded via `Load YAML` from `config_loader.py`
- Test cases never hardcode data

## Customer Types

### NTB (New To Bank)
- Full flow: Common Onboarding → OCR → Face Verification → PIN Setup
- Milestone 3-5 (implementation pending)

### ETB (Existing To Bank)
- Simplified flow (TBD)
- Milestone 6 (implementation pending)

## Test Data Fields

| Field | Example | Type |
|-------|---------|------|
| Citizen ID | `1111111111111` | 13-digit string |
| Date of Birth | `1990-01-01` | YYYY-MM-DD string |
| Mobile Number | `0811111111` | 10-digit string |

## Environment Dependencies

- VPN required for backend connectivity
- Dev backend may return `Service is not available now` — this is an environment limitation, not a test failure
- Appium must run with `--relaxed-security`
- Device or emulator must be connected and stable

## Investigation Workflow

1. Evidence capture (screenshot, XML)
2. Manual vs automation comparison
3. Hypothesis formation
4. One experiment at a time
5. Document findings in `knowledge/`
6. Escalate if 3+ fixes fail

## Internal Project Truth

This strategy reflects the actual test organization and data model of the project. External test strategy suggestions from skills are secondary to the project's proven patterns and architecture.
