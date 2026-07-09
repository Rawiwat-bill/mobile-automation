*** Settings ***
Documentation    DOB-01 — spike: can a visible DOB day-wheel item be selected by tapping its text node?
...              Emulator only, DEV only, DOB picker focus. Does NOT modify the production
...              Select DOB Picker Value keyword (uses it read-only for year/month only).
...              Day wheel uses a tap experiment + slow 400ms drag to bring target into view.
Library          AppiumLibrary
Library          OperatingSystem
Library          Process
Library          String
Library          ../../libraries/config_loader.py
Resource         ../../resources/app/app_keywords.resource
Resource         ../../resources/pages/onboarding/landing_screen_page.resource
Resource         ../../resources/pages/onboarding/consent_screen_page.resource
Resource         ../../resources/pages/onboarding/profile_screen_page.resource


*** Variables ***
${EMULATOR_SERIAL}     emulator-5554
${EMULATOR_DEVICE}     Android Emulator
${REPORT_DIR}          reports/ocr_runtime
${EVIDENCE}            ${REPORT_DIR}/evidence/dob01
${TESTDATA}            testdata/onboarding/ntb.local.yaml
${TARGET_DAY}          15
${TARGET_YEAR}         1992
${TARGET_MONTH}        January
${DRAG_DURATION}       400
${DAY_TEXT_TARGET}     xpath=//*[@resource-id="screenProfile_calendarDatePicker-dateScroll"]//android.widget.TextView[@text="${TARGET_DAY}"]


*** Test Cases ***
DOB Wheel Tap Selection Spike
    Create Directory    ${REPORT_DIR}
    Create Directory    ${EVIDENCE}
    Clear App Data On Emulator
    Open Application On Emulator
    Allow Android Permission If Visible
    Drive To Profile
    Capture Spike Evidence    profile_before_picker
    Tap Profile Element Center    ${PROFILE_DOB_CONTAINER}
    Wait Until Element Is Visible    ${PROFILE_DOB_DAY_PICKER}    5s
    Capture Spike Evidence    picker_opened
    Run Keyword And Ignore Error    Select DOB Picker Value    ${PROFILE_DOB_YEAR_PICKER}    ${TARGET_YEAR}    number
    Run Keyword And Ignore Error    Select DOB Picker Value    ${PROFILE_DOB_MONTH_PICKER}    ${TARGET_MONTH}    month
    Capture Spike Evidence    day_before_tap
    ${result}=    Day Tap Spike
    Capture Spike Evidence    day_after_tap
    ${field_ok}=    Tap Done And Read Field
    Capture Spike Evidence    after_done
    Write Classification    ${result}    ${field_ok}
    [Teardown]    Run Keyword And Ignore Error    Close Application


*** Keywords ***
Clear App Data On Emulator
    Run Process    adb    -s    ${EMULATOR_SERIAL}    shell    pm clear    ${APP_PACKAGE}
    ...    timeout=30s    on_timeout=terminate

Open Application On Emulator
    Open Application
    ...    ${APPIUM_URL}
    ...    platformName=Android
    ...    automationName=UiAutomator2
    ...    udid=${EMULATOR_SERIAL}
    ...    deviceName=${EMULATOR_DEVICE}
    ...    appPackage=${APP_PACKAGE}
    ...    appActivity=${APP_ACTIVITY}
    ...    noReset=${TRUE}
    ...    autoGrantPermissions=${TRUE}
    ...    ignoreHiddenApiPolicyError=${TRUE}
    ...    disableWindowAnimation=${TRUE}
    ...    uiautomator2ServerInstallTimeout=120000
    ...    uiautomator2ServerLaunchTimeout=120000
    ...    newCommandTimeout=300

Drive To Profile
    Allow Android Permission If Visible
    ${landing_tapped}=    Run Keyword And Return Status    Tap Landing Ready Button
    Allow Android Permission If Visible
    ${consent_visible}=    Run Keyword And Return Status    Wait Until Element Is Visible    ${CONSENT_TITLE_TEXT}    20s
    IF    not ${consent_visible}
        Tap Landing Bottom Center On Emulator
        Allow Android Permission If Visible
        Wait Until Element Is Visible    ${CONSENT_TITLE_TEXT}    20s
    END
    Run Keyword And Ignore Error    Scroll Down Consent Terms    15
    Run Keyword And Ignore Error    Tap Consent Accept Button
    Wait Until Profile Screen Is Displayed
    Log    [DOB-01] Reached Profile screen

