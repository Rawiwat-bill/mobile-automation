*** Settings ***
Documentation    Sprint 2.40 — Capture authId lengths per stage
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

*** Test Cases ***
Capture AuthId Per Stage
    Open Mobile Application
    ${prev}=    Set Log Level    NONE
    ${data}=    Load YAML    testdata/onboarding/ntb.local.yaml
    Set Log Level    ${prev}

    # Attach Frida early
    Run Process    tools/frida/start_frida_bg.sh    tools/frida/mid_q30_test.js
    Sleep    5s
    Log    [FRIDA] Attached    WARN

    # Run flow
    Complete Common Onboarding    ${data['profile']['citizen_id']}    ${data['profile']['date_of_birth']}    ${data['profile']['mobile_number']}
    Log    [FLOW] Done    WARN

    # Save Frida log
    Run Process    sh    -c    pkill -f "frida -U" 2>/dev/null
    Sleep    3s
    ${frida_log}=    Run Process    cat    /tmp/frida_listener.log
    Create File    reports/investigation/frida_node_listener/authid_per_stage.txt    ${frida_log.stdout}    UTF-8

    Close Application
