*** Settings ***
Library    AppiumLibrary
Library    Process
Library    Collections
Library    String
Library    OperatingSystem
Library    ../benchmark/BenchmarkMetrics.py
Resource   ../app/app_constants.resource


*** Variables ***
${BENCHMARK_PERM_TIMEOUT}      5s
${BENCHMARK_ELEMENT_TIMEOUT}   30s

# Locators (benchmark-isolated — not importing production locators)
${BENCHMARK_LANDING_SKIP}       xpath=//*[@resource-id="screenLanding_skipButton"]
${BENCHMARK_LANDING_READY}      xpath=//*[@resource-id="screenLanding_buttonReady"]
${BENCHMARK_PERM_ALLOW}         xpath=//*[@resource-id="com.android.permissioncontroller:id/permission_allow_button"]
${BENCHMARK_CONSENT_TITLE}      xpath=//*[@text="Terms and Conditions"]
${BENCHMARK_CONSENT_ACCEPT}     accessibility_id=Accept
${BENCHMARK_PROFILE_TITLE}      xpath=//*[@text="Tell us about you"]
${BENCHMARK_CITIZEN_INPUT}      xpath=//android.widget.EditText[@resource-id="cid"]
${BENCHMARK_CITIZEN_CONTAINER}  xpath=//*[@resource-id="cid-container"]
${BENCHMARK_DOB_INPUT}          xpath=//*[@resource-id="screenProfile_textInputDob"]
${BENCHMARK_DOB_CONTAINER}      xpath=//*[@resource-id="screenProfile_textInputDob-container"]
${BENCHMARK_DOB_DAY_PICKER}     xpath=//*[@resource-id="screenProfile_calendarDatePicker-dateScroll"]
${BENCHMARK_DOB_MONTH_PICKER}   xpath=//*[@resource-id="screenProfile_calendarDatePicker-monthScroll"]
${BENCHMARK_DOB_YEAR_PICKER}    xpath=//*[@resource-id="screenProfile_calendarDatePicker-yearScroll"]
${BENCHMARK_DOB_CONFIRM}        xpath=//*[@content-desc="Done"]
${BENCHMARK_MOBILE_INPUT}       xpath=//android.widget.EditText[@resource-id="screenProfile_textInputMobileNumber"]
${BENCHMARK_MOBILE_CONTAINER}   xpath=//*[@resource-id="screenProfile_textInputMobileNumber-container"]
${BENCHMARK_NEXT_CONTAINER}     xpath=//*[@resource-id="screenProfile_buttonNext"]


*** Keywords ***
Open Benchmark Application
    Start Phase    open_app
    Open Application
    ...    ${APPIUM_URL}
    ...    platformName=Android
    ...    automationName=UiAutomator2
    ...    deviceName=${DEVICE_NAME}
    ...    app=${APK_PATH}
    ...    appPackage=${APP_PACKAGE}
    ...    appActivity=${APP_ACTIVITY}
    ...    noReset=false
    Record Appium Action
    End Phase

Close Benchmark Application
    Start Phase    close_app
    Run Keyword And Ignore Error    Close Application
    Record Appium Action
    End Phase

Allow Android Permission If Visible
    ${is_visible}=    Run Keyword And Return Status
    ...    Wait Until Element Is Visible    ${BENCHMARK_PERM_ALLOW}    ${BENCHMARK_PERM_TIMEOUT}
    IF    ${is_visible}
        Click Element    ${BENCHMARK_PERM_ALLOW}
        Record Appium Action
        Activate Application    ${APP_PACKAGE}
        Record Appium Action
    END

Navigate To Landing
    Start Phase    navigate_landing
    ${result}=    Run Keyword And Ignore Error
    ...    Wait Until Keyword Succeeds    ${BENCHMARK_ELEMENT_TIMEOUT}    500ms    Landing Screen Should Be Visible
    IF    '${result}[0]' == 'FAIL'
        Save Screen Diagnostic
        Fail    ${result}[1]
    END
    End Phase

Landing Screen Should Be Visible
    ${is_skip}=    Run Keyword And Return Status    Element Should Be Visible    ${BENCHMARK_LANDING_SKIP}
    ${is_ready}=    Run Keyword And Return Status    Element Should Be Visible    ${BENCHMARK_LANDING_READY}
    Should Be True    ${is_skip} or ${is_ready}

Save Screen Diagnostic
    Run Keyword And Ignore Error    Capture Page Screenshot
    ${diag_dir}=    Set Variable    ${CURDIR}/../../reports/diagnostic/landing
    Create Directory    ${diag_dir}
    ${timestamp}=    Evaluate    str(time.time()).replace('.', '')
    ${src}=    Run Keyword And Ignore Error    Get Source
    IF    '${src}[0]' == 'PASS'
        Create File    ${diag_dir}/pagesource_${timestamp}.xml    ${src}[1]    UTF-8
        Log    Diagnostic saved: ${diag_dir}/pagesource_${timestamp}.xml    WARN
    ELSE
        Log    Could not capture page source for landing diagnostic    WARN
    END

Tap Landing Ready
    Start Phase    tap_ready
    ${is_ready}=    Run Keyword And Return Status    Element Should Be Visible    ${BENCHMARK_LANDING_READY}
    IF    ${is_ready}
        Click Element    ${BENCHMARK_LANDING_READY}
        Record Appium Action
    ELSE
        Click Element    ${BENCHMARK_LANDING_SKIP}
        Record Appium Action
        Wait Until Element Is Visible    ${BENCHMARK_LANDING_READY}    ${BENCHMARK_ELEMENT_TIMEOUT}
        Click Element    ${BENCHMARK_LANDING_READY}
        Record Appium Action
    END
    End Phase

Navigate To Consent
    Start Phase    navigate_consent
    ${result}=    Run Keyword And Ignore Error
    ...    Wait Until Element Is Visible    ${BENCHMARK_CONSENT_TITLE}    30s
    IF    '${result}[0]' == 'FAIL'
        Save Screen Diagnostic
        Fail    ${result}[1]
    END
    End Phase

Tap Consent Accept
    [Arguments]    ${strategy}=Hardcoded Swipe
    Start Phase    tap_accept
    Run Keyword    Consent Scroll - ${strategy}
    Wait Until Element Is Visible    ${BENCHMARK_CONSENT_ACCEPT}    ${BENCHMARK_ELEMENT_TIMEOUT}
    Click Element    ${BENCHMARK_CONSENT_ACCEPT}
    Record Appium Action
    End Phase

Navigate To Profile
    Start Phase    navigate_profile
    Open Benchmark Application
    Allow Android Permission If Visible
    Navigate To Landing
    Tap Landing Ready
    Allow Android Permission If Visible
    Navigate To Consent
    Tap Consent Accept
    End Phase

Wait For Profile
    Start Phase    wait_profile
    Wait Until Element Is Visible    ${BENCHMARK_PROFILE_TITLE}    30s
    End Phase

Log Benchmark Result
    [Arguments]    ${field}    ${strategy}    ${status}=PASS
    Set Strategy    ${field}    ${strategy}
    Set Result    ${status}
    End Benchmark
