*** Settings ***
Documentation    Sprint 2.30 Resume — Frida OCR Injection at Camera Screen
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
${DIR}    reports/investigation/frida_ocr_resume
${TESTDATA}    testdata/onboarding/ntb.local.yaml

*** Test Cases ***
Frida OCR Injection at Camera Screen
    Create Directory    ${DIR}
    Open Mobile Application
    ${prev}=    Set Log Level    NONE
    ${data}=    Load YAML    ${TESTDATA}
    Set Log Level    ${prev}

    # Navigate to camera screen
    Complete Common Onboarding    ${data['profile']['citizen_id']}    ${data['profile']['date_of_birth']}    ${data['profile']['mobile_number']}
    Log    [FLOW] Reached camera screen — app still running    WARN

    # App is now on camera screen — attach Frida
    Log    [FRIDA] Attaching Frida...    WARN
    ${result}=    Run Process    tools/frida/attach_and_wait.sh    tools/frida/ocr_callback_injector.js
    ...    timeout=20s    on_timeout=continue
    Log    [FRIDA] Result: ${result.stdout}    WARN

    # Wait a moment for hooks to settle
    Sleep    3s

    # Clear logcat for clean capture
    Run Process    adb    logcat    -c    2>/dev/null

    # Tap Take Photo via ADB (Frida hooks should be active)
    Log    [ACTION] Tapping Take Photo with Frida active    WARN
    Run Process    adb    shell    input    tap    540    2196

    # Wait for processing
    Sleep    15s

    # Capture evidence
    ${src}=    Get Source
    Create File    ${DIR}/after_take_photo.xml    ${src}    UTF-8
    Run Process    sh    -c    adb exec-out screencap -p > ${DIR}/after_take_photo.png

    # Check result
    ${has_rvcamera}=    Run Keyword And Return Status    Page Should Contain Element    xpath=//*[@resource-id="RVCamera"]
    Log    [RESULT] Still on camera: ${has_rvcamera}    WARN
    Run Keyword If    not ${has_rvcamera}
    ...    Log    [RESULT] *** SCREEN TRANSITIONED — OCR may have proceeded! ***    WARN

    # Capture logcat
    ${logcat}=    Run Process    adb    logcat    -d
    Create File    ${DIR}/logcat.txt    ${logcat.stdout}    UTF-8

    # Kill Frida and save its log
    Run Process    sh    -c    pkill -f "frida -U" 2>/dev/null
    Sleep    2s
    ${frida_log}=    Run Process    cat    /tmp/frida_attach_live.log
    Create File    ${DIR}/frida_log.txt    ${frida_log.stdout}    UTF-8

    # If transitioned, capture more evidence
    IF    not ${has_rvcamera}
        Log    [DISCOVERY] Capturing next screen details    WARN
        ${texts}=    Get Text    xpath=//*[1]
        Log    [DISCOVERY] Page texts: ${texts}    WARN
    END

    Close Application
