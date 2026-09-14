*** Settings ***
Documentation    NTB Onboarding Flow
Resource         ../../../resources/app/app_keywords.resource
Resource         ../../../resources/keywords/onboarding_common.resource
Resource         ../../../resources/keywords/ntb_keywords.resource
Library          ../../../libraries/config_loader.py
Library          ../../../libraries/robot_output_sanitizer.py
Library          OperatingSystem

Suite Setup      Open Mobile Application
Suite Teardown   Close Application

*** Variables ***
${NTB_TESTDATA}    ${EMPTY}

*** Test Cases ***
NTB Onboarding Flow
    ${previous_log_level}=    Set Log Level    NONE
    Should Not Be Empty    ${NTB_TESTDATA}    NTB_TESTDATA must point to an approved local YAML profile.
    File Should Exist    ${NTB_TESTDATA}    NTB_TESTDATA file does not exist.
    ${data}=    Load YAML    ${NTB_TESTDATA}
    Set Log Level    ${previous_log_level}
    ${common_result}=    Complete Common Onboarding    ${data['profile']['citizen_id']}    ${data['profile']['date_of_birth']}    ${data['profile']['mobile_number']}
    Should Be Equal As Strings    ${common_result}    COMMON_ONBOARDING_COMPLETED
    ...    COMMON_ONBOARDING_BLOCKED=${common_result}
