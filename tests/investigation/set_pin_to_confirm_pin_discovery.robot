*** Settings ***
Documentation    Set PIN entry + Confirm PIN discovery — fresh flow through Set PIN → Confirm PIN.
Library          AppiumLibrary
Library          OperatingSystem
Library          Process
Library          ../../libraries/config_loader.py
Resource         ../../resources/keywords/onboarding_common.resource
Resource         ../../resources/pages/onboarding/dopa_information_page.resource
Resource         ../../resources/pages/onboarding/verify_mobile_otp_page.resource
Resource         ../../resources/pages/onboarding/set_pin_page.resource


*** Variables ***
${EMULATOR_SERIAL}    emulator-5554
${REPORT_DIR}         ${CURDIR}/../../reports/investigation/set_pin_to_confirm_pin
${NTB_TESTDATA}       ${CURDIR}/../../testdata/onboarding/ntb.local.yaml


*** Test Cases ***
Set PIN Entry and Confirm PIN Discovery
    [Tags]    investigation    set_pin    confirm_pin
    Create Directory    ${REPORT_DIR}
    ${data}=    Load YAML    ${NTB_TESTDATA}
    ${t0}=    Evaluate    time.time()    modules=time
    Run Process    adb    -s    ${EMULATOR_SERIAL}    shell    pm clear    ${APP_PACKAGE}
    ...    timeout=30s    on_timeout=terminate
    Open Application
    ...    ${APPIUM_URL}
    ...    platformName=Android
    ...    automationName=UiAutomator2
    ...    udid=${EMULATOR_SERIAL}
    ...    deviceName=${DEVICE_NAME}
    ...    appPackage=${APP_PACKAGE}
    ...    appActivity=${APP_ACTIVITY}
    ...    noReset=${TRUE}
    ...    autoGrantPermissions=${TRUE}
    ...    ignoreHiddenApiPolicyError=${TRUE}
    ...    uiautomator2ServerInstallTimeout=120000
    ...    uiautomator2ServerLaunchTimeout=120000
    ...    newCommandTimeout=300
    Log    [PIN_TEST] Starting flow    WARN
    Run Keyword And Ignore Error    Complete Common Onboarding
    ...    ${data['profile']['citizen_id']}
    ...    ${data['profile']['date_of_birth']}
    ...    ${data['profile']['mobile_number']}
    ${on_camera}=    Run Keyword And Return Status    Page Should Contain Element    accessibility_id=Take photo
    IF    ${on_camera}
        Run Process    adb    -s    ${EMULATOR_SERIAL}    shell    input    tap    540    2039
        ...    timeout=15s    on_timeout=terminate
        Sleep    5s
    END
    ${dopa_ok}=    Run Keyword And Return Status    Wait Until DOPA Information Screen Is Displayed
    IF    not ${dopa_ok}
        Capture Evidence    environment    blocked
        Create File    ${REPORT_DIR}/result.json    {"classification": "ENVIRONMENT_BLOCKED"}\n    UTF-8
        Fail    ENVIRONMENT_BLOCKED — DOPA not reached
    END
    Log    [PIN_TEST] DOPA reached    WARN
    Sleep    2s
    Fill DOPA English Names    ${data['dopa']['english']['first_name']}    ${data['dopa']['english']['last_name']}
    Set DOPA Date Via Picker    ${DOPA_DATE_OF_ISSUE_INPUT}    21    August    2023
    Set DOPA Date Via Picker    ${DOPA_DATE_OF_EXPIRE_INPUT}    21    August    2032
    Fill DOPA Laser Code    ${data['dopa']['laser']['part1']}    ${data['dopa']['laser']['part2']}    ${data['dopa']['laser']['part3']}
    Scroll DOPA To Top
    Sleep    1s
    ${navigated}=    Tap DOPA Next
    Should Be True    ${navigated}    DOPA Next did not navigate
    Wait Until OTP Screen Is Displayed
    Log    [PIN_TEST] OTP screen reached    WARN
    Enter OTP Code    ${data['otp']['code']}
    Log    [PIN_TEST] OTP entered    WARN
    Wait Until Set PIN Screen Is Displayed
    Log    [PIN_TEST] Set PIN screen reached    WARN
    Capture Evidence    set_pin    before
    Enter PIN Using Custom Keypad    ${data['pin']['value']}
    Log    [PIN_TEST] PIN entered via keypad    WARN
    Sleep    2s
    Capture Evidence    set_pin    after_entry
    ${confirm_reached}=    Run Keyword And Return Status    Wait Until Page Contains Element    xpath=//*[contains(@text,"Confirm") or contains(@resource-id,"confirm") or contains(@resource-id,"Confirm") or contains(@text,"confirm")]    20s
    Log    [PIN_TEST] Confirm PIN reached: ${confirm_reached}    WARN
    IF    ${confirm_reached}
        Capture Evidence    confirm_pin    confirm_pin
    END
    ${t1}=    Evaluate    time.time()    modules=time
    ${elapsed}=    Evaluate    round(${t1} - ${t0}, 2)
    Log    [PIN_TEST] Total: ${elapsed}s — Confirm PIN reached: ${confirm_reached}    WARN
    Create File    ${REPORT_DIR}/result.json    {"confirm_pin_reached": ${confirm_reached}, "elapsed_s": ${elapsed}}\n    UTF-8
    [Teardown]    Run Keyword And Ignore Error    Close Application


*** Keywords ***
Capture Evidence
    [Arguments]    ${subdir}    ${label}
    ${dir}=    Set Variable    ${REPORT_DIR}/${subdir}
    Create Directory    ${dir}
    ${source}=    Get Source
    Create File    ${dir}/${label}_page_source.xml    ${source}    UTF-8
    Capture Page Screenshot    ${dir}/${label}_screenshot.png
    Log    [PIN_TEST] Captured: ${subdir}/${label}    WARN
