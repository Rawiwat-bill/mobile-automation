# Appium Playbook

## When to Use
- Diagnosing an Appium session failure
- Investigating a device connection issue
- Configuring capabilities for a new device or platform
- Troubleshooting gesture or interaction failures
- Setting up a new Appium server instance

## Inputs Required
- Device type (emulator or real device, Android version)
- Appium server URL and port
- App package name and activity (from existing config)
- App path or app capability

## Evidence Required
- Appium server log output
- `adb devices` output
- Appium session creation log
- Page source XML for interaction issues
- Screenshot for visual state confirmation

## Step-by-Step Workflow
1. Verify Appium server is running: check endpoint at `http://localhost:4723`.
2. Verify device is connected: `adb devices`.
3. Check capabilities match the target device and app.
4. Start an Appium Inspector session to explore the app interactively.
5. For interaction issues:
   - Capture page source XML.
   - Verify element exists, is visible, and is enabled.
   - Try different interaction strategies (click, tap, adb shell).
6. For React Native issues:
   - If `Click Element` fails, try `adb shell input tap` with bounds.
   - If `Input Text` fails, try `Press Keycode` per digit.
   - If swipe fails, try `adb shell input swipe`.
7. Distinguish automation issue from app, device, environment, backend, data issues.
8. Document findings and any capability changes required.

## Validation
- Confirm Appium session starts successfully: `python3 -m robot --dryrun <test_path>`.
- Confirm device interaction works: run a minimal test that taps a known element.
- If capabilities changed: verify both session creation and interaction.

## Output Format
Summary:
Environment:
Device:
Appium Finding:
Suspected Area:
Evidence:
Files Checked:
Files Changed:
Validation Command:
Validation Result:
Risk / Note:

## Stop Conditions
- **AppPackage or AppActivity unknown** — stop, never guess.
- **Element not visible in page source** — stop, collect evidence first.
- **Device not connected** — stop, ask user to connect device.
- **Appium server not reachable** — stop, ask user to start Appium.
- **Session fails with capability mismatch** — stop, verify capabilities with user.
