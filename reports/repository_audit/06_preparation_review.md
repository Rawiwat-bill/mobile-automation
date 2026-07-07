# 06 — Preparation Review

## What Is "Preparation"?

Preparation flows are reusable setup/teardown sequences that prepare the app state
for testing without being tests themselves. In this repo, the preparation flow is
`Complete Common Onboarding` — it navigates Landing → Consent → Profile → PDPA →
Sign Up → Scan Card → ID Card Photo, preparing the app for OCR/Face/PIN milestones.

## Preparation Inventory

### Core Preparation Keyword

| File | Keyword | Lines | Purpose |
|------|---------|-------|---------|
| `onboarding_common.resource:13` | `Complete Common Onboarding` | 47 | Full common onboarding flow, takes citizen_id, dob, mobile_number |

### Supporting Preparation Keywords

| File | Keywords |
|------|----------|
| `app_keywords.resource` | `Open Mobile Application`, `Allow Android Permission If Visible` |
| `landing_screen_page.resource` | `Wait Until Landing Screen Is Displayed`, `Tap Landing Ready Button`, `Skip Landing Screen`, `Switch Landing Language To Thai/English` |
| `consent_screen_page.resource` | `Wait Until Consent Screen Is Displayed`, `Scroll Down Consent Terms`, `Tap Consent Accept Button` |
| `profile_screen_page.resource` | `Wait Until Profile Screen Is Displayed`, `Input Citizen ID`, `Input Date Of Birth`, `Input Mobile Number`, `Tap Profile Next` |
| `pdpa_consent_page.resource` | `Wait Until PDPA Consent Screen Is Displayed`, `Tap PDPA Consent Accept Button` |
| `sign_up_page.resource` | `Wait Until Sign Up Screen Is Displayed`, `Tap Sign Up Lets Start Button` |
| `scan_card_intro_page.resource` | `Wait Until Scan Card Intro Screen Is Displayed`, `Tap Scan Card Intro Next` |
| `id_card_camera_capture_page.resource` | `Wait Until ID Card Camera Capture Screen Is Displayed`, `Navigate Virtual Camera To Poster`, `Tap Take Photo` |

---

## Findings

### Strengths

| # | Finding |
|---|---------|
| 1 | Single aggregation point (`Complete Common Onboarding`) — all tests call the same preparation flow |
| 2 | Arguments (citizen_id, dob, mobile) decouple preparation from test data |
| 3 | Health checkpoints embedded in preparation — visibility without separate instrumentation |
| 4 | PDPA blocker handling returns gracefully (`RETURN` on blocker) instead of failing hard |

### Issues

| # | Severity | Finding | Evidence | Recommendation |
|---|----------|---------|----------|----------------|
| 1 | High | Preparation is all-or-nothing — no partial preparation | `Complete Common Onboarding` runs the full flow; can't stop at Profile for OCR-only tests | Add optional `${stop_at}` argument or split into `Complete Onboarding Until Profile` / `Complete Onboarding Until ID Card` |
| 2 | Medium | `Navigate Virtual Camera To Poster` is emulator-specific | Uses `tools/emulator/navigate_camera.py` with environment variables CAM_YAW/CAM_PITCH/CAM_FWD | Will fail on real device; needs platform conditional |
| 3 | Medium | `id_card_camera_capture_page.resource:20` writes to hardcoded path | `reports/investigation/emulator_camera_calibration/camera_after_nav.png` | Should use `${OUTPUT_DIR}` not hardcoded `reports/` |
| 4 | Medium | Profile field input uses adb keycodes for Citizen ID but swipe-picker for DOB | Inconsistent input strategies | Document why (RN gesture handling) in knowledge/profile/next_button.md (already done) |
| 5 | Low | `Tap Profile Next` has complex fallback logic (adb tap → Appium tap → check navigation) | `profile_screen_page.resource:178-200` | Acceptable — documented RN workaround; keep |

---

## Reusability Assessment

| Consumer | How It Uses Preparation | Works? |
|----------|------------------------|--------|
| `ntb_flow.robot` | Full flow → stops | Yes |
| `etb_flow.robot` | Full flow → stops | Fails (empty test data) |
| `identity_validation.robot` | Full flow → stops at Profile Next | Yes |
| `onboarding_health_check.robot` | Full flow + health tracking + API capture | Yes |
| Benchmark tests | Do NOT use `Complete Common Onboarding` — they reimplement Navigate To Profile | Intentional isolation |
| Investigation tests | Mixed — some use `Complete Common Onboarding`, some reimplement | Inconsistent |

## Recommendation

Preparation flow is well-designed and reusable. C2 should:
1. Add a `${stop_at}` parameter or split into stage-based preparation keywords.
2. Fix hardcoded `reports/` path in `id_card_camera_capture_page.resource`.
3. Add platform conditional for emulator camera navigation.
4. Document that benchmark intentionally does NOT use shared preparation.
