*** Settings ***
Documentation    Sprint 2.28 — Final Virtual Scene Validation (Evidence Only)
...              Navigates real app to ID Card Camera Capture with Frida attached
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
${EVIDENCE_DIR}    reports/investigation/final_virtual_scene
${TESTDATA}        testdata/onboarding/ntb.local.yaml

*** Test Cases ***
Final Virtual Scene Validation
    Create Directory    ${EVIDENCE_DIR}
    Open Mobile Application
    ${previous_log_level}=    Set Log Level    NONE
    ${data}=    Load YAML    ${TESTDATA}
    Set Log Level    ${previous_log_level}

    # Navigate through real app flow to camera screen
    Complete Common Onboarding    ${data['profile']['citizen_id']}    ${data['profile']['date_of_birth']}    ${data['profile']['mobile_number']}

    # Now on camera screen — wait for it to stabilize
    Sleep    3s

    # Capture state BEFORE Take Photo
    ${source}=    Get Source
    Create File    ${EVIDENCE_DIR}/xml_before.xml    ${source}    UTF-8
    Run Process    sh    -c    adb exec-out screencap -p > ${EVIDENCE_DIR}/screenshot_before.png
    Log    [EVIDENCE] Before state captured

    # Clear logcat for clean capture
    Run Process    adb    logcat    -c

    # Tap Take Photo using the app button
    Log    [ACTION] Tapping Take Photo    WARN
    Click Element    accessibility_id=Take photo

    # Wait for processing
    Sleep    10s

    # Capture state AFTER Take Photo
    ${source}=    Get Source
    Create File    ${EVIDENCE_DIR}/xml_after.xml    ${source}    UTF-8
    Run Process    sh    -c    adb exec-out screencap -p > ${EVIDENCE_DIR}/screenshot_after.png

    # Capture logcat
    ${logcat}=    Run Process    adb    logcat    -d
    Create File    ${EVIDENCE_DIR}/logcat.txt    ${logcat.stdout}    UTF-8

    # Check if screen changed
    ${has_rvcamera}=    Run Keyword And Return Status
    ...    Page Should Contain Element    xpath=//*[@resource-id="RVCamera"]
    Run Keyword If    not ${has_rvcamera}
    ...    Log    [RESULT] *** SCREEN TRANSITIONED — OCR may have proceeded ***    WARN
    Run Keyword If    ${has_rvcamera}
    ...    Log    [RESULT] Still on camera screen — OCR did not proceed    WARN

    Close Application
