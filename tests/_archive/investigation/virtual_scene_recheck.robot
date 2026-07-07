*** Settings ***
Documentation    Sprint 2.24.1 — Virtual Scene Visual Recheck
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
${EVIDENCE_DIR}    reports/investigation/virtual_scene_recheck
${TESTDATA}        testdata/onboarding/ntb.local.yaml

*** Test Cases ***
Recheck Virtual Scene With Variants
    Create Directory    ${EVIDENCE_DIR}
    Open Mobile Application
    ${previous_log_level}=    Set Log Level    NONE
    ${data}=    Load YAML    ${TESTDATA}
    Set Log Level    ${previous_log_level}

    # Navigate to camera screen (full onboarding)
    Complete Common Onboarding    ${data['profile']['citizen_id']}    ${data['profile']['date_of_birth']}    ${data['profile']['mobile_number']}

    # Now on camera screen — capture for each variant
    Sleep    3s

    # The poster was already set before this test by the bash script
    # Capture current state
    Run Process    sh    -c    adb exec-out screencap -p > ${EVIDENCE_DIR}/camera_view.png
    Log    [RECHECK] Camera view captured
    Close Application
