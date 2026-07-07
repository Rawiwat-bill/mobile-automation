# 11 — Repository Health Score

## Scoring Matrix

| Dimension | Weight | Score | Weighted | Notes |
|-----------|--------|-------|----------|-------|
| Folder Structure | 15% | 7.0 | 1.05 | Clean Page Object layout; investigation/frida unclassified |
| Architecture | 20% | 6.0 | 1.20 | Good layering in docs; `.agents/` empty, reality mismatch |
| Reusability | 20% | 7.0 | 1.40 | `Complete Common Onboarding` excellent; benchmark duplicates |
| Classification | 15% | 4.0 | 0.60 | Investigation/benchmark/health/preparation not separated |
| Technical Debt | 15% | 5.0 | 0.75 | 8 duplicate blocks, 3 placeholders, empty configs, no requirements.txt |
| Merge Readiness | 15% | 3.0 | 0.45 | 130 untracked, staged deletions, .DS_Store tracked, no deps |
| **Overall** | **100%** | — | **5.45** | **Needs C2 cleanup before merge** |

---

## Detailed Scores

### Folder Structure — 7/10

| Criterion | Score | Notes |
|-----------|-------|-------|
| Page Object separation | 9/10 | `locators/` ↔ `resources/pages/` ↔ `resources/keywords/` — clean 1:1 mapping |
| Test organization | 5/10 | Production tests in 3 locations (onboarding/, ntb/, common/); investigation mixed in |
| Tool organization | 7/10 | `tools/` has logical subdivision; Frida scripts unclassified (67 files flat) |
| Config organization | 3/10 | `configs/` exists but all files empty |
| Root cleanliness | 6/10 | Robot outputs at root; `.DS_Store` tracked |

### Architecture — 6/10

| Criterion | Score | Notes |
|-----------|-------|-------|
| Layer separation (docs) | 8/10 | Architecture.md defines clear 7-layer model |
| Layer implementation | 4/10 | `.agents/` empty — 8+ agents described but don't exist |
| Knowledge layer | 9/10 | `knowledge/` well-structured with playbooks + patterns |
| Shared flow design | 8/10 | `Complete Common Onboarding` is the right pattern |
| Coupling | 5/10 | `onboarding_common` imports `health_check_keywords` (coupling); benchmark duplicates instead of imports |

### Reusability — 7/10

| Criterion | Score | Notes |
|-----------|-------|-------|
| Shared keywords | 8/10 | `Complete Common Onboarding`, `Allow Android Permission`, scroll helpers |
| Shared utilities | 6/10 | `config_loader.py` (5 lines), `api_log_redactor.py` — could be more |
| Benchmark reusability | 7/10 | Good strategy comparison framework; duplicated from production |
| Health check reusability | 8/10 | Three-state model, JSON+MD output — production quality |
| Locator reusability | 7/10 | Clean separation; benchmark copies instead of imports |

### Classification — 4/10

| Criterion | Score | Notes |
|-----------|-------|-------|
| Test type separation | 3/10 | No tags; no folder separation between regression/health/benchmark/investigation |
| Investigation classification | 2/10 | 63 files all in one flat directory, untracked |
| Benchmark classification | 7/10 | Well-tagged in test docs; folder separated |
| Health classification | 5/10 | Good resource separation; test file untracked |
| Preparation classification | 5/10 | `Complete Common Onboarding` is clear; no partial preparation |

### Technical Debt — 5/10

| Criterion | Score | Notes |
|-----------|-------|-------|
| Duplicate code | 3/10 | 8 keyword blocks, 17 locator vars, 3 month_map copies |
| Dead code | 5/10 | 1 orphaned resource, 2 placeholder resources, 1 empty test data |
| Empty scaffolding | 2/10 | 3 empty config files, empty requirements.txt, empty .agents/ |
| Dependency management | 1/10 | requirements.txt is 0 bytes — no pinned deps |
| Documentation accuracy | 5/10 | Architecture.md describes non-existent agents |

### Merge Readiness — 3/10

| Criterion | Score | Notes |
|-----------|-------|-------|
| Git hygiene | 2/10 | `.DS_Store` tracked, root outputs present, 130 untracked files |
| Staged changes | 3/10 | 6 staged deletions uncommitted; 2 files staged+modified |
| Test viability | 4/10 | `etb_flow.robot` will fail (empty data); duplicates exist |
| Dependency reproducibility | 1/10 | No requirements.txt |
| Security | 5/10 | PII gitignored (good); root outputs may contain PII (bad) |

---

## Trend Analysis

| Metric | Current | Target (post-C2) | Target (post-C3) |
|--------|---------|-------------------|-------------------|
| Overall Health | 5.5 | 7.5 | 8.5 |
| Merge Readiness | 3 | 8 | 9 |
| Duplicate Blocks | 8 | 2 | 0 |
| Untracked Files | 130 | 0 | 0 |
| Empty Configs | 6 | 0 | 0 |
| Tracked .DS_Store | 2 | 0 | 0 |

## Risk Assessment

| Risk | Probability | Impact | Mitigation |
|------|-------------|--------|------------|
| Merge loses investigation work | High | High | Classify + track/archive before merge |
| CI fails due to missing deps | High | High | Populate requirements.txt |
| PII leaks via root outputs | Medium | Critical | Delete outputs; audit tracked files |
| Benchmark diverges from production | Medium | Medium | Add locator consistency check |
| ETB test fails in CI | High | Low | Fix test data reference |
| Date format bug causes DOB failure | Medium | High | Standardize format |
