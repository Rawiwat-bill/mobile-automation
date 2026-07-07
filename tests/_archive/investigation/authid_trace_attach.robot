*** Settings ***
Documentation    Sprint 2.51 — AuthId Trace (attach to running app)
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
Resource   ../../resources/keywords/onboarding_common.resource
Library    ../../libraries/config_loader.py

*** Variables ***
${DIR}    reports/investigation/auth_session_trace/evidence
${TESTDATA}    testdata/onboarding/ntb.local.yaml

*** Test Cases ***
AuthId Trace
    Create Directory    ${DIR}
    # Attach to running app
    Open Application
    ...    http://127.0.0.1:4723
    ...    platformName=Android
    ...    automationName=UiAutomator2
    ...    deviceName=Android Emulator
    ...    appPackage=com.bangkokbank.blue.dev
    ...    appActivity=com.bangkokbank.blue.MainActivity
    ...    noReset=true
    ...    dontStopAppOnReset=true

    ${prev}=    Set Log Level    NONE
    ${data}=    Load YAML    ${TESTDATA}
    Set Log Level    ${prev}

    # Attach Frida trace hooks
    Run Process    tools/frida/start_frida_bg.sh    authid_session_trace.js
    Sleep    5s
    Log    [FRIDA] Trace active    WARN

    # Complete remaining flow from current state
    Wait Until Consent Screen Is Displayed
    Tap Consent Accept Button
    Wait Until Profile Screen Is Displayed
    Input Citizen ID    ${data['profile']['citizen_id']}
    Input Date Of Birth    ${data['profile']['date_of_birth']}
    Input Mobile Number    ${data['profile']['mobile_number']}
    Tap Profile Next
    Wait Until PDPA Consent Screen Is Displayed
    ${pdpa}=    Tap PDPA Consent Accept Button
    Should Be True    ${pdpa}
    Wait Until Sign Up Screen Is Displayed
    Tap Sign Up Lets Start Button
    Allow Android Permission If Visible
    Wait Until Scan Card Intro Screen Is Displayed
    Tap Scan Card Intro Next
    Allow Android Permission If Visible
    Wait Until ID Card Camera Capture Screen Is Displayed
    Log    [FLOW] Camera screen reached — waiting for OCR injection    WARN

    Sleep    90s

    Run Process    sh    -c    pkill -f "frida -U" 2>/dev/null
    Sleep    3s
    ${frida_log}=    Run Process    cat    /tmp/frida_listener.log
    Create File    ${DIR}/frida_log.txt    ${frida_log.stdout}    UTF-8
    Log    [FLOW] Done    WARN

    Close Application
