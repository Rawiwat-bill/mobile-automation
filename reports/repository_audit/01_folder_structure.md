# 01 — Folder Structure Review

## Current Structure

```
BBL/
├── .agents/                    # EMPTY — Architecture.md describes 8+ agents
├── .opencode/                  # Opencode config (untracked)
├── AGENTS.md                   # Master agent policy
├── SKILLS.md                   # Skill inventory
├── PROJECT_MATURITY.md         # Maturity assessment
├── README.md
├── opencode.json               # Ponytail plugin config
├── package.json                # Ponytail deps only
├── requirements.txt            # EMPTY (0 bytes)
├── skills-lock.json
├── apps/android/               # APK storage (gitignored)
├── configs/
│   ├── devices/                # emulator.yaml (0 bytes), real_device.yaml (0 bytes)
│   └── env/                    # dev.yaml (0 bytes)
├── docs/
│   ├── Architecture.md         # Describes .agents/ files that don't exist
│   ├── principles/
│   ├── decisions/ADR-*.md
│   ├── architecture/           # Untracked
│   ├── knowledge/              # Untracked
│   ├── research/               # Untracked
│   └── reviews/                # Untracked
├── knowledge/                  # Well-organized: *.md, playbooks/, patterns/, profile/
├── libraries/
│   ├── config_loader.py        # 5-line YAML wrapper
│   └── api_log_redactor.py     # Untracked
├── locators/android/onboarding/  # 7 locator files, clean
├── resources/
│   ├── app/app_keywords.resource
│   ├── benchmark/              # 3 files (untracked)
│   ├── keywords/               # 8 keyword files
│   └── pages/onboarding/       # 7 page files
├── testdata/onboarding/        # 5 YAML files
├── tests/
│   ├── android/                # 6 production tests
│   ├── benchmark/              # 3 benchmark tests (untracked)
│   ├── demo/                   # 1 demo test (untracked)
│   └── investigation/          # 63 investigation tests (untracked)
├── tools/
│   ├── ci/                     # 1 shell script
│   ├── emulator/               # 3 Python scripts
│   ├── frida/                  # 67 JS scripts (untracked)
│   └── performance/            # 5 files
├── log.html                    # Robot output (gitignored, present)
├── output.xml                  # Robot output (gitignored, present)
└── report.html                 # Robot output (gitignored, present)
```

## Findings

### Critical

| # | Finding | Evidence | Recommendation |
|---|---------|----------|----------------|
| 1 | `.agents/` is empty but `Architecture.md:62-72` lists 8+ agent files | `find .agents -type f` → 0 results | Create agent files OR correct Architecture.md to match reality |
| 2 | `configs/` all 3 files are 0 bytes | `wc -c configs/**/*.yaml` → 0 | Populate with DEV/SIT/UAT + device configs, or remove scaffold |
| 3 | `tests/investigation/` has 63 untracked files mixed with production tests | `git ls-files tests/investigation/` → 0 | Move to `tests/_investigation/` or `reports/investigation/scripts/` to separate from production |

### High

| # | Finding | Evidence | Recommendation |
|---|---------|----------|----------------|
| 4 | `tools/frida/` has 67 untracked scripts with no classification | `git ls-files tools/frida/` → 0 | Subfolder by milestone: `tools/frida/ocr/`, `tools/frida/face/`, `tools/frida/debug/` |
| 5 | Root-level robot outputs pollute project root | `ls log.html output.xml report.html` → present | Delete; `.gitignore` already covers them |
| 6 | `docs/` has 4 untracked subdirectories (architecture/, knowledge/, research/, reviews/) | `git status --porcelain` → `??` for each | Track or gitignore — currently in limbo |

### Medium

| # | Finding | Evidence | Recommendation |
|---|---------|----------|----------------|
| 7 | `tests/android/onboarding/` and `tests/android/ntb/` both contain NTB onboarding tests | `ntb_onboarding.robot` ≈ `ntb_flow.robot` | Consolidate to one location |
| 8 | `libraries/__pycache__/` present | `ls libraries/` → `__pycache__/` | Already gitignored; clean from working tree |
| 9 | No iOS locator/test structure despite AGENTS.md mentioning "iOS where needed" | `locators/` has only `android/` | Acceptable for Android-first; document as future |

## What's Good

- `locators/android/onboarding/` — clean 1:1 mapping to page resources
- `resources/pages/onboarding/` — consistent Page Object naming
- `knowledge/` — well-structured with playbooks/ and patterns/
- `testdata/onboarding/` — example + local separation is correct
- `tools/` — logical subdivision (ci, emulator, frida, performance)

## Recommended Structure (for C2)

```
tests/
├── android/          # Production regression (tracked)
├── benchmark/        # Reusable benchmarks (track)
├── health/           # Health checks (track)
└── _investigation/   # One-off scripts (gitignore or archive)
tools/
├── frida/
│   ├── ocr/          # Milestone 3
│   ├── face/         # Milestone 4
│   └── debug/        # General debugging
└── ...
configs/
├── env/
│   ├── dev.yaml      # Populate
│   ├── sit.yaml      # Add
│   └── uat.yaml      # Add
└── devices/
    ├── emulator.yaml # Populate
    └── real_device.yaml  # Populate
```
