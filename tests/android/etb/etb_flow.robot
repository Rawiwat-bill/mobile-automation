*** Settings ***
Documentation       ETB Onboarding Flow (placeholder)

Resource            ../../../resources/app/app_keywords.resource
Resource            ../../../resources/keywords/etb/etb_keywords.resource
Library             ../../../libraries/config_loader.py
Library             ../../../libraries/etb_teardown.py

Suite Setup         Open Mobile Application
Suite Teardown      Close Application


*** Variables ***
${ETB_TESTDATA}     testdata/onboarding/etb.local.yaml


*** Test Cases ***
ETB Onboarding Flow
    [Documentation]    Complete the onboarding flow for ETB using test data from ${ETB_TESTDATA}
    ${previous_log_level}=    Set Log Level    NONE
    ${data}=    Load YAML    ${ETB_TESTDATA}
    Set Log Level    ${previous_log_level}
    ${business_pass}=    Complete ETB Onboarding
    ...    ${data['profile']['citizen_id']}
    ...    ${data['profile']['date_of_birth']}
    ...    ${data['profile']['mobile_number']}
    ...    ${data['profile']['laser_code']}
    ...    ${data['profile']['otp']}
    ...    ${data['profile']['pin']}
    IF    ${business_pass}
        ${teardown}=    Delete ETB Profile After Success    ${ETB_TESTDATA}    ${OUTPUT DIR}
        ${teardown_status}=    Set Variable    ${teardown['etb_teardown']}
        ${teardown_classification}=    Set Variable    ${teardown['cleanup_classification']}
        ${first_http_status}=    Set Variable    ${teardown['first_response']['http_status']}
        ${second_http_status}=    Set Variable    ${teardown['second_response']['http_status']}
        IF    '${teardown_status}' == 'PASS'
            Log    [ETB_TEARDOWN] PASS first_status=${first_http_status} second_status=${second_http_status} classification=${teardown_classification}    INFO
            Mark Health Checkpoint    ETB_TEARDOWN_PASS
        ELSE
            Log    [ETB_TEARDOWN] FAIL first_status=${first_http_status} second_status=${second_http_status} classification=${teardown_classification}; profile may not be reusable    WARN
            Mark Health Checkpoint    ETB_TEARDOWN_FAIL
        END
    END
