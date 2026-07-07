# 03 — Test Classification

## Test Inventory

### Production Tests (`tests/android/`) — 6 files

| File | Test Data | Status | Classification | Notes |
|------|-----------|--------|----------------|-------|
| `onboarding/ntb_onboarding.robot` | `ntb.local.yaml` (PII) | Tracked | **Regression** | Duplicates `ntb/ntb_flow.robot` |
| `onboarding/onboarding_health_check.robot` | `ntb.local.yaml` (PII) | Untracked | **Health Check** | E2E + API capture + DOB stability |
| `common/onboarding_common.robot` | `ntb.example.yaml` | Tracked | **Regression** | Uses example (safe) data |
| `common/identity_validation.robot` | `ntb.example.yaml` | Tracked | **Regression** | ≈ onboarding_common + 1 log line |
| `ntb/ntb_flow.robot` | `ntb.local.yaml` (PII) | Tracked | **Regression** | Duplicates `onboarding/ntb_onboarding.robot` |
| `etb/etb_flow.robot` | `etb.local.yaml` (EMPTY) | Tracked | **Regression** | Will fail — empty test data |

### Benchmark Tests (`tests/benchmark/`) — 3 files

| File | Status | Classification |
|------|--------|----------------|
| `profile_field_benchmark.robot` | Untracked | **Benchmark** — reusable |
| `consent_benchmark.robot` | Untracked | **Benchmark** — reusable |
| `landing_benchmark.robot` | Untracked | **Benchmark** — reusable |

### Demo (`tests/demo/`) — 1 file

| File | Status | Classification |
|------|--------|----------------|
| `live_demo.robot` | Untracked | **Throwaway** — hardcoded UDID, coordinate taps |

### Investigation (`tests/investigation/`) — 63 files

All untracked. See `07_investigation_promotion.md` for per-file classification.

---

## Findings

### Critical

| # | Finding | Evidence | Impact |
|---|---------|----------|--------|
| 1 | `etb_flow.robot` uses `etb.local.yaml` which is 0 bytes | `wc -c testdata/onboarding/etb.local.yaml` → 0 | Test will fail at `Load YAML` — `NoneType` subscript error |
| 2 | `ntb_onboarding.robot` and `ntb_flow.robot` are near-identical | Both: `Load YAML ntb.local.yaml` → `Complete Common Onboarding`. Same Suite Setup/Teardown. | Redundant; one should be removed |
| 3 | `onboarding_common.robot` and `identity_validation.robot` are near-identical | Both: `Load YAML ntb.example.yaml` → `Complete Common Onboarding`. identity_validation adds 1 `Log` line. | Redundant; differentiate by tags or merge |

### High

| # | Finding | Evidence | Recommendation |
|---|---------|----------|----------------|
| 4 | 3 production tests depend on `ntb.local.yaml` (real PII) | `ntb_onboarding.robot`, `ntb_flow.robot`, `onboarding_health_check.robot` all reference it | Tests should default to `ntb.example.yaml`; local data only for real-device runs |
| 5 | `live_demo.robot` hardcodes device UDID | `${UDID} 48ZYD25C01422768` at line 11 | Security: device identifier exposed. Move to local config or remove. |
| 6 | `live_demo.robot` uses coordinate taps | `adb shell input tap 360 1511` | Violates locator baseline (reject coordinates as locators) |

### Medium

| # | Finding | Evidence | Recommendation |
|---|---------|----------|----------------|
| 7 | No test tags for CI filtering | No `[Tags]` on production tests | Add tags: `regression`, `smoke`, `health`, `benchmark`, `ntb`, `etb` |
| 8 | No SIT/UAT test data | Only `ntb.example.yaml` + `ntb.local.yaml` | Add `ntb.sit.yaml`, `ntb.uat.yaml` when environments are ready |

---

## Recommended Test Classification

| Suite | Location | Tags | Data | CI |
|-------|----------|------|------|----|
| NTB Regression | `tests/android/ntb/ntb_flow.robot` | `regression ntb` | `ntb.example.yaml` | Yes |
| ETB Regression | `tests/android/etb/etb_flow.robot` | `regression etb` | `etb.example.yaml` (populate) | Yes |
| Identity Validation | `tests/android/common/identity_validation.robot` | `regression identity` | `ntb.example.yaml` | Yes |
| Health Check | `tests/android/onboarding/onboarding_health_check.robot` | `health` | `ntb.local.yaml` (real device only) | Manual |
| Benchmark | `tests/benchmark/*.robot` | `benchmark` | `ntb.example.yaml` | Nightly |
| Demo | Remove or move to `reports/investigation/` | — | — | No |

### Consolidation

- **Remove** `tests/android/onboarding/ntb_onboarding.robot` — duplicate of `ntb/ntb_flow.robot`
- **Remove** `tests/android/common/onboarding_common.robot` — duplicate of `identity_validation.robot`
- **Keep** `identity_validation.robot` as the canonical common-flow regression test
