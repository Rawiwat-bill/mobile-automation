*** Settings ***
Documentation    Sprint 2.21 — Debug Panel Discovery
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
${EVIDENCE_DIR}    reports/investigation/debug_panel
${TESTDATA}        testdata/onboarding/ntb.local.yaml
${DBG_BUTTON}      accessibility_id=Open debug panel

*** Test Cases ***
Discover Debug Panel
    Create Directory    ${EVIDENCE_DIR}
    Open Mobile Application
    ${previous_log_level}=    Set Log Level    NONE
    ${data}=    Load YAML    ${TESTDATA}
    Set Log Level    ${previous_log_level}

    # Navigate to camera screen (reuse full onboarding flow)
    Complete Common Onboarding    ${data['profile']['citizen_id']}    ${data['profile']['date_of_birth']}    ${data['profile']['mobile_number']}

    # Now on camera screen — tap DBG button
    Sleep    2s
    Capture Page Screenshot    ${EVIDENCE_DIR}/01_camera_screen.png
    ${source}=    Get Source
    Create File    ${EVIDENCE_DIR}/01_camera_screen.xml    ${source}    UTF-8
    Log    [DBG] Camera screen captured

    # Open debug panel
    Click Element    ${DBG_BUTTON}
    Sleep    2s
    Capture Page Screenshot    ${EVIDENCE_DIR}/02_debug_panel.png
    ${source}=    Get Source
    Create File    ${EVIDENCE_DIR}/02_debug_panel.xml    ${source}    UTF-8
    Log    [DBG] Debug panel captured

    Close Application
