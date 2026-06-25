*** Settings ***
Documentation    Common Onboarding Flow (shared by NTB and ETB)
Resource         ../../../resources/app/app_keywords.resource
Resource         ../../../resources/keywords/onboarding_common.resource
Library          ../../../libraries/config_loader.py

Suite Setup      Open Mobile Application
Suite Teardown   Close Application

*** Variables ***
${TESTDATA}    testdata/onboarding/ntb.example.yaml

*** Test Cases ***
Common Onboarding Flow
    ${previous_log_level}=    Set Log Level    NONE
    ${data}=    Load YAML    ${TESTDATA}
    Set Log Level    ${previous_log_level}
    Complete Common Onboarding    ${data['profile']['citizen_id']}    ${data['profile']['date_of_birth']}    ${data['profile']['mobile_number']}
