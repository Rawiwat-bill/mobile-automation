*** Settings ***
Documentation    DOPA laser code + Next navigation — complete all fields and reach OTP.
Library          AppiumLibrary
Library          OperatingSystem
Library          Process
Library          ../../libraries/config_loader.py
Resource         ../../resources/keywords/onboarding_common.resource
Resource         ../../resources/pages/onboarding/dopa_information_page.resource


*** Variables ***
${EMULATOR_SERIAL}    emulator-5554
${REPORT_DIR}         ${CURDIR}/../../reports/investigation/dopa_laser_and_next
${NTB_TESTDATA}       ${CURDIR}/../../testdata/onboarding/ntb.local.yaml


*** Test Cases ***
DOPA Laser Code and Next Navigation
    [Tags]    investigation    dopa    laser
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
    Log    [DOPA_TEST] On camera screen: ${on_camera}    WARN
    IF    ${on_camera}
        Run Process    adb    -s    ${EMULATOR_SERIAL}    shell    input    tap    540    2039
        ...    timeout=15s    on_timeout=terminate
        Sleep    5s
    END
    ${dopa_ok}=    Run Keyword And Return Status    Wait Until DOPA Information Screen Is Displayed
    IF    not ${dopa_ok}
        Capture Evidence    dopa_not_reached
        Log    [DOPA_TEST] DOPA not reached — check evidence    WARN
        Fail    DOPA_NOT_REACHED
    END
    Log    [DOPA_TEST] DOPA reached    WARN
    Sleep    2s
    Fill DOPA English Names    ${data['dopa']['english']['first_name']}    ${data['dopa']['english']['last_name']}
    Set DOPA Date Via Picker    ${DOPA_DATE_OF_ISSUE_INPUT}    21    August    2023
    Set DOPA Date Via Picker    ${DOPA_DATE_OF_EXPIRE_INPUT}    21    August    2032
    Capture Evidence    before_laser
    Verify Laser Fields Are Hints
    Fill DOPA Laser Code    ${data['dopa']['laser']['part1']}    ${data['dopa']['laser']['part2']}    ${data['dopa']['laser']['part3']}
    Capture Evidence    after_laser
    Verify Laser Fields Are Filled
    Scroll DOPA To Top
    Sleep    1s
    Refill English Names If Lost    ${data['dopa']['english']['first_name']}    ${data['dopa']['english']['last_name']}
    Capture Evidence    before_next
    ${navigated}=    Tap DOPA Next
    Sleep    3s
    Capture Evidence    after_next
    ${otp_reached}=    Run Keyword And Return Status    Wait Until Page Contains Element    xpath=//*[contains(@resource-id,"otp") or contains(@text,"OTP") or contains(@text,"verification")]    20s
    Log    [DOPA_TEST] OTP reached: ${otp_reached}    WARN
    Create File    ${REPORT_DIR}/result.json    {"otp_reached": ${otp_reached}, "navigated": ${navigated}}\n    UTF-8
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

Verify Laser Fields Are Hints
    ${source}=    Get Source
    ${all_hints}=    Evaluate    [e.get('showing-hint','') for e in __import__('xml.etree.ElementTree', fromlist=['ET']).fromstring($source).iter() if 'text-input-flat' in (e.get('resource-id') or '')]
    Log    [DOPA_TEST] Laser showing-hint before: ${all_hints}    WARN

Verify Laser Fields Are Filled
    ${source}=    Get Source
    ${all_hints}=    Evaluate    [e.get('showing-hint','') for e in __import__('xml.etree.ElementTree', fromlist=['ET']).fromstring($source).iter() if 'text-input-flat' in (e.get('resource-id') or '')]
    ${all_texts}=    Evaluate    [e.get('text','') for e in __import__('xml.etree.ElementTree', fromlist=['ET']).fromstring($source).iter() if 'text-input-flat' in (e.get('resource-id') or '')]
    Log    [DOPA_TEST] Laser showing-hint after: ${all_hints}    WARN
    Log    [DOPA_TEST] Laser texts after: ${all_texts}    WARN

Refill English Names If Lost
    [Arguments]    ${first_name}    ${last_name}
    ${source}=    Get Source
    ${fn}=    Evaluate    next((e.get('text','') for e in __import__('xml.etree.ElementTree', fromlist=['ET']).fromstring($source).iter() if 'inputFirstNameEng' in (e.get('resource-id') or '') and 'EditText' in (e.get('class') or '')), 'NOT_FOUND')
    ${ln}=    Evaluate    next((e.get('text','') for e in __import__('xml.etree.ElementTree', fromlist=['ET']).fromstring($source).iter() if 'inputLastNameEng' in (e.get('resource-id') or '') and 'EditText' in (e.get('class') or '')), 'NOT_FOUND')
    Log    [DOPA_TEST] English name check: first='${fn}' last='${ln}'    WARN
    ${fn_lost}=    Evaluate    'Enter first name' in '${fn}'
    ${ln_lost}=    Evaluate    'Enter last name' in '${ln}'
    IF    ${fn_lost}
        Log    [DOPA_TEST] English first name lost — refilling    WARN
        Input Text    xpath=//*[@text="Enter first name in English"]    ${first_name}
        Run Keyword And Ignore Error    Hide Keyboard
    END
    IF    ${ln_lost}
        Log    [DOPA_TEST] English last name lost — refilling    WARN
        Scroll DOPA Down
        Input Text    xpath=//*[@text="Enter last name in English"]    ${last_name}
        Run Keyword And Ignore Error    Hide Keyboard
        Scroll DOPA To Top
    END
