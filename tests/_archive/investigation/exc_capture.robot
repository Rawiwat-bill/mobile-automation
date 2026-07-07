*** Settings ***
Documentation    Sprint 2.44 v3 — Resolve AuthId Injection
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
${DIR}    reports/investigation/promise_state_verification
${TESTDATA}    testdata/onboarding/ntb.local.yaml

*** Test Cases ***
Resolve AuthId Injection
    Create Directory    ${DIR}
    Open Mobile Application
    ${prev}=    Set Log Level    NONE
    ${data}=    Load YAML    ${TESTDATA}
    Set Log Level    ${prev}
    Log    [FLOW] App launched    WARN

    Run Process    tools/frida/start_frida_bg.sh    current_node_inject.js
    Sleep    5s
    Log    [FRIDA] Resolve hook active    WARN

    Complete Common Onboarding    ${data['profile']['citizen_id']}    ${data['profile']['date_of_birth']}    ${data['profile']['mobile_number']}
    Log    [FLOW] Camera screen reached    WARN

    Sleep    30s

    ${src}=    Get Source
    Create File    ${DIR}/after_resolve_inject.xml    ${src}    UTF-8
    Run Process    sh    -c    adb exec-out screencap -p > ${DIR}/after_resolve_inject.png

    ${has_rvcamera}=    Run Keyword And Return Status    Page Should Contain Element    xpath=//*[@resource-id="RVCamera"]
    Log    [RESULT] Still on camera: ${has_rvcamera}    WARN
    Run Keyword If    not ${has_rvcamera}
    ...    Log    [RESULT] *** UI TRANSITIONED! ***    WARN

    Run Process    sh    -c    pkill -f "frida -U" 2>/dev/null
    Sleep    3s
    ${frida_log}=    Run Process    cat    /tmp/frida_listener.log
    Create File    ${DIR}/frida_resolve_inject.txt    ${frida_log.stdout}    UTF-8
    Log    [FLOW] Log saved    WARN

    Close Application
