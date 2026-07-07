*** Settings ***
Documentation    Sprint 2.68 — Android Real Device Baseline (no Frida)
...              Wrapper only: does NOT modify production Open Mobile Application.
...              Reuses onboarding page keywords. Skips emulator-only virtual-camera step.
Library          AppiumLibrary
Library          OperatingSystem
Library          Process
Library          ../../libraries/config_loader.py
Resource         ../../resources/pages/onboarding/landing_screen_page.resource
Resource         ../../resources/pages/onboarding/consent_screen_page.resource
Resource         ../../resources/pages/onboarding/profile_screen_page.resource
Resource         ../../resources/pages/onboarding/pdpa_consent_page.resource
Resource         ../../resources/pages/onboarding/sign_up_page.resource
Resource         ../../resources/pages/onboarding/scan_card_intro_page.resource
Resource         ../../resources/pages/onboarding/id_card_camera_capture_page.resource
Resource         ../../resources/app/app_keywords.resource

*** Variables ***
${UDID}           48ZYD25C01422768
${EVIDENCE}       reports/investigation/real_device_baseline/evidence
${TESTDATA}       testdata/onboarding/ntb.local.yaml
${SCREEN_TIMEOUT}    60s

*** Test Cases ***
Phase 0 Appium Smoke
    [Documentation]    Confirm Appium controls the real device: open app, capture, close.
    Create Directory    ${EVIDENCE}
    Open Application On Real Device
    Sleep    5s
    Run Process    sh    -c    adb -s ${UDID} exec-out screencap -p > ${EVIDENCE}/phase0_screenshot.png
    ${src}=    Get Source
    Create File    ${EVIDENCE}/phase0_source.xml    ${src}    UTF-8
    Log    [PHASE0] App opened and source captured on real device ${UDID}    WARN
    [Teardown]    Close Application

