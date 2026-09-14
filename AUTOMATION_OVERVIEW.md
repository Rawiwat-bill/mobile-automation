# Mobile Banking Automation Overview

อัปเดตจาก implementation ปัจจุบัน ณ 14 สิงหาคม 2026 เอกสารนี้เป็นภาพรวมหลักฉบับเดียวสำหรับ automation scope, coverage, architecture, execution และข้อจำกัด ส่วนวิธีติดตั้งและรันสำหรับ Business อยู่ที่ [README.md](README.md)

## Executive summary

- Framework: Robot Framework + AppiumLibrary + Appium UiAutomator2
- Platform: Android-first
- Environment: ETB รองรับ DEV / SIT / DEV_MOCK; UAT ยังไม่ configured
- Application: React Native
- Supported execution: local Android emulator และ real device
- Test design: Page Object, locator แยกตาม platform/screen, test data แยกจาก test logic
- Security: local approved data เท่านั้น, report/log/evidence ต้อง mask ก่อนแชร์

## Automation ที่มีอยู่

### Onboarding flows

ปัจจุบันมี onboarding implementation สองชุด ไม่ใช่ keyword เดียวที่ทุก suite reuse:

**NTB/health-check flow** - `resources/keywords/onboarding_common.resource`

1. Landing และ permission
2. Terms and Conditions
3. Profile: Citizen ID, Date of Birth, Mobile Number
4. PDPA consent
5. Sign-up introduction
6. ID card scan introduction
7. OCR camera/capture boundary

**ETB flow** - `resources/keywords/common_onboarding/common_onboarding_keyword.resource`

1. Landing และเปลี่ยนภาษาเป็น English
2. Terms and Conditions
3. Profile: Citizen ID, Date of Birth, Mobile Number
4. ส่งผล `NEXT`, service/backend handoff หรือ branch ไป ETB regression flow

React Native บาง interaction ไม่ตอบสนองต่อ Appium click ปกติ Framework จึงใช้ ADB interaction เฉพาะจุดที่มี evidence รองรับ และ Appium server ต้องเปิดด้วย `--address 127.0.0.1 --relaxed-security` เท่านั้น ห้าม expose privileged server นี้ออก LAN

### ETB regression

Canonical suite: `tests/android/etb/etb_regression.robot`

| Coverage | Cases |
|---|---:|
| Positive registration / PDPA / product selection | TC-ETB-001 ถึง TC-ETB-004 |
| Mobile/DOB mismatch popup | TC-ETB-005 ถึง TC-ETB-006 |
| Expired ID, high-risk, low IAL, mule warning full-screen RGI | TC-ETB-007 ถึง TC-ETB-013 |
| รวม | 13 cases |

เลือก run ได้ทั้ง case, tag, smoke และ full regression ผ่าน `./run etb`

ก่อนและหลัง ETB case มี state preparation/cleanup สำหรับ CIS และบาง case มี PDPA preparation ตาม case contract การรันจริงจึงขึ้นกับ environment-specific readiness ไม่ใช่ UI อย่างเดียว: DEV ตรวจ CIS transport/backend, SIT ใช้ external-prepared CIS confirmation และ DEV_MOCK ใช้ mock-build readiness contract

### NTB

Entry point: `tests/android/ntb/ntb_flow.robot`

`./run ntb` เรียก NTB onboarding ด้วย local profile และแตะ `Take Photo` ตาม implementation ปัจจุบัน จึงเป็น real-device-only ห้ามใช้กับ emulator เพราะ emulator camera ไม่มี usable frame

### Health check

Entry point: `tests/android/onboarding/onboarding_health_check.robot`

Health check ทำหน้าที่:

- ตรวจ E2E onboarding checkpoints
- เก็บ ADB/API diagnostic log ผ่าน redaction layer
- สรุปสถานะ `PASS`, `FAIL` หรือ `BLOCKED`
- สร้าง Robot report และ health-check artifacts

Health-check dry-run ไม่ต้องใช้ device แต่ full health check เป็น real-device-only เพราะเรียก NTB onboarding และแตะ `Take Photo` จริง Health check ไม่ใช่ตัวแทนของ ETB regression 13 cases และไม่ควรใช้แทน business acceptance

## Architecture

```text
tests/
  Android suites และ business scenarios
        |
resources/keywords/
  business flow และ reusable orchestration
        |
resources/pages/
  screen interaction
        |
locators/android/
  locator แยกตาม screen

libraries/
  YAML loading, CIS/PDPA preparation, teardown, log sanitization

testdata/
  committed contract/example + gitignored approved local profiles

reports/
  Robot output, health check, investigation evidence
```

หลักสำคัญ:

- Test case อธิบาย business flow
- Page resource เป็นเจ้าของ screen interaction
- Locator ไม่อยู่ใน test case
- Test data ไม่ hardcode ใน test logic
- ใช้ explicit/condition-based wait แทน fixed wait ใน production path
- Flaky issue ต้องมี screenshot, Appium XML และ manual-vs-automation comparison ก่อนแก้

