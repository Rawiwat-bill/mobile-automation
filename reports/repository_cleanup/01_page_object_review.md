# 01 — Page Object Review

> Does each Page Object contain only page-specific behavior?

---

## Page Object Inventory

| File | Lines | Verdict |
|------|-------|---------|
| `landing_screen_page.resource` | 45 | Clean — all page-specific |
| `consent_screen_page.resource` | 42 | Clean — all page-specific |
| `profile_screen_page.resource` | 271 | **Mixed** — contains generic helpers |
| `pdpa_consent_page.resource` | 65 | Clean — all page-specific |
| `sign_up_page.resource` | 15 | Clean — all page-specific |
| `scan_card_intro_page.resource` | 14 | Clean — all page-specific |
| `id_card_camera_capture_page.resource` | 25 | Clean — all page-specific |

---

## profile_screen_page.resource — Detailed Analysis

### Page-specific keywords (correctly placed)

| Keyword | Why page-specific |
|---------|-------------------|
| `Wait Until Profile Screen Is Displayed` | Uses `${PROFILE_TITLE_TEXT}`, `${PROFILE_CITIZEN_ID_INPUT}` |
| `Capture Profile Handoff Snapshot` | Writes to `${PROFILE_INVESTIGATION_DIR}` |
| `Capture Profile Debug Panel Evidence` | Uses `${PROFILE_DEBUG_PANEL_BUTTON}` |
| `Tap Profile Element Center` | Uses `${PROFILE_TIMEOUT}` for wait |
| `Tap Profile Blank Area` | Hardcodes x=540 (profile screen width) |
| `Wait Until Profile Fields Are Blurred` | Checks 3 specific profile fields |
| `Profile Fields Should Be Blurred` | Checks citizen, DOB, mobile locators |
| `Input Citizen ID` | Uses `${PROFILE_CITIZEN_ID_CONTAINER}` |
| `Input Date Of Birth` | Full DOB picker flow (out of scope) |
| `Input Mobile Number` | Uses `${PROFILE_MOBILE_NUMBER_CONTAINER}` |
| `Tap Profile Next Using Adb` | Uses `${PROFILE_NEXT_BUTTON_CONTAINER}` |
| `Tap Profile Next Button` | Profile navigation logic |
| `Tap Profile Next` | Profile alias |
| `Select DOB Picker Value` | DOB algorithm (out of scope) |
| `Read DOB Picker Visible Value` | DOB algorithm (out of scope) |
| `Verify DOB Field Value` | Uses `${PROFILE_DOB_INPUT}` |
| `Tap Date Of Birth Field` | Uses `${PROFILE_DOB_INPUT}` |

### Generic keywords (architecturally misplaced)

| Keyword | Why generic | Callers | Move? |
|---------|-------------|---------|-------|
| `Normalize Digits` | Pure string manipulation — strips non-digits. No page-specific logic. | 3 calls, all within this file | **Recommend** move to shared resource. **Not moved** — would add import. |
| `Input Text Field` | Generic input pattern: clear → type → read → return. No page-specific logic. | 2 calls, all within this file | **Recommend** move to shared resource. **Not moved** — would add import. |
| `Verify Field Value` | Generic field verification using Normalize Digits. No page-specific logic. | 2 calls, all within this file | **Recommend** move with Normalize Digits. **Not moved** — would add import. |

### Why not moved

The sprint rules require ALL three conditions:
1. Responsibility clearly improves — YES
2. Imports become simpler — **NO** (would add 1 import to profile_screen_page)
3. Behavior remains identical — YES

Condition 2 fails. Move deferred to future sprint when `resources/shared/` is
created with enough content to justify the import overhead.

### Future recommendation

When creating `resources/shared/input_helpers.resource`:
- Move `Normalize Digits`, `Input Text Field`, `Verify Field Value` there
- Profile_screen_page imports it (1 new import)
- Benchmark can also import it if needed
- Net benefit increases as more page objects reuse these helpers

---

## Other Page Objects

All other Page Objects are clean — they contain only page-specific keywords.
No generic logic found in:
- landing_screen_page (45 lines)
- consent_screen_page (42 lines)
- pdpa_consent_page (65 lines)
- sign_up_page (15 lines)
- scan_card_intro_page (14 lines)
- id_card_camera_capture_page (25 lines)
