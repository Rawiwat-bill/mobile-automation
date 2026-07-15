*** Settings ***
Documentation    OTP entry + Set PIN discovery — fresh flow Landing through Set PIN screen.
Library          AppiumLibrary
Library          OperatingSystem
Library          Process
Library          ../../libraries/config_loader.py
Resource         ../../resources/keywords/onboarding_common.resource
Resource         ../../resources/pages/onboarding/dopa_information_page.resource
Resource         ../../resources/pages/onboarding/verify_mobile_otp_page.resource


*** Variables ***
${EMULATOR_SERIAL}    emulator-5554
${REPORT_DIR}         ${CURDIR}/../../reports/investigation/otp_to_set_pin
${NTB_TESTDATA}       ${CURDIR}/../../testdata/onboarding/ntb.local.yaml


*** Test Cases ***
OTP Entry and Set PIN Discovery
    [Tags]    investigation    otp    set_pin
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
    Log    [OTP_TEST] Starting flow    WARN
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
        ${source}=    Get Source
        ${is_aji}=    Evaluate    'AJI' in $source or 'Service is not available' in $source
        Log    [OTP_TEST] DOPA not reached — AJI-001: ${is_aji}    WARN
        Create File    ${REPORT_DIR}/result.json    {"classification": "ENVIRONMENT_BLOCKED", "aji001": ${is_aji}}\n    UTF-8
        [Teardown]    Run Keyword And Ignore Error    Close Application
        Fail    ENVIRONMENT_BLOCKED — DOPA not reached
    END
    Log    [OTP_TEST] DOPA reached    WARN
    Sleep    2s
    Fill DOPA English Names    ${data['dopa']['english']['first_name']}    ${data['dopa']['english']['last_name']}
    Set DOPA Date Via Picker    ${DOPA_DATE_OF_ISSUE_INPUT}    21    August    2023
    Set DOPA Date Via Picker    ${DOPA_DATE_OF_EXPIRE_INPUT}    21    August    2032
    Fill DOPA Laser Code    ${data['dopa']['laser']['part1']}    ${data['dopa']['laser']['part2']}    ${data['dopa']['laser']['part3']}
    Scroll DOPA To Top
    Sleep    1s
    ${navigated}=    Tap DOPA Next
    Should Be True    ${navigated}    DOPA Next did not navigate
    Log    [OTP_TEST] DOPA Next navigated    WARN
    Wait Until OTP Screen Is Displayed
    Log    [OTP_TEST] OTP screen reached    WARN
    Capture Evidence    otp    otp
    Enter OTP Code    ${data['otp']['code']}
    Log    [OTP_TEST] OTP entered: ${data['otp']['code']}    WARN
    Sleep    2s
    Capture Evidence    otp    after_entry
    ${set_pin_reached}=    Run Keyword And Return Status    Wait Until Page Contains Element    xpath=//*[contains(@resource-id,"pin") or contains(@text,"PIN") or contains(@text,"pin") or contains(@resource-id,"Pin") or contains(@resource-id,"setPin") or contains(@resource-id,"SetPin")]    30s
    Log    [OTP_TEST] Set PIN reached: ${set_pin_reached}    WARN
    IF    ${set_pin_reached}
        Capture Evidence    set_pin    set_pin
    END
    ${t1}=    Evaluate    time.time()    modules=time
    ${elapsed}=    Evaluate    round(${t1} - ${t0}, 2)
    Log    [OTP_TEST] Total: ${elapsed}s — Set PIN reached: ${set_pin_reached}    WARN
    Create File    ${REPORT_DIR}/result.json    {"set_pin_reached": ${set_pin_reached}, "elapsed_s": ${elapsed}}\n    UTF-8
    [Teardown]    Run Keyword And Ignore Error    Close Application


*** Keywords ***
Capture Evidence
    [Arguments]    ${subdir}    ${label}
    ${dir}=    Set Variable    ${REPORT_DIR}/${subdir}
    Create Directory    ${dir}
    ${source}=    Get Source
    Create File    ${dir}/${label}_page_source.xml    ${source}    UTF-8
    Capture Page Screenshot    ${dir}/${label}_screenshot.png
    Log    [OTP_TEST] Captured: ${subdir}/${label}    WARN
