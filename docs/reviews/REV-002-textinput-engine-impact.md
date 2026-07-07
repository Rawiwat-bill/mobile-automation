# REV-002: TextInput Engine — Production Impact Assessment

## Summary

| Attribute | Value |
|-----------|-------|
| Change under review | Migrate React Native `TextInput` fields from keycode-based entry to Appium `Input Text` |
| Current production keyword | `Enter Digits By Keycodes` in `profile_screen_page.resource` |
| Investigation evidence | Sprint 2.10, 2.10.1, 2.10.3 — `reports/investigation/input_value_verification/`, `input_inline_error/`, `cid_input_parity/` |
| Fields investigated | Citizen ID, Mobile Number, Date of Birth |
| **Recommendation** | **Approved — migrate Citizen ID and Mobile Number to Input Text. Keep Picker+Gesture engines unchanged.** |

---

## Impact Matrix

### Production Keywords

| # | Screen | Keyword | Current Method | Works? | Candidate | Safe to Replace | Risk | Evidence |
|---|--------|---------|---------------|:------:|-----------|:---------------:|------|----------|
| 1 | Profile — CID | `Input Citizen ID` | `Tap Profile Element Center` → `Enter Digits By Keycodes` → blur | ✅ Works | `Input Text` single call | **YES** | Low | Sprint 2.10.3: 4 experiments, formatted `123456` → `1-2345-6` exact match. `Get Text` verified. |
| 2 | Profile — Mobile | `Input Mobile Number` | `Enter Digits By Keycodes` + `Press Keycode 66` → fallback `Input Text Into Current Element` | ✅ Works | `Input Text` + IME handling | **YES** | Low | Sprint 2.10: `Input Text` injects `0812345678` → `081-234-5678`. Current implementation already uses `Input Text` as fallback (line 151). |
| 3 | Profile — Mobile | `Input Mobile Number` — `Press Keycode 66` | IME ENTER action after keycodes | ✅ Works | `Press Keycode 66` or `Hide Keyboard` | **KEEP** IME handling | Medium | `Press Keycode 66` is IME confirmation (Done/Next on keyboard). This may trigger field validation/dismissal. Need to verify whether Input Text alone dismisses keyboard or requires explicit IME action. |
| 4 | Profile — DOB | `Input Date Of Birth` | Picker: `Execute Adb Shell input swipe` + center text detection | ✅ Works | Keep existing Picker Engine | **NO** — Direct input not supported | None | Sprint 2.10: DOB field rejects `Input Text`. Picker interaction required. |
| 5 | Profile — DOB | `Try Direct DOB Input` | `Input Text` + `Execute Adb Shell input text` (fallback, gated by `DOB_TRY_DIRECT_INPUT`) | ❌ Fails | Keep as-is | **KEEP** (already gated) | None | Both direct text methods fail. Picker is the only reliable path. |
| 6 | Profile — Next Button | `Tap Profile Next Using Adb` | `Execute Adb Shell input tap` | ✅ Works | Keep | **NO** — Gesture, not text | None | RN gesture handling. Separate concern. |
| 7 | Profile — Next Button | `Tap Profile Next Button` | ADB tap + Appium tap fallback | ✅ Works | Keep | **NO** — Gesture, not text | None | RN gesture handling. Separate concern. |
| 8 | Profile — blur | `Wait Until Profile Fields Are Blurred` | `Get Element Attribute focused` check | ✅ Works | Keep | **NO** — verification only | None | Not an input method. |
| 9 | Profile — blur | `Tap Profile Blank Area` | Coordinate `Tap` with Y param | ✅ Works | Keep | **NO** — blur mechanism | None | Required for field blur after input. |

### Shared Keywords

| # | Keyword | Current Method | Used By | Safe to Replace | Risk | Notes |
|---|---------|---------------|---------|:---------------:|------|-------|
| 10 | `Enter Digits By Keycodes` | `Press Keycode` per digit | `Input Citizen ID`, `Enter Mobile Number By Keycodes`, Benchmark baselines | **YES** for TextInput fields | Low | Can be deprecated for TextInput. May still be needed for future PIN/OTP fields. |
| 11 | `Enter Mobile Number By Keycodes` | `Enter Digits By Keycodes` + `Press Keycode 66` | `Input Mobile Number` | **YES** | Low | Replace with `Input Text` + IME handling. |

### Benchmark Keywords (No Change Required)

