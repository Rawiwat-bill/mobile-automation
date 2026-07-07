*** Settings ***
Documentation    Sprint 2.34 — Frida Node Injection for OCR Unblock
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
${DIR}    reports/investigation/frida_node_injection
${TESTDATA}    testdata/onboarding/ntb.local.yaml

*** Test Cases ***
Frida Node Injection for OCR
    Create Directory    ${DIR}
    Open Mobile Application
    ${prev}=    Set Log Level    NONE
    ${data}=    Load YAML    ${TESTDATA}
    Set Log Level    ${prev}

    # Navigate to camera screen
    Complete Common Onboarding    ${data['profile']['citizen_id']}    ${data['profile']['date_of_birth']}    ${data['profile']['mobile_number']}
    Log    [FLOW] Reached camera screen    WARN


    # Attach Frida with Node injector
    Log    [FRIDA] Attaching Node injector...    WARN
    ${result}=    Run Process    tools/frida/attach_and_wait.sh    tools/frida/ocr_image_embedded.js
    ...    timeout=25s    on_timeout=continue
    Log    [FRIDA] ${result.stdout}    WARN

    # Wait for all format attempts to complete (4 formats × 10s each + buffer)
    Sleep    25s

    # Capture evidence
    ${src}=    Get Source
    Create File    ${DIR}/after_injection.xml    ${src}    UTF-8
    Run Process    sh    -c    adb exec-out screencap -p > ${DIR}/after_injection.png

    # Check result
    ${has_rvcamera}=    Run Keyword And Return Status    Page Should Contain Element    xpath=//*[@resource-id="RVCamera"]
    Log    [RESULT] Still on camera: ${has_rvcamera}    WARN

    IF    not ${has_rvcamera}
        Log    [RESULT] *** SCREEN TRANSITIONED — OCR MAY HAVE ADVANCED! ***    WARN
        ${texts}=    Get Text    xpath=//*[1]
        Log    [DISCOVERY] Page content: ${texts}    WARN
    END

    # Kill Frida and save log
    Run Process    sh    -c    pkill -f "frida -U" 2>/dev/null
    Sleep    3s
    ${frida_log}=    Run Process    cat    /tmp/frida_attach_live.log
    Create File    ${DIR}/frida_injection.log    ${frida_log.stdout}    UTF-8

    # Save logcat
    ${logcat}=    Run Process    adb    logcat    -d
    Create File    ${DIR}/logcat.txt    ${logcat.stdout}    UTF-8

    Close Application
