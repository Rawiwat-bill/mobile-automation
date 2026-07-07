*** Settings ***
Documentation    Navigate to camera, sleep for Frida attachment
Library    AppiumLibrary
Library    OperatingSystem
Library    Process
Resource   ../../resources/app/app_keywords.resource
Resource   ../../resources/keywords/onboarding_common.resource
Library    ../../libraries/config_loader.py

*** Variables ***
${TESTDATA}    testdata/onboarding/ntb.local.yaml
${LANDING_TIMEOUT}    120s

*** Test Cases ***
Camera And Sleep
    Open Mobile Application
    ${prev}=    Set Log Level    NONE
    ${data}=    Load YAML    ${TESTDATA}
    Set Log Level    ${prev}
    Log    [FLOW] App launched    WARN

    Complete Common Onboarding
    ...    ${data['profile']['citizen_id']}
    ...    ${data['profile']['date_of_birth']}
    ...    ${data['profile']['mobile_number']}
    Log    [FLOW] *** CAMERA REACHED + TAKE PHOTO DONE ***    WARN

    Sleep    300s
    Log    [FLOW] Sleep done    WARN
    Close Application
