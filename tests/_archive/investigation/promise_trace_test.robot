*** Settings ***
Documentation    Sprint 2.63 — Real Promise Capture: trace all bridge.next promises
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
${DIR}    reports/investigation/promise_trace/evidence
${TESTDATA}    testdata/onboarding/ntb.local.yaml
${LANDING_TIMEOUT}    120s
${CONSENT_TIMEOUT}    60s

*** Test Cases ***
Promise Trace Full Flow
    Create Directory    ${DIR}
    Open Mobile Application
    ${prev}=    Set Log Level    NONE
    ${data}=    Load YAML    ${TESTDATA}
    Set Log Level    ${prev}
    Log    [FLOW] App launched    WARN

    Navigate To Camera For Promise Trace    ${data['profile']['citizen_id']}    ${data['profile']['date_of_birth']}    ${data['profile']['mobile_number']}
    Log    [FLOW] Camera screen reached    WARN

    Wait Until Element Is Visible    ${ID_CARD_CAMERA_VIEW}
    Log    [FLOW] *** CAMERA SCREEN REACHED ***    WARN

    Run Process    tools/frida/start_frida_bg.sh    promise_trace.js
    Sleep    5s
    Log    [FRIDA] Promise tracing active    WARN

    Sleep    5s
    Log    [FLOW] *** TAPPING TAKE PHOTO ***    WARN
    Click Element    ${ID_CARD_TAKE_PHOTO}
    Log    [FLOW] *** TAKE PHOTO CLICKED ***    WARN

    Sleep    20s
    Log    [FLOW] 20s after Take Photo — capturing results    WARN

    ${frida_log}=    Run Process    cat    /tmp/frida_listener.log
    Create File    ${DIR}/frida_trace.txt    ${frida_log.stdout}    UTF-8

    Capture Page Screenshot    ${DIR}/final_screen.png

    ${on_camera}=    Run Keyword And Return Status
    ...    Page Should Contain Element    xpath=//*[@resource-id="RVCamera"]
    Log    [RESULT] On camera: ${on_camera}    WARN

    Run Process    sh    -c    pkill -f "frida -U" 2>/dev/null
    Sleep    2s
    Log    [FLOW] Done    WARN
    Close Application

*** Keywords ***
Navigate To Camera For Promise Trace
    [Arguments]    ${citizen_id}    ${date_of_birth}    ${mobile_number}
    Wait Until Landing Screen Is Displayed
    Tap Landing Ready Button
    Allow Android Permission If Visible
    Wait Until Consent Screen Is Displayed
    Tap Consent Accept Button
    Wait Until Profile Screen Is Displayed
    Input Citizen ID    ${citizen_id}
    Input Date Of Birth    ${date_of_birth}
    Input Mobile Number    ${mobile_number}
    Tap Profile Next
    Wait Until PDPA Consent Screen Is Displayed
    ${pdpa_accepted}=    Tap PDPA Consent Accept Button
    Should Be True    ${pdpa_accepted}    PDPA did not transition before camera navigation.
    Wait Until Sign Up Screen Is Displayed
    Tap Sign Up Lets Start Button
    Allow Android Permission If Visible
    Wait Until Scan Card Intro Screen Is Displayed
    Tap Scan Card Intro Next
    Allow Android Permission If Visible
    Wait Until ID Card Camera Capture Screen Is Displayed
    Navigate Virtual Camera To Poster
