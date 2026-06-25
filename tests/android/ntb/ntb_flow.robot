*** Settings ***
Documentation    NTB Onboarding Flow
Resource         ../../../resources/app/app_keywords.resource
Resource         ../../../resources/keywords/onboarding_common.resource
Resource         ../../../resources/keywords/ntb_keywords.resource
Library          ../../../libraries/config_loader.py

Suite Setup      Open Mobile Application
Suite Teardown   Close Application

*** Variables ***
${NTB_TESTDATA}    testdata/onboarding/ntb.local.yaml

*** Test Cases ***
NTB Onboarding Flow
    ${previous_log_level}=    Set Log Level    NONE
    ${data}=    Load YAML    ${NTB_TESTDATA}
    Set Log Level    ${previous_log_level}
    Complete Common Onboarding    ${data['profile']['citizen_id']}    ${data['profile']['date_of_birth']}    ${data['profile']['mobile_number']}
