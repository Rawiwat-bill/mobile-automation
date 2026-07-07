# 10 — Merge Readiness Assessment

## Verdict: **BLOCKED**

The repository is **not ready for merge** to `main`. There are 6 blocking issues
that must be resolved in Sprint C2 before merge.

---

## Blocking Issues

### 1. `.DS_Store` tracked in git [CRITICAL]

| | |
|---|---|
| **Evidence** | `git ls-files .DS_Store` → `.DS_Store` (tracked despite `.gitignore:16`) |
| **Also** | `testdata/.DS_Store` tracked |
| **Fix** | `git rm --cached .DS_Store testdata/.DS_Store` |
| **Why block** | Pollutes every clone; macOS noise in diffs |

### 2. `requirements.txt` is empty [CRITICAL]

| | |
|---|---|
| **Evidence** | `wc -c requirements.txt` → 0 |
| **Why block** | No dependency pinning; CI cannot reproduce environment. Robot Framework, AppiumLibrary, PyYAML versions undefined. |
| **Fix** | Populate with: `robotframework`, `robotframework-appiumlibrary`, `pyyaml` + versions |

### 3. 130 untracked files in working tree [HIGH]

| | |
|---|---|
| **Evidence** | 63 investigation tests + 67 Frida scripts, all `git ls-files` → 0 |
| **Why block** | Merge will either lose this work (if not tracked) or include it unclassified. Need to decide: track, archive, or gitignore. |
| **Fix** | Follow `07_investigation_promotion.md` classification |

### 4. Staged deletions not committed [HIGH]

| | |
|---|---|
| **Evidence** | `git diff --cached --name-status` shows 6 files staged as deleted: `identity_verification_locators.resource`, `mobile_verification_locators.resource`, `identity_verification_page.resource`, `mobile_verification_page.resource`, `etb_onboarding.robot`, `onboarding_skip.robot` |
| **Why block** | Ambiguous merge state — are these intentional removals? |
| **Fix** | Confirm deletions are intentional, commit them |

### 5. `etb_flow.robot` references empty test data [HIGH]

| | |
|---|---|
| **Evidence** | `etb_flow.robot:12` → `${ETB_TESTDATA} testdata/onboarding/etb.local.yaml`; `etb.local.yaml` is 0 bytes |
| **Why block** | Test will fail at runtime with `NoneType` error |
| **Fix** | Populate `etb.local.yaml` or switch to `etb.example.yaml` |

### 6. Root robot outputs in working tree [MEDIUM]

| | |
|---|---|
| **Evidence** | `log.html` (294KB), `output.xml` (227KB), `report.html` (244KB) at root |
| **Why block** | May contain PII from test runs using `ntb.local.yaml`; will clutter merge |
| **Fix** | Delete from working tree |

---

## Non-Blocking Issues (should fix in C2 but not merge blockers)

| # | Severity | Issue | Reference |
|---|----------|-------|-----------|
| 7 | High | Duplicate code: 8 keyword blocks, 17 locator vars | `02_resource_classification.md` |
| 8 | High | App package hardcoded in 3 places | `09_environment_review.md` |
| 9 | High | `configs/` all empty | `09_environment_review.md` |
| 10 | High | `.agents/` empty vs Architecture.md | `01_folder_structure.md` |
| 11 | Medium | Date format inconsistency (YYYY-MM-DD vs DD-MM-YYYY) | `knowledge/profile/dob_picker.md` |
| 12 | Medium | Orphaned `onboarding_keywords.resource` | `02_resource_classification.md` |
| 13 | Medium | Duplicate test suites (ntb_onboarding ≈ ntb_flow) | `03_test_classification.md` |
| 14 | Medium | `live_demo.robot` hardcodes device UDID | `03_test_classification.md` |
| 15 | Low | Placeholder keywords (ntb_keywords, etb_keywords) | `02_resource_classification.md` |

---

## Pre-Merge Checklist

- [ ] `git rm --cached .DS_Store testdata/.DS_Store`
- [ ] Populate `requirements.txt` with pinned dependencies
- [ ] Classify 130 untracked files (track / archive / gitignore)
- [ ] Commit or revert 6 staged deletions
- [ ] Fix `etb_flow.robot` test data reference
- [ ] Delete root `log.html`, `output.xml`, `report.html`
- [ ] Verify no PII in any tracked file
- [ ] Run `python3 -m robot --dryrun tests/android/` to validate syntax
- [ ] Security review of all files to be committed

## Post-Merge (C2+)

- [ ] Extract shared keywords (keycodes, tap, blur, month_map)
- [ ] Populate environment configs (DEV/SIT/UAT)
- [ ] Refactor hardcoded values to config-driven
- [ ] Add test tags for CI filtering
- [ ] Subfolder Frida scripts by milestone
- [ ] Create `.agents/` files or fix Architecture.md
