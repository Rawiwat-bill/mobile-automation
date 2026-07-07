# Sprint C1 — Repository Audit Report (Read Only)

> **Status:** AUDIT ONLY. No files modified, moved, renamed, or deleted.
> **Branch:** `spike/appium-skill`
> **Date:** 2026-07-07
> **Input:** `ponytail_audit.md` (developer-review layer) + QA automation review
> **Next Sprint:** C2 performs cleanup after approval.

---

## Executive Summary

The repository has a **solid automation core** — Page Object pattern, separated
locators, shared `Complete Common Onboarding` keyword, evidence-first workflow.
Milestones M1 (shared onboarding) and M2 (identity validation) are done.

However, the repository is **not merge-ready** due to:

1. **130 untracked working artifacts** (63 investigation tests + 67 Frida scripts)
   polluting the working tree but not committed — merge will lose or ignore them.
2. **Staged deletions** of 6 files (identity/mobile verification pages, etb_onboarding,
   onboarding_skip) that haven't been committed.
3. **`.DS_Store` tracked in git** despite `.gitignore`.
4. **Root-level robot outputs** (`log.html`, `output.xml`, `report.html`) in working tree.
5. **Duplicate code** between production and benchmark resources (8 keyword blocks,
   17 locator vars).
6. **Empty scaffolding**: `configs/` (3 files, 0 bytes), `requirements.txt` (0 bytes),
   `etb.local.yaml` (0 bytes), `.agents/` (empty, but Architecture.md describes 8+
   agents).
7. **Date format inconsistency**: example data is YYYY-MM-DD, local data is DD-MM-YYYY,
   production code and benchmark code parse parts in opposite order.
8. **Real PII** in `ntb.local.yaml` (gitignored, safe — but root robot outputs may
   contain it in logs).

**Merge readiness: BLOCKED** — see `10_merge_readiness.md`.

---

## Ponytail Audit Disposition

| Ponytail Finding | QA Disposition | Notes |
|-----------------|----------------|-------|
| Investigation tests untracked | **Agree** | Promote useful ones, archive rest — see `07_investigation_promotion.md` |
| Frida scripts untracked | **Agree** | Same — classify per milestone |
| `.DS_Store` tracked | **Agree** | Merge blocker |
| Benchmark duplicates locators | **Agree but nuanced** | Benchmark isolation is intentional for measurement purity — see `04_benchmark_review.md` |
| Duplicate `Allow Android Permission` | **Agree** | Shared keyword candidate |
| Duplicate blur coordinates | **Agree** | Single source |
| App package hardcoded 3x | **Agree** | Single source |
| `month_map` duplicated 3x | **Agree** | Extract |
| DOB picker logic duplicated | **Agree but nuanced** | Benchmark may need isolated copy — see `04_benchmark_review.md` |
| `onboarding_keywords.resource` orphaned | **Agree** | 0 importers confirmed |
| `ntb_keywords`/`etb_keywords` placeholders | **Partially disagree** | Keep as milestone scaffolding markers, but document — see `02_resource_classification.md` |
| `configs/` empty | **Agree** | Populate for DEV/SIT/UAT — see `09_environment_review.md` |
| `requirements.txt` empty | **Agree** | Merge blocker — see `10_merge_readiness.md` |
| Demo test throwaway | **Agree** | Move to investigation |
| `.agents/` empty vs Architecture.md | **Agree** | Doc/reality mismatch |

### QA findings Ponytail missed

1. **Root robot outputs contain potential PII** — `log.html`/`output.xml`/`report.html`
   at root may log citizen ID / phone from test runs. Security concern.
2. **Demo test hardcodes device UDID** — `48ZYD25C01422768` in `tests/demo/live_demo.robot:11`.
3. **`onboarding_common.robot` and `identity_validation.robot` are near-identical** —
   Ponytail caught the NTB duplicate but missed this pair.
4. **Staged deletions not committed** — 6 files staged as deleted but not committed;
   merge state is ambiguous.
5. **`onboarding_common.resource` imports `health_check_keywords`** — couples the
   shared flow to health-check infrastructure; tests that don't want health tracking
   still pull it in.
6. **No DEV/SIT/UAT environment separation** — `configs/env/dev.yaml` is empty;
   everything is hardcoded to dev package `com.bangkokbank.blue.dev`.

---

## Repository Health Score

| Dimension | Score | Notes |
|-----------|-------|-------|
| Folder Structure | 7/10 | Clean Page Object layout; investigation/frida unclassified |
| Architecture | 6/10 | Good layering in docs; `.agents/` empty, reality mismatch |
| Reusability | 7/10 | `Complete Common Onboarding` is excellent; benchmark duplicates instead of reuses |
| Classification | 4/10 | Investigation/benchmark/health/preparation not separated in folder structure |
| Technical Debt | 5/10 | 8 duplicate blocks, 3 placeholders, empty configs, no requirements.txt |
| Merge Readiness | 3/10 | 130 untracked files, staged deletions, .DS_Store tracked, no deps pinned |
| **Overall** | **5.3/10** | Good foundation, needs C2 cleanup before merge |

---

## Deliverables

| File | Topic |
|------|-------|
| `01_folder_structure.md` | Directory organization review |
| `02_resource_classification.md` | Resource/keyword classification |
| `03_test_classification.md` | Test suite classification |
| `04_benchmark_review.md` | Benchmark review (reusable, NOT temporary) |
| `05_health_review.md` | Health check review |
| `06_preparation_review.md` | Preparation flow review |
| `07_investigation_promotion.md` | Investigation promotion recommendations |
| `08_gitignore_review.md` | .gitignore and hygiene review |
| `09_environment_review.md` | Environment review (DEV/SIT/UAT) |
| `10_merge_readiness.md` | Merge readiness assessment |
| `11_repository_health_score.md` | Detailed health scoring |
