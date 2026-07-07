# REV-001: Consent Scrollbar Drag — Production Readiness Review

## Summary

| Attribute | Value |
|-----------|-------|
| Change under review | Promote scrollbar drag strategy from benchmark layer to production automation |
| Current production keyword | `Scroll Down Consent Terms` in `consent_screen_page.resource` |
| Benchmark evidence | reports/benchmark/dashboard.md |
| Decision record | *(deleted — DEC-001 removed in cleanup)* |
| Device tested | Android Emulator API 34, 1080×2400 |
| **Recommendation** | **Approved with conditions** |

---

## Evidence from Benchmark / Dashboard

### Performance Improvement

| Metric | Current Production (Hardcoded) | Scrollbar Drag (1060_300) | Improvement |
|--------|:-----------------------------:|:-------------------------:|:-----------:|
| Scroll time | 12.071s | 0.821s | **-93%** |
| Total time (benchmark) | 29.627s | 17.861s | **-40%** |
| ADB calls per scroll | 4–6 | 1 | **-75–83%** |

*(Source: `reports/benchmark/dashboard.md`, Strategies 1 vs 3)*

### Strategy Ranking (fastest → slowest)

| Rank | Strategy | Total (s) | Scroll (s) | ADB |
|------|----------|-----------|------------|:---:|
| 1 | `scrollbar_1060_300` | 17.861 | 0.821 | 1 |
| 2 | `dynamic` | 27.650 | 9.659 | 6 |
| 3 | `hardcoded` | 29.627 | 12.071 | 4 |

*(Source: `reports/benchmark/dashboard.md` §Latest Benchmark Summary)*

### Spread
39.7% improvement from worst (`hardcoded`) to best (`scrollbar_1060_300`).

### Key Evidence
- Benchmark tested 6 strategies across 4 scrollbar coordinate variants
- `accessibility_id=Accept` was confirmed visible and clickable after every scrollbar drag trial
- `Tap Consent Accept Benchmark With Evidence` keyword confirmed Accept availability via screenshot evidence on every trial
- No failures or timeouts recorded for any scrollbar drag test case
- H₁ accepted (H₀ rejected): scrollbar drag reduces scroll time by >90% while maintaining Accept availability

---

## Production Impact Analysis

### Current Production Flow

```
Tap Consent Accept Button
  → Wait Until Consent Screen Is Displayed
  → Scroll Down Consent Terms
      → FOR 1..12: adb swipe 540,1950 → 540,350, 50ms
      → Check "I have read and understood" every 2 swipes (starts at swipe 4)
      → BREAK on text match
  → Wait Until Element Is Visible  ${CONSENT_ACCEPT_BUTTON}  3s
  → Click ${CONSENT_ACCEPT_BUTTON}
  → Verify transition (page does not contain CONSENT_TITLE_TEXT)
```

### Proposed Production Flow

```
Tap Consent Accept Button
  → Wait Until Consent Screen Is Displayed
  → Scroll Down Consent Terms (REFACTORED)
      → Single adb swipe {x},450 → {x},1900, 150ms  (x = calculated from screen width)
      → Wait Until Element Is Visible  ${CONSENT_ACCEPT_BUTTON}  3s
  → Click ${CONSENT_ACCEPT_BUTTON}
  → Verify transition
```

### Impact Summary

| Aspect | Impact | Detail |
|--------|--------|--------|
| Test execution time | **Reduced** | -40% total (29.6s → ~17.9s) per consent interaction |
| ADB commands | **Reduced** | 12× swipes → 1× swipe |
| End detection reliability | **Improved** | `Element Should Be Visible` on `accessibility_id=Accept` is more direct than text-in-webview |
| CI pipeline time | **Reduced** | Each test that reaches consent saves ~10–12s |
| Code complexity | **Reduced** | No loop, no counter variables, no interval math |
| Parse/readability | **Improved** | Single swipe is self-documenting |
| Risk of regression | **Low** | Accept button detection is the same locator production already uses |

### Diff Estimate

If approved, the change to `Scroll Down Consent Terms` would modify approximately **15 lines**: replace the FOR loop + counter logic + text check with a single swipe + element wait.

---

## Security Review

| Check | Status | Evidence |
|-------|--------|----------|
| ADB shell usage unchanged | ✅ | Production already uses `Run Process  adb  shell  input  swipe` |
| Same ADB command family | ✅ | `input swipe` — no new shell commands introduced |
| No credential/PII exposure | ✅ | No data passed in swipe commands |
| No relaxed-security escalation | ✅ | No new security modes required beyond current `--relaxed-security` |
| No app package/activity changes | ✅ | No changes to app lifecycle |

**Conclusion:** No new security surface introduced. The change reduces the number of ADB calls (12→1), which marginally reduces the ADB attack surface.

---

## Device / Resolution Risk