Tap Landing Bottom Center On Emulator
    ${size_result}=    Run Process    adb    -s    ${EMULATOR_SERIAL}    shell    wm    size
    ...    timeout=15s    on_timeout=terminate
    ${width}=    Evaluate    int(__import__('re').search(r'(\\d+)x(\\d+)', """${size_result.stdout}""").group(1))
    ${height}=    Evaluate    int(__import__('re').search(r'(\\d+)x(\\d+)', """${size_result.stdout}""").group(2))
    ${center_x}=    Evaluate    int(${width} * 0.5)
    ${bottom_y}=    Evaluate    int(${height} * 0.94)
    Run Process    adb    -s    ${EMULATOR_SERIAL}    shell    input    tap    ${center_x}    ${bottom_y}
    ...    timeout=15s    on_timeout=terminate
    Sleep    1s

Read Day Wheel Value
    ${cd}=    Run Keyword And Ignore Error    Get Element Attribute    ${PROFILE_DOB_DAY_PICKER}    content-desc
    ${val}=    Set Variable IF    '${cd[0]}' == 'PASS'    ${cd[1]}    Day picker, ?
    ${day}=    Fetch From Right    ${val}    ,
    ${day}=    Strip String    ${day}
    RETURN    ${day}

Day Tap Spike
    ${current}=    Read Day Wheel Value
    Log    [DOB-01] day current=${current} target=${TARGET_DAY}
    ${result}=    Set Variable    TARGET_NOT_VISIBLE
    FOR    ${i}    IN RANGE    15
        ${visible}=    Run Keyword And Return Status    Wait Until Element Is Visible    ${DAY_TEXT_TARGET}    2s
        IF    ${visible}
            Log    [DOB-01] target '${TARGET_DAY}' visible — tapping text node
            Run Keyword And Ignore Error    Click Element    ${DAY_TEXT_TARGET}
            Sleep    0.6s
            ${after}=    Read Day Wheel Value
            Log    [DOB-01] day after tap=${after}
            ${result}=    Set Variable If    '${after}' == '${TARGET_DAY}'    TAP_SELECT_WORKS    TAP_SELECT_VISIBLE_BUT_NO_SELECTION
            RETURN    ${result}
        END
        Log    [DOB-01] target not visible (iter ${i}) — slow drag ${DRAG_DURATION}ms
        Slow Drag Day Wheel    ${current}
        Sleep    0.4s
        ${current}=    Read Day Wheel Value
        Log    [DOB-01] day current after drag=${current}
    END
    RETURN    ${result}

Slow Drag Day Wheel
    [Arguments]    ${current}
    ${rect}=    Get Element Rect    ${PROFILE_DOB_DAY_PICKER}
    ${cx}=    Evaluate    int(${rect['x']} + (${rect['width']} / 2))
    ${top}=    Evaluate    int(${rect['y']} + (${rect['height']} * 0.30))
    ${bottom}=    Evaluate    int(${rect['y']} + (${rect['height']} * 0.70))
    ${cur_int}=    Convert To Integer    ${current}
    ${tgt_int}=    Convert To Integer    ${TARGET_DAY}
    IF    ${cur_int} < ${tgt_int}
        Execute Adb Shell    input    swipe    ${cx}    ${bottom}    ${cx}    ${top}    ${DRAG_DURATION}
    ELSE
        Execute Adb Shell    input    swipe    ${cx}    ${top}    ${cx}    ${bottom}    ${DRAG_DURATION}
    END

Tap Done And Read Field
    Run Keyword And Ignore Error    Click Element    ${PROFILE_DOB_CONFIRM_BUTTON}
    Run Keyword And Ignore Error    Wait Until Page Does Not Contain Element    ${PROFILE_DOB_DAY_PICKER}    5s
    ${status}    ${field}=    Run Keyword And Ignore Error    Get Text    ${PROFILE_DOB_INPUT}
    ${field}=    Set Variable IF    '${status}' == 'PASS'    ${field}    <read_failed>
    Log    [DOB-01] DOB field after Done='${field}'
    ${clean}=    Replace String Using Regexp    ${field}    \\.    ${EMPTY}
    ${clean}=    Strip String    ${clean}
    ${ok}=    Set Variable If    '${clean}' == '15 Jan 1992'    ${TRUE}    ${FALSE}
    RETURN    ${ok}

Write Classification
    [Arguments]    ${result}    ${field_ok}
    Create File    ${EVIDENCE}/classification.txt
    ...    classification=${result}\ndob_field_is_15_jan_1992=${field_ok}\ntarget_day=${TARGET_DAY}\n
    ...    UTF-8
    Log    [DOB-01] CLASSIFICATION=${result} field_ok=${field_ok}

Capture Spike Evidence
    [Arguments]    ${label}
    Run Process    sh    -c    adb -s ${EMULATOR_SERIAL} exec-out screencap -p > ${EVIDENCE}/${label}.png
    ...    timeout=30s    on_timeout=terminate
    ${status}    ${source}=    Run Keyword And Ignore Error    Get Source
    ${body}=    Set Variable IF    '${status}' == 'PASS'    ${source}    XML_CAPTURE_FAILED:${source}
    Create File    ${EVIDENCE}/${label}.xml    ${body}    UTF-8
