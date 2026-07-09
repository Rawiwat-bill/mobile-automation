*** Settings ***
Documentation    RD-01 — real-device framework validation: fresh state -> OCR Camera (STOP, no capture).
...              OCR-10 lesson: the Consent WebView hangs Appium accessibility on Huawei/EMUI.
...              Mitigation: drive Consent (scroll + Accept) ADB-ONLY via tools/rd/adb_helpers.py;
...              no Appium Find Element / Get Source while the WebView is visible. Appium resumes on
...              native screens (Profile onward). Evidence captured via adb throughout.
Library          AppiumLibrary
Library          OperatingSystem
Library          Process
Library          String
Library          ../../libraries/config_loader.py
Resource         ../../resources/app/app_keywords.resource
Resource         ../../resources/pages/onboarding/landing_screen_page.resource
Resource         ../../resources/pages/onboarding/profile_screen_page.resource
Resource         ../../resources/pages/onboarding/pdpa_consent_page.resource
Resource         ../../resources/pages/onboarding/sign_up_page.resource
Resource         ../../resources/pages/onboarding/scan_card_intro_page.resource
Resource         ../../resources/pages/onboarding/id_card_camera_capture_page.resource


*** Variables ***
${UDID}             48ZYD25C01422768
${DEVICE_NAME}      MGA_LX3
${PLATFORM_VERSION}    10
${REPORT_DIR}       reports/real_device_validation/rd01
${EVIDENCE}         ${REPORT_DIR}/evidence
${HELPER}           ${CURDIR}/../../tools/rd/adb_helpers.py
${TESTDATA}         testdata/onboarding/ntb.local.yaml


*** Test Cases ***
Real Device Framework To OCR Camera
    Create Directory    ${REPORT_DIR}
    Create Directory    ${EVIDENCE}
    Reset App
    Open Installed App
    Allow Android Permission If Visible
    Capture Adb    landing
    Run Keyword And Ignore Error    Tap Landing Ready Button
    Allow Android Permission If Visible
    Wait Until Adb Screen Is    consent    40    CONSENT_HANG
    Capture Adb    consent_before
    ${cp}=    Run Process    python3    ${HELPER}    consent_pass    ${UDID}    timeout=120s    on_timeout=terminate
    Log    [RD-01] consent_pass stdout=${cp.stdout}
    ${profile_reached}=    Run Keyword And Return Status    Should Contain    ${cp.stdout}    profile_reached=1
    Capture Adb    consent_after
    Run Keyword If    not ${profile_reached}    Block And Stop    CONSENT_NO_TRANSITION
    ${profile_ok}=    Run Keyword And Return Status    Wait Until Profile Screen Is Displayed
    Run Keyword If    not ${profile_ok}    Block And Stop    PROFILE_BLOCKED
    Capture Adb    profile
    Fill Profile Fields Masked
    Run Keyword And Ignore Error    Tap Profile Next
    ${pdpa_ok}=    Run Keyword And Return Status    Wait Until PDPA Consent Screen Is Displayed
    Run Keyword If    not ${pdpa_ok}    Block And Stop    PDPA_BLOCKED
    Run Keyword And Ignore Error    Tap PDPA Consent Accept Button
    Capture Adb    pdpa
    ${signup_ok}=    Run Keyword And Return Status    Wait Until Sign Up Screen Is Displayed
    Run Keyword If    not ${signup_ok}    Block And Stop    SIGNUP_BLOCKED
    Run Keyword And Ignore Error    Tap Sign Up Lets Start Button
    Allow Android Permission If Visible
    Capture Adb    signup
    ${scan_ok}=    Run Keyword And Return Status    Wait Until Scan Card Intro Screen Is Displayed
    Run Keyword If    not ${scan_ok}    Block And Stop    SCAN_CARD_INTRO_BLOCKED
    Run Keyword And Ignore Error    Tap Scan Card Intro Next
    Allow Android Permission If Visible
    Capture Adb    scan_card_intro
    ${cam_ok}=    Run Keyword And Return Status    Wait Until ID Card Camera Capture Screen Is Displayed
    Run Keyword If    not ${cam_ok}    Block And Stop    OCR_CAMERA_NOT_REACHED
    Capture Adb    ocr_camera
    Write Result    RD_FRAMEWORK_TO_CAMERA_PASS
    [Teardown]    Run Keyword And Ignore Error    Close Application


