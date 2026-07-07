# 01 — Keyword Review

> Every candidate generic keyword, its locations, duplicate comparison, and classification.

---

## Classification Key

| Class | Meaning | Action |
|-------|---------|--------|
| TRUE DUPLICATE | Same logic, same side effects, same signature | Merge |
| INTENTIONAL DUPLICATE | Same concept, different logic/signature/side effects | Keep |
| BENCHMARK ISOLATION | Same concept, benchmark adds measurement or uses isolated locators | Keep |
| PLACEHOLDER | Stub for future milestone | Keep |
| UNKNOWN | Cannot determine safely | Report only |

---

## 1. Allow Android Permission If Visible

| Field | Value |
|-------|-------|
| **Location A** | `resources/app/app_keywords.resource:25` |
| **Location B** | `resources/benchmark/benchmark_base.resource:56` |
| **Duplicate With** | Each other |

### Implementation A (production)
```robotframework
Allow Android Permission If Visible
    ${is_visible}=    Run Keyword And Return Status
    ...    Wait Until Element Is Visible    ${ANDROID_PERMISSION_ALLOW_BUTTON}    ${ANDROID_PERMISSION_TIMEOUT}
    IF    ${is_visible}
        Click Element    ${ANDROID_PERMISSION_ALLOW_BUTTON}
        Activate Application    ${APP_PACKAGE}
    END
```

### Implementation B (benchmark)
```robotframework
Allow Android Permission If Visible
    ${is_visible}=    Run Keyword And Return Status
    ...    Wait Until Element Is Visible    ${BENCHMARK_PERM_ALLOW}    ${BENCHMARK_PERM_TIMEOUT}
    IF    ${is_visible}
        Click Element    ${BENCHMARK_PERM_ALLOW}
        Record Appium Action
        Activate Application    ${APP_PACKAGE}
        Record Appium Action
    END
```

### Differences

| Aspect | Production | Benchmark |
|--------|-----------|-----------|
| Locator | `${ANDROID_PERMISSION_ALLOW_BUTTON}` (broader: includes `permission_allow_foreground_only_button`) | `${BENCHMARK_PERM_ALLOW}` (narrower: only `permission_allow_button`) |
| Timeout | `${ANDROID_PERMISSION_TIMEOUT}` (5s) | `${BENCHMARK_PERM_TIMEOUT}` (5s) |
| Measurement | None | `Record Appium Action` x2 |
| Side effects | Click + Activate | Click + Record + Activate + Record |

### Callers
- Production: `onboarding_common.resource` (3 calls), 15+ health/regression/preparation tests
- Benchmark: `benchmark_base.resource` `Navigate To Profile` (2 calls), 3 benchmark tests

### Classification: **BENCHMARK ISOLATION** → Keep

Merging would either add `Record Appium Action` to production (behavior change)
or remove it from benchmark (breaks measurement). Different locator robustness
is intentional — benchmark uses simpler locator for measurement consistency.

---

## 2. Landing Screen Should Be Visible

| Field | Value |
|-------|-------|
| **Location A** | `resources/pages/onboarding/landing_screen_page.resource:14` |
| **Location B** | `resources/benchmark/benchmark_base.resource:76` |
| **Duplicate With** | Each other |

### Implementation A (production)
```robotframework
Landing Screen Should Be Visible
    Wait Until Keyword Succeeds    ${LANDING_TIMEOUT}    500ms    Landing Action Should Be Visible
```
Where `Landing Action Should Be Visible` checks skip first (early RETURN), then ready.

### Implementation B (benchmark)
```robotframework
Landing Screen Should Be Visible
    ${is_skip}=    Run Keyword And Return Status    Element Should Be Visible    ${BENCHMARK_LANDING_SKIP}
    ${is_ready}=    Run Keyword And Return Status    Element Should Be Visible    ${BENCHMARK_LANDING_READY}
    Should Be True    ${is_skip} or ${is_ready}
```

### Differences

| Aspect | Production | Benchmark |
|--------|-----------|-----------|
| Retry | 60s with 500ms interval (built in) | None (caller wraps in retry) |
| Logic | Delegates to `Landing Action Should Be Visible` (early return on skip) | Checks both, then asserts |
| Locator vars | `${LANDING_SKIP_BUTTON}` / `${LANDING_READY_BUTTON}` | `${BENCHMARK_LANDING_SKIP}` / `${BENCHMARK_LANDING_READY}` |
| Timeout behavior | Blocks up to 60s | Instant check |

### Callers
- Production: `Wait Until Landing Screen Is Displayed` in same file
- Benchmark: `Navigate To Landing` (wraps in `Wait Until Keyword Succeeds`), `landing_benchmark.robot`

### Classification: **BENCHMARK ISOLATION** → Keep