Real Device Clean Baseline
    [Documentation]    Walk Landing -> Consent -> Profile -> PDPA -> SignUp -> ScanCardIntro -> Camera -> Take Photo
    ...                Capture screenshot+XML at each major screen. No Frida.
    Create Directory    ${EVIDENCE}
    Open Application On Real Device

    # --- Landing ---
    ${landing}=    Run Keyword And Return Status    Wait Until Landing Screen Is Displayed
    Capture Stage Evidence    landing    ${landing}
    Run Keyword If    not ${landing}    Fail    Landing screen not reached on real device.

    ${ready}=    Run Keyword And Return Status    Tap Landing Ready Button
    Allow Android Permission If Visible
    Capture Stage Evidence    01_after_landing    ${ready}

    # --- Consent ---
    ${consent}=    Run Keyword And Return Status    Wait Until Element Is Visible    ${CONSENT_TITLE_TEXT}    ${SCREEN_TIMEOUT}
    Capture Stage Evidence    02_consent    ${consent}
    Run Keyword If    not ${consent}    Fail    Consent screen not reached.
    Run Keyword If    ${consent}    Run Keyword And Ignore Error    Tap Consent Accept Button

    # --- Profile (CND input) ---
    ${profile}=    Run Keyword And Return Status    Wait Until Element Is Visible    ${PROFILE_TITLE_TEXT}    ${SCREEN_TIMEOUT}
    Capture Stage Evidence    03_profile    ${profile}
    Run Keyword If    not ${profile}    Fail    Profile screen not reached.
    ${data}=    Load YAML    ${TESTDATA}
    Run Keyword If    ${profile}    Run Keyword And Ignore Error    Input Citizen ID    ${data['profile']['citizen_id']}
    Run Keyword If    ${profile}    Run Keyword And Ignore Error    Input Date Of Birth    ${data['profile']['date_of_birth']}
    Run Keyword If    ${profile}    Run Keyword And Ignore Error    Input Mobile Number    ${data['profile']['mobile_number']}
    Capture Stage Evidence    03b_profile_filled    ${TRUE}
    Run Keyword If    ${profile}    Run Keyword And Ignore Error    Tap Profile Next
    Capture Stage Evidence    04_after_profile    ${TRUE}

    # --- PDPA ---
    ${pdpa}=    Run Keyword And Return Status    Wait Until Element Is Visible    ${PDPA_SCREEN_HEADER}    ${SCREEN_TIMEOUT}
    Capture Stage Evidence    05_pdpa    ${pdpa}
    Run Keyword If    not ${pdpa}    Fail    PDPA screen not reached.
    Run Keyword If    ${pdpa}    Run Keyword And Ignore Error    Tap PDPA Consent Accept Button
    Capture Stage Evidence    06_after_pdpa    ${TRUE}

    # --- Sign Up ---
    ${signup}=    Run Keyword And Return Status    Wait Until Element Is Visible    ${SIGN_UP_LETS_START}    ${SCREEN_TIMEOUT}
    Capture Stage Evidence    07_signup    ${signup}
    Run Keyword If    ${signup}    Click Element    ${SIGN_UP_LETS_START}
    Allow Android Permission If Visible

    # --- Scan Card Intro ---
    ${scan}=    Run Keyword And Return Status    Wait Until Element Is Visible    ${SCAN_CARD_INTRO_STEP_BAR}    ${SCREEN_TIMEOUT}
    Capture Stage Evidence    08_scan_card_intro    ${scan}
    Run Keyword If    ${scan}    Click Element    ${SCAN_CARD_INTRO_NEXT}
    Allow Android Permission If Visible

    # --- ID Card Camera ---
    ${camera}=    Run Keyword And Return Status    Wait Until Element Is Visible    ${ID_CARD_CAMERA_VIEW}    ${SCREEN_TIMEOUT}
    Capture Stage Evidence    09_camera_before_ocr    ${camera}
    Run Keyword If    not ${camera}    Fail    ID Card Camera screen not reached.

    # --- Tap Take Photo and observe ---
    ${take_photo}=    Run Keyword And Return Status    Wait Until Element Is Visible    ${ID_CARD_TAKE_PHOTO}    15s
    Run Keyword If    ${take_photo}    Click Element    ${ID_CARD_TAKE_PHOTO}
    Sleep    20s
    Capture Stage Evidence    10_after_take_photo    ${TRUE}
    Log    [BASELINE] Flow complete up to post-Take-Photo observation.    WARN
    [Teardown]    Close Application

*** Keywords ***
Open Application On Real Device
    Open Application
    ...    http://127.0.0.1:4723
    ...    platformName=Android
    ...    automationName=UiAutomator2
    ...    udid=${UDID}
    ...    deviceName=MGA_LX3
    ...    platformVersion=10
    ...    appPackage=com.bangkokbank.blue.dev
    ...    appActivity=com.bangkokbank.blue.MainActivity
    ...    noReset=${TRUE}
    ...    autoGrantPermissions=${TRUE}
    ...    ignoreHiddenApiPolicyError=${TRUE}
    ...    disableWindowAnimation=${TRUE}
    ...    uiautomator2ServerInstallTimeout=120000
    ...    uiautomator2ServerLaunchTimeout=120000
    ...    newCommandTimeout=300

Capture Stage Evidence
    [Arguments]    ${stage}    ${reached}
    ${png}=    Set Variable    ${EVIDENCE}/${stage}.png
    ${xml}=    Set Variable    ${EVIDENCE}/${stage}.xml
    Run Process    sh    -c    adb -s ${UDID} exec-out screencap -p > ${png}
    ...    timeout=30s    on_timeout=ignore
    ${status}    ${src}=    Run Keyword And Ignore Error    Get Source
    Run Keyword If    '${status}' == 'PASS'    Create File    ${xml}    ${src}    UTF-8
    Log    [BASELINE] stage=${stage} reached=${reached}    WARN
