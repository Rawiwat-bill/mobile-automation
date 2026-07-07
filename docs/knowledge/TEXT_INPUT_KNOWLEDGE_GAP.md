# TextInput Knowledge Gap — Documents Requiring Revision

## Summary

Previous investigations (Milestone 2, Sprint 2.7–2.8) concluded that `Press Keycode` per digit was required for React Native text input. Sprint 2.10.3 proved this conclusion was incorrect for `TextInput` components. The original finding was valid only for **gesture** components (buttons, pickers), not for `TextInput` fields.

The following documents contain statements that merge or conflate these two concerns and require correction.

---

## Documents Requiring Revision

### 1. `knowledge/appium.md`

**Current text (line 21):**
> For text input, Appium `Input Text` (which uses `element.sendKeys()`) does not trigger RN `onChange` events reliably. `adb shell input keyevent` per digit (keycodes) is the proven approach for Citizen ID and Mobile Number.

**Should become:**
> For React Native `TextInput` fields (Citizen ID, Mobile Number): Appium `Input Text` works correctly. It triggers RN `onChangeText` with the full value, and formatting/validation execute identically to manual input.
>
> For React Native gesture components (buttons, touchables): Appium `Click Element` does not reliably trigger `onPress`. Use `adb shell input tap` with element center coordinates.

**Correction type:** Statement is partially incorrect (true for gesture, false for TextInput). Must split into two statements.

---

### 2. `knowledge/profile/next_button.md`

**Current text (line 21):**
> The form data entry method also matters: using `Press Keycode` (adb keycodes) for Citizen ID and Mobile Number triggers proper React Native `onChange` events, unlike `Input Text` which uses `element.sendKeys()`.

**Should become:**
> Text input method (keycodes vs `Input Text`) was previously thought to affect RN event handling. Evidence from Sprint 2.10.3 shows `Input Text` produces identical formatted output and triggers correct `onChangeText` events. The Next button issue is about **gesture handling** (React Native `TouchableOpacity` not responding to Appium tap), not about text input events. The two concerns are independent:
> - **TextInput fields**: `Input Text` is the correct approach
> - **Next button tap**: `adb shell input tap` is required

**Correction type:** Statement conflates two independent concerns. Must separate text input from gesture handling.

---

### 3. `knowledge/adb.md`

**Current text (line 28):**
> Used for Citizen ID and Mobile Number input. Each digit is sent as a separate keyevent. This triggers proper RN onChange events unlike Appium `sendKeys()`.

**Should become:**
> Used for Citizen ID and Mobile Number input (current production approach). Each digit is sent as a separate keyevent. However, Sprint 2.10.3 proved that Appium `Input Text` (sendKeys) also triggers correct RN `onChangeText` events and produces identical formatted output. Keycodes remain a valid alternative but are no longer required for TextInput fields. Keycodes may still be useful for:
> - OTP/PIN fields (future) where per-character validation is required
> - Fields that use `maxLength` to limit per-character input
> - Environments where `Input Text` behaves differently

**Correction type:** Statement is outdated. Must acknowledge `Input Text` as a valid alternative.

---

### 4. `knowledge/performance.md`

**Current text (lines 10-13):**
> - **Issue:** Appium `Input Text` does not reliably trigger RN onChange events
> - **Workaround:** `Press Keycode` per digit via adb (≈13 keycodes for 13-digit ID)

**Should become:**
> - **Issue (resolved):** Appium `Input Text` was previously thought to not trigger RN onChange events. Sprint 2.10.3 proved it works correctly for TextInput fields.
> - **Benchmark reference:** `Input Text` (single call) is ~13x faster than `Press Keycode` per digit (13 calls vs 1 call). Benchmark data at `reports/benchmark/`.

**Correction type:** Issue status should be "resolved" with updated recommendation.

---

### 5. `knowledge/benchmark.md`

**Current text (lines 81, 94):**
> - Press Keycodes (`Press Keycode` per digit — current production)

**Should become (after migration):**
> - Press Keycodes (`Press Keycode` per digit — legacy approach, replaced by `Input Text`)
> - Input Text (`sendKeys` — current production)

**Correction type:** Outdated reference to production method. Update after migration sprint.

---

### 6. `knowledge/playbooks/appium-playbook.md`

**Current text (line 34):**
> 6. For React Native issues:
>    - If `Click Element` fails, try `adb shell input tap` with bounds.
>    - If `Input Text` fails, try `Press Keycode` per digit.

**Should become:**
> 6. For React Native issues:
>    - **TextInput fields**: Use `Input Text`. It works and triggers correct RN events.
>    - **If `Input Text` fails**: Try `Press Keycode` per digit as fallback.
>    - **Buttons / Touchables**: If `Click Element` fails, try `adb shell input tap` with bounds.
>    - **Scroll views**: If Appium swipe fails, try `adb shell input swipe`.

**Correction type:** Missing distinction between TextInput and gesture components.

---

### 7. `docs/Architecture.md`

**Current text (lines 187, 191):**
> │ Enter Digits By Keycodes (citizen ID)
> │ Enter Digits By Keycodes (mobile number)

**Should become (after migration):**
> │ TextInput Engine — Input Text (citizen ID)
> │ TextInput Engine — Input Text (mobile number)

**Correction type:** Architecture diagram reference. Update after migration sprint.

---

## Documents NOT Requiring Revision

| Document | Reason |
|----------|--------|
| `docs/principles/engineering-principles.md` | Generic principle about RN compatibility. Remains valid — the principle "adapt to RN's event model" is unchanged. |
| `docs/decisions/ADR-002-use-adb-swipe-for-consent-scroll.md` | About scroll behavior, not text input. Unaffected. |
| `knowledge/locator.md` | References keycodes for focus context only. Statement is about the container locator, not input method. |

---

## Timeline for Revisions

| Priority | Document | When |
|:--------:|----------|------|
| P0 | `knowledge/appium.md` | Before migration sprint (corrects misleading guidance) |
| P0 | `knowledge/profile/next_button.md` | Before migration sprint (resolves contradiction) |
| P1 | `knowledge/adb.md` | Before migration sprint (updates keycode reference) |
| P1 | `knowledge/performance.md` | Before migration sprint (updates issue status) |
| P2 | `knowledge/playbooks/appium-playbook.md` | During migration sprint |
| P2 | `knowledge/benchmark.md` | After migration sprint (when production changes) |
| P3 | `docs/Architecture.md` | After migration sprint (architecture diagram update) |
