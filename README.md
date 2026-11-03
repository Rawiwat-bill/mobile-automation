# Mobile Banking Automation - Business Runbook

คู่มือนี้สำหรับผู้ใช้งานฝั่ง Business/QA ที่ต้องการ clone โปรเจกต์ ติดตั้งเครื่องมือ และรัน Android automation บน macOS หรือ Windows โดยไม่ต้องเข้าใจโครงสร้างโค้ดทั้งหมด

ภาพรวม coverage, flow, architecture และข้อจำกัดรวมอยู่ที่ [AUTOMATION_OVERVIEW.md](AUTOMATION_OVERVIEW.md)

> ขอบเขตปัจจุบัน: Android automation โดย ETB runner เลือก environment ผ่าน `ETB_ENVIRONMENT=DEV`, `ETB_ENVIRONMENT=SIT` หรือ `ETB_ENVIRONMENT=DEV_MOCK`; ยังไม่รองรับ iOS หรือ UAT เส้นทาง Windows Git Bash มีคู่มือตาม runtime ปัจจุบัน แต่ยังรอ clean-machine validation บน Windows

## 1. สิ่งที่ต้องขอก่อนเริ่ม

ขอจากทีม Automation ผ่านช่องทางที่ได้รับอนุมัติ:

1. สิทธิ์ clone repository
2. APK สำหรับ DEV
3. ไฟล์ test data แบบ synthetic/approved (`*.local.yaml`)
4. สิทธิ์ VPN/DEV backend ถ้าจะรันจริง
5. CA bundle สำหรับ CIS/PDPA ถ้าสภาพแวดล้อมของทีมกำหนด

ห้ามนำข้อมูลลูกค้าจริง, Citizen ID, เบอร์โทร, account, password, OTP, token, certificate หรือ APK ขึ้น Git

## 2. เวอร์ชันที่รองรับ

| เครื่องมือ | ข้อกำหนด | Tested baseline ของโปรเจกต์ |
|---|---:|---:|
| Python | 3.8+ | 3.14.7 |
| Robot Framework | `>=7.0` | 7.4.2 |
| AppiumLibrary | `>=3.0` | 3.2.1 |
| PyYAML | `>=6.0` | 6.0.3 |
| Node.js | `^20.19.0`, `^22.12.0` หรือ `>=24.0.0`; แนะนำ LTS | 24.16.0 |
| npm | 10+ | 12.0.2 |
| Java JDK | 17 แนะนำ | 17.0.12 |
| Appium | 3.x | 3.5.0 |
| UiAutomator2 driver | 7.x | 7.6.1 |
| Android SDK Platform-Tools | ต้องมี `adb` | 37.0.0 |

ไฟล์ `requirements.txt` ระบุ minimum version สำหรับ install ปกติ ส่วน `requirements-mobile.lock.txt` เป็น exact snapshot จาก `.venv` ที่ใช้ตรวจ mobile automation รอบปัจจุบัน (รวม transitive packages) เพื่อเป็น tested reproducibility baseline ปัจจุบัน F17 Git-index proof ผ่านแล้ว (`F17_CLEAN_CHECKOUT_PROOF=PASS`): transfer set จาก Git index สามารถสร้าง clean candidate และ `TC-ETB-001 --dry-run` ผ่านได้ อย่างไรก็ตาม independent clean-machine fresh-install proof ยังไม่ได้รัน จึงยังไม่ควรอ้างว่า dependency setup ถูกพิสูจน์บนเครื่องใหม่ครบถ้วน

