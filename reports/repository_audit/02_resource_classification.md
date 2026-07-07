# 02 — Resource Classification

## Resource Inventory

### Page Objects (`resources/pages/onboarding/`)

| File | Lines | Status | Classification |
|------|-------|--------|----------------|
| `landing_screen_page.resource` | 45 | Tracked | **Production** — active |
| `consent_screen_page.resource` | 42 | Tracked | **Production** — active |
| `profile_screen_page.resource` | 275 | Modified (staged) | **Production** — active, largest page |
| `pdpa_consent_page.resource` | 65 | Untracked | **Production** — active |
| `sign_up_page.resource` | 15 | Untracked | **Production** — active |
| `scan_card_intro_page.resource` | 14 | Untracked | **Production** — active |
| `id_card_camera_capture_page.resource` | 25 | Untracked | **Production** — active |

### Keywords (`resources/keywords/`)

| File | Lines | Status | Classification | Notes |
|------|-------|--------|----------------|-------|
| `onboarding_common.resource` | 59 | Modified (staged) | **Production** — core | Aggregation point, imports all pages + health_check |
| `health_check_keywords.resource` | 152 | Untracked | **Health Check** — reusable | Checkpoint tracking, JSON+MD report generation |
| `dob_stability_keywords.resource` | 144 | Untracked | **Health Check** — reusable | DOB picker timing/retry tracking |
| `scroll_keywords.resource` | 146 | Tracked | **Shared utility** — reusable | Responsive scroll + consent big fling |
| `api_capture_keywords.resource` | 75 | Untracked | **Health Check** — reusable | ADB logcat capture + redaction |
| `onboarding_keywords.resource` | 8 | Tracked | **DEAD** — orphaned | 0 importers; `Accept Terms And Conditions` duplicates consent_screen_page |
| `ntb_keywords.resource` | 11 | Tracked | **Placeholder** — Milestone 3 | Single `Log` keyword |
| `etb_keywords.resource` | 11 | Tracked | **Placeholder** — Milestone 6 | Single `Log` keyword |

### App Keywords (`resources/app/`)

| File | Lines | Status | Classification |
|------|-------|--------|----------------|
| `app_keywords.resource` | 42 | Modified | **Production** — core | App launch, permission handling, debug helpers |

### Benchmark (`resources/benchmark/`)

| File | Lines | Status | Classification |
|------|-------|--------|----------------|
| `benchmark_base.resource` | 152 | Untracked | **Benchmark** — reusable | App lifecycle + isolated locators |
| `benchmark_strategies.resource` | 301 | Untracked | **Benchmark** — reusable | Strategy executors, largest file |
| `consent_scroll_strategies.resource` | — | Untracked | **Benchmark** — reusable | Consent scroll strategy comparison |

---

## Findings

### Dead Code

| # | Severity | Finding | Evidence |
|---|----------|---------|----------|
| 1 | High | `onboarding_keywords.resource` is orphaned | `grep -rl "onboarding_keywords.resource"` → 0 results. Its only keyword `Accept Terms And Conditions` duplicates `consent_screen_page.resource` (Wait + Tap). |
| 2 | Medium | `ntb_keywords.resource` / `etb_keywords.resource` are placeholder-only | Each has 1 keyword that just `Log`s a message. **Ponytail says delete.** QA partially disagrees: keep as milestone scaffolding markers but add `[Tags] placeholder` and document in the milestone tracker. |

### Duplication (shared keyword opportunities)

| # | Severity | Duplicate | Locations | Recommendation |
|---|----------|-----------|-----------|----------------|
| 3 | High | `Allow Android Permission If Visible` | `app_keywords.resource:25` + `benchmark_base.resource:60` | Benchmark should import from app_keywords |
| 4 | High | `Landing Screen Should Be Visible` | `landing_screen_page.resource:14` + `benchmark_base.resource:80` | Benchmark should import from landing_screen_page |
| 5 | High | Blur Y coordinates (780/1095/1600) | `benchmark_strategies.resource:10-12` + `profile_screen_page.resource:15-17` | Single source variable |
| 6 | High | App package `com.bangkokbank.blue.dev` | `app_keywords.resource:10` + `benchmark_base.resource:11` + `api_capture_keywords.resource:7` | Single `${APP_PACKAGE}` |
| 7 | High | App activity `com.bangkokbank.blue.MainActivity` | `app_keywords.resource:22` + `benchmark_base.resource:12` | Single `${APP_ACTIVITY}` |
| 8 | Medium | `month_map` dict | `profile_screen_page.resource:121` + `benchmark_strategies.resource:84` + `benchmark_strategies.resource:289` | Extract to shared variables file |
| 9 | Medium | DOB picker select algorithm | `profile_screen_page.resource:205` (`Select DOB Picker Value`) + `benchmark_strategies.resource:238` (`Select Benchmark Picker Value`) | See `04_benchmark_review.md` for nuance |
| 10 | Medium | `month_indexes` dict | `profile_screen_page.resource:207` + `benchmark_strategies.resource:240` | Extract with `month_map` |

### Coupling

| # | Severity | Finding | Evidence |
|---|----------|---------|----------|
| 11 | Medium | `onboarding_common.resource:10` imports `health_check_keywords` | Shared flow is coupled to health-check infrastructure. Tests that don't want health tracking still pull it in. `Mark Health Checkpoint` is a no-op when `HEALTH_CHECK_ACTIVE` is false (good design), but the import coupling remains. |

---

## Shared Keyword Candidates (new)

| Candidate | Source Keywords | Rationale |
|-----------|----------------|-----------|
| `Enter Digits By Keycodes` | Already in benchmark_strategies:222 | Should move to `resources/keywords/input_keywords.resource` — reused by production Citizen ID + Mobile input |
| `Tap By Coordinates` | Already in benchmark_strategies:216 | Generic helper, should be shared |
| `Field Should Be Blurred` | Already in benchmark_strategies:211 | Generic helper, should be shared |
| `Normalize Digits` | In profile_screen_page:76 | Should be shared — used for field verification |
| `month_map` / `month_indexes` | 3 locations | Extract to `resources/keywords/date_helpers.resource` or variables file |

---

## Disagreement with Ponytail

**Ponytail:** Delete `ntb_keywords.resource` / `etb_keywords.resource` (YAGNI).

**QA:** Keep as milestone scaffolding. Reasoning:
- AGENTS.md Milestones section explicitly tracks M3 (NTB OCR) and M6 (ETB Flow) as
  pending. The placeholder files serve as structural markers for where milestone code
  will live.
- Cost of keeping: 22 lines total. Cost of deleting + recreating: lost structural
  context.
- **Recommendation:** Keep, but add `[Tags] placeholder` and a `TODO` referencing the
  milestone. Do NOT invest in real implementation until milestone starts.
