*** Settings ***
Documentation    Sprint 2.29 — Virtual Scene Navigation Research
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
${EVIDENCE_DIR}    reports/investigation/virtual_scene_navigation
${TESTDATA}        testdata/onboarding/ntb.local.yaml

*** Test Cases ***
Virtual Scene Navigation Research
    Create Directory    ${EVIDENCE_DIR}
    Open Mobile Application
    ${previous_log_level}=    Set Log Level    NONE
    ${data}=    Load YAML    ${TESTDATA}
    Set Log Level    ${previous_log_level}

    # Navigate to camera screen through real app flow
    Complete Common Onboarding    ${data['profile']['citizen_id']}    ${data['profile']['date_of_birth']}    ${data['profile']['mobile_number']}

    # Confirm we're on camera screen
    Sleep    3s
    ${source}=    Get Source
    Create File    ${EVIDENCE_DIR}/camera_screen_baseline.xml    ${source}    UTF-8
    Run Process    sh    -c    adb exec-out screencap -p > ${EVIDENCE_DIR}/camera_screen_baseline.png
    Log    [NAV] Camera screen reached. Starting navigation.    WARN

    # Run the virtual scene navigation script
    ${result}=    Run Process    python3    tools/emulator/virtual_scene_navigation.py
    ...    timeout=120s    on_timeout=continue
    Create File    ${EVIDENCE_DIR}/navigation_stdout.txt    ${result.stdout}    UTF-8
    Create File    ${EVIDENCE_DIR}/navigation_stderr.txt    ${result.stderr}    UTF-8
    Log    [NAV] Navigation complete    WARN
    Log    [NAV] ${result.stdout}    WARN

    Close Application
