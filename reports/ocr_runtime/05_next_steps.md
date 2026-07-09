# OCR-01 — Next Steps

## Immediate (unblocks OCR capture classification)

1. **Connect real device** (`48ZYD25C01422768` / MGA_LX3) and run:
   ```bash
   python3 -m robot -d reports/ocr_runtime/robot -L TRACE \
       tests/investigation/dev_ocr_real_device.robot
   ```
2. **Read `reports/ocr_runtime/evidence/ocr01/OCR_RESULT.txt`** → branch value.
3. Classify per `03_real_device_ocr_result.md`:
   - `DOPA_INFORMATION` → step 4.
   - `RGI_055` / `OCR_ERROR` → step 5.
   - `NO_CAPTURE` → step 6.

## If DOPA_information reached

4. Open `result_DOPA_INFORMATION.xml` → extract screen-specific `resource-id`s for DOPA
   elements (confirm/next button, editable fields). Add to
   `locators/android/onboarding/dopa_information_locators.resource` and add business keywords
   to `resources/pages/onboarding/dopa_information_page.resource`. **No locators without this
   XML.** Stop before OTP.

## If RGI-055 / OCR error

5. Capture exact error text + activity. Decide between:
   - **Real-capture path**: improve lighting/card framing, retry once.
   - **Frida OCR mock injection**: existing scripts in `tools/frida/ocr/` inject realistic mock
     OCR responses — use if the real camera path is blocked by environment, not by code.
   Do NOT modify Frida unless required (mission rule). One experiment at a time, revert on failure.

## If NO_CAPTURE

6. Evidence-first: capture camera XML + screenshot + logcat around the capture attempt.
   Compare manual capture (works?) vs automation (fails?) before any code change.
   Likely causes: permission not granted, card not detected in frame, RN camera surface issue.

## After OCR result is classified + stable

7. Promote `tests/investigation/dev_ocr_real_device.robot` to `tests/regression/` **only when
   stable** (per mission task 6). Keep as investigation until then.
8. Update `knowledge/ocr.md` and `knowledge/playbooks/ocr-playbook.md` with the confirmed
   capture result + locators (both are currently Milestone-3 placeholders). Evidence only.
9. Populate `knowledge/facescan.md` prep when OCR→Face handoff is observed.

## Security / Merge Gate (unchanged from C3.5)

10. Before any merge to `main`/shared branch: sanitize the 8 tracked files with mock-realistic
    PII (see `reports/repository_certification/C3_5_DEFER_SECURITY_NOTE.md`). **Not now** —
    mission defers sanitization; DEV research retains realistic data.

## Not in scope (mission-excluded)

- SIT / UAT env configs.
- Environment architecture redesign.
- Framework refactor (unless required to unblock OCR — none required this session).
- Frida modification (unless capture path demands it).
- APK patch.
- PII sanitization (deferred).
