# 08 — .gitignore & Repository Hygiene Review

## Current `.gitignore`

```gitignore
# IDE
.idea/
.vscode/

# Robot Framework
reports/
output.xml
log.html
report.html

# Python
__pycache__/
*.pyc

# Mac
.DS_Store

# APK
apps/android/*.apk

# Local sensitive test data
*.local.yaml
*.secret.yaml
.env

# Local sensitive test data
node_modules/
```

---

## Findings

### Critical

| # | Finding | Evidence | Recommendation |
|---|---------|----------|----------------|
| 1 | `.DS_Store` is TRACKED in git despite `.gitignore` line 16 | `git ls-files .DS_Store` → `.DS_Store` | `git rm --cached .DS_Store` — **merge blocker** |
| 2 | `testdata/.DS_Store` is tracked | `git ls-files testdata/.DS_Store` | `git rm --cached testdata/.DS_Store` |
| 3 | Root robot outputs present in working tree | `ls log.html output.xml report.html` → 3 files, ~765KB total | Delete from working tree; `.gitignore` already covers them |

### High

| # | Finding | Evidence | Recommendation |
|---|---------|----------|----------------|
| 4 | `reports/` is gitignored BUT `reports/investigation/consent/` contains tracked `.robot` files | `reports/investigation/consent/test_skip_and_adb_ready.robot`, `verify_landing_fix.robot` | Tests should not live under `reports/` (gitignored). Move to `tests/` or they'll be lost. |
| 5 | 130 files untracked in working tree | 63 investigation + 67 frida | Classify (see `07_investigation_promotion.md`) then track or gitignore |
| 6 | `libraries/__pycache__/` present in working tree | `ls libraries/` | Clean; already gitignored |

### Medium

| # | Finding | Evidence | Recommendation |
|---|---------|----------|----------------|
| 7 | Duplicate comment block in `.gitignore` | Lines 21 and 26 both say "Local sensitive test data" | Remove duplicate comment |
| 8 | `node_modules/` has generic comment "Local sensitive test data" | Line 26 | Should be "# Dependencies" |
| 9 | `.opencode/` untracked | `git status` → `?? .opencode/` | Track or gitignore |
| 10 | `apps/` untracked (contains APK + mock images) | `git status` → `?? apps/` | APK is gitignored; track mock image directory if needed |
| 11 | `opencode.json`, `package.json`, `package-lock.json` untracked | `git status` → `??` | Track — project config files |
| 12 | `skills-lock.json` tracked but purpose unclear | Root-level file | Document or remove |

### Low

| # | Finding | Evidence | Recommendation |
|---|---------|----------|----------------|
| 13 | No `.gitignore` entry for `*.log` | API capture logs could leak | Add `*.log` to be safe |
| 14 | No `.gitignore` entry for `*.png` outside `reports/` | Screenshots in investigation | Acceptable — `reports/` covers most |
| 15 | No `.gitignore` entry for IDE files: `.opencode/` | Present | Add `.opencode/` if local-only |

---

## Generated Files Audit

| Location | File Type | Gitignored? | Present? | Action |
|----------|-----------|-------------|----------|--------|
| Root | `log.html`, `output.xml`, `report.html` | Yes | Yes | Delete from working tree |
| `reports/` | All outputs | Yes | Yes (many) | OK — gitignored |
| `libraries/__pycache__/` | `.pyc` | Yes | Yes | Clean |
| `tools/performance/__pycache__/` | `.pyc` | Yes | Yes | Clean |
| `apps/android/` | APK | Yes | Unknown | OK |

## Sensitive Data in Generated Files

| Risk | Evidence | Recommendation |
|------|----------|----------------|
| Root `log.html`/`output.xml` may contain PII from test runs | Tests use `ntb.local.yaml` with real citizen ID + phone | Delete root outputs before any commit; never commit `reports/` |
| `reports/investigation/` XML files contain app page source | May include citizen ID field values | Already gitignored; verify no PII in tracked files |

---

## Recommended `.gitignore` Additions

```gitignore
# Robot Framework (existing — keep)
reports/
output.xml
log.html
report.html

# Logs
*.log

# Opencode local config (if local-only)
.opencode/

# Investigation working artifacts (if not tracking)
# tests/investigation/
# tools/frida/
```

## Recommendation

C2 should:
1. `git rm --cached .DS_Store testdata/.DS_Store` — **merge blocker**.
2. Delete root `log.html`, `output.xml`, `report.html` from working tree.
3. Move `reports/investigation/consent/*.robot` to `tests/`.
4. Track `opencode.json`, `package.json`, `package-lock.json`.
5. Clean `__pycache__/` directories.
6. Add `*.log` to `.gitignore`.
7. Fix duplicate comment block.
