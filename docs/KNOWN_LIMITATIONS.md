# Known Limitations

> Project-level baseline of current automation limitations, after the OCR emulator boundary
> (OCR-01/02/03) and the DOB calibrated slow-drag patch (DOB-01/02/03).
> **Scope: DEV only.** Update this file when a limitation is resolved or a new one is confirmed.

---

## 1. Emulator Limitation

| Aspect | Status |
|--------|--------|
| Onboarding up to OCR Camera | Validated on emulator (`tests/health/emulator_revival.robot`) |
| OCR capture (`Take Photo`) | **Not possible on emulator** |
| Reason | Emulator camera produces no usable frames (0-FPS); the OCR surface never receives an image |

- The emulator is the primary CI/CD target and is sufficient for Landing → Consent → Profile → PDPA → SignUp → ScanCardIntro → **OCR Camera**.
- **Do not tap `Take Photo` on the emulator** — it cannot capture. Stop at the OCR Camera boundary.

## 2. Real Device Requirement

| Aspect | Status |
|--------|--------|
| OCR capture + post-capture classification | **Real device required** |
| DOB calibrated picker on real device | **Pending validation** (emulator-validated only) |
| Frida instrumentation | **Unavailable unless** the device is rooted, the app is debuggable, or a Frida Gadget is embedded |

- OCR capture, result classification (DOPA_information / RGI-055 / OCR error / no capture), and
  anything past the OCR Camera boundary must run on a real device.
- The DOB picker calibration uses wheel-relative ratios and is expected to transfer to the
  720×1604 real device, but this is **not yet measured**.

## 3. DOB Picker Status

| Aspect | Status |
|--------|--------|
| Calibrated slow-drag patch | **Applied** to production `Select DOB Picker Value` |
| DOB exact `15 Jan 1992` | **Confirmed on emulator** (`Verify DOB Field Value` PASS) |
| Real device validation | **Pending** |
| Large year jumps | **Future benchmark debt** |

- Production uses 400ms calibrated drags: coarse `0.70→0.30` (~2 rows), fine `0.60→0.40` (~1 row).
  Constants live in `resources/app/app_constants.resource`.
- Calibration was measured on the **day wheel only** (1–31). The same constants govern the year
  and month wheels; a year jump greater than ~50 rows could exceed the 25-retry bound.

## 4. Security Status

| Aspect | Status |
|--------|--------|
| DEV research | **Approved** (`reports/repository_certification/C3_5_DEFER_SECURITY_NOTE.md`) |
| Shared / `main` merge | **Blocked** until PII sanitization |
| Realistic mock data | **Retained intentionally** for DEV OCR validation |

- Mock-realistic PII (citizen ID, names, DOB, address) is intentionally kept in tracked files for
  DEV OCR/runtime validation. It is **not** real customer data.
- Sanitization is **mandatory** before any merge to `main` or a shared remote, and before any
  CI/CD pipeline that logs or exposes file contents.

## 5. Scope Status

| Environment | Status |
|-------------|--------|
| DEV | Supported (partial — app package hardcoded, env config empty) |
| SIT | **Not configured** |
| UAT | **Not configured** |
| LOCAL | **Not a supported environment** (`*.local.yaml` is gitignored) |

- All current automation targets **DEV only**. SIT/UAT configs are deferred.
- `LOCAL` files (`ntb.local.yaml`, `etb.local.yaml`, `.env`) are local-only research data and are
  not part of any supported environment.
