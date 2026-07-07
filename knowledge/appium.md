# Appium Knowledge

## Session Configuration

Appium must start with `--relaxed-security` for `adb shell` commands:
```bash
appium --relaxed-security
```

Without this flag, `Execute Adb Shell` is blocked by Appium's security policy.

## Automation Engine

- **Android:** UiAutomator2 (automationName: `UiAutomator2`)
- **iOS:** XCUITest (not yet implemented, scoped for future)

## React Native Compatibility

The app uses React Native with custom gesture handling. Appium's `Click Element`, `Tap`, and W3C Actions do not reliably trigger RN `TouchableOpacity`/`onPress` handlers. The proven workaround is `adb shell input tap` at the element's center coordinates.

For text input, Appium `Input Text` (which uses `element.sendKeys()` → UiAutomator2 `setText()`) triggers RN `onChangeText` reliably with a single event containing the full value. This was verified byte-identical to manual typing in Sprint 2.10.3 (cid_input_parity). `Input Text` is now the production method for Citizen ID and Mobile Number fields — keycodes have been removed from production paths.

For gesture components (buttons, pickers), `Input Text` does NOT trigger RN `onPress`/`onChange` handlers — those still require `adb shell input tap` or adb swipe.

## Gesture Patterns

- **Tap:** Element-based via Appium or coordinate-based via adb shell
- **Swipe/Scroll:** adb shell swipe for consent terms scrolling
- **Long press:** Not yet needed, use W3C Actions when required

## Known Limitations

- Appium `Input Text` reliably fills RN TextInput fields (verified: Citizen ID, Mobile Number). Fails for picker-based fields (DOB) — those require adb swipe + picker interaction.
- `Clear Text` may not work on RN fields that manage their own state. Use `Tap Profile Element Center` first to focus the field before clearing.
- `Hide Keyboard` may not dismiss the keyboard on some devices/OS versions
- Coordinate-based `Tap` from Appium does not trigger RN gesture handlers (buttons, picker scroll). Use `adb shell input tap` for gesture components.

## Internal Project Truth

This knowledge overrides external appium-skill guidance when React Native behavior contradicts standard Appium patterns. Appium Inspector and real device evidence always take precedence over skill suggestions.
