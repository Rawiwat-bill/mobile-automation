# 03 — Keywords Kept

> All duplicate keywords kept, with justification.

---

## BENCHMARK ISOLATION (2 keywords)

### 1. Allow Android Permission If Visible

| Field | Value |
|-------|-------|
| **Production** | `resources/app/app_keywords.resource:25` |
| **Benchmark** | `resources/benchmark/benchmark_base.resource:56` |
| **Reason kept** | Benchmark version calls `Record Appium Action` twice for measurement. Production version does not. Different locator variables (${ANDROID_PERMISSION_ALLOW_BUTTON} broader vs ${BENCHMARK_PERM_ALLOW} simpler). Merging would either add measurement to production (behavior change) or remove it from benchmark (breaks timing). |
| **Future merge condition** | Only if benchmark measurement is refactored to use a wrapper/decorator pattern that doesn't require inline `Record Appium Action` calls. |

### 2. Landing Screen Should Be Visible

| Field | Value |
|-------|-------|
| **Production** | `resources/pages/onboarding/landing_screen_page.resource:14` |
| **Benchmark** | `resources/benchmark/benchmark_base.resource:76` |
| **Reason kept** | Production has 60s built-in retry via `Wait Until Keyword Succeeds`. Benchmark has no retry (caller `Navigate To Landing` wraps it). Different timing behavior — merging would change benchmark measurement. |
| **Future merge condition** | Only if retry logic is extracted to a parameter and both callers pass their own retry config. |

---

## INTENTIONAL DUPLICATE (1 keyword)

### 3. Field Should Be Blurred / Profile Fields Should Be Blurred

| Field | Value |
|-------|-------|
| **Benchmark (generic)** | `resources/benchmark/benchmark_strategies.resource:204` — `Field Should Be Blurred` |
| **Production (page-specific)** | `resources/pages/onboarding/profile_screen_page.resource:56` — `Profile Fields Should Be Blurred` |
| **Reason kept** | Different signatures: benchmark takes `${locator}` (checks 1 field), production takes no args (checks 3 hardcoded fields). Production could call benchmark 3x, but that's a Page Object modification — explicitly out of scope. |
| **Future merge condition** | After Page Object refactor (out of C3 scope): `Profile Fields Should Be Blurred` could call a shared `Field Should Be Blurred` 3 times. |

---

## NOT DUPLICATES (kept, no action needed)

| Keyword | Location | Note |
|---------|----------|------|
| Tap By Coordinates | `benchmark_strategies.resource:209` | Only in benchmark. `Tap Profile Blank Area` is similar but page-specific (hardcoded x=540, no measurement). |
| Tap Profile Element Center | `profile_screen_page.resource:39` | Only in production. Page-specific. |
| Enter Digits By Keycodes | `benchmark_strategies.resource:215` | Only in benchmark. Production uses `Input Text`, not keycodes. |
| Normalize Digits | `profile_screen_page.resource:74` | Only in production. |

---

## NOT FOUND (3 candidates)

| Keyword | Status |
|---------|--------|
| Wait For App Ready | Does not exist in codebase |
| Wait Until Activity Changes | Does not exist in codebase |
| Execute Adb Shell wrappers | Does not exist — `Execute Adb Shell` called directly from AppiumLibrary |
| Generic Retry helpers | Does not exist — `Wait Until Keyword Succeeds` used inline |
