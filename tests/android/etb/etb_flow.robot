*** Settings ***
Documentation    ETB Onboarding Flow (placeholder)
Resource         ../../../resources/app/app_keywords.resource
Resource         ../../../resources/keywords/onboarding_common.resource
Resource         ../../../resources/keywords/etb_keywords.resource
Library          ../../../libraries/config_loader.py

Suite Setup      Open Mobile Application
Suite Teardown   Close Application

*** Variables ***
${ETB_TESTDATA}    testdata/onboarding/etb.example.yaml

*** Test Cases ***
ETB Onboarding Flow
    ${previous_log_level}=    Set Log Level    NONE
    ${data}=    Load YAML    ${ETB_TESTDATA}
    Set Log Level    ${previous_log_level}
    Complete Common Onboarding    ${data['profile']['citizen_id']}    ${data['profile']['date_of_birth']}    ${data['profile']['mobile_number']}