### Tested Configuration
- **1 device:** Android Emulator (API 34), 1080×2400 resolution
- **Scrollbar x tested:** 1030, 1040, 1060 — all produced Accept visibility
- **Duration tested:** 150ms, 300ms — both sufficient

### Untested Configurations

| Variation | Risk | Required Before Production |
|-----------|------|---------------------------|
| Physical devices (Samsung, Xiaomi, OPPO, etc.) | High — scrollbar position varies by screen density and Android skin | Validate on ≥3 physical Android devices |
| Different resolutions (720p, 1440p, foldables) | High — x=1040 is specific to 1080×2400 | Calculate x from `display.width` or scrollbar element bounds |
| Android versions 10–14 | Medium — scrollbar rendering differs across API levels | Validate on API 29, 31, 33, 34 |
| Tablets | Medium — scrollbar position differs | Not a near-term target; document as known limitation |
| iOS | High — ADB does not exist on iOS | Requires separate touch-action strategy (not scoped) |

### Recommended Dynamic Calculation

```robot
${screen_width}=    Get Window Width
${scrollbar_x}=    Evaluate    ${screen_width} - 40
```

Or, if the scrollbar element has a resource-id:

```robot
${scrollbar_bounds}=    Get Element Rect    ${CONSENT_SCROLLBAR}
${scrollbar_x}=    Evaluate    ${scrollbar_bounds['x']} + (${scrollbar_bounds['width']} / 2)
```

---

## Locator / Readiness Signal Review

### Current Signals

| Locator | Type | Used For | Stable? |
|---------|------|----------|---------|
| `${CONSENT_TITLE_TEXT}` | `xpath=//*[@text="Terms and Conditions"]` | Screen detection | Yes — language-dependent? |
| `${CONSENT_WEBVIEW}` | `xpath=//android.webkit.WebView` | Screen detection | Yes |
| `${CONSENT_ACCEPT_BUTTON}` | `accessibility_id=Accept` | Accept click | **Yes — stable, screen-specific** |
| `${CONSENT_END_TEXT}` | `I have read and understood` | Scroll-end signal | **No — fails after scrollbar drag** |

### Proposed Change

| Signal | Current | Proposed | Reason |
|--------|---------|----------|--------|
| Scroll-end detection | `Page Should Contain Text "${CONSENT_END_TEXT}"` | `Element Should Be Visible ${CONSENT_ACCEPT_BUTTON}` | Text is not rendered after scrollbar drag (RN render behavior) |

**The production locator `${CONSENT_ACCEPT_BUTTON}` (accessibility_id=Accept) is already defined** in `locators/android/onboarding/consent_screen_locators.resource` and used by `Tap Consent Accept Button`. The benchmark layer uses an equivalent locator (`${BENCHMARK_CONSENT_ACCEPT}` = `accessibility_id=Accept`). No new locator is needed.

### Risks to Readiness Signal

| Risk | Assessment |
|------|------------|
| `accessibility_id=Accept` changes upstream | Low — accessibility ids are stable in RN |
| Multiple elements match `accessibility_id=Accept` | Low — only one Accept button on consent screen |
| Accept button not rendered after single swipe | Very low — passed 100% in benchmark trials |
| Accept button disabled (not clickable) | Low — benchmark confirmed clickable via `Tap Consent Accept Benchmark With Evidence` |

---

## Rollback Plan

| Scenario | Rollback Action | Impact Duration |
|----------|----------------|-----------------|
| Scrollbar position wrong on device X | Fall back to content swipe by restoring `CONSENT_MAX_SWIPES` variable | One pipeline run |
| Accept button not visible after swipe | `Wait Until Element Is Visible` times out (current 3s → 10s max); `Scroll Down Consent Terms` falls back to content swipe | One pipeline run |
| ADB swipe fails on device | Error surfaces immediately; CI catches; revert commit | One commit revert |
| RN update changes scroll behavior | Revert to content swipe; investigate new RN scroll parameters | One sprint |

The production change is **easily revertible** — it affects only one keyword body (`Scroll Down Consent Terms`) and no data, locators, or test structure.

---

## Required Code Changes if Approved

### 1. `resources/pages/onboarding/consent_screen_page.resource`

**Replace** the `Scroll Down Consent Terms` keyword body:

```robot
Scroll Down Consent Terms
    ${screen_width}=    Get Window Width
    ${scrollbar_x}=    Evaluate    ${screen_width} - 40
    Execute Adb Shell    input    swipe    ${scrollbar_x}    450    ${scrollbar_x}    1900    150
    ${accept_visible}=    Run Keyword And Return Status
    ...    Wait Until Element Is Visible    ${CONSENT_ACCEPT_BUTTON}    10s
    IF    not ${accept_visible}
        Log    Scrollbar drag did not reveal Accept button; falling back to content swipe.    WARN
        # Fallback: content swipe loop (existing logic)
        FOR    ${index}    IN RANGE    ${CONSENT_MAX_SWIPES}
            ...
        END
    END
```

