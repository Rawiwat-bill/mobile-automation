*** Settings ***
Documentation    Sprint 2.63 — Emit topInitialized + hook takePhoto
Library    AppiumLibrary
Library    OperatingSystem
Library    Process
Resource   ../../resources/app/app_keywords.resource
Resource   ../../resources/pages/onboarding/landing_screen_page.resource
Resource   ../../resources/pages/onboarding/consent_screen_page.resource
Resource   ../../resources/pages/onboarding/profile_screen_page.resource
Resource   ../../resources/pages/onboarding/pdpa_consent_page.resource
Resource   ../../resources/pages/onboarding/sign_up_page.resource
Resource   ../../resources/pages/onboarding/scan_card_intro_page.resource
Resource   ../../resources/pages/onboarding/id_card_camera_capture_page.resource
Library    ../../libraries/config_loader.py

*** Variables ***
${DIR}    reports/investigation/init_takephoto/evidence
${TESTDATA}    testdata/onboarding/ntb.local.yaml
${LANDING_TIMEOUT}    120s
${CONSENT_TIMEOUT}    60s

*** Test Cases ***
Init And TakePhoto Injection
    Create Directory    ${DIR}
    Open Mobile Application
    ${prev}=    Set Log Level    NONE
    ${data}=    Load YAML    ${TESTDATA}
    Set Log Level    ${prev}
    Log    [FLOW] App launched    WARN

    Run Process    tools/frida/start_frida_bg.sh    init_and_takephoto.js
    Sleep    5s
    Log    [FRIDA] init+takePhoto hooks active    WARN

    Wait Until Landing Screen Is Displayed
    Tap Landing Ready Button
    Allow Android Permission If Visible
    Log    [FLOW] Landing done    WARN

    Wait Until Consent Screen Is Displayed
    Tap Consent Accept Button
    Log    [FLOW] Consent done    WARN

    Wait Until Profile Screen Is Displayed
    Input Citizen ID    ${data['profile']['citizen_id']}
    Input Date Of Birth    ${data['profile']['date_of_birth']}
    Input Mobile Number    ${data['profile']['mobile_number']}
    Sleep    2s
    Tap Profile Next
    Log    [FLOW] Profile done    WARN

    Wait Until PDPA Consent Screen Is Displayed
    Tap PDPA Consent Accept Button
    Log    [FLOW] PDPA done    WARN

    Wait Until Sign Up Screen Is Displayed
    Tap Sign Up Lets Start Button
    Allow Android Permission If Visible
    Log    [FLOW] Sign Up done    WARN

    Wait Until Scan Card Intro Screen Is Displayed
    Tap Scan Card Intro Next
    Allow Android Permission If Visible
    Log    [FLOW] Scan Card Intro done    WARN

    Wait Until Element Is Visible    ${ID_CARD_CAMERA_VIEW}
    Log    [FLOW] *** CAMERA SCREEN REACHED ***    WARN

    Sleep    10s
    Log    [FLOW] 10s buffer for topInitialized event    WARN

    Click Element    ${ID_CARD_TAKE_PHOTO}
    Log    [FLOW] *** TAKE PHOTO TAPPED ***    WARN

    Sleep    30s
    Log    [FLOW] 30s elapsed — checking results    WARN

    Run Process    sh    -c    adb exec-out screencap -p > ${DIR}/result_screen.png
    ${src}=    Get Source
    Create File    ${DIR}/result_source.xml    ${src}    UTF-8

    ${on_camera}=    Run Keyword And Return Status
    ...    Page Should Contain Element    xpath=//*[@resource-id="RVCamera"]
    Log    [RESULT] On camera: ${on_camera}    WARN
    Run Keyword If    not ${on_camera}
    ...    Log    [RESULT] *** NOT on camera — UI TRANSITIONED! ***    WARN

    ${frida_log}=    Run Process    cat    /tmp/frida_listener.log
    Create File    ${DIR}/frida_log.txt    ${frida_log.stdout}    UTF-8

    Run Process    sh    -c    pkill -f "frida -U" 2>/dev/null
    Sleep    2s
    Log    [FLOW] Done    WARN
    Close Application
