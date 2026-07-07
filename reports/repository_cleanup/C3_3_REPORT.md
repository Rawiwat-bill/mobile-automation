# Sprint C3.3 — Repository Architecture Cleanup Report

> **Baseline:** baseline-c2 + C3.1 + C3.2 + C2.5
> **Date:** 2026-07-07
> **Scope:** Improve resource responsibility placement. No runtime changes.

---

## Executive Summary

Reviewed all 7 Page Objects, 8 keyword resources, 2 Python libraries, and the
folder structure. Found the architecture already sound after C3.1 constants
cleanup. One safe move identified and executed.

### What was done

Moved 3 generic interaction helpers from `benchmark_strategies.resource` to
`benchmark_base.resource`:
- `Tap By Coordinates`
- `Field Should Be Blurred`
- `Enter Digits By Keycodes`

**Why:** benchmark_strategies already imports benchmark_base. Moving primitives
there improves responsibility separation (base = primitives, strategies = composed
flows) with zero new imports and zero behavior change.

### What was NOT done (and why)

- Profile page generic helpers (`Normalize Digits`, `Input Text Field`, `Verify Field Value`):
  Moving to a shared resource would ADD an import to profile_screen_page — violates
  "imports become simpler" rule. Recommend only.
- Creating `resources/shared/` directory: No moves qualify under the sprint rules.
  Premature structure without content.
- Python library expansion: Current Robot/Python split is correct.

### Validation

| Suite | Result |
|-------|--------|
| `tests/android/` | 6/6 passed |
| `tests/benchmark/` | 14/14 passed |
| `tests/health/` | 8/8 passed |

### Changed files

| File | Change |
|------|--------|
| `resources/benchmark/benchmark_base.resource` | +3 keywords (moved from strategies) |
| `resources/benchmark/benchmark_strategies.resource` | -3 keywords (moved to base) |

**Total: 2 files modified. 0 new files. 0 behavior changes.**
