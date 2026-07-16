*** Settings ***
Documentation       RCT (Reactivate) Flow - Happy Case
...                 Reactivate with correct old PIN and accept PDPA clause 6.

Resource            ../../../resources/app/app_keywords.resource
Resource            ../../../resources/keywords/rct/rct_keywords.resource
Library             ../../../libraries/config_loader.py

Suite Setup         Open Mobile Application
# Suite Teardown      Close Application


*** Variables ***
${RCT_TESTDATA}     testdata/rct/rct.local.yaml


*** Test Cases ***
RCT Reactivate Happy Flow
    [Documentation]    Reactivate with correct old PIN and answer PDPA clause 6 = Accept.
    ${previous_log_level}=    Set Log Level    NONE
    ${data}=    Load YAML    ${RCT_TESTDATA}
    Set Log Level    ${previous_log_level}
    Complete RCT Reactivate
    ...    ${data['profile']['citizen_id']}
    ...    ${data['profile']['date_of_birth']}
    ...    ${data['profile']['mobile_number']}
    ...    ${data['profile']['pin']}
    ...    ${data['profile']['laser_code']}
