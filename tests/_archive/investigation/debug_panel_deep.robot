*** Settings ***
Documentation    Sprint 2.21 — Debug Panel Deep Discovery
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
Deep Discover Debug Panel
    Create Directory    ${EVIDENCE_DIR}
    Open Mobile Application
    ${previous_log_level}=    Set Log Level    NONE
    ${data}=    Load YAML    ${TESTDATA}
    Set Log Level    ${previous_log_level}

    Complete Common Onboarding    ${data['profile']['citizen_id']}    ${data['profile']['date_of_birth']}    ${data['profile']['mobile_number']}

    # On camera screen — open debug panel
    Sleep    2s
    Click Element    ${DBG_BUTTON}
    Sleep    2s

    # Tap "Degug" button to discover sub-options
    Click Element    accessibility_id=Degug
    Sleep    2s
    Capture Page Screenshot    ${EVIDENCE_DIR}/03_after_degug.png
    ${source}=    Get Source
    Create File    ${EVIDENCE_DIR}/03_after_degug.xml    ${source}    UTF-8
    Log    [DBG] After Degug tapped

    # Go back — close whatever opened, reopen debug panel
    Run Keyword And Ignore Error    Click Element    accessibility_id=Close
    Sleep    1s
    Run Keyword And Ignore Error    Click Element    ${DBG_BUTTON}
    Sleep    1s

    # Expand the OCR network response
    Click Element    accessibility_id=Copy response
    Sleep    1s
    ${clipboard}=    Run Process    sh    -c    pbpaste
    Log    [DBG] Clipboard: ${clipboard.stdout[:500]}
    Create File    ${EVIDENCE_DIR}/04_ocr_response.txt    ${clipboard.stdout}    UTF-8

    # Expand first response entry
    Run Keyword And Ignore Error    Click Element    xpath=(//*[@content-desc="▼ , {"])[1]
    Sleep    1s
    Capture Page Screenshot    ${EVIDENCE_DIR}/05_expanded_response.png
    ${source}=    Get Source
    Create File    ${EVIDENCE_DIR}/05_expanded_response.xml    ${source}    UTF-8

    Close Application
