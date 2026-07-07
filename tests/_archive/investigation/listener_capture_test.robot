*** Settings ***
Documentation    Sprint 2.40 — Real Listener OCR Injection
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
${DIR}    reports/investigation/frida_node_listener
${TESTDATA}    testdata/onboarding/ntb.local.yaml

*** Test Cases ***
Real Listener OCR Injection
    Create Directory    ${DIR}
    Open Mobile Application
    ${prev}=    Set Log Level    NONE
    ${data}=    Load YAML    ${TESTDATA}
    Set Log Level    ${prev}
    Log    [FLOW] App launched    WARN

    # Attach Frida EARLY to capture listener during normal flow
    Run Process    tools/frida/start_frida_bg.sh    tools/frida/real_listener_inject.js
    Sleep    5s
    Log    [FRIDA] Early attach — listener capture active    WARN

    # Navigate through flow (Frida captures listener transparently)
    Complete Common Onboarding    ${data['profile']['citizen_id']}    ${data['profile']['date_of_birth']}    ${data['profile']['mobile_number']}
    Log    [FLOW] Reached camera screen — Frida should auto-inject    WARN

    # Wait for injection + server response + UI transition
    Sleep    40s

    # Capture evidence
    ${src}=    Get Source
    Create File    ${DIR}/after_injection.xml    ${src}    UTF-8
    Run Process    sh    -c    adb exec-out screencap -p > ${DIR}/after_injection.png

    # Check if screen transitioned
    ${has_rvcamera}=    Run Keyword And Return Status    Page Should Contain Element    xpath=//*[@resource-id="RVCamera"]
    Log    [RESULT] Still on camera: ${has_rvcamera}    WARN

    IF    not ${has_rvcamera}
        Log    [RESULT] *** UI TRANSITIONED — OCR ADVANCED! ***    WARN
        ${texts}=    Get Text    xpath=//*[1]
        Log    [DISCOVERY] Screen texts: ${texts}    WARN
    END

    # Kill Frida and save log
    Run Process    sh    -c    pkill -f "frida -U" 2>/dev/null
    Sleep    3s
    ${frida_log}=    Run Process    cat    /tmp/frida_listener.log
    Create File    ${DIR}/frida_log.txt    ${frida_log.stdout}    UTF-8

    Close Application
