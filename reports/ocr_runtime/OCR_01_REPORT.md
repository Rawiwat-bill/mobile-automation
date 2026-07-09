# OCR-01 — DEV OCR Runtime Stabilization Report

| Field | Value |
|-------|-------|
| **Mission** | OCR-01 — DEV OCR Runtime Stabilization |
| **Date** | 2026-07-07 |
| **Branch** | `spike/appium-skill` |
| **Scope** | DEV only (no SIT/UAT/LOCAL) |
| **Baseline** | Post Phase-1 cleanup, CERTIFICATION 33/33 dryrun PASS |

## Summary

Stabilized the DEV OCR route definition and prepared the real-device capture path. The full
onboarding prefix (Landing → Consent → Profile → PDPA → SignUp → ScanCardIntro → OCR Camera)
is **proven** by existing tests. The OCR **capture + classification** step was missing and is
now implemented as an investigation test, dryrun-validated, ready to run on a connected real
device. The DOPA_information page object was missing and is now created as a minimal skeleton
(container locator only — evidence-confirmed; element locators deferred to live XML).

**Live capture was not executed** because no device was connected this session (`adb devices`
empty). Appium is running with `--relaxed-security`, so the only blocker is attaching the real
device. Exact handoff command is in `03_real_device_ocr_result.md`.

## Success Criteria

| # | Criterion | Status |
|---|-----------|--------|
| A | DEV fresh-state reaches OCR Camera reliably | MET (code) — `emulator_revival.robot` proves to camera; `dev_ocr_real_device.robot` extends through capture. Live re-confirm pending device. |
| B | Real-device OCR capture result classified | PARTIAL — classification logic implemented + dryrun-validated; live classification pending device. |
| C | DOPA_information page object readiness known | MET — was missing; skeleton created (container-only). Element locators blocked on live DOPA XML. |
| D | Emulator boundary clearly documented | MET — see `04_emulator_boundary.md`. |

## Agents Used
- qa-orchestrator (this session; code changes explicitly authorized by mission task 6)

## Files Checked
- `reports/repository_certification/CERTIFICATION.md`
- `reports/repository_certification/C3_5_DEFER_SECURITY_NOTE.md`
- `tests/health/emulator_revival.robot`
- `tests/regression/onboarding_branch_decision.robot`
- `resources/pages/onboarding/*` (7 page objects) + `resources/app/app_keywords.resource`, `app_constants.resource`
- `locators/android/onboarding/*` (7 locator files)
- `knowledge/ocr.md`, `knowledge/playbooks/ocr-playbook.md`, `knowledge/playbooks/locator-playbook.md`, `knowledge/patterns/page-object-pattern.md`
- `testdata/onboarding/ntb.local.yaml`, `ntb.example.yaml`
- `configs/env/dev.yaml`, `configs/devices/real_device.yaml`
- `apps/android/mock/ntb_id_card.png` (EXISTS, 2.6 MB)
- `reports/investigation/onboarding_branch_decision/REPORT.md` — **not present** (only evidence artifacts are produced by the regression test at runtime)

## Files Changed
| File | Change | Reason |
|------|--------|--------|
| `locators/android/onboarding/dopa_information_locators.resource` | NEW | DOPA container locator (confirmed via `onboarding_branch_decision.robot:169`) |
| `resources/pages/onboarding/dopa_information_page.resource` | NEW | `Wait Until DOPA Information Screen Is Displayed` (page-object-pattern compliance) |
| `tests/investigation/dev_ocr_real_device.robot` | NEW | Fresh-state real-device OCR route + capture + classification (investigation; unstable) |
| `.gitignore` | +3 lines | Track `reports/ocr_runtime/` deliverables; keep `evidence/` + `robot/` ignored |
| `reports/ocr_runtime/*.md` (6 files) | NEW | Deliverables |

No existing tracked files modified. `onboarding_branch_decision.robot` and `emulator_revival.robot`
left untouched (stable/proven — out of scope).

## Validation Command
```bash
python3 -m robot --dryrun --outputdir /tmp/ocr01_dryrun tests/investigation/dev_ocr_real_device.robot
python3 -m robot --dryrun --outputdir /tmp/ocr01_full_dryrun tests/android tests/benchmark tests/health tests/preparation tests/regression
```

## Validation Result
- New investigation test: **1 passed, 0 failed**.
- Certified suites: **33 passed, 0 failed** (no regression).
- New test deliberately kept under `tests/investigation/` (not in certified suites) per task 6.

## Security Review
- No PII added. Citizen ID / phone / DOB referenced in reports as `[MASKED_*]`.
- `ntb.local.yaml` remains gitignored; mock-realistic data retained per mission (sanitization deferred to pre-merge, per C3.5).
- Real device UDID reused from existing `onboarding_branch_decision.robot` (already in repo; not flagged by C3.5).
- No APK, OTP, token, or credential touched.
- **review-agent + security-review-agent approval required before any commit** (Final Quality Gate).

## Performance Review
- No fixed long sleeps added. Capture wait uses bounded `Wait Until Page Contains Element` (90s timeout, event-based).
- Evidence capture reuses the proven png+xml+activity pattern (one screencap + one source dump per step).
- Consent loop bounded (≤20 swipes with break-on-bottom).

## Risk / Note
- **Primary risk: live OCR capture never executed.** All capture/classification code is dryrun-only until a real device is connected. Classification branches are inferred from `onboarding_branch_decision.robot`'s error markers + mission description; real result may reveal new branches.
- DOPA page object is container-only — cannot interact with DOPA elements until live XML is captured. No locators invented.
- `configs/env/dev.yaml` and `configs/devices/real_device.yaml` remain empty (known debt; mission excludes env redesign). Tests hardcode device caps (consistent with existing `branch_decision` pattern).
- Investigation test duplicates `Pass Consent Screen Reliably` / `Fill Profile Fields Masked` / `Detect Current Screen` / `Capture Step Evidence` from `branch_decision` — acceptable per page-object-pattern "When Not to Use" (investigation script). Refactor to shared resource deferred (not required to unblock OCR).

## Playbook / Pattern Used
- `knowledge/playbooks/locator-playbook.md` — locator evidence rule (container locator evidence-confirmed; element locators deferred per "No evidence" stop condition).
- `knowledge/patterns/page-object-pattern.md` — DOPA page object structure; investigation-script duplication exception.
- `knowledge/ocr.md` + `knowledge/playbooks/ocr-playbook.md` — consulted (both Milestone-3 placeholders); updated knowledge deferred to post-capture (evidence-only policy).

## Next Recommended Action
Connect the real device and run:
```bash
python3 -m robot -d reports/ocr_runtime/robot -L TRACE tests/investigation/dev_ocr_real_device.robot
```
Then follow `05_next_steps.md` based on the `OCR_RESULT.txt` branch value.

## Deliverables Index
- `01_dev_route_matrix.md` — fresh / persisted / real-device / emulator-boundary routes
- `02_fresh_state_ocr_route.md` — fresh-state route step→keyword→locator map
- `03_real_device_ocr_result.md` — classification schema + handoff command + DOPA readiness
- `04_emulator_boundary.md` — 0-FPS boundary documentation
- `05_next_steps.md` — post-run actions per branch
- `OCR_01_REPORT.md` — this file
