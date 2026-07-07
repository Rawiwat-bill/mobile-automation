*** Settings ***
Documentation    Sprint 2.60 Diagnostic — Does Take Photo trigger bridge.next()?
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
${DIR}    reports/investigation/diag_take_photo/evidence
${TESTDATA}    testdata/onboarding/ntb.local.yaml
${LANDING_TIMEOUT}    120s

*** Test Cases ***
Diagnostic Take Photo
    Create Directory    ${DIR}
    Open Mobile Application
    ${prev}=    Set Log Level    NONE
    ${data}=    Load YAML    ${TESTDATA}
    Set Log Level    ${prev}
    Log    [FLOW] App launched    WARN

    Run Process    tools/frida/start_frida_bg.sh    diag_take_photo.js
    Sleep    5s
    Log    [FRIDA] Diagnostic hooks active    WARN

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
    Log    [FLOW] Scan Card Intro Next tapped    WARN

    Wait Until Element Is Visible    ${ID_CARD_CAMERA_VIEW}    30s
    Log    [FLOW] Camera screen reached    WARN
    Sleep    3s
    Click Element    ${ID_CARD_TAKE_PHOTO}
    Log    [FLOW] Take Photo tapped — checking if bridge.next fires    WARN

    Sleep    15s
    Log    [FLOW] 15s after Take Photo — check Frida log    WARN

    Run Process    sh    -c    adb exec-out screencap -p > ${DIR}/after_take_photo.png

    ${frida_log}=    Run Process    cat    /tmp/frida_listener.log
    Create File    ${DIR}/frida_log.txt    ${frida_log.stdout}    UTF-8

    Run Process    sh    -c    pkill -f "frida -U" 2>/dev/null
    Sleep    2s
    Log    [FLOW] Done    WARN
    Close Application
