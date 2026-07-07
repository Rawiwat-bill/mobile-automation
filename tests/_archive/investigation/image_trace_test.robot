*** Settings ***
Documentation    Sprint 2.67 — Image pipeline trace
Library    AppiumLibrary
Library    OperatingSystem
Library    Process
Resource   ../../resources/app/app_keywords.resource
Resource   ../../resources/keywords/onboarding_common.resource
Library    ../../libraries/config_loader.py

*** Variables ***
${TESTDATA}    testdata/onboarding/ntb.local.yaml
${DIR}    reports/investigation/image_pipeline/evidence
${LANDING_TIMEOUT}    120s

*** Test Cases ***
Image Pipeline Trace
    Create Directory    ${DIR}
    Open Mobile Application
    ${prev}=    Set Log Level    NONE
    ${data}=    Load YAML    ${TESTDATA}
    Set Log Level    ${prev}
    Log    [FLOW] App launched    WARN

    Run Process    tools/frida/start_frida_bg.sh    image_pipeline_trace.js
    Sleep    5s
    Log    [FRIDA] Image pipeline trace active    WARN

    Complete Common Onboarding
    ...    ${data['profile']['citizen_id']}
    ...    ${data['profile']['date_of_birth']}
    ...    ${data['profile']['mobile_number']}
    Log    [FLOW] Camera reached + Take Photo tapped    WARN

    Sleep    15s
    Log    [FLOW] 15s buffer    WARN

    ${frida_log}=    Run Process    cat    /tmp/frida_listener.log
    Create File    ${DIR}/frida_trace.txt    ${frida_log.stdout}    UTF-8

    Run Process    sh    -c    pkill -f "frida -U" 2>/dev/null
    Sleep    2s
    Close Application