เอกสารต้นทาง: [Appium requirements](https://appium.io/docs/en/latest/quickstart/requirements/), [Appium installation](https://appium.io/docs/en/latest/quickstart/install/), [UiAutomator2 setup](https://appium.io/docs/en/latest/quickstart/uiauto2-driver/), [Android SDK Manager](https://developer.android.com/tools/sdkmanager), [Robot Framework installation](https://robotframework.org/robotframework/latest/RobotFrameworkUserGuide.html#installation-instructions)

## 3. ติดตั้งบน macOS

### 3.1 ติดตั้งโปรแกรมพื้นฐาน

ติดตั้ง Xcode Command Line Tools:

```bash
xcode-select --install
```

ติดตั้งเครื่องมือต่อไปนี้จาก official installer หรือ package manager ขององค์กร:

- [Python 3.14](https://www.python.org/downloads/)
- [Node.js 24 LTS](https://nodejs.org/en/download)
- [JDK 17](https://adoptium.net/temurin/releases/?version=17)
- [Android Studio](https://developer.android.com/studio)

ใน Android Studio > SDK Manager ให้ติดตั้ง:

- Android SDK Platform ที่รองรับ APK ของทีม
- Android SDK Platform-Tools
- Android SDK Command-line Tools (latest)
- Android Emulator และ system image ถ้าจะใช้ emulator

เพิ่ม Android SDK ลง `~/.zshrc`:

```bash
export JAVA_HOME="$(/usr/libexec/java_home -v 17)"
export PATH="$JAVA_HOME/bin:$PATH"
export ANDROID_HOME="$HOME/Library/Android/sdk"
export PATH="$PATH:$ANDROID_HOME/platform-tools:$ANDROID_HOME/emulator:$ANDROID_HOME/cmdline-tools/latest/bin"
```

เปิด Terminal ใหม่ แล้วรับ Android licenses:

```bash
sdkmanager --licenses
```

### 3.2 ติดตั้ง Appium

```bash
npm install -g appium@3.5.0
appium driver install uiautomator2@7.6.1
```

ถ้า driver ถูกติดตั้งแล้วและคำสั่งแจ้งว่า installed อยู่แล้ว ให้ตรวจเวอร์ชันแทน ไม่ต้องติดตั้งซ้ำ:

```bash
appium --version
appium driver list --installed
appium driver doctor uiautomator2
```

### 3.3 Clone และติดตั้ง Python dependencies

```bash
git clone <REPOSITORY_URL> mobile-banking-automation
cd mobile-banking-automation
./setup
```

## 4. ติดตั้งบน Windows

Runner ของโปรเจกต์เป็น Bash เพื่อให้ใช้คำสั่งชุดเดียวกันบน macOS และ Windows ฝั่ง Windows ให้รันผ่าน **Git Bash** ไม่ใช่ Command Prompt

### 4.1 ติดตั้งด้วย Windows Package Manager

เปิด PowerShell แบบปกติ:

```powershell
winget install --exact --id Git.Git
winget install --exact --id Python.Python.3.14
winget install --exact --id OpenJS.NodeJS.LTS
winget install --exact --id EclipseAdoptium.Temurin.17.JDK
winget install --exact --id Google.AndroidStudio
```

หา JDK 17 directory ที่ติดตั้งจริง:

```powershell
Get-ChildItem "C:\Program Files\Eclipse Adoptium" -Directory
```

ตั้ง `JAVA_HOME` โดยแทน `<JDK_17_DIRECTORY>` ด้วย directory ที่คำสั่งด้านบนแสดง:

```powershell
[Environment]::SetEnvironmentVariable("JAVA_HOME", "<JDK_17_DIRECTORY>", "User")
```

ปิดและเปิด Terminal ใหม่หลังติดตั้ง จากนั้นเปิด Android Studio > SDK Manager และติดตั้งรายการเดียวกับ macOS

### 4.2 ตั้งค่า Android SDK ใน Git Bash

เพิ่มบรรทัดต่อไปนี้ใน `~/.bashrc`:

```bash
export ANDROID_HOME="/c/Users/$USERNAME/AppData/Local/Android/Sdk"
export PATH="$PATH:$ANDROID_HOME/platform-tools:$ANDROID_HOME/emulator:$ANDROID_HOME/cmdline-tools/latest/bin"
```

เปิด Git Bash ใหม่ แล้วรัน:

```bash
sdkmanager --licenses
npm install -g appium@3.5.0
appium driver install uiautomator2@7.6.1
```

### 4.3 Clone และติดตั้ง Python dependencies

ใน Git Bash แนะนำให้ clone ไว้ใน path ที่ไม่มีช่องว่างเพื่อให้ shell tooling และ project runner ทำงานสม่ำเสมอ:

```bash
mkdir -p /c/automation
cd /c/automation
git clone <REPOSITORY_URL> mobile-banking-automation
cd mobile-banking-automation
python -m venv .venv
./.venv/Scripts/python.exe -m pip install --upgrade pip
./.venv/Scripts/python.exe -m pip install -r requirements.txt
export PYTHON_BIN="$PWD/.venv/Scripts/python.exe"
```

`./setup` ใช้ layout `.venv/bin/python` ของ macOS/Linux จึงไม่ใช้บน Windows ให้ใช้คำสั่งด้านบน และกำหนด `PYTHON_BIN` ทุกครั้งที่เปิด Git Bash ใหม่ก่อนเรียก `./run`

## 5. ตรวจเครื่องก่อนรัน

ใช้คำสั่งนี้ได้ทั้ง macOS Terminal และ Windows Git Bash:

```bash
git --version
python3 --version || python --version
node --version
npm --version
java -version
printf 'JAVA_HOME=%s\n' "$JAVA_HOME"
adb version
appium --version
appium driver list --installed
appium driver doctor uiautomator2
"${PYTHON_BIN:-./.venv/bin/python}" -m robot --version
```

ผลที่ต้องได้:

- `adb` ถูกเรียกได้
- `JAVA_HOME` ชี้ไปที่ JDK 17 directory จริง
- Appium แสดงเวอร์ชัน 3.x
- installed drivers มี `uiautomator2`
- Robot Framework แสดงเวอร์ชัน 7.x
- `appium driver doctor uiautomator2` ไม่มี required check ที่ fail

## 6. เตรียม APK และอุปกรณ์

ETB ใช้ canonical APK แยกตาม environment:

```text
DEV: apps/android/app-dev.apk
SIT: apps/android/app-sit-mmplot2.apk
```

`DEV_MOCK` ไม่ติดตั้ง APK จาก runner; ต้องมี approved mock target ติดตั้งอยู่ก่อน และต้องตั้ง `CIS_READINESS_SOURCE=MOCK_BUILD_NOT_REQUIRED`

เปิด emulator หรือเชื่อม Android device ที่เปิด Developer Options และ USB debugging แล้วตรวจ serial ที่จะใช้:

```bash
adb devices
```

สถานะเป้าหมายต้องเป็น `device` ไม่ใช่ `unauthorized` หรือ `offline` จากนั้นตั้ง `DEVICE_UDID` ให้ตรงกับ environment/device ที่ต้องการ เช่น DEV emulator `emulator-5554` หรือ SIT emulator `emulator-5556`. Runner ส่ง serial นี้เข้า ADB/Robot runtime และใช้ target guard ก่อน CIS/package preparation. สำหรับ `./run etb --dry-run` ไม่ต้องตั้ง `DEVICE_UDID` เพราะเป็น syntax/selection-only และจะไม่เข้า device/backend preflight

เมื่อรันจริง DEV/SIT runner จะตรวจ package/activity, ลบเฉพาะ competing package บน device เป้าหมาย และติดตั้ง canonical APK เฉพาะเมื่อ target package ยังไม่มี; ไม่ต้อง `adb install` ด้วย path กลางเอง

## 7. เตรียม test data

ไฟล์ที่ commit อยู่เป็น schema/example เท่านั้น การรันจริงต้องใช้ approved local data:

```text
testdata/onboarding/etb_cases.local.yaml
testdata/onboarding/ntb.local.yaml
```

ETB ใช้ `ETB_CASE_PROFILES` เป็น runtime profile source. ถ้าไม่กำหนด runner จะ default ไปที่ `testdata/onboarding/etb_cases.local.yaml`; ถ้ากำหนด path อื่น runner จะ resolve เป็น absolute path แล้วส่ง source เดียวกันให้ Robot ทั้ง selector dry-run และ runtime. การรันจริงต้องให้ไฟล์นั้นอ่านได้และเป็น approved local YAML; dry-run ไม่อ่าน profile contents

กำหนด environment variables ใน Terminal/Git Bash เดียวกับที่จะรัน โดยขอ endpoint และ CA bundle ผ่านช่องทางปลอดภัยของทีม ห้ามใส่ค่าจริงใน README หรือ Git:

```bash
export NTB_TESTDATA="$PWD/testdata/onboarding/ntb.local.yaml"
export CIS_CLEAR_URL="<TEAM_APPROVED_CIS_CLEAR_URL>"
export PDPA_BASE_URL="<TEAM_APPROVED_PDPA_BASE_URL>"
export PDPA_CA_BUNDLE="$PWD/local/certs/cis-ca-bundle.pem"
```

- `CIS_CLEAR_URL` จำเป็นสำหรับ ETB real run ทุก case
- `PDPA_BASE_URL` จำเป็นเมื่อ full regression รวม TC-ETB-002
- `PDPA_CA_BUNDLE` ต้องชี้ไปที่ approved CA file ที่ทีมส่งให้ และเก็บใต้ `local/` ซึ่งถูก gitignore
- ถ้าไม่ได้รับ endpoint/CA ให้หยุดและขอทีม Automation ห้ามเดาค่าเอง

อย่า print, paste หรือแนบค่าจาก local data ลง log, ticket, chat หรือ Git

## 8. Start Appium

ใช้ managed Appium launcher ของ project เป็น canonical entry point:

```bash
pnpm appium
```

launcher จะ bind ที่ `127.0.0.1` และเปิดเฉพาะ `--allow-insecure=uiautomator2:adb_shell` ที่ framework ต้องใช้ ห้ามใช้ `--relaxed-security` เป็น default และห้าม expose server ผ่าน LAN, public interface หรือ port forwarding

ถ้าต้องใช้ Inspector ให้เปิดแบบ explicit:

```bash
pnpm appium:inspector
```

## 9. Run automation

เปิด Terminal/Git Bash อีกหน้าต่าง เข้า project directory และตั้ง environment variables ตามข้อ 7

### ตรวจ syntax/selection ก่อน โดยไม่เปิด Appium session

```bash
./run etb --dry-run
```

### ETB

ตัวอย่าง DEV emulator:

```bash
ETB_ENVIRONMENT=DEV ANDROID_EXECUTION_TARGET=DIAGNOSTIC_CONTROL DEVICE_UDID=emulator-5554 ./run etb
ETB_ENVIRONMENT=DEV ANDROID_EXECUTION_TARGET=DIAGNOSTIC_CONTROL DEVICE_UDID=emulator-5554 ./run etb TC-ETB-013
./run etb --tag rgi
./run etb --smoke
```

ตัวอย่าง SIT emulator ใช้ `ETB_ENVIRONMENT=SIT` และ serial ของ SIT โดย runner จะเปิด external CIS readiness gate ก่อน mobile runtime:

```bash
ETB_ENVIRONMENT=SIT ANDROID_EXECUTION_TARGET=DIAGNOSTIC_CONTROL DEVICE_UDID=emulator-5556 ./run etb TC-ETB-001
```

`DEV_MOCK` เป็น diagnostic/mock lane และต้องใช้ approved mock target ที่ติดตั้งอยู่แล้ว พร้อม `CIS_READINESS_SOURCE=MOCK_BUILD_NOT_REQUIRED`; runner จะไม่ติดตั้ง APK ให้ lane นี้

### NTB

`./run ntb` เป็น **real-device-only** ใน implementation ปัจจุบัน เพราะ flow แตะ `Take Photo` จริง ห้ามใช้คำสั่งนี้กับ emulator

```bash
./run ntb
```


## 10. ผลลัพธ์

| คำสั่ง | Output |
|---|---|
| `./run etb ...` | `reports/run-etb/` |
| `./run ntb` | `reports/run-ntb/` |

ไฟล์หลัก:

- ETB/NTB: `report.html`, `log.html`, `output.xml`

ก่อนแชร์ report/log/screenshot ต้องตรวจและ mask PII, OTP, token, account และ device identifier ทุกครั้ง

## 11. Troubleshooting

| อาการ | ตรวจอะไร |
|---|---|
| `python3: command not found` บน Windows | ใช้ Git Bash, สร้าง `.venv` ตามข้อ 4.3 และ export `PYTHON_BIN` |
| `adb: command not found` | ตรวจ `ANDROID_HOME` และ `PATH` |
| Appium doctor แจ้ง `JAVA_HOME` fail | ตั้ง `JAVA_HOME` ตามข้อ 3.1 หรือ 4.1 แล้วเปิด Terminal ใหม่ |
| device เป็น `unauthorized` | ปลดล็อก device และกดอนุญาต USB debugging |
| Appium หา driver ไม่พบ | `appium driver install uiautomator2@7.6.1` |
| Appium ไม่พร้อม | ใช้ `pnpm appium`; สำหรับ Inspector ใช้ `pnpm appium:inspector` |
| APK ไม่พบ/เปิดไม่ได้ | ตรวจ environment ที่เลือก: DEV ใช้ `apps/android/app-dev.apk`; SIT ใช้ `apps/android/app-sit-mmplot2.apk`; DEV_MOCK ต้องมี approved mock target ติดตั้งอยู่ก่อน |
| ETB readiness fail | ตรวจ readiness ตาม lane: DEV = VPN/CIS/backend, SIT = external CIS confirmation, DEV_MOCK = mock-build contract |
| ETB หา profile ไม่พบ | ตรวจ `ETB_CASE_PROFILES`; ถ้าไม่กำหนดจะใช้ `testdata/onboarding/etb_cases.local.yaml` และ real run ต้องอ่านไฟล์ได้ |
| Emulator ไปต่อหลัง OCR ไม่ได้ | เป็นข้อจำกัดที่ยืนยันแล้ว ให้ใช้ real device |
| Test fail | เปิด `log.html` ของ run นั้นและส่งเฉพาะหลักฐานที่ mask แล้วให้ทีม Automation |

## 12. Clean rerun

ไม่ต้องลบ repository หรือ reinstall ทุกครั้ง ให้ทำเฉพาะเมื่อ dependency เสีย:

```bash
rm -rf .venv
./setup
```

Windows ให้ลบ `.venv` ใน Git Bash แล้วทำข้อ 4.3 ใหม่แทน `./setup` ถ้ายังแก้ไม่ได้ ให้เก็บข้อความ error ที่ไม่มีข้อมูลอ่อนไหว พร้อมผลจากข้อ 5 ส่งให้ทีม Automation


## ETB Traceability and acceptance references

- Full static traceability TC001–TC013: `docs/standards/ETB_TRACEABILITY_MATRIX.md`
- Machine-readable registry: `configs/etb_traceability_full.json`
- Current acceptance snapshot: `docs/standards/BBL_ETB_ACCEPTANCE_SNAPSHOT_2026-09-27.md`
- Current remediation status: `docs/standards/BBL_REMEDIATION_CHECKLIST.md`
