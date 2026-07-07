# C2.5 — .gitignore Review

> **Date:** 2026-07-07
> **Scope:** Review and fix `.gitignore` to allow repository documentation tracking
> while keeping generated artifacts ignored.

---

## Problem

The `.gitignore` had `reports/` on line 6, which ignores the **entire** `reports/`
directory tree. This blocked all repository documentation from being tracked:

| Path | Content | Should Be | Was |
|------|---------|-----------|-----|
| `reports/repository_audit/` | 16 `.md` audit reports (C1/C2) | TRACKED | IGNORED |
| `reports/repository_cleanup/` | 7 `.md` cleanup reports (C3) | TRACKED | IGNORED |
| `reports/benchmark/` | Robot output, screenshots, XML | IGNORED | IGNORED (correct) |
| `reports/investigation/` | Screenshots, XML dumps, evidence | IGNORED | IGNORED (correct) |
| `reports/stability/` | DOB stability JSON/PNG | IGNORED | IGNORED (correct) |
| `reports/health_check/` | Health check JSON/MD (generated) | IGNORED | IGNORED (correct) |
| `reports/performance/` | Performance benchmark results | IGNORED | IGNORED (correct) |
| 200+ other `reports/*` dirs | Generated runtime artifacts | IGNORED | IGNORED (correct) |

**Root cause:** `reports/` ignores the directory itself, preventing `!` exceptions
from working. Git never traverses into an ignored directory.

---

## Change Made

**File modified:** `.gitignore` (only file modified this sprint)

### Before
```gitignore
# Robot Framework
reports/
output.xml
log.html
report.html
```

### After
```gitignore
# Robot Framework
/reports/*
!/reports/repository_audit/
!/reports/repository_cleanup/
output.xml
log.html
report.html
```

### What changed

| Line | Before | After | Reason |
|------|--------|-------|--------|
| 6 | `reports/` | `/reports/*` | Ignore **contents** of reports/, not the directory itself. Allows exceptions. |
| 7 | (none) | `!/reports/repository_audit/` | Un-ignore audit documentation directory |
| 8 | (none) | `!/reports/repository_cleanup/` | Un-ignore cleanup documentation directory |

**Diff:** 1 line changed, 2 lines added. Minimal.

---

## Validation

### `git check-ignore` tests

| Path | Result | Expected |
|------|--------|----------|
| `reports/repository_audit/REPORT.md` | Not ignored | TRACKABLE |
| `reports/repository_cleanup/C3_1_REPORT.md` | Not ignored | TRACKABLE |
| `reports/benchmark/output.xml` | Ignored | IGNORED |
| `reports/investigation/screenshot.png` | Ignored | IGNORED |
| `reports/stability/test.json` | Ignored | IGNORED |
| `output.xml` | Ignored | IGNORED |
| `log.html` | Ignored | IGNORED |
| `report.html` | Ignored | IGNORED |

All pass.

### `git status --short`
```
 M .gitignore
?? reports/
```

- `.gitignore` modified (working tree)
- `reports/` now visible as untracked (documentation files can be `git add`-ed)
- All other previously-staged/modified files unchanged

### Generated artifacts check

All 200+ generated report directories remain ignored. Only the two documentation
directories (`repository_audit/`, `repository_cleanup/`) are now trackable.

---

## Path Classification

| Path | Classification | Reason |
|------|----------------|--------|
| `reports/repository_audit/` | **KEEP TRACKED** | Project documentation — audit reports, merge readiness, health scores |
| `reports/repository_cleanup/` | **KEEP TRACKED** | Project documentation — cleanup reports, keyword reviews, validation |
| `reports/benchmark/` | **KEEP IGNORED** | Generated Robot output, screenshots, timing data |
| `reports/benchmark-latest/` | **KEEP IGNORED** | Generated benchmark results |
| `reports/benchmark-history/` | **KEEP IGNORED** | Generated benchmark history |
| `reports/investigation/` | **KEEP IGNORED** | Generated investigation evidence (screenshots, XML dumps) |
| `reports/stability/` | **KEEP IGNORED** | Generated DOB stability tracking JSON/PNG |
| `reports/health_check/` | **KEEP IGNORED** | Generated health check reports (runtime output) |
| `reports/performance/` | **KEEP IGNORED** | Generated performance benchmark results |
| `reports/api_logs/` | **KEEP IGNORED** | Generated API capture logs (may contain PII) |
| `reports/diagnostic/` | **KEEP IGNORED** | Generated diagnostic screenshots/XML |
| All other `reports/*` | **KEEP IGNORED** | Generated runtime artifacts |
| `output.xml` | **KEEP IGNORED** | Root Robot output |
| `log.html` | **KEEP IGNORED** | Root Robot log |
| `report.html` | **KEEP IGNORED** | Root Robot report |

### Archive candidates

None. All generated artifacts are correctly ignored. No action needed.

---

## Migration Impact

- **No runtime behavior change.** `.gitignore` does not affect test execution.
- **No Robot Framework logic modified.**
- **No Page Objects modified.**
- **No locators modified.**
- Documentation files under `reports/repository_audit/` and `reports/repository_cleanup/`
  are now visible to git and can be `git add`-ed in the next commit.
- Generated artifacts remain ignored — no risk of accidental commits.
