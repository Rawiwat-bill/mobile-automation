# Date of Birth (DOB) Picker — Full Reference

> Purpose: collect every date-picker-related locator, keyword, data format,
> and app-structure fact in one place so an AI (or human) can propose an
> alternative automation approach. The current swipe-based wheel approach is
> flaky — see "Known Problems" at the bottom.

---

## 1. App Structure (from Appium XML evidence)

The DOB picker is **NOT** the Android native `DatePickerDialog`. It is a
**custom React Native wheel picker** with three independent scroll wheels.

Source XML: `reports/investigation/input_value_verification/dob_picker_opened.xml`

### The DOB input field (picker closed)

```
resource-id = "screenProfile_textInputDob"
content-desc = "profile_screen.dob"
class       = android.widget.EditText
text        = "Select date of birth"   (placeholder / hint when empty)
container   = "screenProfile_textInputDob-container"
label text  = "Date of birth"
```

The field is **read-only display** — tapping it opens the custom wheel picker.
Typing into it directly does NOT set the value (tested: see benchmark
strategies `input_text`, `input_value`, `adb_shell` — all failed to register).

### The three picker wheels (picker open)

Each wheel is an `android.widget.SeekBar` whose **`content-desc` carries the
current selected value** in the format `"<Kind> picker, <value>"`.

| Wheel  | resource-id                                         | content-desc example       | values          |
|--------|-----------------------------------------------------|----------------------------|-----------------|
| Day    | `screenProfile_calendarDatePicker-dateScroll`       | `"Day picker, 1"`          | 1–31 (numeric)  |
| Month  | `screenProfile_calendarDatePicker-monthScroll`      | `"Month picker, January"`  | January–December (English names) |
| Year   | `screenProfile_calendarDatePicker-yearScroll`       | `"Year picker, 2011"`      | ~1900–current (numeric) |

Each SeekBar contains a vertical flatlist:
```
SeekBar
 └─ ViewGroup
    └─ ScrollView  resource-id="<wheel>-flatlist"   scrollable=true
       └─ ViewGroup
          └─ ViewGroup[index]  (one per visible row)
             └─ TextView  resource-id="text"  text="<value>"  content-desc="<value>"
```

Only ~5 rows are rendered at a time (virtualized list). The **center row** is
the selected value. The selected value is ALSO echoed in the SeekBar
`content-desc` — that is the most reliable read path.

### Confirm button

```
content-desc = "Done"
resource-id  = "base-btn"            (generic, NOT screen-specific)
class        = android.widget.Button
container    = "base-btn-container"
```

### Picker wrapper

```
resource-id = "screenProfile_calendarDatePicker-selectedHeaderWrapper"
```

---

## 2. Locators (production)

File: `locators/android/onboarding/profile_screen_locators.resource`

```robotframework
${PROFILE_DOB_CONTAINER}           xpath=//*[@resource-id="screenProfile_textInputDob-container"]
${PROFILE_DOB_INPUT}               xpath=//*[@resource-id="screenProfile_textInputDob"]
${PROFILE_DOB_INPUT_FALLBACK}      xpath=//*[@content-desc="profile_screen.dob"]
${PROFILE_DOB_DAY_PICKER}          xpath=//*[@resource-id="screenProfile_calendarDatePicker-dateScroll"]
${PROFILE_DOB_MONTH_PICKER}        xpath=//*[@resource-id="screenProfile_calendarDatePicker-monthScroll"]
${PROFILE_DOB_YEAR_PICKER}         xpath=//*[@resource-id="screenProfile_calendarDatePicker-yearScroll"]
${PROFILE_DOB_CONFIRM_BUTTON}      xpath=//*[@content-desc="Done"]
```

### Locators (benchmark-isolated copy)

File: `resources/benchmark/benchmark_base.resource`

```robotframework
${BENCHMARK_DOB_INPUT}             xpath=//*[@resource-id="screenProfile_textInputDob"]
${BENCHMARK_DOB_CONTAINER}         xpath=//*[@resource-id="screenProfile_textInputDob-container"]
${BENCHMARK_DOB_DAY_PICKER}        xpath=//*[@resource-id="screenProfile_calendarDatePicker-dateScroll"]
${BENCHMARK_DOB_MONTH_PICKER}      xpath=//*[@resource-id="screenProfile_calendarDatePicker-monthScroll"]
${BENCHMARK_DOB_YEAR_PICKER}       xpath=//*[@resource-id="screenProfile_calendarDatePicker-yearScroll"]
${BENCHMARK_DOB_CONFIRM}           xpath=//*[@content-desc="Done"]
```

