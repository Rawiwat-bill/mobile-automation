# 03 — Shared Utility Review

> Should utility logic live in resources/shared/ or libraries/?

---

## Current Python Libraries

| File | Lines | Responsibility | Correct placement? |
|------|-------|----------------|-------------------|
| `libraries/config_loader.py` | 5 | YAML file loading (`yaml.safe_load` wrapper) | Yes — Robot needs a Library bridge to PyYAML |
| `libraries/api_log_redactor.py` | — | PII redaction in logcat captures | Yes — complex string processing belongs in Python |
| `resources/benchmark/BenchmarkMetrics.py` | — | Benchmark measurement tracking (timing, phase recording) | Yes — state management and timing in Python |

---

## Robot vs Python Decision Matrix

| Logic type | Should be | Reasoning |
|------------|-----------|-----------|
| Appium interaction (tap, swipe, input) | Robot | Uses AppiumLibrary keywords directly |
| ADB shell execution | Robot | Uses `Execute Adb Shell` from AppiumLibrary |
| String manipulation (normalize, redact) | Python | Complex regex/string ops are cleaner in Python |
| File I/O (read/write/parse) | Python | `os`, `json` modules are more robust |
| State tracking (timing, checkpoints) | Python | State management is cleaner in Python classes |
| Flow orchestration (onboarding steps) | Robot | Readable BDD-style step sequence |
| Report generation (JSON/MD) | Python or Robot | Either works; current Robot impl is adequate |

---

## `resources/shared/` Directory Assessment

### Should it be created?

**Not yet.** There are only 3 candidate keywords for a shared resource:
- `Normalize Digits` (1 line)
- `Input Text Field` (6 lines)
- `Verify Field Value` (6 lines)

Total: 13 lines. Creating a directory + resource file + import for 13 lines
adds more overhead than it saves. Wait until more generic helpers accumulate
(e.g., when OCR, Face, or PIN milestones add page objects that need the same
helpers).

### When to create it

Create `resources/shared/input_helpers.resource` when:
- 2+ page objects need `Normalize Digits` or `Input Text Field`
- Total shared keyword lines exceed ~30
- A new milestone (OCR, Face, PIN) adds a page object with input fields

### Recommended structure (future)

```
resources/
├── app/
│   ├── app_constants.resource    # Constants only
│   └── app_keywords.resource     # App lifecycle, permission, debug
├── shared/                        # Create when justified
│   └── input_helpers.resource     # Normalize Digits, Input Text Field, Verify Field Value
├── keywords/
│   ├── onboarding_common.resource
│   ├── health_check_keywords.resource
│   ├── dob_stability_keywords.resource
│   ├── api_capture_keywords.resource
│   └── scroll_keywords.resource
├── pages/onboarding/
│   └── (7 page files)
└── benchmark/
    ├── benchmark_base.resource    # Lifecycle + primitives (after C3.3)
    ├── benchmark_strategies.resource  # Strategy executors only (after C3.3)
    ├── consent_scroll_strategies.resource
    └── BenchmarkMetrics.py
```

---

## Library Responsibility Recommendations

| Current location | Keyword/Logic | Recommendation |
|-----------------|---------------|----------------|
| `profile_screen_page.resource` | `Normalize Digits` | Move to `resources/shared/` when created. Not worth a Python library — it's a one-line regex. |
| `profile_screen_page.resource` | `Input Text Field` | Move to `resources/shared/` when created. Robot keyword is correct — uses AppiumLibrary's `Clear Text`, `Input Text`, `Get Text`. |
| `health_check_keywords.resource` | `Log Health Check Summary` (JSON+MD generation) | Could be Python for cleaner string handling. Currently 80+ lines of `Catenate` in Robot. **Recommend** future refactor to Python library. Not moved this sprint — out of scope. |
| `dob_stability_keywords.resource` | `Generate DOB Stability Report` | Same as above — JSON generation could be Python. **Recommend** future refactor. |

---

## Summary

| Question | Answer |
|----------|--------|
| Should Python libraries own more logic? | Only health check report generation (future) |
| Should `resources/shared/` be created? | Not yet — insufficient content (13 lines) |
| Is current Robot/Python split correct? | Yes — Appium interactions in Robot, string/file/state in Python |
| Any moves this sprint? | No — conditions not met for shared utility moves |
