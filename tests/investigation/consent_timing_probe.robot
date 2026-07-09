*** Settings ***
Documentation    Consent performance probe — measure granular timing of scroll->Accept-enabled->tap->transition.
...              Does NOT modify the production Consent keyword. Replicates the big-fling swipe (45ms + 0.12s sleep)
...              with per-swipe Accept-enabled detection, then taps IMMEDIATELY when enabled.
Library          AppiumLibrary
Library          OperatingSystem
Library          Process
Library          String
Resource         ../../resources/app/app_keywords.resource
Resource         ../../resources/pages/onboarding/consent_screen_page.resource


*** Variables ***
${EMULATOR_SERIAL}     emulator-5554
${EMULATOR_DEVICE}     Android Emulator
${REPORT_DIR}          reports/ocr_runtime
${EVIDENCE}            ${REPORT_DIR}/evidence/consent_perf
${SWIPE_DURATION}      45
${SHORT_PAUSE}         0.12
${MAX_SWIPES}          60


*** Test Cases ***
Consent Timing Breakdown
    Create Directory    ${REPORT_DIR}
    Create Directory    ${EVIDENCE}
    Clear App Data On Emulator
    Open Application On Emulator
    Allow Android Permission If Visible
    Drive To Consent
    ${scroll_start}    ${swipes_to_enabled}    ${accept_enabled_time}    ${accept_tap_time}    ${transition_time}    ${marker_time}=    Instrumented Scroll And Tap
    Create File    ${EVIDENCE}/timing.txt
    ...    scroll_start=${scroll_start}\nswipes_to_accept_enabled=${swipes_to_enabled}\naccept_enabled_time=${accept_enabled_time}\naccept_tap_time=${accept_tap_time}\ntransition_time=${transition_time}\nmarker_time=${marker_time}\n
    ...    UTF-8
    Log    [CONSENT-PERF] scroll_start=${scroll_start} swipes_to_enabled=${swipes_to_enabled} accept_enabled_time=${accept_enabled_time} accept_tap_time=${accept_tap_time} transition_time=${transition_time} marker_time=${marker_time}
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

Drive To Consent
    Allow Android Permission If Visible
    ${landing_tapped}=    Run Keyword And Return Status    Tap Landing Ready Button
    Allow Android Permission If Visible
    ${consent_visible}=    Run Keyword And Return Status    Wait Until Element Is Visible    ${CONSENT_TITLE_TEXT}    20s
    IF    not ${consent_visible}
        Tap Landing Bottom Center On Emulator
        Allow Android Permission If Visible
        Wait Until Element Is Visible    ${CONSENT_TITLE_TEXT}    20s
    END
    Log    [CONSENT-PERF] Reached Consent screen

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

Instrumented Scroll And Tap
    ${width}=    Get Window Width
    ${height}=    Get Window Height
    ${start_x}=    Evaluate    int(${width} * 0.5)
    ${start_y}=    Evaluate    int(${height} * 0.87)
    ${end_y}=    Evaluate    int(${height} * 0.12)
    ${scroll_start}=    Evaluate    round(time.time(), 3)    modules=time
    ${accept_enabled_time}=    Set Variable    None
    ${marker_time}=    Set Variable    None
    ${swipes}=    Set Variable    0
    FOR    ${i}    IN RANGE    ${MAX_SWIPES}
        Execute Adb Shell    input    swipe    ${start_x}    ${start_y}    ${start_x}    ${end_y}    ${SWIPE_DURATION}
        ${swipes}=    Evaluate    ${swipes} + 1
        Sleep    ${SHORT_PAUSE}
        ${enabled}=    Run Keyword And Return Status    Element Should Be Enabled    ${CONSENT_ACCEPT_BUTTON}
        ${now}=    Evaluate    round(time.time(), 3)    modules=time
        IF    ${enabled} and '${accept_enabled_time}' == 'None'
            ${accept_enabled_time}=    Set Variable    ${now}
            ${marker_time}=    Evaluate    round(time.time(), 3)    modules=time
            Log    [CONSENT-PERF] Accept enabled at swipe=${swipes} t=${accept_enabled_time} (scroll_start=${scroll_start}, delta=${round(${accept_enabled_time} - ${scroll_start}, 3)})
            BREAK
        END
    END
    ${accept_tap_time}=    Evaluate    round(time.time(), 3)    modules=time
    ${tap_ok}=    Run Keyword And Return Status    Click Element    ${CONSENT_ACCEPT_BUTTON}
    ${transition_passed}=    Run Keyword And Return Status    Wait Until Page Does Not Contain Element    ${CONSENT_TITLE_TEXT}    30s
    ${transition_time}=    Evaluate    round(time.time(), 3)    modules=time
    Log    [CONSENT-PERF] tap_ok=${tap_ok} transition_passed=${transition_passed} accept_tap_time=${accept_tap_time} transition_time=${transition_time}
    Log    [CONSENT-PERF] DELTA enabled->tap=${round(${accept_tap_time} - ${accept_enabled_time}, 3)} tap->transition=${round(${transition_time} - ${accept_tap_time}, 3)} total(scroll->transition)=${round(${transition_time} - ${scroll_start}, 3)}
    RETURN    ${scroll_start}    ${swipes}    ${accept_enabled_time}    ${accept_tap_time}    ${transition_time}    ${marker_time}
