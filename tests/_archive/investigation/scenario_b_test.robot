*** Settings ***
Documentation    Sprint 2.59 Scenario B — Bridge Only
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
${DIR}    reports/investigation/transaction_ownership/evidence
${TESTDATA}    testdata/onboarding/ntb.local.yaml

*** Test Cases ***
Scenario B Bridge Only
    Create Directory    ${DIR}
    Open Mobile Application
    ${prev}=    Set Log Level    NONE
    ${data}=    Load YAML    ${TESTDATA}
    Set Log Level    ${prev}
    Log    [FLOW] App launched    WARN

    Run Process    tools/frida/start_frida_bg.sh    scenario_b_bridge_only.js
    Sleep    5s
    Log    [FRIDA] Scenario B hooks active    WARN

    Complete Common Onboarding    ${data['profile']['citizen_id']}    ${data['profile']['date_of_birth']}    ${data['profile']['mobile_number']}
    Log    [FLOW] Camera screen reached    WARN

    Run Process    sh    -c    adb exec-out screencap -p > ${DIR}/before_ocr.png

    Sleep    60s

    Run Process    sh    -c    adb exec-out screencap -p > ${DIR}/after_ocr.png
    ${src}=    Get Source
    Create File    ${DIR}/after_ocr.xml    ${src}    UTF-8

    ${has_rvcamera}=    Run Keyword And Return Status    Page Should Contain Element    xpath=//*[@resource-id="RVCamera"]
    Log    [RESULT] Still on camera: ${has_rvcamera}    WARN
    Run Keyword If    not ${has_rvcamera}
    ...    Log    [RESULT] *** UI TRANSITIONED! ***    WARN

    Run Process    sh    -c    pkill -f "frida -U" 2>/dev/null
    Sleep    3s
    ${frida_log}=    Run Process    cat    /tmp/frida_listener.log
    Create File    ${DIR}/frida_log_scenario_b.txt    ${frida_log.stdout}    UTF-8
    Log    [FLOW] Done    WARN
    Close Application
