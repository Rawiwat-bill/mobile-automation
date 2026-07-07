# 09 — Environment Review

> Target environments: **DEV, SIT, UAT**.
> Do NOT recommend LOCAL as an environment.

## Current State

### Config Files

| File | Content | Status |
|------|---------|--------|
| `configs/env/dev.yaml` | **EMPTY (0 bytes)** | No environment configuration |
| `configs/devices/emulator.yaml` | **EMPTY (0 bytes)** | No device configuration |
| `configs/devices/real_device.yaml` | **EMPTY (0 bytes)** | No device configuration |

### Hardcoded Environment Values

| Value | Location | Used By |
|-------|----------|---------|
| `com.bangkokbank.blue.dev` | `app_keywords.resource:10` | All production tests |
| `com.bangkokbank.blue.dev` | `benchmark_base.resource:11` | All benchmark tests |
| `com.bangkokbank.blue.dev` | `api_capture_keywords.resource:7` | API capture |
| `com.bangkokbank.blue.MainActivity` | `app_keywords.resource:22` | All production tests |
| `com.bangkokbank.blue.MainActivity` | `benchmark_base.resource:12` | All benchmark tests |
| `http://127.0.0.1:4723` | `app_keywords.resource:16` | Appium URL |
| `http://127.0.0.1:4723` | `benchmark_base.resource:13` | Appium URL |
| `Android Emulator` | `app_keywords.resource:19` | Device name |
| `Android Emulator` | `benchmark_base.resource:14` | Device name |
| `${CURDIR}/../../apps/android/app.apk` | `app_keywords.resource:20` | APK path |
| `${CURDIR}/../../apps/android/app.apk` | `benchmark_base.resource:15` | APK path |

### Test Data by Environment

| File | Environment | PII? | Status |
|------|-------------|------|--------|
| `ntb.example.yaml` | Example (safe) | No — all 1s | Tracked |
| `etb.example.yaml` | Example (safe) | No — all 2s | Tracked |
| `ntb.local.yaml` | LOCAL (real PII) | **Yes** — citizen ID, phone, names | Gitignored |
| `etb.local.yaml` | LOCAL | N/A — empty | Gitignored |

---

## Findings

### Critical

| # | Finding | Evidence | Impact |
|---|---------|----------|--------|
| 1 | No SIT or UAT environment configuration exists | `configs/env/` has only `dev.yaml` (empty) | Cannot run tests against SIT/UAT |
| 2 | App package hardcoded to DEV (`com.bangkokbank.blue.dev`) in 3 places | See table above | Switching to SIT/UAT requires code changes in 3 files |
| 3 | `configs/` directory is entirely empty | All 3 YAML files are 0 bytes | Config scaffold exists but was never populated |

### High

| # | Finding | Evidence | Recommendation |
|---|---------|----------|----------------|
| 4 | No environment variable override mechanism | App package is a `${VARIABLE}` in Robot but set to a literal, not from config/env | Load from `configs/env/<env>.yaml` via `config_loader.py` |
| 5 | Appium URL hardcoded to localhost | `http://127.0.0.1:4723` | Should be configurable for remote Appium (SaaS, grid) |
| 6 | Device name hardcoded to "Android Emulator" | `app_keywords.resource:19` | Real device tests need different deviceName; should come from `configs/devices/` |
| 7 | APK path hardcoded | `apps/android/app.apk` | SIT/UAT may use different APK; should be configurable |

### Medium

| # | Finding | Evidence | Recommendation |
|---|---------|----------|----------------|
| 8 | `ntb.local.yaml` uses real PII | citizen_id `3872637115880`, phone `0625591307` | LOCAL is not an environment per requirements; this data should be in a gitignored `.env` or secret manager, not a YAML that could be confused with environment config |
| 9 | Date format differs between example and local data | Example: `1990-01-01` (YYYY-MM-DD), Local: `15-01-1992` (DD-MM-YYYY) | Production code expects DD-MM-YYYY; example data doesn't match. See `ponytail_audit.md` and `knowledge/profile/dob_picker.md` |
| 10 | `live_demo.robot` hardcodes device UDID | `48ZYD25C01422768` | Should be in `configs/devices/real_device.yaml` |

---

## Recommended Environment Structure

```
configs/
├── env/
│   ├── dev.yaml          # DEV environment
│   ├── sit.yaml          # SIT environment
│   └── uat.yaml          # UAT environment
├── devices/
│   ├── emulator.yaml     # Emulator capabilities
│   └── real_device.yaml  # Real device capabilities
└── default.yaml          # Fallback / shared defaults
```

### Example `configs/env/dev.yaml`

```yaml
app_package: "com.bangkokbank.blue.dev"
app_activity: "com.bangkokbank.blue.MainActivity"
appium_url: "http://127.0.0.1:4723"
apk_path: "apps/android/app.apk"
```

### Example `configs/env/sit.yaml`

```yaml
app_package: "com.bangkokbank.blue.sit"
app_activity: "com.bangkokbank.blue.MainActivity"
appium_url: "http://127.0.0.1:4723"
apk_path: "apps/android/app-sit.apk"
```

### Example `configs/devices/emulator.yaml`

```yaml
platform_name: "Android"
automation_name: "UiAutomator2"
device_name: "Android Emulator"
no_reset: false
```

### Example `configs/devices/real_device.yaml`

```yaml
platform_name: "Android"
automation_name: "UiAutomator2"
udid: "${DEVICE_UDID}"  # From environment variable, not hardcoded
platform_version: "10"
no_reset: true
```

---

## Environment Selection Mechanism

Tests should select environment via a variable:

```robotframework
# In test or suite setup
${env}=    Get Environment Variable    TEST_ENV    dev
${config}=    Load YAML    configs/env/${env}.yaml
Set Suite Variable    ${APP_PACKAGE}    ${config['app_package']}
Set Suite Variable    ${APP_ACTIVITY}    ${config['app_activity']}
```

Run with: `TEST_ENV=sit python3 -m robot -d reports tests/android/ntb/ntb_flow.robot`

---

## Recommendation

C2 should:
1. Populate `configs/env/dev.yaml` with current hardcoded values.
2. Create `configs/env/sit.yaml` and `configs/env/uat.yaml` (even if values are TBD).
3. Populate `configs/devices/emulator.yaml` and `real_device.yaml`.
4. Refactor `app_keywords.resource` to load from config instead of hardcoding.
5. Refactor `benchmark_base.resource` to import from `app_keywords` (eliminates duplicate hardcoding).
6. Remove `ntb.local.yaml` PII from working tree or mask values — LOCAL is not an environment.
7. Standardize date format across all test data files.
