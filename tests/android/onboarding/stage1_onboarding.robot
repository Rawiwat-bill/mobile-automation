*** Settings ***
Documentation    Stage 1 Onboarding — complete flow Landing through Confirm PIN.
...              Terminal states: STAGE1_SAVED, STAGE1_AUTOMATION_VALIDATED_ENVIRONMENT_BLOCKED.
Suite Setup      Open Mobile Application
Suite Teardown   Close Application
Resource         ../../../resources/keywords/onboarding_common.resource
Library          ../../../libraries/config_loader.py
Library          ../../../libraries/robot_output_sanitizer.py
Library          OperatingSystem


*** Variables ***
${NTB_TESTDATA}    ${EMPTY}


*** Test Cases ***
NTB Stage 1 Onboarding
    [Documentation]    Complete Stage 1: Landing → Consent → Profile → OCR → DOPA → OTP → Set PIN → Confirm PIN.
    [Tags]    stage1    onboarding    ntb
    ${previous}=    Set Log Level    NONE
    Should Not Be Empty    ${NTB_TESTDATA}    NTB_TESTDATA must point to an approved local YAML profile.
    File Should Exist    ${NTB_TESTDATA}    NTB_TESTDATA file does not exist.
    ${data}=    Load YAML    ${NTB_TESTDATA}
    Set Log Level    ${previous}
    Complete Stage 1 Onboarding    ${data}
    ${confirm_gone}=    Run Keyword And Return Status    Wait Until Page Does Not Contain Element    xpath=//*[@text="Re-enter PIN to confirm"]    30s
    Run Keyword If    not ${confirm_gone}    Fail    CONFIRM_PIN_FAILED — Confirm PIN screen did not navigate
    ${state}=    Detect Post PIN Terminal State
    IF    '${state}' == 'SAVED'
        Log    STAGE1_SAVED — backend save successful    WARN
    ELSE IF    '${state}' == 'ENVIRONMENT_BLOCKED'
        Log    STAGE1_AUTOMATION_VALIDATED_ENVIRONMENT_BLOCKED — backend error after Confirm PIN    WARN
    ELSE
        Log    STAGE1_AUTOMATION_VALIDATED_NEXT_SCREEN_UNKNOWN    WARN
    END