Production has 60s retry built in — needed for real app startup. Benchmark has
no retry (caller controls retry timing for measurement). Merging would change
benchmark timing behavior.

---

## 3. Tap By Coordinates

| Field | Value |
|-------|-------|
| **Location** | `resources/benchmark/benchmark_strategies.resource:209` |
| **Duplicate With** | None (similar concept: `Tap Profile Blank Area` in profile_screen_page) |

### Implementation (benchmark)
```robotframework
Tap By Coordinates
    [Arguments]    ${x}    ${y}
    ${tap_point}=    Create List    ${x}    ${y}
    Tap    ${tap_point}
    Record Appium Action
```

### Similar but NOT duplicate: `Tap Profile Blank Area`
```robotframework
Tap Profile Blank Area
    [Arguments]    ${blank_y}
    ${tap_point}=    Create List    540    ${blank_y}
    Tap    ${tap_point}
```

### Differences
- Different signature: `Tap By Coordinates` takes (x, y); `Tap Profile Blank Area` takes only y (x hardcoded to 540)
- Benchmark has `Record Appium Action`; production does not
- `Tap Profile Blank Area` is page-specific (hardcoded x=540 for profile screen width)

### Classification: **Not a duplicate** → No action

---

## 4. Tap Element Center

| Field | Value |
|-------|-------|
| **Location** | `resources/pages/onboarding/profile_screen_page.resource:39` as `Tap Profile Element Center` |
| **Duplicate With** | None |

### Classification: **Not a duplicate** → No action
Only exists in one location. Page-specific (uses `${PROFILE_TIMEOUT}`).

---

## 5. Field Should Be Blurred vs Profile Fields Should Be Blurred

| Field | Value |
|-------|-------|
| **Location A** | `resources/benchmark/benchmark_strategies.resource:204` — `Field Should Be Blurred` |
| **Location B** | `resources/pages/onboarding/profile_screen_page.resource:56` — `Profile Fields Should Be Blurred` |
| **Duplicate With** | Each other (concept) |

### Implementation A (benchmark — generic)
```robotframework
Field Should Be Blurred
    [Arguments]    ${locator}
    ${focused}=    Get Element Attribute    ${locator}    focused
    Should Be Equal As Strings    ${focused}    false
```

### Implementation B (production — page-specific)
```robotframework
Profile Fields Should Be Blurred
    ${citizen_focused}=    Get Element Attribute    ${PROFILE_CITIZEN_ID_INPUT}    focused
    ${dob_focused}=    Get Element Attribute    ${PROFILE_DOB_INPUT}    focused
    ${mobile_focused}=    Get Element Attribute    ${PROFILE_MOBILE_NUMBER_INPUT}    focused
    Should Be Equal As Strings    ${citizen_focused}    false
    Should Be Equal As Strings    ${dob_focused}    false
    Should Be Equal As Strings    ${mobile_focused}    false
```

### Differences
- Different signature: benchmark takes `${locator}`; production takes no args
- Different logic: benchmark checks 1 field; production checks 3 fields
- Different names
- Production could theoretically call benchmark version 3x, but that's a Page Object modification — OUT OF SCOPE

### Classification: **INTENTIONAL DUPLICATE** → Keep

---

## 6. Enter Digits By Keycodes

| Field | Value |
|-------|-------|
| **Location** | `resources/benchmark/benchmark_strategies.resource:215` |
| **Duplicate With** | None |

### Classification: **Not a duplicate** → No action
Only in benchmark. Production uses `Input Text` for Citizen ID/Mobile, not keycodes.
Keycodes are a benchmark strategy variant, not a shared utility.

---

## 7. Normalize Digits

| Field | Value |
|-------|-------|
| **Location** | `resources/pages/onboarding/profile_screen_page.resource:74` |
| **Duplicate With** | None |

### Classification: **Not a duplicate** → No action
Only in one location. Page-specific helper for field value verification.

---

## 8. Wait For App Ready

| Field | Value |
|-------|-------|
| **Status** | Not found in codebase |

### Classification: **N/A** → No action

---

## 9. Wait Until Activity Changes

| Field | Value |
|-------|-------|
| **Status** | Not found in codebase |

### Classification: **N/A** → No action

---

## 10. Execute Adb Shell Wrappers

| Field | Value |
|-------|-------|
| **Status** | Not found — `Execute Adb Shell` is called directly from AppiumLibrary, no wrapper |

### Classification: **N/A** → No action

---

## 11. Generic Retry Helpers

| Field | Value |
|-------|-------|
| **Status** | Not found — `Wait Until Keyword Succeeds` is used inline, no wrapper keyword |

### Classification: **N/A** → No action

---

## Newly Discovered Duplicates

None discovered. All generic keywords in the codebase were accounted for in the
11 candidates above.
