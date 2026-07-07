# 05 — Architecture Score

> Repository architecture health assessment after C3.3.

---

## Scoring

| Dimension | Score | Notes |
|-----------|-------|-------|
| Single Responsibility | 7.5/10 | Profile page has 3 generic helpers that belong elsewhere (deferred). Benchmark base/strategies separation improved. |
| Coupling | 7/10 | onboarding_common → health_check_keywords coupling is intentional (no-op when inactive). Profile → dob_stability coupling is tight but necessary for DOB tracking. |
| Cohesion | 8/10 | Most files have clear single purpose. benchmark_strategies now focuses purely on strategy executors. |
| Shared Reuse | 7/10 | Constants shared (C3.1). Generic helpers still siloed in page objects. Will improve when shared/ is created. |
| Folder Organization | 7.5/10 | Clean locators/pages/keywords/benchmark structure. Missing shared/ (justified — insufficient content). tests/ well-classified after C2. |
| Maintainability | 8/10 | Clear naming conventions. Page Object pattern consistent. 271-line profile page is largest concern but DOB algorithm can't be extracted (out of scope). |
| **Overall** | **7.5/10** | Good architecture. Minor debt in profile page generic helpers. Benchmark structure improved this sprint. |

---

## Score Trend

| Dimension | C1 (start) | C3.1 | C3.2 | C3.3 (now) | Trend |
|-----------|-----------|------|------|------------|-------|
| Single Responsibility | 6.0 | 6.5 | 6.5 | 7.5 | ↑ |
| Coupling | 6.0 | 6.5 | 6.5 | 7.0 | ↑ |
| Cohesion | 6.5 | 7.0 | 7.0 | 8.0 | ↑ |
| Shared Reuse | 5.0 | 7.0 | 7.0 | 7.0 | → |
| Folder Organization | 7.0 | 7.0 | 7.0 | 7.5 | ↑ |
| Maintainability | 6.5 | 7.5 | 7.5 | 8.0 | ↑ |
| **Overall** | **6.2** | **6.9** | **6.9** | **7.5** | ↑ |

---

## Strengths

1. **Page Object pattern is consistent** — 7 page files, each with Wait/Tap/Input keywords
2. **Locator separation is clean** — 1:1 mapping between locators and pages
3. **Shared constants (C3.1)** — single source of truth for app config, months, blur coords
4. **Benchmark isolation preserved** — own locators, own lifecycle, own measurement
5. **Health check is non-invasive** — no-op when inactive, soft coupling via imports
6. **Test classification (C2)** — production/benchmark/health/regression/preparation/archive

## Weaknesses

1. **Profile page is 271 lines** — contains DOB algorithm (can't extract), 3 generic helpers (should extract but import rule blocks)
2. **No `resources/shared/` directory** — justified now, but will be needed for OCR/Face/PIN milestones
3. **Empty config files** — `configs/env/dev.yaml`, `configs/devices/*.yaml` are 0 bytes
4. **`.agents/` empty** — Architecture.md describes agents that don't exist as files
5. **onboarding_common imports health_check_keywords** — coupling between flow and infrastructure

## Recommendations for Future Sprints

| Priority | Item | When |
|----------|------|------|
| Medium | Create `resources/shared/input_helpers.resource` with Normalize Digits, Input Text Field, Verify Field Value | When OCR milestone adds second page with input fields |
| Medium | Populate `configs/env/dev.yaml` with current hardcoded values | Before SIT/UAT environment work |
| Low | Refactor health check report generation to Python library | When report format changes or grows complex |
| Low | Create `.agents/` files or fix Architecture.md | When agent system is activated |
| Low | Split benchmark_strategies by field (citizen/dob/mobile) | When file exceeds 350 lines (currently 263) |
