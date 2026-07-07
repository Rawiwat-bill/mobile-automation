# 02 — Shared Keyword Review

> Review of generic reusable keyword candidates across all resources.

---

## Current Shared Keyword Locations

### `resources/app/app_keywords.resource`
| Keyword | Generic? | Used by |
|---------|----------|---------|
| `Open Mobile Application` | Yes — app lifecycle | onboarding_common, tests |
| `Allow Android Permission If Visible` | Yes — permission | onboarding_common, tests |
| `Debug Screenshot` | Yes — debug | (conditional on DEBUG_MODE) |
| `Debug Log` | Yes — debug | (conditional on DEBUG_MODE) |

### `resources/keywords/scroll_keywords.resource`
| Keyword | Generic? | Used by |
|---------|----------|---------|
| `Scroll Down Page Responsively` | Yes — scroll | consent_screen_page |
| `Scroll Down Consent Terms With Big Fling` | Semi-generic (consent-specific defaults) | consent_screen_page |
| `Dump Current Screen Xml Stats With Adb` | Yes — ADB utility | scroll_keywords (internal) |
| `Get Current Screenshot Hash With Adb` | Yes — ADB utility | scroll_keywords (internal) |
| `Count Scroll XML Markers` | Yes — utility | scroll_keywords (internal) |

### `resources/keywords/health_check_keywords.resource`
| Keyword | Generic? | Used by |
|---------|----------|---------|
| `Start Health Check` | Health-specific | onboarding_health_check.robot |
| `Mark Health Checkpoint` | Health-specific | onboarding_common |
| `Set Health Check Blocker` | Health-specific | onboarding_common |
| `End Health Check` | Health-specific | onboarding_health_check.robot |

### `resources/keywords/api_capture_keywords.resource`
| Keyword | Generic? | Used by |
|---------|----------|---------|
| `Start API Capture` | API-specific | onboarding_health_check.robot |
| `Stop API Capture` | API-specific | onboarding_health_check.robot |

### `resources/benchmark/benchmark_base.resource` (after C3.3 move)
| Keyword | Generic? | Used by |
|---------|----------|---------|
| `Tap By Coordinates` | Yes — tap primitive | benchmark_strategies (3 calls) |
| `Field Should Be Blurred` | Yes — field check | benchmark_strategies (3 calls) |
| `Enter Digits By Keycodes` | Yes — input primitive | benchmark_strategies (4 calls) |

---

## Candidate Review

### ADB helpers
| Candidate | Location | Status |
|-----------|----------|--------|
| `Dump Current Screen Xml Stats With Adb` | scroll_keywords | Correctly placed — only used by scroll |
| `Get Current Screenshot Hash With Adb` | scroll_keywords | Correctly placed — only used by scroll |
| `Execute Adb Shell` | AppiumLibrary built-in | No wrapper exists — used directly. Correct. |

### Permission helpers
| Candidate | Location | Status |
|-----------|----------|--------|
| `Allow Android Permission If Visible` | app_keywords | Correctly placed — shared app keyword |

### Tap helpers
| Candidate | Location | Status |
|-----------|----------|--------|
| `Tap By Coordinates` | benchmark_base (moved C3.3) | Correctly placed — benchmark primitive |
| `Tap Profile Element Center` | profile_screen_page | Correctly placed — page-specific (uses PROFILE_TIMEOUT) |
| `Tap Profile Blank Area` | profile_screen_page | Correctly placed — page-specific (hardcodes x=540) |

### Retry helpers
| Candidate | Location | Status |
|-----------|----------|--------|
| `Wait Until Keyword Succeeds` | Robot built-in | No wrapper. Used inline. Correct. |

### Blur helpers
| Candidate | Location | Status |
|-----------|----------|--------|
| `Field Should Be Blurred` | benchmark_base (moved C3.3) | Correctly placed — benchmark primitive |
| `Profile Fields Should Be Blurred` | profile_screen_page | Correctly placed — page-specific (checks 3 fields) |
| `Wait Until Profile Fields Are Blurred` | profile_screen_page | Correctly placed — page-specific wrapper |

### Input helpers
| Candidate | Location | Status |
|-----------|----------|--------|
| `Enter Digits By Keycodes` | benchmark_base (moved C3.3) | Correctly placed — benchmark primitive |
| `Input Text Field` | profile_screen_page | **Recommend** move to shared — deferred (see 01_page_object_review.md) |
| `Normalize Digits` | profile_screen_page | **Recommend** move to shared — deferred |

### Wait helpers
| Candidate | Location | Status |
|-----------|----------|--------|
| `Wait Until Landing Screen Is Displayed` | landing_screen_page | Correctly placed — page-specific |
| `Wait Until Consent Screen Is Displayed` | consent_screen_page | Correctly placed — page-specific |
| `Wait Until Profile Screen Is Displayed` | profile_screen_page | Correctly placed — page-specific |
| `Wait For Profile` | benchmark_base | Correctly placed — benchmark-specific |

---

## Summary

| Category | Candidates reviewed | Moves made | Recommendations (deferred) |
|----------|--------------------|------------|---------------------------|
| ADB | 3 | 0 | 0 |
| Permission | 1 | 0 | 0 |
| Tap | 3 | 1 (Tap By Coordinates → benchmark_base) | 0 |
| Retry | 1 | 0 | 0 |
| Blur | 3 | 1 (Field Should Be Blurred → benchmark_base) | 0 |
| Input | 3 | 1 (Enter Digits By Keycodes → benchmark_base) | 2 (Normalize Digits, Input Text Field) |
| Wait | 4 | 0 | 0 |
| **Total** | **18** | **3** | **2** |
