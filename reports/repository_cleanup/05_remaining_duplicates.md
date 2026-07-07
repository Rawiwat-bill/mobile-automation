# 05 — Remaining Duplicates

> Duplicate keywords that remain after C3.2, with conditions for future merge.

---

## Summary

| Duplicate | Class | Reason Not Merged | Future Merge Condition |
|-----------|-------|--------------------|-----------------------|
| Allow Android Permission If Visible | BENCHMARK ISOLATION | Benchmark has `Record Appium Action` measurement calls; different locator | Refactor benchmark measurement to decorator/wrapper pattern |
| Landing Screen Should Be Visible | BENCHMARK ISOLATION | Production has 60s built-in retry; benchmark has none | Extract retry as parameter |
| Field Should Be Blurred / Profile Fields Should Be Blurred | INTENTIONAL DUPLICATE | Different signatures (generic vs page-specific, 1 field vs 3 fields) | Page Object refactor — production calls generic 3x |

---

## Detailed Future Merge Conditions

### Allow Android Permission If Visible

**Current state:**
- Production: click + activate (no measurement)
- Benchmark: click + record + activate + record

**Merge path (future):**
1. Create a shared `Allow Android Permission If Visible` in `app_keywords.resource` that takes optional `${record_actions}=${FALSE}` parameter.
2. When `${record_actions}` is true, call `Record Appium Action` after click and activate.
3. Benchmark calls with `${record_actions}=${TRUE}`.
4. **Blocker:** This changes the keyword signature, which may affect all callers. Requires careful migration.

**Risk:** Medium — adding a parameter is backward-compatible if defaulted, but benchmark timing could be affected by the conditional logic.

---

### Landing Screen Should Be Visible

**Current state:**
- Production: 60s retry built in via `Wait Until Keyword Succeeds`
- Benchmark: instant check, no retry

**Merge path (future):**
1. Create a shared keyword with `${timeout}=0s` parameter.
2. When timeout > 0, wrap in `Wait Until Keyword Succeeds`.
3. When timeout = 0, do instant check.
4. Production calls with `${timeout}=${LANDING_TIMEOUT}`.
5. Benchmark calls with `${timeout}=0s`.

**Risk:** Low — parameterized retry is a clean pattern. But benchmark caller already wraps in retry, so double-retry must be avoided.

---

### Field Should Be Blurred / Profile Fields Should Be Blurred

**Current state:**
- Benchmark: `Field Should Be Blurred` — generic, takes `${locator}`, checks 1 field
- Production: `Profile Fields Should Be Blurred` — page-specific, checks 3 fields

**Merge path (future):**
1. Move `Field Should Be Blurred` to a shared keywords resource.
2. Refactor `Profile Fields Should Be Blurred` to call it 3 times.
3. **Blocker:** This is a Page Object modification — explicitly out of scope for C3.

**Risk:** Low — the refactor is straightforward, but it touches a Page Object file.

---

## Recommendation

These duplicates are **acceptable technical debt**. They exist for legitimate
reasons (measurement, timing, page-specificity) and cannot be merged without
either:
- Changing runtime behavior (prohibited)
- Modifying Page Objects (out of scope)
- Refactoring benchmark measurement architecture (future sprint)

**No action recommended for C3.** Revisit after benchmark measurement
refactoring or Page Object redesign.
