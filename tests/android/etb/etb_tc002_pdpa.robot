*** Settings ***
Documentation    TC02 PDPA preparation and verification-only regression.
Resource         ../../../resources/app/app_keywords.resource
Resource         ../../../resources/keywords/etb/etb_keywords.resource
Resource         ../../../resources/keywords/common_onboarding/common_onboarding_keyword.resource
Library          ../../../libraries/config_loader.py
Library          ../../../libraries/pdpa_preparation.py
Library          ../../../libraries/cis_preparation.py
Library          OperatingSystem
Library          ../../../libraries/robot_output_sanitizer.py

Suite Setup      Open Mobile Application
Suite Teardown   Normalize TC02 Application State

*** Variables ***
${ETB_CASE_PROFILES}    ${CURDIR}/../../../testdata/onboarding/etb_cases.local.yaml

*** Test Cases ***
TC-ETB-002 PDPA Preparation And Verification
    ${base_url}=    Get Environment Variable    PDPA_BASE_URL    ${EMPTY}
    Should Not Be Empty    ${base_url}    PDPA_BASE_URL must be supplied by the runtime environment.
    ${profiles}=    config_loader.Load YAML    ${ETB_CASE_PROFILES}
    ${profile}=    Set Variable    ${profiles['cases']['etb_tc_002']['profile']}
    ${dob}=    Replace String    ${profile['date_of_birth']}    /    -

    # Required preparation order: CIS Clear, then PDPA Clear, then mobile execution.
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

    Reset TC02 Application To Landing
    TRY
        ${old_log_level}=    Set Log Level    NONE
        ${business_pass}=    Run Keyword And Return Status    Complete ETB Onboarding
        ...    ${profile['citizen_id']}
        ...    ${dob}
        ...    ${profile['mobile_number']}
        ...    ${profile['laser_code']}
        ...    ${profile['otp']}
        ...    ${profile['pin']}
        Set Log Level    ${old_log_level}
        Capture Page Screenshot    ${OUTPUT DIR}/etb_tc_002_result.png
        Should Be True    ${business_pass}    TC02 supported onboarding did not complete.
    FINALLY
        # Result/evidence is captured before mandatory post-test CIS cleanup.
        ${cis_cleanup}=    Cleanup CIS State    ${ETB_CASE_PROFILES}    etb_tc_002    ${OUTPUT DIR}
        Log    POST_TEST_CIS_CLEANUP=${cis_cleanup['cis_clear']}    INFO

        # Existing approved PDPA mechanism; cleanup is explicitly best effort.
        ${pdpa_cleanup_status}=    Run Keyword And Return Status    Prepare Pdpa State From Profile
        ...    ${ETB_CASE_PROFILES}
        ...    etb_tc_002
        ...    CI
        ...    base_url=${base_url}
        Log    CASE_SPECIFIC_PDPA_CLEANUP=${pdpa_cleanup_status}    INFO
    END

*** Keywords ***
Reset TC02 Application To Landing
    Run Keyword And Ignore Error    Terminate Application    ${APP_PACKAGE}
    Execute Adb Shell    am    force-stop    ${APP_PACKAGE}
    Activate Application    ${APP_PACKAGE}
    Wait Until Landing Screen Is Displayed

Normalize TC02 Application State
    Run Keyword And Ignore Error    Execute Adb Shell    am    force-stop    ${APP_PACKAGE}