**Also remove** these variables no longer needed:
- `${CONSENT_SWIPE_COUNT}`
- `${CONSENT_END_CHECK_COUNT}`
- `${CONSENT_FIRST_END_CHECK_AT}`
- `${CONSENT_END_CHECK_INTERVAL}`

**Keep** these variables still used:
- `${CONSENT_TIMEOUT}` — used by `Wait Until Consent Screen Is Displayed`
- `${CONSENT_END_TEXT}` — could remain for fallback path
- `${CONSENT_MAX_SWIPES}` — could remain for fallback path

### 2. `resources/pages/onboarding/consent_screen_page.resource` — `Tap Consent Accept Button`

**Replace** the end-detection signal inside the function:

```robot
Wait Until Element Is Visible    ${CONSENT_ACCEPT_BUTTON}    10s
```

(The current code already has this after `Scroll Down Consent Terms`. The change is that `Scroll Down Consent Terms` now produces the Accept button directly, so the wait timeout can be reduced from 3s to something appropriate.)

### 3. Variable scope changes

Remove or deprecate these `*** Variables ***`:
- `${CONSENT_SWIPE_COUNT}`
- `${CONSENT_END_CHECK_COUNT}`
- `${CONSENT_FIRST_END_CHECK_AT}`
- `${CONSENT_END_CHECK_INTERVAL}`

These are only used by the current FOR-loop implementation.

---

## Validation Checklist

- [ ] **Dynamic coordinate calculation**: `Get Window Width` → `evaluate x - 40` tested on ≥3 resolutions
- [ ] **`accessibility_id=Accept` detection after scrollbar drag**: confirmed on physical devices
- [ ] **Fallback content swipe works**: when scrollbar drag fails, `Page Should Contain Text` flow still operates
- [ ] **Transition verification passes**: page transitions off consent screen after Accept tap
- [ ] **Dryrun passes**: `python3 -m robot --dryrun tests/android/onboarding/ntb_onboarding.robot`
- [ ] **Regression suite passes**: full onboarding flow with scrollbar drag on ≥1 physical device
- [ ] **iOS check**: confirm `Run Process  adb` guarded or skipped on iOS
- [ ] **Security review**: passed (this review)
- [ ] **Performance review**: benchmark evidence confirms 93% scroll time reduction
- [ ] **Review-agent approval**: required before merging

---

## Final Recommendation

## ✅ Approved with Conditions

The benchmark evidence is conclusive. The scrollbar drag strategy:
- Reduces scroll time by **93%** (12.07s → 0.82s)
- Maintains **100% Accept-button availability** across all trials
- Uses **1 ADB call instead of 12**
- Eliminates complex counter/math/interval logic

### Conditions

Before the production keyword is modified, the following must be satisfied:

| # | Condition | Owner | Evidence Required |
|---|-----------|-------|-------------------|
| 1 | **Cross-device validation** on ≥3 physical Android devices (Samsung, Xiaomi, OPPO or similar) with ≥2 different resolutions | Review-agent | Validation report + screenshots |
| 2 | **Dynamic scrollbar x calculation** from `Get Window Width` or element bounds — not hardcoded 1040 | Review-agent | Code review |
| 3 | **Content swipe fallback** — if scrollbar drag does not reveal Accept within timeout, fall back to existing FOR-loop | Review-agent | Code review |
| 4 | **`CONSENT_END_TEXT` kept** as fallback path variable | Review-agent | Code review |
| 5 | **Dryrun + full onboarding regression** on physical device before merge | Review-agent | CI pipeline green |
| 6 | **Android-only guard** — ensure no ADB call on iOS targets | Security-review-agent | Guard condition in code |
| 7 | **Performance re-benchmark** after production change — confirm improvement holds in production context | Performance-agent | Before/after in dashboard |

### Rationale

The benchmark data is strong enough to justify the change, but the evidence base is limited to **one device/resolution**. The production risk is low (easily revertible, single keyword body), but the conditions ensure the change works on the real device matrix before it becomes the default path for all test runs.

### Blockers if Conditions Not Met

- **Cross-device failure risk** — x=1040 may not work on different screen widths
- **No fallback** — if scrollbar drag fails silently, onboarding tests would time out at the profile screen
- **iOS ADB call** — `Run Process  adb` on iOS will fail; must be guarded

---

## Review Metadata

| Field | Value |
|-------|-------|
| Review ID | REV-001 |
| Date | 2026-06-26 |
| Author | review-agent |
| Files inspected | `consent_screen_page.resource`, `consent_screen_locators.resource`, `consent_scroll_strategies.resource`, `dashboard.md` |
| Production files modified | **None** (this review only) |
| Benchmark files modified | **None** (this review only) |
| Next step | Hand off to performance-agent for cross-device validation |