## Entry points

| งาน | คำสั่ง |
|---|---|
| ติดตั้ง Python environment | `./setup` |
| ตรวจ ETB selection/syntax | `./run etb --dry-run` |
| ETB full regression | `./run etb` |
| ETB case เดียว | `./run etb TC-ETB-xxx` |
| ETB tag | `./run etb --tag <tag>` |
| ETB smoke | `./run etb --smoke` |
| NTB | `./run ntb` |
| Health-check syntax | `./health-check --dryrun` |
| Full health check | `tools/ci/run_health_check.sh` พร้อม variables ตาม README |

## Data and security boundary

- Repository ไม่มี runnable customer profile
- `*.local.yaml`, `.env`, APK, reports และ runtime artifacts ต้องไม่ commit
- Committed YAML ใช้เป็น contract/example เท่านั้น
- ห้ามใช้ real customer data
- ห้าม log Citizen ID, phone, account, password, OTP, token หรือ certificate
- Screenshot/XML/log/report ต้องตรวจและ mask ก่อนแชร์
- NTB/health check รับ profile path ผ่าน environment variable
- ETB runner ใช้ `ETB_CASE_PROFILES` เป็น runtime profile source; ถ้าไม่กำหนดจะ default ไปที่ `testdata/onboarding/etb_cases.local.yaml`, resolve เป็น absolute path และส่ง source เดียวกันให้ Robot; real run ต้องใช้ approved local file ที่อ่านได้
- ETB runtime evidence scope ใช้ `ETB_RUN_ID` + canonical case id เพื่อแยกหลักฐานข้าม run/case และยังอยู่ภายใต้ private-local artifact policy

## Current support matrix

| Area | Status |
|---|---|
| Android DEV | ETB configured; canonical APK `apps/android/app-dev.apk`; DEV emulator `emulator-5554`; real runs require environment/device/CIS readiness |
| Android SIT | ETB configured/gated; canonical APK `apps/android/app-sit-mmplot2.apk`; SIT emulator `emulator-5556`; mobile runtime opens only after external CIS readiness confirmation |
| DEV_MOCK | Diagnostic/mock ETB lane; requires installed approved mock target + `CIS_READINESS_SOURCE=MOCK_BUILD_NOT_REQUIRED`; runner does not install APK |
| macOS runner | Supported |
| Windows runner | Git Bash path documented; clean-machine validation pending |
| Android emulator | ETB according to lane/case scope and dry-run; NTB/full health check OCR capture remains real-device-only |
| Android real device | Required for NTB, full health check, OCR capture and post-capture |
| iOS | Not implemented |
| UAT | Not configured |
| Reproducible mobile dependency baseline | `requirements-mobile.lock.txt` exists as exact tested snapshot; F17 Git-index/clean-candidate proof passes, while independent clean-machine fresh-install proof remains pending |
| Parallel execution | Not configured |
| Device cloud | Not integrated |
| CI/CD | Health-check script exists; pipeline integration not complete |

## Known limitations

1. Emulator camera ไม่มี usable frame จึงไม่รองรับ OCR capture จริง
2. DOB picker บน real device ยังต้องการ runtime validation เพิ่ม
3. Environment readiness ยังทำให้ผลเป็น blocker ได้: DEV = VPN/CIS/backend, SIT = external CIS confirmation, DEV_MOCK = approved mock context
4. DEV/SIT ใช้ package และ canonical APK แยกกัน; UAT ยังไม่ configured และ DEV_MOCK พึ่ง preinstalled approved mock target
5. `requirements.txt` ยังเป็น minimum-range install contract; `requirements-mobile.lock.txt` เป็น exact tested snapshot และ F17 Git-index/clean-candidate proof ปิดแล้ว (`F17_CLEAN_CHECKOUT_PROOF=PASS`) แต่ independent clean-machine fresh-install proof ยัง pending
6. Report และ investigation evidence อาจมีข้อมูลอ่อนไหว ต้อง sanitize ก่อนแชร์

## Definition of a trustworthy result

ผล automation จะถือว่าใช้อ้างอิงได้เมื่อ:

1. ใช้ approved APK และ approved synthetic/local profile
2. Appium, UiAutomator2, ADB และ device doctor ผ่าน
3. Device แสดงเป็น `device` ใน `adb devices`
4. DEV/VPN/backend พร้อม
5. เลือก suite/case/tag ถูกต้อง
6. Robot report จบด้วย expected terminal state
7. Log/report/evidence ผ่านการตรวจข้อมูลอ่อนไหวก่อนส่งต่อ

ถ้า environment ไม่พร้อม ให้รายงานเป็น `BLOCKED` พร้อมหลักฐานที่ mask แล้ว ไม่ควรสรุปเป็น product defect โดยไม่มี evidence
