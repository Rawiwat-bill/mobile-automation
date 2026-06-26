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

For text input, Appium `Input Text` (which uses `element.sendKeys()`) does not trigger RN `onChange` events reliably. `adb shell input keyevent` per digit (keycodes) is the proven approach for Citizen ID and Mobile Number.

## Gesture Patterns

- **Tap:** Element-based via Appium or coordinate-based via adb shell
- **Swipe/Scroll:** adb shell swipe for consent terms scrolling
- **Long press:** Not yet needed, use W3C Actions when required

## Known Limitations

- Appium `Send Keys` may trigger the soft keyboard without filling the field on RN
- `Clear Text` may not work on RN fields that manage their own state
- `Hide Keyboard` may not dismiss the keyboard on some devices/OS versions
- Coordinate-based `Tap` from Appium does not trigger RN navigation buttons

## Internal Project Truth

This knowledge overrides external appium-skill guidance when React Native behavior contradicts standard Appium patterns. Appium Inspector and real device evidence always take precedence over skill suggestions.