| # | Keyword | Current Method | Change Required | Reason |
|---|---------|---------------|:---------------:|--------|
| 12 | `Run Citizen ID press_keycodes` | `Enter Digits By Keycodes` | **NO** | Benchmark intentionally tests multiple strategies. `press_keycodes` is a reference baseline. |
| 13 | `Run Mobile press_keycodes` | `Enter Digits By Keycodes` | **NO** | Same — benchmark baseline. |
| 14 | `Baseline Fill Citizen ID` | `Enter Digits By Keycodes` | **NO** | Benchmark filler uses production method at time of benchmark. Can be updated when production changes. |
| 15 | `Baseline Fill Mobile` | `Enter Digits By Keycodes` | **NO** | Same as above. |

---

## Special Investigation: Fields That Must NOT Be Replaced Blindly

### OTP / PIN / Secure Fields

| Concern | Found in Project? | Risk |
|---------|:-----------------:|------|
| OTP input | ❌ Not implemented | OTP screens are TBD (Milestone 3 — OCR, Milestone 5 — PIN). When implemented: OTP fields may be per-character input fields that REQUIRE keycode-style entry. `Input Text` on OTP fields could bypass per-character validation. |
| PIN setup | ❌ Not implemented | PIN fields are TBD (Milestone 5). PIN fields typically mask input; `Input Text` may not interact correctly with masked fields. |
| Password / Secure Text | ❌ Not implemented | No password fields exist. |
| Clipboard paste | ❌ Not used | No clipboard operations. Method D from Sprint 2.10.1 was removed due to no Appium keyword support. |

### IME Actions / Focus Movement

| Concern | Found in Project? | Impact |
|---------|:-----------------:|--------|
| `Press Keycode 66` (IME ENTER) | ✅ Used in `Enter Mobile Number By Keycodes` and `Input Mobile Number` | After mobile number input, `Press Keycode 66` confirms the keyboard (Done/Next action). When migrating to `Input Text`, need to verify whether the keyboard dismisses automatically or requires explicit IME action. |
| `Hide Keyboard` | ✅ Used in `Input Mobile Number` | Available as blur alternative. |
| Tab / Focus next | ❌ Not used | No sequential tab navigation between fields. |
| Keyboard navigation | ❌ Not used | Each field is tapped individually. |

**Conclusion: No safe-to-replace TextInput depends on keycodes for navigation or IME behavior.** The single `Press Keycode 66` usage in mobile entry is for keyboard confirmation, which can be handled via `Hide Keyboard` or left as-is.

---

## Migration Safety Summary

| Field | Current Method | New Method | Safe? | Migration Complexity |
|-------|---------------|-----------|:-----:|:--------------------:|
| Citizen ID | `Enter Digits By Keycodes` (13 keycodes) | `Input Text` (1 call) | ✅ **Safe** | Low — replace 1 keyword |
| Mobile Number | `Enter Digits By Keycodes` (10 keycodes) + `Press Keycode 66` | `Input Text` + IME handling | ✅ **Safe** | Low — replace 1 keyword, keep IME |
| Date of Birth | `Execute Adb Shell input swipe` (Picker) | Keep Picker Engine | ✅ **Already correct** | None |
| Next Button | `Execute Adb Shell input tap` | Keep Gesture Engine | ✅ **Already correct** | None |
| OTP / PIN | Not implemented | TBD — may need keycodes | N/A | N/A |

## Risk Assessment

| Risk | Probability | Impact | Mitigation |
|------|:-----------:|:------:|------------|
| `Input Text` fails on a future app build that changes TextInput behavior | Low | High | Keep `Enter Digits By Keycodes` as fallback. Run smoke tests after each app update. |
| IME keyboard confirmation differs between keycodes and `Input Text` | Medium | Low | Verify via benchmark. `Hide Keyboard` can replace `Press Keycode 66`. |
| Formatting differs between single-event and per-character input for edge cases | Very Low | Medium | Sprint 2.10.3 proved formatting is identical. RN formatting is stateless (reformats entire string per event). |
| Future TextInput fields (Name, Email) behave differently from CID/Mobile | Medium | Low | Test each new field independently before applying TextInput Engine pattern. |

## Files Requiring Modification (when implementation sprint begins)

| File | Change |
|------|--------|
| `resources/pages/onboarding/profile_screen_page.resource` | `Input Citizen ID`: replace `Enter Digits By Keycodes` with `Input Text`. `Input Mobile Number`: simplify, remove keycode fallback path. |
| `resources/benchmark/benchmark_strategies.resource` | Update `Baseline Fill Citizen ID` and `Baseline Fill Mobile` to use `Input Text` (when benchmark is next updated). |
