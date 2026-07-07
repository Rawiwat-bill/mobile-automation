*** Settings ***
Documentation    Sprint 2.52 — Network Boundary Trace (late attach)
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
${DIR}    reports/investigation/ntb_lc_network_boundary/evidence
${TESTDATA}    testdata/onboarding/ntb.local.yaml

*** Test Cases ***
Network Boundary Trace
    Create Directory    ${DIR}
    Open Mobile Application
    ${prev}=    Set Log Level    NONE
    ${data}=    Load YAML    ${TESTDATA}
    Set Log Level    ${prev}

    # Navigate to camera screen WITHOUT Frida (fast)
    Complete Common Onboarding    ${data['profile']['citizen_id']}    ${data['profile']['date_of_birth']}    ${data['profile']['mobile_number']}
    Log    [FLOW] Camera screen reached    WARN

    # NOW attach Frida (late — only NTB_LC submit needs OkHttp hooks)
    Run Process    tools/frida/start_frida_bg.sh    network_boundary_trace.js
    Sleep    5s
    Log    [FRIDA] Late attach — hooks active    WARN

    # Wait for OCR + NTB_LC trace
    Sleep    90s

    Run Process    sh    -c    pkill -f "frida -U" 2>/dev/null
    Sleep    3s
    ${frida_log}=    Run Process    cat    /tmp/frida_listener.log
    Create File    ${DIR}/frida_log.txt    ${frida_log.stdout}    UTF-8
    Log    [FLOW] Done    WARN

    Close Application
