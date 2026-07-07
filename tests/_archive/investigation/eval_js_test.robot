*** Settings ***
Documentation    Sprint 2.61 — evaluateJavaScript OCR injection
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
${DIR}    reports/investigation/eval_js/evidence
${TESTDATA}    testdata/onboarding/ntb.local.yaml
${LANDING_TIMEOUT}    120s

*** Test Cases ***
Eval JS OCR Injection
    Create Directory    ${DIR}
    Open Mobile Application
    ${prev}=    Set Log Level    NONE
    ${data}=    Load YAML    ${TESTDATA}
    Set Log Level    ${prev}
    Log    [FLOW] App launched    WARN

    Run Process    tools/frida/start_frida_bg.sh    eval_js_ocr.js
    Sleep    5s
    Log    [FRIDA] eval_js hooks active    WARN

    Complete Common Onboarding
    ...    ${data['profile']['citizen_id']}
    ...    ${data['profile']['date_of_birth']}
    ...    ${data['profile']['mobile_number']}
    Log    [FLOW] Complete Common Onboarding finished (camera + take photo)    WARN

    Sleep    90s
    Log    [FLOW] 90s elapsed — Frida should have evaluated JS by now    WARN

    Run Process    sh    -c    adb exec-out screencap -p > ${DIR}/result_screen.png
    ${src}=    Get Source
    Create File    ${DIR}/result_source.xml    ${src}    UTF-8

    ${on_camera}=    Run Keyword And Return Status
    ...    Page Should Contain Element    xpath=//*[@resource-id="RVCamera"]
    Log    [RESULT] On camera: ${on_camera}    WARN
    Run Keyword If    not ${on_camera}
    ...    Log    [RESULT] *** NOT on camera — UI may have transitioned! ***    WARN

    ${frida_log}=    Run Process    cat    /tmp/frida_listener.log
    Create File    ${DIR}/frida_log.txt    ${frida_log.stdout}    UTF-8

    Run Process    sh    -c    pkill -f "frida -U" 2>/dev/null
    Sleep    2s
    Log    [FLOW] Done    WARN
    Close Application
