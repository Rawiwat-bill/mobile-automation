# OCR-01 — Real-Device OCR Capture Result

## Current Status: NOT YET CAPTURED (device-blocked)

No device was connected this session (`adb devices` returned empty). Appium **is** running
(`--relaxed-security --allow-insecure get_server_logs,adb_shell`), so the only blocker is a
connected real device. The capture route is **prepared and dryrun-validated**, ready to execute
on device connect.

## Capture Route

`tests/investigation/dev_ocr_real_device.robot` — fresh state (`pm clear`) → full onboarding →
OCR Camera → **one** `Tap Take Photo` → classify → stop before OTP.

- Reuses all shared onboarding page objects + branch_decision's real-device consent.
- Real device: `48ZYD25C01422768` (MGA_LX3, Android 10) — same as `onboarding_branch_decision.robot`.
- Mock card available: `apps/android/mock/ntb_id_card.png`.

## Result Classification Schema

After `Tap Take Photo`, `Classify OCR Result` waits up to `${CAPTURE_TIMEOUT}` (90s) and classifies:

| Branch | Detection | Meaning |
|--------|-----------|---------|
| `DOPA_INFORMATION` | `${DOPA_INFORMATION_SCREEN}` visible (resource-id contains `screenDopaInformation`) | Backend accepted OCR; routed to DOPA data confirm |
| `RGI_055` | page contains text `RGI-` | Specific backend/OCR rejection code |
| `OCR_ERROR` | page contains `GOD-`, or error resource-id, or `not available` | Generic OCR/backend error |
| `NO_CAPTURE` | ScanCardIntro re-appeared (retake) or timeout | Camera did not produce a capturable result |

Result is written to `reports/ocr_runtime/evidence/${TRIAL_TAG}/OCR_RESULT.txt` + evidence (png/xml/activity).

## Live Run Command (handoff)

```bash
# 1. Connect real device, confirm:
adb devices -l          # expect 48ZYD25C01422768

# 2. Ensure Appium already running with --relaxed-security (it is).

# 3. Run fresh-state OCR capture:
python3 -m robot -d reports/ocr_runtime/robot -L TRACE \
    tests/investigation/dev_ocr_real_device.robot

# Optional overrides (persisted state instead of fresh):
#   -v CLEAR_APP:False
# Optional trial tag:
#   -v TRIAL_TAG:trial_2
```

## Post-Run Actions

1. Read `reports/ocr_runtime/evidence/ocr01/OCR_RESULT.txt` → branch.
2. If `DOPA_INFORMATION`: capture `result_DOPA_INFORMATION.xml` → populate DOPA page object element locators (currently container-only).
3. If `RGI_055` / `OCR_ERROR`: capture error text → decide Frida OCR mock injection vs real-capture path.
4. If `NO_CAPTURE`: camera/permission issue → investigate before code change (evidence-first).

## DOPA Page Object Readiness

| Item | State |
|------|-------|
| Locators file `locators/android/onboarding/dopa_information_locators.resource` | CREATED — container only (`screenDopaInformation`) |
| Page object `resources/pages/onboarding/dopa_information_page.resource` | CREATED — `Wait Until DOPA Information Screen Is Displayed` only |
| Element locators (buttons/inputs on DOPA screen) | PENDING live XML evidence |
| Container locator provenance | `onboarding_branch_decision.robot:169` (prior real-device run) |

**Readiness: skeleton ready; element locators blocked on live DOPA XML.** No locators invented.
