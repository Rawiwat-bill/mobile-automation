*** Settings ***
Documentation    Stage 1 flow discovery — extends existing flow past OCR to discover DOPA/OTP/PIN screens.
...              Captures XML + screenshot at each new screen for locator analysis.
Library          AppiumLibrary
Library          OperatingSystem
Library          Process
Library          ../../libraries/config_loader.py
Resource         ../../resources/keywords/onboarding_common.resource
Resource         ../../resources/pages/onboarding/dopa_information_page.resource


*** Variables ***
${EMULATOR_SERIAL}    emulator-5554
${REPORT_DIR}         ${CURDIR}/../../reports/investigation/stage1_discovery
${NTB_TESTDATA}       ${CURDIR}/../../testdata/onboarding/ntb.local.yaml
${OTP_VALUE}          999999
${PIN_VALUE}          123123


*** Test Cases ***
Stage 1 Flow Discovery
    [Tags]    investigation    stage1
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
    Log    [DISCOVERY] Starting Complete Common Onboarding    WARN
    ${flow_ok}=    Run Keyword And Return Status    Complete Common Onboarding
    ...    ${data['profile']['citizen_id']}
    ...    ${data['profile']['date_of_birth']}
    ...    ${data['profile']['mobile_number']}
    IF    not ${flow_ok}
        Capture Stage Evidence    flow_failure
        Log    [DISCOVERY] Complete Common Onboarding failed — captured evidence    WARN
        Create File    ${REPORT_DIR}/route.log    Complete Common Onboarding failed — check flow_failure/ evidence\n    UTF-8
        Fail    FLOW_FAILED: Complete Common Onboarding did not reach OCR — check flow_failure/ evidence
    END
    Log    [DISCOVERY] Complete Common Onboarding finished — checking camera state    WARN
    ${on_camera}=    Run Keyword And Return Status    Page Should Contain Element    accessibility_id=Take photo
    IF    ${on_camera}
        Log    [DISCOVERY] Camera screen still active — adb tap photo capture at 540,2039    WARN
        Run Process    adb    -s    ${EMULATOR_SERIAL}    shell    input    tap    540    2039
        ...    timeout=15s    on_timeout=terminate
        Sleep    5s
    END
    ${dopa_ok}=    Run Keyword And Return Status    Wait Until DOPA Information Screen Is Displayed
    IF    not ${dopa_ok}
        Capture Stage Evidence    ocr_result
        Log    [DISCOVERY] DOPA not reached — capturing current screen    WARN
        Create File    ${REPORT_DIR}/route.log    OCR may have failed — check ocr_result/ evidence\n    UTF-8
        Fail    OCR_FAILED: DOPA screen not reached after OCR
    END
    Log    [DISCOVERY] DOPA screen reached    WARN
    Capture Stage Evidence    dopa
    Discover And Proceed From DOPA
    ${dopa_gone}=    Run Keyword And Return Status    Wait Until Page Does Not Contain Element    xpath=//*[contains(@resource-id,'screenDopaInformation')]    20s
    IF    not ${dopa_gone}
        Capture Stage Evidence    dopa_next_failed
        Log    [DISCOVERY] DOPA Next did not navigate — capturing evidence    WARN
        Create File    ${REPORT_DIR}/route.log    DOPA Next failed — check dopa_next_failed/ evidence\n    UTF-8
        Fail    DOPA_NEXT_FAILED
    END
    Capture Stage Evidence    after_dopa
    Discover And Proceed From OTP
    Sleep    5s
    Capture Stage Evidence    after_otp
    Discover And Proceed From PIN
    Sleep    5s
    Capture Stage Evidence    after_pin
    Discover And Proceed From PIN
    Sleep    5s
    Capture Stage Evidence    stage1_saved
    ${t1}=    Evaluate    time.time()    modules=time
    ${elapsed}=    Evaluate    round(${t1} - ${t0}, 2)
    Create File    ${REPORT_DIR}/route.log    Total elapsed: ${elapsed}s\n    UTF-8
    Log    [DISCOVERY] Total elapsed: ${elapsed}s    WARN
    [Teardown]    Run Keyword And Ignore Error    Close Application


*** Keywords ***
Capture Stage Evidence
    [Arguments]    ${label}
    ${dir}=    Set Variable    ${REPORT_DIR}/${label}
    Create Directory    ${dir}
    ${source}=    Get Source
    Create File    ${dir}/page_source.xml    ${source}    UTF-8
    Capture Page Screenshot    ${dir}/screenshot.png
    Log    [DISCOVERY] Captured evidence: ${label}    WARN

