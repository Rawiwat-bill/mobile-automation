*** Settings ***
Documentation    Sprint 2.63 — Promise trace with Complete Common Onboarding
Library    AppiumLibrary
Library    OperatingSystem
Library    Process
Resource   ../../resources/app/app_keywords.resource
Resource   ../../resources/keywords/onboarding_common.resource
Library    ../../libraries/config_loader.py

*** Variables ***
${TESTDATA}    testdata/onboarding/ntb.local.yaml
${DIR}    reports/investigation/promise_trace/evidence
${LANDING_TIMEOUT}    120s

*** Test Cases ***
Promise Trace With Full Flow
    Create Directory    ${DIR}
    Open Mobile Application
    ${prev}=    Set Log Level    NONE
    ${data}=    Load YAML    ${TESTDATA}
    Set Log Level    ${prev}
    Log    [FLOW] App launched    WARN

    Run Process    tools/frida/start_frida_bg.sh    promise_trace.js
    Sleep    5s
    Log    [FRIDA] Promise trace active    WARN

    Complete Common Onboarding
    ...    ${data['profile']['citizen_id']}
    ...    ${data['profile']['date_of_birth']}
    ...    ${data['profile']['mobile_number']}
    Log    [FLOW] *** COMPLETE FLOW DONE (camera + take photo) ***    WARN

    Sleep    20s
    Log    [FLOW] 20s buffer after Take Photo    WARN

    ${frida_log}=    Run Process    cat    /tmp/frida_listener.log
    Create File    ${DIR}/frida_trace.txt    ${frida_log.stdout}    UTF-8

    Capture Page Screenshot    ${DIR}/final_screen.png

    Run Process    sh    -c    pkill -f "frida -U" 2>/dev/null
    Sleep    2s
    Log    [FLOW] Done    WARN
    Close Application
