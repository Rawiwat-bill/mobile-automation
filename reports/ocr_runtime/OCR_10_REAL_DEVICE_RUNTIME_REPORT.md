# OCR-10 — Real Device OCR Runtime Verification Report

| Field | Value |
|-------|-------|
| **Mission** | OCR-10 — Real Device OCR Runtime Verification |
| **Date** | 2026-07-08 |
| **Branch** | `spike/appium-skill` |
| **Scope** | Real device only, DEV only, one capture, stop before OTP |
| **Device** | `48ZYD25C01422768` — Huawei MGA_LX3 (JUYO-L21), Android 10 / EMUI, 720×1604 |
| **Classification** | **APP_HUNG** |

## Summary

The real-device OCR runtime verification is **blocked at the Consent screen** by a deterministic
Appium/UiAutomator2 accessibility deadlock on this device. Across **3 runs** (10, 25, and
20 min), the test consistently captured only `launch` + `start_consent` evidence, then hung on
the next Appium `Find Element` call. The route did **not** reach OCR Camera; no capture was
attempted.

## Pre-check (all PASS)

| Check | Result |
|-------|--------|
| `adb devices -l` | Real device `48ZYD25C01422768` (MGA_LX3) connected |
| Appium running with `--relaxed-security` | Yes (`--relaxed-security --allow-insecure get_server_logs,adb_shell`) |
| DEV app installed on device | Yes (`com.bangkokbank.blue.dev`) |

## Run Log

| Run | Duration | Evidence captured | Outcome |
|-----|----------|-------------------|---------|
| 1 | 10 min (killed) | launch, start_consent | Hung at `Find Element` after consent `Get Source` |
| 2 | 25 min (killed) | launch, start_consent | Same hang (consent batching experiment — no effect) |
| 3 | 20 min (killed) | launch, start_consent | Same hang; UiAutomator2 server clean (no crash) → confirms deadlock, not orphan-crash |

The consent-batching experiment (run 2) was **reverted**; `dev_ocr_real_device.robot` is back to
its OCR-01 form.

## Root Cause (evidence-based)

**Appium accessibility operations deadlock when traversing the Consent WebView on this device.**

- `Detect Current Screen` and `Capture Step Evidence` each call Appium `Get Source` on the consent
  WebView — these **complete** (return a partial hierarchy, ~2 KB).
- The **next** Appium call — `Wait Until Element Is Visible ${LANDING_READY_BUTTON}` (a
  `Find Element` over the same tree) — **hangs indefinitely**, ignoring its 20 s timeout. The
  process only ends when the runner is killed.
- Runs 1–2 logcat showed `FATAL EXCEPTION: UiAutomationService ... already registered!` (orphaned
  UiAutomator2 servers from the killed runs conflicting). Run 3 was started with a fully cleaned
  UiAutomator2 (`force-stop io.appium.uiautomator2.server(.test)`, verified no orphans) and
  produced **no** FATAL/crash — yet the identical hang recurred. This **rules out orphan-session
  conflict as the sole cause** and confirms the deadlock is in Appium's accessibility traversal
  of the WebView itself.

This is a known class of incompatibility between UiAutomator2 and React Native WebViews on
older Android / EMUI builds: the accessibility bridge stalls when dumping/searching a WebView
that also runs its own Chrome accessibility tree.

## Where It Stalls (deterministic)

```
Open Application (real device) ............... OK
Capture Step Evidence launch ................. OK  (Landing, native)
Detect Current Screen → consent .............. OK  (Get Source on consent WebView)
Capture Step Evidence start_consent .......... OK  (Get Source on consent WebView again)
Wait Until Element Is Visible LANDING_READY  ← HANG (Find Element over consent WebView)
...rest of route never reached...
```

## Evidence

- `reports/ocr_runtime/evidence/ocr10/launch.{png,xml,_activity.txt}` — Landing (native, captured OK)
- `reports/ocr_runtime/evidence/ocr10/start_consent.{png,xml,_activity.txt}` — Consent WebView (captured OK)
- `reports/ocr_runtime/evidence/ocr10/app_hung_state.{png,xml}` — device state at kill
- `reports/ocr_runtime/evidence/ocr10/logcat.txt` — full logcat (incl. run-1/2 `UiAutomationService already registered` FATAL)
- `reports/ocr_runtime/evidence/ocr10/OCR_RESULT.txt` — `classification=APP_HUNG`
- Robot output: `reports/ocr_runtime/robot_ocr10/output.xml`

## Classification

**APP_HUNG** — Appium session deadlocks at the Consent WebView; route cannot progress to OCR Camera.

(Other branches considered and ruled out: `DEVICE_NOT_CONNECTED` — no, device present;
`DOPA_INFORMATION` / `RGI_055` / `OCR_ERROR` / `NO_CAPTURE` — not reached.)

## Success Criteria

| # | Criterion | Status |
|---|-----------|--------|
| A | Real device connected | **MET** |
| B | OCR Camera reached | **NOT MET** — hung at Consent |
| C | One capture attempt executed | **NOT MET** — did not reach OCR Camera |
| D | Result classified | **MET** — APP_HUNG |
| E | Stop before OTP | **MET** — stopped at Consent, well before OTP |

## Recommended Fix (separate mission — not applied)

The consent WebView must be driven **without Appium accessibility operations** on this device.
Options, in order of preference:

1. **adb-only Consent drive** in the investigation test: detect the WebView + scroll via
   `adb shell input swipe`, detect bottom via `adb shell uiautomator dump | grep` (or a fixed
   swipe count), and tap Accept via `adb shell input tap` at its bounds — issuing **zero** Appium
   `Get Source` / `Find Element` while the WebView is on screen. Resume Appium once on the native
   Profile screen.
2. **Chromedriver / native-context handling**: switch Appium to the native context (skip the
   WebView accessibility tree) for consent, or add chromedriver for the WebView.
3. **Device/OS**: validate whether the deadlock reproduces on a newer Android / non-EMUI device
   (the emulator, which has no real WebView accessibility conflict, reaches OCR Camera fine).

Until one of these is in place, real-device OCR runtime cannot be verified end-to-end.

## Files Changed
- `tests/investigation/dev_ocr_real_device.robot` — **unchanged** (consent-batching experiment reverted; back to OCR-01 form).
- `reports/ocr_runtime/evidence/ocr10/*` — new evidence (this mission).
- `reports/ocr_runtime/OCR_10_REAL_DEVICE_RUNTIME_REPORT.md` — this file.

No production code, DOB, Consent keyword, OCR Frida scripts, or APK modified.

## Next Recommended Action
Open a focused **real-device Consent unblock** mission implementing option 1 (adb-only consent
drive in the investigation test), then re-run OCR-10. The emulator route to OCR Camera remains
validated (OCR-02/03), and the DOB calibration (DOB-03) is unaffected — only the real-device
Consent→Profile handoff is blocked by this Appium/WebView deadlock.