---

## 3. Test Data Format

File: `testdata/onboarding/ntb.example.yaml`

```yaml
profile:
  date_of_birth: "1990-01-01"     # YYYY-MM-DD
```

Local (gitignored): `testdata/onboarding/ntb.local.yaml`

```yaml
date_of_birth: "15-01-1992"        # DD-MM-YYYY
date_of_birth: "15 Jan. 1992"      # alt display format
```

### WARNING — date format inconsistency in the code

The **production** keyword and the **benchmark** keyword split the date string
on `-` but index the parts in **opposite order**:

| Code location | `parts[0]` | `parts[1]` | `parts[2]` | Expects |
|---------------|-----------|-----------|-----------|---------|
| `profile_screen_page.resource` → `Input Date Of Birth` | day | month | year | **DD-MM-YYYY** |
| `benchmark_strategies.resource` → `Run DOB picker_calculated` | year | month | day | **YYYY-MM-DD** |
| `benchmark_strategies.resource` → `Baseline Fill DOB` | year | month | day | **YYYY-MM-DD** |

The example data file (`1990-01-01` = YYYY-MM-DD) matches the **benchmark**
order but would be mis-parsed by the **production** keyword
(day="1990", month="01", year="01"). This must be reconciled.

---

## 4. Current Implementation (production)

File: `resources/pages/onboarding/profile_screen_page.resource`

### Entry point

```robotframework
Input Date Of Birth
    [Arguments]    ${date_of_birth}
    Start DOB Interaction
    ${parts}=    Split String    ${date_of_birth}    -
    ${day}=    Set Variable    ${parts[0]}
    ${month_token}=    Set Variable    ${parts[1]}
    ${year}=    Set Variable    ${parts[2]}
    ${month_map}=    Evaluate    {'01': 'January', '02': 'February', '03': 'March', '04': 'April', '05': 'May', '06': 'June', '07': 'July', '08': 'August', '09': 'September', '10': 'October', '11': 'November', '12': 'December'}
    ${month}=    Set Variable    ${month_token}
    ${has_numeric_month}=    Run Keyword And Return Status    Dictionary Should Contain Key    ${month_map}    ${month_token}
    IF    ${has_numeric_month}
        ${month}=    Get From Dictionary    ${month_map}    ${month_token}
    END
    Tap Profile Element Center    ${PROFILE_DOB_CONTAINER}
    Record DOB Picker Visible
    Record DOB Year Start
    TRY
        Select DOB Picker Value    ${PROFILE_DOB_YEAR_PICKER}    ${year}    number
    EXCEPT    AS    ${error}
        Record DOB Failure    year    ${year}    ${error}
        Capture DOB Failure Evidence    year    ${year}
        Fail    ${error}
    END
    Record DOB Year End
    Record DOB Month Start
    TRY
        Select DOB Picker Value    ${PROFILE_DOB_MONTH_PICKER}    ${month}    month
    EXCEPT    AS    ${error}
        Record DOB Failure    month    ${month}    ${error}
        Capture DOB Failure Evidence    month    ${month}
        Fail    ${error}
    END
    Record DOB Month End
    Record DOB Day Start
    TRY
        Select DOB Picker Value    ${PROFILE_DOB_DAY_PICKER}    ${day}    number
    EXCEPT    AS    ${error}
        Record DOB Failure    day    ${day}    ${error}
        Capture DOB Failure Evidence    day    ${day}
        Fail    ${error}
    END
    Record DOB Day End
    Click Element    ${PROFILE_DOB_CONFIRM_BUTTON}
    Tap Profile Blank Area    ${PROFILE_BLUR_AFTER_DOB_Y}
    Wait Until Profile Fields Are Blurred
    Record DOB Success
    Verify DOB Field Value    ${day}    ${year}
```

Order of selection: **Year → Month → Day**.

### Wheel value selector (swipe-based, up to 25 retries)

