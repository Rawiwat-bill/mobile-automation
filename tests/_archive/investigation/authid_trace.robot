*** Settings ***
Documentation    Sprint 2.51 — AuthId Session Trace
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
AuthId Session Trace
    Create Directory    ${DIR}
    Open Mobile Application
    ${prev}=    Set Log Level    NONE
    ${data}=    Load YAML    ${TESTDATA}
    Set Log Level    ${prev}
    Log    [FLOW] App launched    WARN

    Run Process    tools/frida/start_frida_bg.sh    authid_session_trace.js
    Sleep    5s
    Log    [FRIDA] Trace hooks active    WARN

    Complete Common Onboarding    ${data['profile']['citizen_id']}    ${data['profile']['date_of_birth']}    ${data['profile']['mobile_number']}
    Log    [FLOW] Camera screen reached    WARN

    # Wait for OCR injection + NTB_LC submit
    Sleep    90s

    Run Process    sh    -c    pkill -f "frida -U" 2>/dev/null
    Sleep    3s
    ${frida_log}=    Run Process    cat    /tmp/frida_listener.log
    Create File    ${DIR}/frida_log.txt    ${frida_log.stdout}    UTF-8
    Log    [FLOW] Trace log saved    WARN

    Close Application
