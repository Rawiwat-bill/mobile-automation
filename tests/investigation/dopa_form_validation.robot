*** Settings ***
Documentation    DOPA form validation using Profile-aligned patterns (Input Text + text-based XPath).
Library          AppiumLibrary
Library          OperatingSystem
Library          Process
Library          ../../libraries/config_loader.py
Resource         ../../resources/keywords/onboarding_common.resource
Resource         ../../resources/pages/onboarding/dopa_information_page.resource


*** Variables ***
${EMULATOR_SERIAL}    emulator-5554
${REPORT_DIR}         ${CURDIR}/../../reports/investigation/dopa_form_implementation
${NTB_TESTDATA}       ${CURDIR}/../../testdata/onboarding/ntb.local.yaml


*** Test Cases ***
DOPA Form Validation
    [Tags]    investigation    dopa
    Create Directory    ${REPORT_DIR}
    ${data}=    Load YAML    ${NTB_TESTDATA}
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
    Log    [DOPA_TEST] Starting flow    WARN
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
    Wait Until DOPA Information Screen Is Displayed
    Log    [DOPA_TEST] DOPA reached    WARN
    Sleep    2s
    Capture Evidence    before
    Fill DOPA English Names    ${data['dopa']['english']['first_name']}    ${data['dopa']['english']['last_name']}
    Capture Evidence    after_names
    Set DOPA Date Via Picker    ${DOPA_DATE_OF_ISSUE_INPUT}    21    August    2023
    Capture Evidence    after_issue_date
    Set DOPA Date Via Picker    ${DOPA_DATE_OF_EXPIRE_INPUT}    21    August    2032
    Capture Evidence    after_expire_date
    Capture Evidence    before_next
    Tap DOPA Next
    Sleep    5s
    Capture Evidence    after_next
    ${otp_reached}=    Run Keyword And Return Status    Wait Until Page Contains Element    xpath=//*[contains(@resource-id,"otp") or contains(@text,"OTP") or contains(@text,"verification")]    20s
    Log    [DOPA_TEST] OTP reached: ${otp_reached}    WARN
    Create File    ${REPORT_DIR}/result.json    {"otp_reached": ${otp_reached}}\n    UTF-8
    [Teardown]    Run Keyword And Ignore Error    Close Application


*** Keywords ***
Capture Evidence
    [Arguments]    ${label}
    ${dir}=    Set Variable    ${REPORT_DIR}/${label}
    Create Directory    ${dir}
    ${source}=    Get Source
    Create File    ${dir}/page_source.xml    ${source}    UTF-8
    Capture Page Screenshot    ${dir}/screenshot.png
    Log    [DOPA_TEST] Captured: ${label}    WARN
