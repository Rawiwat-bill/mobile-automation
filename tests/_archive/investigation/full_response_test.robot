*** Settings ***
Documentation    Sprint 2.58 — Full Response Bridge Fix
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
${DIR}    reports/investigation/full_response_bridge_fix/evidence
${TESTDATA}    testdata/onboarding/ntb.local.yaml

*** Test Cases ***
Full Response Bridge Fix
    Create Directory    ${DIR}
    Open Mobile Application
    ${prev}=    Set Log Level    NONE
    ${data}=    Load YAML    ${TESTDATA}
    Set Log Level    ${prev}

    Complete Common Onboarding    ${data['profile']['citizen_id']}    ${data['profile']['date_of_birth']}    ${data['profile']['mobile_number']}
    Log    [FLOW] Camera screen reached    WARN

    # Capture before screenshot
    Run Process    sh    -c    adb exec-out screencap -p > ${DIR}/before_ocr.png

    # Attach Frida with the fix
    Run Process    tools/frida/start_frida_bg.sh    full_response_fix.js
    Sleep    5s
    Log    [FRIDA] Full Response fix attached    WARN

    # Wait for OCR injection + bridge.next() with full payload
    Sleep    60s

    # Capture after screenshot
    Run Process    sh    -c    adb exec-out screencap -p > ${DIR}/after_ocr.png

    # Capture page source
    ${src}=    Get Source
    Create File    ${DIR}/after_ocr.xml    ${src}    UTF-8

    # Check result
    ${has_rvcamera}=    Run Keyword And Return Status    Page Should Contain Element    xpath=//*[@resource-id="RVCamera"]
    Log    [RESULT] Still on camera: ${has_rvcamera}    WARN
    Run Keyword If    not ${has_rvcamera}
    ...    Log    [RESULT] *** UI TRANSITIONED — OCR ADVANCED! ***    WARN

    # Save Frida log
    Run Process    sh    -c    pkill -f "frida -U" 2>/dev/null
    Sleep    3s
    ${frida_log}=    Run Process    cat    /tmp/frida_listener.log
    Create File    ${DIR}/frida_log.txt    ${frida_log.stdout}    UTF-8

    # Save logcat
    ${logcat}=    Run Process    adb    logcat    -d
    Create File    ${DIR}/logcat.txt    ${logcat.stdout}    UTF-8

    Log    [FLOW] Done    WARN
    Close Application
