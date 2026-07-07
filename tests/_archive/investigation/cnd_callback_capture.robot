*** Settings ***
Documentation    Sprint 2.32 — CND Callback Capture
...              Navigates to Profile, taps Next, captures debug panel response
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
${EVIDENCE_DIR}    reports/investigation/cnd_callback_mismatch
${TESTDATA}        testdata/onboarding/ntb.local.yaml

*** Test Cases ***
Capture CND Response
    Create Directory    ${EVIDENCE_DIR}
    Open Mobile Application
    ${previous_log_level}=    Set Log Level    NONE
    ${data}=    Load YAML    ${TESTDATA}
    Set Log Level    ${previous_log_level}

    # Navigate to Profile screen only (don't tap Next yet)
    Wait Until Landing Screen Is Displayed
    Tap Landing Ready Button
    Allow Android Permission If Visible
    Wait Until Consent Screen Is Displayed
    Tap Consent Accept Button
    Wait Until Profile Screen Is Displayed

    # Enter profile data
    Input Citizen ID    ${data['profile']['citizen_id']}
    Input Date Of Birth    ${data['profile']['date_of_birth']}
    Input Mobile Number    ${data['profile']['mobile_number']}
    Capture Profile Handoff Snapshot    profile_filled

    # Capture debug panel BEFORE Next
    Click Element    accessibility_id=Open debug panel
    Sleep    2s
    ${source}=    Get Source
    Create File    ${EVIDENCE_DIR}/debug_before_next.xml    ${source}    UTF-8
    Click Element    accessibility_id=Close
    Sleep    1s

    # Tap Next
    Tap Profile Next
    Sleep    5s

    # Capture whatever screen we're on
    ${source}=    Get Source
    Create File    ${EVIDENCE_DIR}/screen_after_next.xml    ${source}    UTF-8
    Run Process    sh    -c    adb exec-out screencap -p > ${EVIDENCE_DIR}/screenshot_after_next.png

    # Open debug panel AFTER Next
    ${has_dbg}=    Run Keyword And Return Status
    ...    Wait Until Element Is Visible    accessibility_id=Open debug panel    5s
    IF    ${has_dbg}
        Click Element    accessibility_id=Open debug panel
        Sleep    2s
        ${source}=    Get Source
        Create File    ${EVIDENCE_DIR}/debug_after_next.xml    ${source}    UTF-8

        # Copy the first response to clipboard
        Run Keyword And Ignore Error    Click Element    accessibility_id=Copy response
        Sleep    1s
        ${clip}=    Run Process    sh    -c    pbpaste
        Create File    ${EVIDENCE_DIR}/cnd_response.json    ${clip.stdout}    UTF-8
    END

    Close Application
