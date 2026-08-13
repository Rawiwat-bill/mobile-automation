*** Settings ***
Documentation       ETB Onboarding Flow (placeholder)

Resource            ../../../resources/app/app_keywords.resource
Resource            ../../../resources/keywords/etb/etb_keywords.resource
Library             ../../../libraries/config_loader.py
Library             ../../../libraries/cis_preparation.py
Library             ../../../libraries/robot_output_sanitizer.py

Suite Setup         Open Mobile Application
Suite Teardown      Close Application


*** Variables ***
${ETB_PROFILE}      etb
${ETB_TESTDATA}     ${EMPTY}


*** Test Cases ***
ETB Onboarding Flow
    [Documentation]    Complete the onboarding flow for ETB using the selected profile or an explicit test-data path
    ${previous_log_level}=    Set Log Level    NONE
    IF    '${ETB_TESTDATA}' != ''
        ${data}=    config_loader.Load YAML    ${ETB_TESTDATA}
        ${teardown_source}=    Set Variable    ${ETB_TESTDATA}
    ELSE
        ${data}=    Load Profile    ${ETB_PROFILE}
        ${teardown_source}=    Set Variable    ${ETB_PROFILE}
    END
    Set Log Level    ${previous_log_level}
    ${normalized_dob}=    Replace String    ${data['profile']['date_of_birth']}    /    -
    ${preparation}=    Prepare CIS State    ${teardown_source}    ${EMPTY}    ${OUTPUT DIR}
    Should Be Equal As Strings    ${preparation['cis_clear']}    PASS    PREPARATION_FAILED_CIS_CLEAR
    TRY
        ${business_pass}=    Run Keyword And Return Status    Complete ETB Onboarding
        ...    ${data['profile']['citizen_id']}
        ...    ${normalized_dob}
        ...    ${data['profile']['mobile_number']}
        ...    ${data['profile']['laser_code']}
        ...    ${data['profile']['otp']}
        ...    ${data['profile']['pin']}
        Capture Page Screenshot    ${OUTPUT DIR}/etb_result.png
        Should Be True    ${business_pass}
    FINALLY
        ${cleanup}=    Cleanup CIS State    ${teardown_source}    ${EMPTY}    ${OUTPUT DIR}
        Log    POST_TEST_CIS_CLEANUP=${cleanup['cis_clear']}    WARN
    END
