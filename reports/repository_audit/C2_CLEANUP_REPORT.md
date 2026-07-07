# C2 — Merge Blocker Resolution Report

> **Sprint:** C2 — Merge Blocker Cleanup
> **Date:** 2026-07-07
> **Scope:** Resolve only the 6 merge blockers from Sprint C1.
> **No refactoring, no framework redesign, no runtime behavior changes.**

---

## Blocker Resolution Summary

| # | Blocker | Status | Resolution |
|---|---------|--------|------------|
| 1 | `.DS_Store` tracked in git | **RESOLVED** | `git rm --cached .DS_Store` |
| 2 | `requirements.txt` empty | **RESOLVED** | Populated with robotframework>=7.0, robotframework-appiumlibrary>=3.0, pyyaml>=6.0 |
| 3 | 130 untracked files | **RESOLVED** | All files classified and staged — see details below |
| 4 | 6 staged deletions uncommitted | **RESOLVED** | Confirmed intentional (Milestone 1 refactor); staged with `git rm` |
| 5 | `etb_flow.robot` references empty `etb.local.yaml` | **RESOLVED** | Changed to `etb.example.yaml` (safe fake data) |
| 6 | Root robot outputs in working tree | **RESOLVED** | Deleted `log.html`, `output.xml`, `report.html` |

---

## Detailed Actions

### Blocker 1: `.DS_Store` tracked in git

**Action:** `git rm --cached .DS_Store`
**Rationale:** `.DS_Store` is macOS Finder metadata. Already in `.gitignore:16` but was committed before the ignore rule existed. Removed from git index only; file remains in working tree (macOS will recreate it).

### Blocker 2: `requirements.txt` empty

**Action:** Wrote `requirements.txt` with:
```
robotframework>=7.0
robotframework-appiumlibrary>=3.0
pyyaml>=6.0
```
**Rationale:** These are the direct Python dependencies. Versions pinned to minimum tested (installed: robotframework 7.3.2, appiumlibrary 3.1, pyyaml 6.0.3). `Appium-Python-Client` is pulled transitively by appiumlibrary.

### Blocker 3: 130 untracked files

**Action:** All files classified and staged. See `C2_FILE_DECISIONS.md` for full detail.

**Summary:**
- 13 investigation tests promoted to `tests/health/`, `tests/benchmark/`, `tests/regression/`, `tests/preparation/`
- 50 investigation tests archived to `tests/_archive/investigation/`
- 65 Frida scripts organized into `tools/frida/{ocr,bridge,face,debug}/`
- 3 Frida shell scripts kept at `tools/frida/` root
- All production code (locators, resources, libraries, tools, configs, docs) tracked
- `.opencode/` (local node_modules) added to `.gitignore`
- Mock image (`apps/android/mock/ntb_id_card.png`) tracked

### Blocker 4: 6 staged deletions

**Action:** Confirmed intentional, staged with `git rm`.

| File | Reason |
|------|--------|
| `locators/android/onboarding/identity_verification_locators.resource` | Identity validation folded into `Complete Common Onboarding` (Milestone 1) |
| `locators/android/onboarding/mobile_verification_locators.resource` | Mobile number entered on Profile screen |
| `resources/pages/onboarding/identity_verification_page.resource` | Same — superseded by shared onboarding |
| `resources/pages/onboarding/mobile_verification_page.resource` | Same |
| `tests/android/onboarding/etb_onboarding.robot` | Superseded by `tests/android/etb/etb_flow.robot` |
| `tests/android/onboarding/onboarding_skip.robot` | Landing skip handled in `landing_screen_page.resource` |

**Evidence:** `grep -rl` for all 6 filenames across all `.robot` and `.resource` files → 0 references found.

### Blocker 5: `etb_flow.robot` references empty test data

**Action:** Changed `${ETB_TESTDATA}` from `testdata/onboarding/etb.local.yaml` (0 bytes) to `testdata/onboarding/etb.example.yaml` (safe fake data).

**Rationale:** `etb.local.yaml` is empty (0 bytes). `etb.example.yaml` contains safe fake data (citizen_id `2222222222222`). LOCAL files are not a supported environment — example data is the correct default.

### Blocker 6: Root robot outputs

**Action:** `rm -f log.html output.xml report.html`
**Rationale:** Gitignored but present in working tree. May contain PII from test runs using `ntb.local.yaml`. Deleted.

---

## .gitignore Updates

Added:
- `*.log` — log files
- `.opencode/` — local opencode node_modules

Fixed:
- Duplicate comment "Local sensitive test data" → corrected to "# Dependencies" for node_modules

---

## Validation Results

### `git status --short`
- **0 untracked files** (`??` count = 0)
- 175 files staged as Added (A)
- 7 files staged as Deleted (D)
- 5 files staged as Modified (M)

### `python3 -m robot --dryrun tests/android/`
```
6 tests, 6 passed, 0 failed
```

### `python3 -m robot --dryrun tests/health/ tests/benchmark/ tests/regression/ tests/preparation/`
```
27 tests, 27 passed, 0 failed
```

### Root outputs
No `log.html`, `output.xml`, `report.html` in project root after validation.

---

## What Was NOT Done (deferred to C3)

- Duplicate code extraction (8 keyword blocks, 17 locator vars)
- Environment config population (DEV/SIT/UAT)
- Hardcoded app package refactoring
- `.agents/` directory population
- Date format standardization
- Test tag addition
- Orphaned `onboarding_keywords.resource` removal
- Placeholder keyword documentation

These are non-blocking issues tracked in `10_merge_readiness.md` and `02_resource_classification.md`.
