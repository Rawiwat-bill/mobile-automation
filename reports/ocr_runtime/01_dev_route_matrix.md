# OCR-01 — DEV OCR Route Matrix

> **Scope:** DEV only. No SIT/UAT. No LOCAL. Realistic mock data retained for DEV OCR research.

## Route Summary

| Route | Trigger | Device | Reaches | Stops At | Test Artifact | Status |
|-------|---------|--------|---------|----------|---------------|--------|
| **Fresh state → OCR Camera** | `pm clear` | Emulator | Landing → … → OCR Camera | OCR Camera (no capture) | `tests/health/emulator_revival.robot` | PROVEN (dryrun + structure) |
| **Fresh state → OCR Capture** | `pm clear` | Real device | Landing → … → OCR Camera → Capture → result | Result classification (pre-OTP) | `tests/investigation/dev_ocr_real_device.robot` | PREPARED — dryrun PASS, live run pending device |
| **Persisted state → DOPA** | no `pm clear` (app retains state) | Real device | Resumes at DOPA_information (or later) | DOPA_information (pre-OTP) | `tests/regression/onboarding_branch_decision.robot` (detects DOPA) | PROVEN detection; DOPA page object = skeleton |
| **Emulator boundary** | `pm clear` | Emulator | … → OCR Camera | OCR Camera (0-FPS, cannot capture) | `tests/health/emulator_revival.robot` | PROVEN boundary |

## Shared Onboarding Prefix (all routes)

```
Landing → Consent → Profile(CND) → PDPA → SignUp → ScanCardIntro → OCR Camera
```

- Landing, Consent, Profile, DOB, PDPA, SignUp are **proven** (CERTIFICATION 33/33).
- Profile Next uses `Execute Adb Shell` (`--relaxed-security`) — handles RN gesture (Milestone 2).
- Consent on the 720×1604 real device uses in-bounds adb swipes (shared scroll is OOB at y=1950).

## Branch Point

After SignUp, fresh state routes to **ScanCardIntro → OCR Camera** (camera path).
After OCR capture, the backend may route to **DOPA_information** (data confirm) or return an error.

- DOPA marker (confirmed): `resource-id` contains `screenDopaInformation`
- Error markers: text `RGI-`, `GOD-`, `not available`, or `error` resource-id

## Device Requirement

| Step | Emulator | Real Device |
|------|:--------:|:-----------:|
| Landing → SignUp | OK | OK |
| ScanCardIntro → OCR Camera | OK | OK |
| OCR Capture (Take Photo) | BLOCKED (0-FPS) | OK |
| Post-capture classification | N/A | OK |

See `04_emulator_boundary.md` for the 0-FPS limitation detail.
