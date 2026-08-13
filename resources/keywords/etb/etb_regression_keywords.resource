*** Settings ***
Documentation    Shared data-driven ETB RGI regression flow.
Library          ../../../libraries/config_loader.py
Library          String
Library          OperatingSystem
Library          ../../../libraries/cis_preparation.py
Library          ../../../libraries/pdpa_preparation.py
Resource         ../../keywords/common_onboarding/common_onboarding_keyword.resource
Resource         ../../keywords/etb/etb_keywords.resource

*** Variables ***
${ETB_CASE_CONTRACT}    ${CURDIR}/../../../testdata/onboarding/etb_cases.yaml
${ETB_CASE_PROFILES}    ${CURDIR}/../../../testdata/onboarding/etb_cases.local.yaml

*** Keywords ***
Run ETB Positive Case
    [Arguments]    ${case_key}    ${assert_3c}=${False}
    ${profiles}=    config_loader.Load YAML    ${ETB_CASE_PROFILES}
    ${profile_case}=    Set Variable    ${profiles['cases']['${case_key}']}
    ${preparation}=    Prepare CIS State    ${ETB_CASE_PROFILES}    ${case_key}    ${OUTPUT DIR}
    Should Be Equal As Strings    ${preparation['cis_clear']}    PASS    PREPARATION_FAILED_CIS_CLEAR
    Reset ETB Regression Application
    ${dob}=    Replace String    ${profile_case['profile']['date_of_birth']}    /    -
    TRY
        ${business_pass}=    Run Keyword And Return Status    Complete ETB Onboarding
        ...    ${profile_case['profile']['citizen_id']}
        ...    ${dob}
        ...    ${profile_case['profile']['mobile_number']}
        ...    ${profile_case['profile']['laser_code']}
        ...    ${profile_case['profile']['otp']}
        ...    ${profile_case['profile']['pin']}
        Capture Page Screenshot    ${OUTPUT DIR}/${case_key}_result.png
        Should Be True    ${business_pass}
        IF    ${assert_3c}
            Assert TC001 Introduction And Control 3C
        END
    FINALLY
        ${cleanup}=    Cleanup CIS State    ${ETB_CASE_PROFILES}    ${case_key}    ${OUTPUT DIR}
        Should Be Equal As Strings    ${cleanup['cis_clear']}    PASS    POST_CIS_CLEANUP_FAILED
    END

Run ETB TC002 PDPA Case
    ${base_url}=    Get Environment Variable    PDPA_BASE_URL    ${EMPTY}
    Should Not Be Empty    ${base_url}    PDPA_BASE_URL must be supplied by the runtime environment.
    ${profiles}=    config_loader.Load YAML    ${ETB_CASE_PROFILES}
    ${profile}=    Set Variable    ${profiles['cases']['etb_tc_002']['profile']}
    ${dob}=    Replace String    ${profile['date_of_birth']}    /    -
    ${cis_preparation}=    Prepare CIS State    ${ETB_CASE_PROFILES}    etb_tc_002    ${OUTPUT DIR}
    Should Be Equal As Strings    ${cis_preparation['cis_clear']}    PASS    PREPARATION_FAILED_CIS_CLEAR
    ${clear_result}=    Prepare Pdpa State From Profile
    ...    ${ETB_CASE_PROFILES}
    ...    etb_tc_002
    ...    CI
    ...    base_url=${base_url}
    Should Be Equal As Strings    ${clear_result['status']}    CLEAR_REQUEST_SUBMITTED
    Should Be Equal As Integers    ${clear_result['post_count']}    1
    Should Not Be True    ${clear_result['semantic_verifiable']}
    Reset ETB Regression Application
    TRY
        ${business_pass}=    Run Keyword And Return Status    Complete ETB Onboarding
        ...    ${profile['citizen_id']}
        ...    ${dob}
        ...    ${profile['mobile_number']}
        ...    ${profile['laser_code']}
        ...    ${profile['otp']}
        ...    ${profile['pin']}
        Capture Page Screenshot    ${OUTPUT DIR}/etb_tc_002_result.png
        Should Be True    ${business_pass}    TC002 supported onboarding did not complete.
    FINALLY
        ${cis_cleanup}=    Cleanup CIS State    ${ETB_CASE_PROFILES}    etb_tc_002    ${OUTPUT DIR}
        Should Be Equal As Strings    ${cis_cleanup['cis_clear']}    PASS    POST_CIS_CLEANUP_FAILED
        ${pdpa_cleanup_status}=    Run Keyword And Return Status    Prepare Pdpa State From Profile
        ...    ${ETB_CASE_PROFILES}
        ...    etb_tc_002
        ...    CI
        ...    base_url=${base_url}
        Log    CASE_SPECIFIC_PDPA_CLEANUP=${pdpa_cleanup_status}    INFO
    END