Discover And Proceed From DOPA
    Log    [DISCOVERY] DOPA: filling all empty fields + adb tap Next    WARN
    Fill Dopa Field    screenDopaInformation_inputFirstNameEng    Somjai
    Run Keyword And Ignore Error    Hide Keyboard
    Sleep    0.5s
    # Scroll down to reveal more fields
    Execute Adb Shell    input    swipe    540    1500    540    600    200
    Sleep    1s
    Fill Dopa Field    screenDopaInformation_inputLastNameEng    Jaidee
    Run Keyword And Ignore Error    Hide Keyboard
    Sleep    0.5s
    Fill Dopa Field    screenDopaInformation_inputDateOfIssue    21 Aug. 2023
    Run Keyword And Ignore Error    Hide Keyboard
    Sleep    0.5s
    # Scroll back to top
    Execute Adb Shell    input    swipe    540    600    540    1800    200
    Sleep    1s
    # Tap Next via container (proven method)
    ${btn}=    Run Keyword And Return Status    Wait Until Element Is Visible    xpath=//*[contains(@resource-id,'base-btn-container')]    5s
    IF    ${btn}
        ${rect}=    Get Element Rect    xpath=//*[contains(@resource-id,'base-btn-container')]
        ${cx}=    Evaluate    int(${rect['x']} + (${rect['width']} / 2))
        ${cy}=    Evaluate    int(${rect['y']} + (${rect['height']} / 2))
        Execute Adb Shell    input    tap    ${cx}    ${cy}
        Log    [DISCOVERY] DOPA: tapped Next container at ${cx},${cy}    WARN
    END

Fill Dopa Field
    [Arguments]    ${field_rid}    ${value}
    ${locator}=    Set Variable    xpath=//*[@resource-id='${field_rid}']
    ${found}=    Run Keyword And Return Status    Wait Until Element Is Visible    ${locator}    5s
    IF    ${found}
        Run Keyword And Ignore Error    Click Element    ${locator}
        Sleep    0.5s
        Run Keyword And Ignore Error    Clear Text    ${locator}
        ${entered}=    Run Keyword And Return Status    Input Text    ${locator}    ${value}
        IF    ${entered}
            Log    [DISCOVERY] DOPA: filled ${field_rid}='${value}'    WARN
        ELSE
            Log    [DISCOVERY] DOPA: Input Text failed for ${field_rid} — trying adb text    WARN
            Execute Adb Shell    input    text    ${value}
            Log    [DISCOVERY] DOPA: adb text entered for ${field_rid}    WARN
        END
    ELSE
        Log    [DISCOVERY] DOPA: ${field_rid} not found    WARN
    END

Discover And Proceed From OTP
    ${source}=    Get Source
    ${texts}=    Create List
    ${match}=    Evaluate    'OTP' in '${source}' or 'verification' in '${source}' or 'code' in '${source}' or 'otp' in '${source}'
    Log    [DISCOVERY] OTP: screen_match=${match} source_len=${source.__len__()}    WARN
    ${has_edit}=    Run Keyword And Return Status    Wait Until Page Contains Element    xpath=//android.widget.EditText    5s
    IF    ${has_edit}
        Run Keyword And Ignore Error    Input Text    xpath=(//android.widget.EditText)[1]    ${OTP_VALUE}
        Log    [DISCOVERY] OTP: entered ${OTP_VALUE}    WARN
        Sleep    2s
    END
    Adb Tap If Visible    accessibility_id=Next
    Adb Tap If Visible    accessibility_id=Continue
    Adb Tap If Visible    accessibility_id=Submit

Discover And Proceed From PIN
    ${source}=    Get Source
    ${match}=    Evaluate    'PIN' in '${source}' or 'pin' in '${source}' or 'Create' in '${source}' or 'Confirm' in '${source}'
    Log    [DISCOVERY] PIN: screen_match=${match} source_len=${source.__len__()}    WARN
    ${has_edit}=    Run Keyword And Return Status    Wait Until Page Contains Element    xpath=//android.widget.EditText    5s
    IF    ${has_edit}
        Run Keyword And Ignore Error    Input Text    xpath=(//android.widget.EditText)[1]    ${PIN_VALUE}
        Log    [DISCOVERY] PIN: entered ${PIN_VALUE}    WARN
        Sleep    2s
    END
    Adb Tap If Visible    accessibility_id=Next
    Adb Tap If Visible    accessibility_id=Continue
    Adb Tap If Visible    accessibility_id=Confirm

Adb Tap If Visible
    [Arguments]    ${locator}
    ${found}=    Run Keyword And Return Status    Wait Until Page Contains Element    ${locator}    3s
    IF    ${found}
        ${loc}=    Get Element Location    ${locator}
        ${sz}=    Get Element Size    ${locator}
        ${cx}=    Evaluate    int($loc['x'] + $sz['width'] / 2)
        ${cy}=    Evaluate    int($loc['y'] + $sz['height'] / 2)
        Run Process    adb    -s    ${EMULATOR_SERIAL}    shell    input    tap    ${cx}    ${cy}
        ...    timeout=15s    on_timeout=terminate
        Log    [DISCOVERY] Adb tapped ${locator} at ${cx},${cy}    WARN
    END
