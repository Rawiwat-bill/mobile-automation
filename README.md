
# Mobile Banking Automation

This repository runs the Android ETB and NTB onboarding business flows with Robot Framework and Appium.

## One-time setup

```sh
./setup
```

The setup command creates a local Python environment and installs the committed runtime dependencies. It does not require any developer tooling or internal reference files.

The Android application package is supplied separately. Put the approved APK at `apps/android/app.apk` and start an emulator or connect an Android device before running a flow.

## Run a flow

```sh
./run etb
./run etb TC-ETB-013
./run etb --tag rgi
./run etb --smoke
./run etb --dry-run
./run ntb
```

ETB runs the canonical consolidated suite at `tests/android/etb/etb_regression.robot`. Testcase and tag selection are owned by Robot metadata; `--smoke` selects the `smoke` tag. `--dry-run` validates selection without opening Appium or changing CIS/PDPA state. Runtime ETB data is local-only: set `ETB_CASE_PROFILES=/path/to/approved/etb_cases.local.yaml` before a real run. NTB runtime data is also local-only: set `NTB_TESTDATA=/path/to/approved/ntb.local.yaml` before a real run. Never commit either file or its values.

Results are written under `reports/run-<flow>/`. Open `report.html` for the summary and `log.html` for step details.

## Health check

```sh
HEALTH_CHECK_TESTDATA=/path/to/approved/ntb.local.yaml ./health-check
```

Use `HEALTH_CHECK_TESTDATA=/path/to/approved/ntb.local.yaml ./health-check --dryrun` to validate Robot syntax without launching the application. Set `HEALTH_CHECK_TESTDATA=/path/to/approved/ntb.local.yaml` first; no private profile is committed. The health-check wrapper requires this variable even for a dry-run so that CI cannot accidentally fall back to local machine state.

## Contributor workflow

```sh
./setup
./run etb --dry-run
./health-check --dryrun
python3 -m unittest discover -s tests -p 'test_*.py'
```

The repository intentionally contains no runnable customer profile. Obtain approved synthetic or local test data through the team's secure channel and keep it in a gitignored `.local.yaml` file. The committed `*.example.yaml` files are documentation examples only and must not be used as real customer data.

## Troubleshooting

- `APP_NOT_FOUND`: verify `apps/android/app.apk` exists and that the configured package/activity in `resources/app/app_constants.resource` matches the APK.
- `APPIUM_NOT_READY`: start Appium on `http://127.0.0.1:4723` with relaxed security.
- `DEVICE_NOT_FOUND`: verify `adb devices` shows an authorised emulator or device.
- A flow failure: open the corresponding `reports/run-<flow>/log.html`, then consult `docs/KNOWN_LIMITATIONS.md`.

Business source diagrams are maintained in SharePoint and are intentionally not stored in this repository. Do not add private SharePoint URLs, credentials, tokens, or production data to Git.
