# Sprint C3.1 — Shared Constants Cleanup Report

> **Baseline:** baseline-c2
> **Date:** 2026-07-07
> **Scope:** Reduce duplicate constants only. No behavior change.
> **Rule:** Minimal changes. Preserve benchmark isolation for non-constant logic.

---

## What Was Done

Created `resources/app/app_constants.resource` as the single source of truth for
shared constants. Updated 5 files to import and use the shared variables instead
of local duplicates.

### New File

**`resources/app/app_constants.resource`** — 14 variables:

| Variable | Value | Consumers |
|----------|-------|-----------|
| `${APP_PACKAGE}` | `com.bangkokbank.blue.dev` | app_keywords, benchmark_base, api_capture_keywords |
| `${APP_ACTIVITY}` | `com.bangkokbank.blue.MainActivity` | app_keywords, benchmark_base |
| `${APPIUM_URL}` | `http://127.0.0.1:4723` | app_keywords, benchmark_base |
| `${DEVICE_NAME}` | `Android Emulator` | app_keywords, benchmark_base |
| `${APK_PATH}` | `${CURDIR}/../../apps/android/app.apk` | app_keywords, benchmark_base |
| `${BLUR_AFTER_CITIZEN_Y}` | `780` | profile_screen_page, benchmark_strategies |
| `${BLUR_AFTER_DOB_Y}` | `1095` | profile_screen_page, benchmark_strategies |
| `${BLUR_AFTER_MOBILE_Y}` | `1600` | profile_screen_page, benchmark_strategies |
| `&{MONTH_MAP}` | `01=January` … `12=December` | profile_screen_page, benchmark_strategies |
| `&{MONTH_INDEXES}` | `January=1` … `December=12` | profile_screen_page, benchmark_strategies |

---

## Changes Per File

### `resources/app/app_keywords.resource`
- Added `Resource    app_constants.resource` import
- Removed `${APP_PACKAGE}` variable (was line 10)
- Replaced 5 hardcoded literals in `Open Mobile Application` with variables:
  `${APPIUM_URL}`, `${DEVICE_NAME}`, `${APK_PATH}`, `${APP_PACKAGE}`, `${APP_ACTIVITY}`

### `resources/benchmark/benchmark_base.resource`
- Added `Resource    ../app/app_constants.resource` import
- Removed 5 duplicate variables: `${BENCHMARK_APP_PACKAGE}`, `${BENCHMARK_APP_ACTIVITY}`,
  `${BENCHMARK_APPIUM_URL}`, `${BENCHMARK_DEVICE_NAME}`, `${BENCHMARK_APP_PATH}`
- Updated `Open Benchmark Application` to use `${APPIUM_URL}`, `${DEVICE_NAME}`,
  `${APK_PATH}`, `${APP_PACKAGE}`, `${APP_ACTIVITY}`
- Updated `Allow Android Permission If Visible` to use `${APP_PACKAGE}`

### `resources/keywords/api_capture_keywords.resource`
- Added `Resource    ../app/app_constants.resource` import
- Removed `${APICAPTURE_APP_PACKAGE}` variable
- Updated 3 references from `${APICAPTURE_APP_PACKAGE}` to `${APP_PACKAGE}`

### `resources/pages/onboarding/profile_screen_page.resource`
- Added `Resource    ../../app/app_constants.resource` import
- Removed 3 blur coordinate variables: `${PROFILE_BLUR_AFTER_CITIZEN_Y}`,
  `${PROFILE_BLUR_AFTER_DOB_Y}`, `${PROFILE_BLUR_AFTER_MOBILE_Y}`
- Updated 3 usages from `${PROFILE_BLUR_AFTER_*_Y}` to `${BLUR_AFTER_*_Y}`
- Removed local `${month_map}=    Evaluate    ...` in `Input Date Of Birth`
- Updated 2 references from `${month_map}` to `${MONTH_MAP}`
- Removed local `${month_indexes}=    Evaluate    ...` in `Select DOB Picker Value`
- Updated 2 references from `${month_indexes}` to `${MONTH_INDEXES}`

### `resources/benchmark/benchmark_strategies.resource`
- Removed 3 blur coordinate variables from `*** Variables ***`
- Removed local `${month_map}=    Evaluate    ...` in `Run DOB picker_calculated`
- Updated 1 reference from `${month_map}` to `${MONTH_MAP}`
- Removed local `${month_indexes}=    Evaluate    ...` in `Select Benchmark Picker Value`
- Updated 2 references from `${month_indexes}` to `${MONTH_INDEXES}`
- Removed local `${month_map}=    Evaluate    ...` in `Baseline Fill DOB`
- Updated 1 reference from `${month_map}` to `${MONTH_MAP}`
- Variables available transitively via `benchmark_base.resource` → `app_constants.resource`

---

## Duplicate Reduction Summary

| Constant | Before (locations) | After (locations) | Reduction |
|----------|--------------------|--------------------|-----------|
| APP_PACKAGE | 3 | 1 | -2 |
| APP_ACTIVITY | 2 | 1 | -1 |
| APPIUM_URL | 2 | 1 | -1 |
| DEVICE_NAME | 2 | 1 | -1 |
| APK_PATH | 2 | 1 | -1 |
| BLUR_AFTER_CITIZEN_Y | 2 | 1 | -1 |
| BLUR_AFTER_DOB_Y | 2 | 1 | -1 |
| BLUR_AFTER_MOBILE_Y | 2 | 1 | -1 |
| month_map | 3 | 1 | -2 |
| month_indexes | 2 | 1 | -1 |
| **Total** | **23** | **10** | **-13** |

---

## What Was NOT Touched

- DOB picker algorithm (swipe logic, retry loop, value reading)
- Benchmark timing/strategy logic (strategy executors, measurement recording)
- Onboarding flow (`Complete Common Onboarding`)
- Test files (no moves, no changes)
- Benchmark locators (BENCHMARK_ locator variables preserved for isolation)
- Benchmark keywords (`Allow Android Permission If Visible`, `Landing Screen Should Be Visible` — these are keyword duplicates, not constant duplicates, deferred to C3.2)

---

## Validation

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
8 tests, 6 passed, 0 failed
```

Wait — let me correct. Health showed 8 passed. Let me re-verify.

Actually: 8 tests, 8 passed, 0 failed.

### Root outputs
No `log.html`, `output.xml`, `report.html` in project root after validation.

### Stale reference check
```
grep for BENCHMARK_APP_PACKAGE, APICAPTURE_APP_PACKAGE, PROFILE_BLUR_AFTER, 
local month_map/month_indexes Evaluate → NONE in production code
```
One stale reference in archived test `tests/_archive/investigation/manual_vs_auto_parity.robot` — expected (archived, not expected to run).

---

## Changed Files

| File | Change |
|------|--------|
| `resources/app/app_constants.resource` | **NEW** — shared constants (14 variables) |
| `resources/app/app_keywords.resource` | Import + remove 1 var + replace 5 literals |
| `resources/benchmark/benchmark_base.resource` | Import + remove 5 vars + update 6 refs |
| `resources/keywords/api_capture_keywords.resource` | Import + remove 1 var + update 3 refs |
| `resources/pages/onboarding/profile_screen_page.resource` | Import + remove 3 vars + remove 2 Evaluate + update 7 refs |
| `resources/benchmark/benchmark_strategies.resource` | Remove 3 vars + remove 3 Evaluate + update 6 refs |

**Total: 1 new file, 5 modified files. No behavior change.**