```robotframework
Select DOB Picker Value
    [Arguments]    ${picker_locator}    ${target_value}    ${value_kind}
    ${month_indexes}=    Evaluate    {'January': 1, 'February': 2, 'March': 3, 'April': 4, 'May': 5, 'June': 6, 'July': 7, 'August': 8, 'September': 9, 'October': 10, 'November': 11, 'December': 12}
    Wait Until Element Is Visible    ${picker_locator}    ${DOB_PICKER_TIMEOUT}
    FOR    ${index}    IN RANGE    25
        ${current_value}=    Read DOB Picker Visible Value    ${picker_locator}
        IF    '${current_value}' == '${target_value}'
            RETURN
        END
        IF    '${value_kind}' == 'month'
            ${current_index}=    Get From Dictionary    ${month_indexes}    ${current_value}
            ${target_index}=    Get From Dictionary    ${month_indexes}    ${target_value}
        ELSE
            ${current_index}=    Convert To Integer    ${current_value}
            ${target_index}=    Convert To Integer    ${target_value}
        END
        ${direction}=    Set Variable If    ${current_index} < ${target_index}    up    down
        Record DOB Picker Attempt    ${value_kind}    ${target_value}    ${current_value}    ${direction}
        ${picker_rect}=    Get Element Rect    ${picker_locator}
        ${center_x}=    Evaluate    int(${picker_rect['x']} + (${picker_rect['width']} / 2))
        ${diff}=    Evaluate    abs(int(${current_index}) - int(${target_index}))
        ${duration}=    Set Variable    500
        IF    ${diff} <= 2
            ${top_y}=    Evaluate    int(${picker_rect['y']} + (${picker_rect['height']} * 0.35))
            ${bottom_y}=    Evaluate    int(${picker_rect['y']} + (${picker_rect['height']} * 0.55))
            ${duration}=    Set Variable    50
        ELSE
            ${top_y}=    Evaluate    int(${picker_rect['y']} + (${picker_rect['height']} * 0.30))
            ${bottom_y}=    Evaluate    int(${picker_rect['y']} + (${picker_rect['height']} * 0.70))
            ${duration}=    Set Variable    50
        END
        IF    '${direction}' == 'up'
            Execute Adb Shell    input    swipe    ${center_x}    ${bottom_y}    ${center_x}    ${top_y}    ${duration}
        ELSE
            Execute Adb Shell    input    swipe    ${center_x}    ${top_y}    ${center_x}    ${bottom_y}    ${duration}
        END
        Sleep    0.1s
    END
    Record DOB Failure    ${value_kind}    ${target_value}    exhausted 25 attempts
    Capture DOB Failure Evidence    ${value_kind}    ${target_value}
    Fail    Could not select DOB picker value '${target_value}' using locator '${picker_locator}'.
```

### Current-value reader

```robotframework
Read DOB Picker Visible Value
    [Arguments]    ${picker_locator}
    Wait Until Element Is Visible    ${picker_locator}    ${DOB_PICKER_TIMEOUT}
    ${desc}=    Get Element Attribute    ${picker_locator}    content-desc
    ${desc_value}=    Set Variable    ${EMPTY}
    IF    '${desc}' != '' and '${desc}' != 'None'
        ${desc_value}=    Fetch From Right    ${desc}    ,
        ${desc_value}=    Strip String    ${desc_value}
        IF    '${desc_value}' != ''
            RETURN    ${desc_value}
        END
    END
    # Fallback: read center visible TextView in the picker wheel.
    ${result_status}    ${center_text}=    Run Keyword And Ignore Error
    ...    Get Text    ${picker_locator}/android.view.ViewGroup/android.widget.ScrollView/android.view.ViewGroup/android.view.ViewGroup[3]/android.widget.TextView
    IF    '${result_status}' == 'PASS'
        ${value}=    Strip String    ${center_text}
        IF    '${value}' != ''
            RETURN    ${value}
        END
    END
    ${desc}=    Get Element Attribute    ${picker_locator}    content-desc
    ${value}=    Fetch From Right    ${desc}    ,
    ${value}=    Strip String    ${value}
    RETURN    ${value}
```

### Verification (after Done)