Run ETB Expected RGI Case
    [Arguments]    ${case_key}    ${handler_keyword}
    ${contract}=    config_loader.Load YAML    ${ETB_CASE_CONTRACT}
    ${profiles}=    config_loader.Load YAML    ${ETB_CASE_PROFILES}
    ${case}=    Set Variable    ${contract['cases']['${case_key}']}
    ${profile_case}=    Set Variable    ${profiles['cases']['${case_key}']}
    ${preparation}=    Prepare CIS State    ${ETB_CASE_PROFILES}    ${case_key}    ${OUTPUT DIR}
    Should Be Equal As Strings    ${preparation['cis_clear']}    PASS    PREPARATION_FAILED_CIS_CLEAR
    Reset ETB Application To Landing
    ${dob}=    Replace String    ${profile_case['profile']['date_of_birth']}    /    -
    ${flow_status}=    Set Variable    PASS
    ${action_status}=    Set Variable    PASS
    TRY
        ${flow_status}    ${flow_result}=    Run Keyword And Ignore Error    Common Onboarding Flow
        ...    ${profile_case['profile']['citizen_id']}    ${dob}    ${profile_case['profile']['mobile_number']}
        IF    '${flow_status}' == 'PASS'
            Should Be Equal As Strings    ${flow_result}    NEXT
            Capture Page Screenshot    ${OUTPUT DIR}/${case_key}_result_before_action.png
            ${action_status}=    Run Keyword And Return Status    Run Keyword    ${handler_keyword}    ${case['expected_error_code']}
        END
        Should Be Equal As Strings    ${flow_status}    PASS
        Should Be True    ${action_status}
    FINALLY
        Run Keyword And Ignore Error    Capture Page Screenshot    ${OUTPUT DIR}/${case_key}_result_after_action.png
        ${cleanup_status}    ${cleanup}=    Run Keyword And Ignore Error    Cleanup CIS State    ${ETB_CASE_PROFILES}    ${case_key}    ${OUTPUT DIR}
    END
    ${post_cis_status}=    Set Variable    FAILED
    IF    '${cleanup_status}' == 'PASS'
        ${post_cis_status}=    Set Variable    ${cleanup['cis_clear']}
    END
    Log    POST_CIS_CLEAR = ${post_cis_status} transport=${cleanup_status}    WARN

Run ETB Expected RGI After Laser Code
    [Arguments]    ${case_key}    ${handler_keyword}    ${action_policy}=STANDARD_FIND_BRANCH_CLOSE_APP
    ${contract}=    config_loader.Load YAML    ${ETB_CASE_CONTRACT}
    ${profiles}=    config_loader.Load YAML    ${ETB_CASE_PROFILES}
    ${case}=    Set Variable    ${contract['cases']['${case_key}']}
    ${profile_case}=    Set Variable    ${profiles['cases']['${case_key}']}
    ${preparation}=    Prepare CIS State    ${ETB_CASE_PROFILES}    ${case_key}    ${OUTPUT DIR}
    Should Be Equal As Strings    ${preparation['cis_clear']}    PASS    PREPARATION_FAILED_CIS_CLEAR
    Reset ETB Application To Landing
    ${dob}=    Replace String    ${profile_case['profile']['date_of_birth']}    /    -

    ${flow_status}=    Set Variable    PASS
    ${action_status}=    Set Variable    PASS
    TRY
        ${flow_status}    ${flow_result}=    Run Keyword And Ignore Error    Common Onboarding Flow
        ...    ${profile_case['profile']['citizen_id']}    ${dob}    ${profile_case['profile']['mobile_number']}
        IF    '${flow_status}' == 'PASS'
            Should Be Equal As Strings    ${flow_result}    NEXT
            Wait Until Check DOPA Fill Laser Code Is Displayed
            Input Laser Code    ${profile_case['profile']['laser_code']}
            Wait Until Element Is Visible    ${CHECK_DOPA_FILL_LASER_CODE_BUTTON_NEXT}    ${NCBD_LOADING_TIMEOUT}
            Click Element    ${CHECK_DOPA_FILL_LASER_CODE_BUTTON_NEXT}
            Capture Page Screenshot    ${OUTPUT DIR}/${case_key}_result_before_action.png
            ${action_status}=    Run Keyword And Return Status    Run Keyword    ${handler_keyword}    ${case['expected_error_code']}    ${NONE}    ${action_policy}
        END
        Should Be Equal As Strings    ${flow_status}    PASS
        Should Be True    ${action_status}
    FINALLY
        Run Keyword And Ignore Error    Capture Page Screenshot    ${OUTPUT DIR}/${case_key}_result_after_action.png
        ${cleanup_status}    ${cleanup}=    Run Keyword And Ignore Error    Cleanup CIS State    ${ETB_CASE_PROFILES}    ${case_key}    ${OUTPUT DIR}
    END
    ${post_cis_status}=    Set Variable    FAILED
    IF    '${cleanup_status}' == 'PASS'
        ${post_cis_status}=    Set Variable    ${cleanup['cis_clear']}
    END
    Log    POST_CIS_CLEAR = ${post_cis_status} transport=${cleanup_status}    WARN

Reset ETB Application To Landing
    Run Keyword And Ignore Error    Terminate Application    ${APP_PACKAGE}
    Execute Adb Shell    am    force-stop    ${APP_PACKAGE}
    Activate Application    ${APP_PACKAGE}
    Wait Until Landing Screen Is Displayed

Reset ETB Regression Application
    Run Keyword And Ignore Error    Terminate Application    ${APP_PACKAGE}
    Execute Adb Shell    am    force-stop    ${APP_PACKAGE}
    Activate Application    ${APP_PACKAGE}
    Allow Android Permission If Visible
    Wait Until Landing Screen Is Displayed

Normalize ETB Regression Application
    Run Keyword If Test Failed    Capture Page Screenshot    ${OUTPUT DIR}/etb_regression_failure.png
    Run Keyword And Ignore Error    Execute Adb Shell    am    force-stop    ${APP_PACKAGE}