*** Keywords ***
Reset App
    Run Process    adb    -s    ${UDID}    shell    am force-stop    ${APP_PACKAGE}
    ...    timeout=30s    on_timeout=terminate
    Run Process    adb    -s    ${UDID}    shell    pm clear    ${APP_PACKAGE}
    ...    timeout=30s    on_timeout=terminate
    Log    [RD-01] app force-stopped + pm cleared (fresh state)

Open Installed App
    Open Application
    ...    ${APPIUM_URL}
    ...    platformName=Android
    ...    automationName=UiAutomator2
    ...    udid=${UDID}
    ...    deviceName=${DEVICE_NAME}
    ...    platformVersion=${PLATFORM_VERSION}
    ...    appPackage=${APP_PACKAGE}
    ...    appActivity=${APP_ACTIVITY}
    ...    noReset=${TRUE}
    ...    autoGrantPermissions=${TRUE}
    ...    ignoreHiddenApiPolicyError=${TRUE}
    ...    disableWindowAnimation=${TRUE}
    ...    uiautomator2ServerInstallTimeout=120000
    ...    uiautomator2ServerLaunchTimeout=120000
    ...    newCommandTimeout=300

Fill Profile Fields Masked
    ${previous_log_level}=    Set Log Level    NONE
    ${data}=    Load YAML    ${TESTDATA}
    Run Keyword And Ignore Error    Input Citizen ID    ${data['profile']['citizen_id']}
    Run Keyword And Ignore Error    Input Date Of Birth    ${data['profile']['date_of_birth']}
    Run Keyword And Ignore Error    Input Mobile Number    ${data['profile']['mobile_number']}
    Set Log Level    ${previous_log_level}
    Log    [RD-01] Profile fields filled (masked)

Wait Until Adb Screen Is
    [Arguments]    ${expected}    ${timeout_s}    ${else}
    FOR    ${i}    IN RANGE    ${timeout_s}
        ${s}=    Adb Screen
        IF    '${s}' == '${expected}'
            Log    [RD-01] reached ${expected} after ${i}s
            RETURN
        END
        Sleep    1s
    END
    Block And Stop    ${else}

Block And Stop
    [Arguments]    ${classification}
    Capture Adb    blocker_${classification}
    Write Result    ${classification}
    Fail    Framework validation blocked: ${classification}

Write Result
    [Arguments]    ${classification}
    Create File    ${REPORT_DIR}/route_result.txt    classification=${classification}\n    UTF-8
    Log    [RD-01] RESULT ${classification}

Adb Screen
    ${r}=    Run Process    python3    ${HELPER}    screen    ${UDID}    timeout=45s    on_timeout=terminate
    ${s}=    Strip String    ${r.stdout}
    Log    [RD-01] adb screen=${s}
    RETURN    ${s}

Capture Adb
    [Arguments]    ${label}
    Run Process    python3    ${HELPER}    capture    ${UDID}    ${EVIDENCE}/${label}.png    ${EVIDENCE}/${label}.xml    ${EVIDENCE}/${label}_activity.txt
    ...    timeout=90s    on_timeout=terminate
    Log    [RD-01] captured ${label}

Adb Tap Resid
    [Arguments]    ${resid}
    ${r}=    Run Process    python3    ${HELPER}    tap_resid    ${UDID}    ${resid}    timeout=45s    on_timeout=terminate
    Log    [RD-01] adb tap_resid ${resid} -> ${r.stdout}
    RETURN    ${r.stdout}