```robotframework
Verify DOB Field Value
    [Arguments]    ${day}    ${year}
    ${field_text}=    Get Text    ${PROFILE_DOB_INPUT}
    ${field_digits}=    Normalize Digits    ${field_text}
    ${expected_digits}=    Set Variable    ${day}${year}
    Should Contain    ${field_digits}    ${expected_digits}
    ...    DOB field value mismatch.
```

Note: verification only checks that **day + year digits** appear in the field
text. Month is not verified (likely because it appears as a localized name).

---

## 5. Benchmark Strategies Tried

File: `resources/benchmark/benchmark_strategies.resource`

Four strategies were benchmarked for DOB input:

| Strategy          | How                                                | Result |
|-------------------|----------------------------------------------------|--------|
| `picker_calculated` | Swipe wheels by computed step count (Year→Month→Day) | Primary approach (production uses a variant of this) |
| `input_text`      | `Input Text` with slash format `YYYY/MM/DD`        | Typed into field but value did **not register** — field is display-only |
| `adb_shell`       | `adb shell input text`                             | Same — text not accepted by the RN field |
| `input_value`     | `Input Value` (RN-setter attempt)                  | Same — not accepted |

Conclusion from benchmark: **only the wheel-picker interaction sets the DOB
value**. Direct text input into `screenProfile_textInputDob` does not work
because the field opens a picker on tap rather than accepting typed input.

---

## 6. Stability Tracking

File: `resources/keywords/dob_stability_keywords.resource`

Tracks per-wheel timing, retry count, and pass/fail. Writes JSON summary to
`${OUTPUT_DIR}/stability/stability.json`. Captures screenshot + XML on failure
to `${OUTPUT_DIR}/stability/dob/dob_fail_<timestamp>.{png,xml}`.

---

## 7. Known Problems

1. **Flaky.** Many failure artifacts exist:
   `reports/*/stability/dob/dob_fail_*.{png,xml}` across 20+ report directories.
   The 25-retry swipe loop frequently exhausts without landing on the target.

2. **Swipe overshoot / undershoot.** The wheel is a virtualized RN ScrollView;
   a fixed-duration adb swipe moves an inconsistent number of rows depending on
   fling momentum. Small `diff` (≤2) and large `diff` use different swipe
   geometries but both are unreliable.

3. **content-desc lag.** After a swipe, the SeekBar `content-desc` may not
   update immediately; the 0.1s sleep is often too short, causing misreads and
   wrong-direction swipes on the next iteration.

4. **Date format mismatch.** Production keyword expects DD-MM-YYYY but example
   data is YYYY-MM-DD (see §3 warning).

5. **Year wheel is huge.** ~100+ years rendered virtually; swiping from 2011 to
   1990 takes many iterations and is the slowest, most failure-prone wheel.

6. **No accessibility setter.** Unlike Citizen ID (which accepts adb keycodes),
   the DOB field rejects all direct input — the picker is the only path.

---

## 8. Key Facts for an Alternative Approach

- App package: `com.bangkokbank.blue.dev` (dev build)
- Framework: **React Native** (horcrux SVG, flatlist virtualized wheels)
- The selected value on each wheel is reliably in the SeekBar `content-desc`
  as `"<Kind> picker, <value>"` — comma-separated, value is the right part.
- Month values are **English full names** (January…December), not numbers.
- Day values are numeric strings "1"…"31" (no zero-padding in content-desc).
- Year values are 4-digit numeric strings.
- The field is opened by tapping the **container**, not the input itself.
- `--relaxed-security` is already enabled (adb shell swipes are in use).
- Done button is `content-desc="Done"`.

### Potentially better approaches to evaluate

- **UiAutomator2 `mobile: scrollGesture`** with element-relative coordinates
  and a controlled step count, polling content-desc until matched.
- **Fling with momentum damping**: shorter swipes + longer settle, then re-read.
- **Two-phase**: coarse fling to get near target, then single-row taps on the
  adjacent visible `TextView` to nudge into place (tap the row above/below
  center to move one step).
- **Direct tap on target row**: if the target value is already rendered in the
  flatlist, tap its `TextView` directly instead of swiping.
- **React props injection via `execute_script` / React DevTools hook** (the app
  exposes a React fiber — if a testID or state setter can be reached).
- **Request developer support** for a `testID` on each wheel or a hidden
  direct-set method (deeplink / debug panel input).
