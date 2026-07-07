*** Settings ***
Documentation    Sprint 2.31 — Backend Availability Gate
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
${EVIDENCE_DIR}    reports/investigation/backend_gate
${TESTDATA}        testdata/onboarding/ntb.local.yaml

*** Test Cases ***
Backend Availability Check
    Create Directory    ${EVIDENCE_DIR}
    Open Mobile Application
    ${previous_log_level}=    Set Log Level    NONE
    ${data}=    Load YAML    ${TESTDATA}
    Set Log Level    ${previous_log_level}

    # Try to navigate through the flow
    ${status}=    Run Keyword And Ignore Error
    ...    Complete Common Onboarding
    ...    ${data['profile']['citizen_id']}
    ...    ${data['profile']['date_of_birth']}
    ...    ${data['profile']['mobile_number']}

    # Capture whatever screen we're on
    Sleep    3s
    ${source}=    Get Source
    Create File    ${EVIDENCE_DIR}/final_screen.xml    ${source}    UTF-8
    Run Process    sh    -c    adb exec-out screencap -p > ${EVIDENCE_DIR}/final_screenshot.png
    Log    [GATE] Final screen captured

    # Try to open debug panel
    ${has_dbg}=    Run Keyword And Return Status
    ...    Wait Until Element Is Visible    accessibility_id=Open debug panel    5s
    IF    ${has_dbg}
        Click Element    accessibility_id=Open debug panel
        Sleep    2s
        ${dbg_source}=    Get Source
        Create File    ${EVIDENCE_DIR}/debug_panel.xml    ${dbg_source}    UTF-8
        Log    [GATE] Debug panel captured
    END

    # Log result
    IF    '${status}[0]' == 'PASS'
        Log    [GATE] Onboarding completed successfully — backend is UP    WARN
    ELSE
        Log    [GATE] Onboarding FAILED — backend may be DOWN    WARN
        Log    [GATE] Error: ${status}[1]    WARN
    END

    Close Application
