# Ponytail Repository Audit

> Audit only. No files modified. Ranked biggest cut first.
> Scope: over-engineering, duplication, dead code, complexity.

---

## Findings

### Critical

1. **delete** `tests/investigation/` — 63 untracked one-off investigation scripts, 0 git-tracked, not referenced by CI or production suites. Replacement: archive to `reports/investigation/archive/` or gitignore. [tests/investigation/]
2. **delete** `tools/frida/` — 67 untracked one-off Frida scripts, 0 git-tracked. Replacement: archive or gitignore if still needed for OCR/face milestones. [tools/frida/]
3. **delete** `.DS_Store` tracked in git despite `.gitignore` line 16. Replacement: `git rm --cached .DS_Store`. [.DS_Store]

### High

4. **shrink** Benchmark duplicates 17 production locators with `BENCHMARK_` prefix instead of importing. Replacement: import `profile_screen_locators.resource` + `landing_screen_locators.resource` + `consent_screen_locators.resource`, alias if isolation needed. [resources/benchmark/benchmark_base.resource:19-36]
5. **shrink** `Allow Android Permission If Visible` duplicated in app_keywords + benchmark_base (near-identical). Replacement: import from app_keywords. [resources/app/app_keywords.resource:25, resources/benchmark/benchmark_base.resource:60]
6. **shrink** `Landing Screen Should Be Visible` duplicated in landing_screen_page + benchmark_base (different impls). Replacement: import from landing_screen_page. [resources/pages/onboarding/landing_screen_page.resource:14, resources/benchmark/benchmark_base.resource:80]
7. **shrink** Blur coordinates duplicated: `BLUR_AFTER_*_Y` (benchmark) = `PROFILE_BLUR_AFTER_*_Y` (production), same values 780/1095/1600. Replacement: single source. [resources/benchmark/benchmark_strategies.resource:10-12, resources/pages/onboarding/profile_screen_page.resource:15-17]
8. **shrink** App package/activity hardcoded in 3 places. Replacement: single `${APP_PACKAGE}` / `${APP_ACTIVITY}` in app_keywords, import everywhere. [app_keywords.resource:10, benchmark_base.resource:11-12, api_capture_keywords.resource:7]
9. **shrink** `month_map` dict duplicated 3x (profile_screen_page + 2x benchmark_strategies). Replacement: extract to shared keyword or variables file. [profile_screen_page.resource:121, benchmark_strategies.resource:84, benchmark_strategies.resource:289]
10. **shrink** DOB picker select logic duplicated: `Select DOB Picker Value` (production) vs `Select Benchmark Picker Value` (benchmark) — same algorithm. Replacement: shared keyword with strategy parameter. [profile_screen_page.resource:205, benchmark_strategies.resource:238]

### Medium

11. **delete** `onboarding_keywords.resource` — orphaned, 0 importers, 1 keyword `Accept Terms And Conditions` that duplicates consent_screen_page (Wait + Tap). Replacement: nothing. [resources/keywords/onboarding_keywords.resource]
12. **delete** `ntb_keywords.resource` / `etb_keywords.resource` — placeholder-only, single `Log` keyword each, no real implementation. Replacement: recreate when milestone work starts (YAGNI now). [resources/keywords/ntb_keywords.resource, etb_keywords.resource]
13. **delete** `configs/` — all 3 YAML files (dev.yaml, emulator.yaml, real_device.yaml) are 0 bytes. Empty scaffold. Replacement: populate or remove. [configs/]
14. **delete** `etb.local.yaml` — 0 bytes. Replacement: populate when ETB milestone starts. [testdata/onboarding/etb.local.yaml]
15. **delete** `requirements.txt` — 0 bytes. No pinned Python deps (robotframework, robotframework-appiumlibrary, pyyaml). Replacement: pin actual deps. [requirements.txt]
16. **delete** Root robot outputs `log.html`, `output.xml`, `report.html` present in working tree (gitignored but not cleaned). Replacement: delete, rely on `reports/`. [log.html, output.xml, report.html]
17. **yagni** `tests/android/onboarding/ntb_onboarding.robot` duplicates `tests/android/ntb/ntb_flow.robot` — both call `Complete Common Onboarding` with `ntb.local.yaml`. Replacement: keep one. [tests/android/onboarding/ntb_onboarding.robot, tests/android/ntb/ntb_flow.robot]
18. **yagni** `tests/android/common/onboarding_common.robot` ≈ `tests/android/common/identity_validation.robot` — both call `Complete Common Onboarding` with `ntb.example.yaml`; identity_validation adds 1 log line. Replacement: merge or differentiate with tags. [tests/android/common/]

### Low

19. **yagni** `tests/demo/live_demo.robot` — hardcoded device UDID `48ZYD25C01422768` + coordinate taps, throwaway demo. Replacement: remove or move to `reports/investigation/`. [tests/demo/live_demo.robot]
20. **yagni** `.agents/` directory empty — `docs/Architecture.md:62-72` describes 8+ agent files (qa-orchestrator.md, evidence-agent.md, etc.) that don't exist. Replacement: create files or fix doc. [.agents/, docs/Architecture.md]
21. **shrink** `config_loader.py` is 5 lines wrapping `yaml.safe_load`. Acceptable as Robot library bridge but could be a one-line `Evaluate yaml.safe_load(open(path).read())` inline. Keep if used widely. [libraries/config_loader.py]

---

## Summary

```
net: -17 duplicate locator vars, -8 duplicate keyword blocks, -3 placeholder files,
     -3 empty config files, -1 orphaned resource, -1 tracked .DS_Store possible.
     130 untracked investigation/frida artifacts to classify (archive or gitignore).
```

The production automation core (onboarding_common → page objects → locators) is lean and
well-structured. The bloat is in: (a) benchmark isolation that duplicates instead of imports,
(b) untracked investigation artifacts, (c) empty scaffolding files, (d) placeholder resources
for unstarted milestones.
