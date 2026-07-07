# 04 — Resource Moves

> Keywords moved this sprint, with rationale and validation.

---

## Moves Executed

### Move 1: Tap By Coordinates

| Field | Value |
|-------|-------|
| **Keyword** | `Tap By Coordinates` |
| **From** | `resources/benchmark/benchmark_strategies.resource` |
| **To** | `resources/benchmark/benchmark_base.resource` |
| **Callers** | 3 calls in benchmark_strategies (Blur Citizen ID, Blur DOB, Blur Mobile) |
| **Import change** | None — benchmark_strategies already imports benchmark_base |

### Move 2: Field Should Be Blurred

| Field | Value |
|-------|-------|
| **Keyword** | `Field Should Be Blurred` |
| **From** | `resources/benchmark/benchmark_strategies.resource` |
| **To** | `resources/benchmark/benchmark_base.resource` |
| **Callers** | 3 calls in benchmark_strategies (Blur Citizen ID, Blur DOB, Blur Mobile) |
| **Import change** | None |

### Move 3: Enter Digits By Keycodes

| Field | Value |
|-------|-------|
| **Keyword** | `Enter Digits By Keycodes` |
| **From** | `resources/benchmark/benchmark_strategies.resource` |
| **To** | `resources/benchmark/benchmark_base.resource` |
| **Callers** | 4 calls in benchmark_strategies (Run Citizen ID press_keycodes, Run Mobile press_keycodes, Baseline Fill Citizen ID, Baseline Fill Mobile) |
| **Import change** | None |

---

## Why These Moves Qualify

All three sprint conditions met:

| Condition | Met? | Evidence |
|-----------|------|----------|
| Responsibility clearly improves | Yes | benchmark_base = primitives + lifecycle; benchmark_strategies = strategy executors only. benchmark_base already had interaction helpers (Tap Landing Ready, Tap Consent Accept). |
| Imports become simpler | Yes | Zero import changes — benchmark_strategies already imports benchmark_base. Keywords available transitively. |
| Behavior remains identical | Yes | Keyword bodies unchanged. Callers unchanged. Same import chain. |

---

## Moves NOT Executed (with reasons)

### Normalize Digits

| Field | Value |
|-------|-------|
| **From** | `resources/pages/onboarding/profile_screen_page.resource` |
| **Proposed to** | `resources/shared/input_helpers.resource` (new) |
| **Reason not moved** | Would add 1 import to profile_screen_page. "Imports become simpler" condition not met. |
| **Future condition** | Create when 2+ page objects need it (OCR/Face/PIN milestones) |

### Input Text Field

| Field | Value |
|-------|-------|
| **From** | `resources/pages/onboarding/profile_screen_page.resource` |
| **Proposed to** | `resources/shared/input_helpers.resource` (new) |
| **Reason not moved** | Same as above — adds import. |
| **Future condition** | Same as above. |

### Verify Field Value

| Field | Value |
|-------|-------|
| **From** | `resources/pages/onboarding/profile_screen_page.resource` |
| **Proposed to** | `resources/shared/input_helpers.resource` (new) |
| **Reason not moved** | Depends on Normalize Digits — move together. |
| **Future condition** | Same as above. |

---

## Validation After Moves

### `python3 -m robot --dryrun tests/android/`
```
6 tests, 6 passed, 0 failed
```

### `python3 -m robot --dryrun tests/benchmark/`
```
14 tests, 14 passed, 0 failed
```

### `python3 -m robot --dryrun tests/health/`
```
8 tests, 8 passed, 0 failed
```

All green. No behavior change.

---

## Files Changed

| File | Change |
|------|--------|
| `resources/benchmark/benchmark_base.resource` | +29 lines (3 keywords added at end) |
| `resources/benchmark/benchmark_strategies.resource` | -29 lines (3 keywords removed) |

**Net: 0 lines changed. 2 files modified. 0 new files.**
