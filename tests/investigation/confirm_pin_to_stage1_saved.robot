*** Settings ***
Documentation    Confirm PIN entry + Stage 1 discovery — complete Stage 1 happy flow.
Library          AppiumLibrary
Library          OperatingSystem
Library          Process
Library          ../../libraries/config_loader.py
Resource         ../../resources/keywords/onboarding_common.resource
Resource         ../../resources/pages/onboarding/dopa_information_page.resource
Resource         ../../resources/pages/onboarding/verify_mobile_otp_page.resource
Resource         ../../resources/pages/onboarding/set_pin_page.resource
Resource         ../../resources/pages/onboarding/confirm_pin_page.resource


*** Variables ***
${EMULATOR_SERIAL}    emulator-5554
${REPORT_DIR}         ${CURDIR}/../../reports/investigation/confirm_pin_to_stage1_saved
${NTB_TESTDATA}       ${CURDIR}/../../testdata/onboarding/ntb.local.yaml


*** Test Cases ***
Confirm PIN and Stage 1 Discovery
    [Tags]    investigation    confirm_pin    stage1
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
    Log    [STAGE1] Starting flow    WARN
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
        Fail    ENVIRONMENT_BLOCKED
    END
    Log    [STAGE1] DOPA reached    WARN
    Sleep    2s
    Fill DOPA English Names    ${data['dopa']['english']['first_name']}    ${data['dopa']['english']['last_name']}
    Set DOPA Date Via Picker    ${DOPA_DATE_OF_ISSUE_INPUT}    21    August    2023
    Set DOPA Date Via Picker    ${DOPA_DATE_OF_EXPIRE_INPUT}    21    August    2032
    Fill DOPA Laser Code    ${data['dopa']['laser']['part1']}    ${data['dopa']['laser']['part2']}    ${data['dopa']['laser']['part3']}
    Scroll DOPA To Top
    Sleep    1s
    ${nav1}=    Tap DOPA Next
    Should Be True    ${nav1}    DOPA Next failed
    Wait Until OTP Screen Is Displayed
    Enter OTP Code    ${data['otp']['code']}
    Log    [STAGE1] OTP done    WARN
    Wait Until Set PIN Screen Is Displayed
    Enter PIN Using Custom Keypad    ${data['pin']['value']}
    Log    [STAGE1] Set PIN done    WARN
    Wait Until Confirm PIN Screen Is Displayed
    Log    [STAGE1] Confirm PIN reached    WARN
    Capture Evidence    confirm_pin    before
    Enter Confirm PIN Using Custom Keypad    ${data['pin']['value']}
    Log    [STAGE1] Confirm PIN entered    WARN
    Sleep    2s
    Capture Evidence    confirm_pin    after_entry
    ${confirm_gone}=    Run Keyword And Return Status    Wait Until Page Does Not Contain Element    ${CONFIRM_PIN_TITLE}    30s
    Log    [STAGE1] Confirm PIN screen gone: ${confirm_gone}    WARN
    IF    ${confirm_gone}
        Sleep    3s
        Capture Evidence    next_screen    next_screen
        Log    [STAGE1] Next screen captured    WARN
    ELSE
        Capture Evidence    next_screen    still_on_confirm
        Log    [STAGE1] Still on Confirm PIN — possible mismatch or stall    WARN
    END
    ${t1}=    Evaluate    time.time()    modules=time
    ${elapsed}=    Evaluate    round(${t1} - ${t0}, 2)
    Log    [STAGE1] Total: ${elapsed}s — navigated: ${confirm_gone}    WARN
    Create File    ${REPORT_DIR}/result.json    {"navigated": ${confirm_gone}, "elapsed_s": ${elapsed}}\n    UTF-8
    [Teardown]    Run Keyword And Ignore Error    Close Application


*** Keywords ***
Capture Evidence
    [Arguments]    ${subdir}    ${label}
    ${dir}=    Set Variable    ${REPORT_DIR}/${subdir}
    Create Directory    ${dir}
    ${source}=    Get Source
    Create File    ${dir}/${label}_page_source.xml    ${source}    UTF-8
    Capture Page Screenshot    ${dir}/${label}_screenshot.png
    Log    [STAGE1] Captured: ${subdir}/${label}    WARN
