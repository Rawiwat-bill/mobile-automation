*** Settings ***
Documentation    Shared data-driven ETB RGI regression flow.
Library         ../../../libraries/config_loader.py
Library         ../../../libraries/adb_device.py
Resource        ../../diagnostics/etb_observability.resource
Library          String
Library          OperatingSystem
Library          Collections
Library          ../../../libraries/cis_preparation.py
Library          ../../../libraries/pdpa_preparation.py
Resource         ../../contracts/flow_states.resource
Resource         ../../keywords/common_onboarding/common_onboarding_keyword.resource
Resource         ../../keywords/etb/etb_keywords.resource

Resource         ../appium_expectations.resource

*** Variables ***
${ETB_CASE_CONTRACT}    ${CURDIR}/../../../testdata/onboarding/etb_cases.yaml
${ETB_CASE_PROFILES}    ${CURDIR}/../../../testdata/onboarding/etb_cases.local.yaml
${ETB_ISOLATED_VALIDATION}    ${EMPTY}
${LANDING_ACTION_RECT}    ${EMPTY}

*** Keywords ***
Assert CIS Preparation Ready
    [Arguments]    ${preparation}
    ${mode}=    Get Environment Variable    CIS_MODE    ${EMPTY}
    ${environment}=    Get Environment Variable    ETB_ENVIRONMENT    DEV
    IF    '${environment}' == 'DEV_MOCK'
        Should Be Equal As Strings    ${preparation['cis_clear']}    NOT_APPLICABLE    Mock build CIS must be NOT_APPLICABLE.
        Should Be Equal As Strings    ${preparation['cis_state_ready']}    NOT_REQUIRED    Mock build CIS must be NOT_REQUIRED.
    ELSE IF    '${mode}' == 'EXTERNAL_PREPARED'
        Should Be Equal As Strings    ${preparation['cis_readiness_status']}    EXTERNALLY_CONFIRMED    CIS readiness must be externally confirmed before runtime.
    ELSE
        Should Be Equal As Strings    ${preparation['cis_clear']}    PASS    PREPARATION_FAILED_CIS_CLEAR
    END

Assert CIS Cleanup Policy
    [Arguments]    ${cleanup}
    ${mode}=    Get Environment Variable    CIS_MODE    ${EMPTY}
    ${environment}=    Get Environment Variable    ETB_ENVIRONMENT    DEV
    IF    '${environment}' == 'DEV_MOCK'
        Should Be Equal As Strings    ${cleanup['cis_clear']}    NOT_APPLICABLE    Mock build CIS cleanup must be NOT_APPLICABLE.
        Should Be Equal As Strings    ${cleanup['cis_state_ready']}    NOT_REQUIRED    Mock build CIS cleanup must be NOT_REQUIRED.
    ELSE IF    '${mode}' == 'EXTERNAL_PREPARED'
        Should Be Equal As Strings    ${cleanup['post_cis_cleanup_owner']}    EXTERNAL_TEAM
    ELSE
        Should Be Equal As Strings    ${cleanup['cis_clear']}    PASS    POST_CIS_CLEANUP_FAILED
    END

Prepare ETB Regression Suite
    ${release}=    Get Variable Value    ${ETB_PRODUCT_RELEASE}    POST_MMP_1
    Should Be True    '${release}' in ['MMP_LOT2_V2', 'POST_MMP_1']    ETB_PRODUCT_RELEASE_INVALID
    Log    ETB suite initialized release=${release}; Robot test setup owns application startup.

Run ETB Positive Case
    [Arguments]    ${case_key}    ${assert_3c}=${False}
    ${contract}=    config_loader.Load YAML    ${ETB_CASE_CONTRACT}
    ${case}=    Set Variable    ${contract['cases']['${case_key}']}
    ${profiles}=    config_loader.Load YAML    ${ETB_CASE_PROFILES}
    ${profile_case}=    Set Variable    ${profiles['cases']['${case_key}']}
    ${dob}=    Replace String    ${profile_case['profile']['date_of_birth']}    /    -
    ${has_confirm_policy}=    Run Keyword And Return Status    Dictionary Should Contain Key    ${case}    confirm_pin_policy
    ${confirm_pin_policy}=    Set Variable If    ${has_confirm_policy}    ${case['confirm_pin_policy']}    REQUIRED
    TRY
        ${preparation}=    Prepare CIS State    ${ETB_CASE_PROFILES}    ${case_key}    ${OUTPUT DIR}
        Assert CIS Preparation Ready    ${preparation}
        ${business_status}    ${business_error}=    Run Keyword And Ignore Error    Complete ETB Onboarding
        ...    ${profile_case['profile']['citizen_id']}
        ...    ${dob}
        ...    ${profile_case['profile']['mobile_number']}
        ...    ${profile_case['profile']['laser_code']}
        ...    ${profile_case['profile']['otp']}
        ...    ${profile_case['profile']['pin']}
        ...    ${case['product_selection_policy']}
        ...    ${case['pdpa_policy']}
        ...    ${case['expected_product_categories']}
        ...    confirm_pin_policy=${confirm_pin_policy}
        Record ETB Evidence Capture    ${OUTPUT DIR}    ${case_key}_result
        Should Be Equal As Strings    ${business_status}    PASS    ${business_error}
        ${execution_mode}=    Get Environment Variable    ETB_EXECUTION_MODE    REGRESSION
        IF    ${assert_3c} and '${execution_mode}' != 'DISCOVERY'
            Assert TC001 Introduction And Control 3C
        END
    FINALLY
        ${cleanup}=    Cleanup CIS State    ${ETB_CASE_PROFILES}    ${case_key}    ${OUTPUT DIR}
        Assert CIS Cleanup Policy    ${cleanup}
    END

Run ETB TC002 PDPA Case
    ${base_url}=    Get Environment Variable    PDPA_BASE_URL    ${EMPTY}
    Should Not Be Empty    ${base_url}    PDPA_BASE_URL must be supplied by the runtime environment.
    ${profiles}=    config_loader.Load YAML    ${ETB_CASE_PROFILES}
    ${contract}=    config_loader.Load YAML    ${ETB_CASE_CONTRACT}
    ${case}=    Set Variable    ${contract['cases']['etb_tc_002']}
    ${profile}=    Set Variable    ${profiles['cases']['etb_tc_002']['profile']}
    ${dob}=    Replace String    ${profile['date_of_birth']}    /    -
    ${has_confirm_policy}=    Run Keyword And Return Status    Dictionary Should Contain Key    ${case}    confirm_pin_policy
    ${confirm_pin_policy}=    Set Variable If    ${has_confirm_policy}    ${case['confirm_pin_policy']}    REQUIRED
    TRY
        ${cis_preparation}=    Prepare CIS State    ${ETB_CASE_PROFILES}    etb_tc_002    ${OUTPUT DIR}
        Assert CIS Preparation Ready    ${cis_preparation}
        ${clear_result}=    Prepare Pdpa State From Profile
        ...    ${ETB_CASE_PROFILES}
        ...    etb_tc_002
        ...    CI
        ...    base_url=${base_url}
        Should Be Equal As Strings    ${clear_result['status']}    CLEAR_REQUEST_SUBMITTED
        Should Be Equal As Integers    ${clear_result['post_count']}    1
        Should Not Be True    ${clear_result['semantic_verifiable']}
        ${business_status}    ${business_error}=    Run Keyword And Ignore Error    Complete ETB Onboarding
        ...    ${profile['citizen_id']}
        ...    ${dob}
        ...    ${profile['mobile_number']}
        ...    ${profile['laser_code']}
        ...    ${profile['otp']}
        ...    ${profile['pin']}
        ...    ${case['product_selection_policy']}
        ...    ${case['pdpa_policy']}
        ...    ${case['expected_product_categories']}
        ...    confirm_pin_policy=${confirm_pin_policy}
        Record ETB Evidence Capture    ${OUTPUT DIR}    etb_tc_002_result
        Should Be Equal As Strings    ${business_status}    PASS    ${business_error}
        Assert TC001 Introduction And Control 3C
    FINALLY
        ${cis_cleanup_status}    ${cis_cleanup}=    Run Keyword And Ignore Error    Cleanup CIS State    ${ETB_CASE_PROFILES}    etb_tc_002    ${OUTPUT DIR}
        ${pdpa_cleanup_status}    ${pdpa_cleanup}=    Run Keyword And Ignore Error    Prepare Pdpa State From Profile
        ...    ${ETB_CASE_PROFILES}
        ...    etb_tc_002
        ...    CI
        ...    base_url=${base_url}
        IF    '${cis_cleanup_status}' == 'PASS'
            Assert CIS Cleanup Policy    ${cis_cleanup}
        END
        IF    '${cis_cleanup_status}' != 'PASS'
            Fail    TC002_CLEANUP_FAILED CIS=${cis_cleanup_status}
        END
        IF    '${pdpa_cleanup_status}' == 'PASS'
            Log    CASE_SPECIFIC_PDPA_CLEANUP=ATTEMPTED status=${pdpa_cleanup['status']} semantic_verifiable=${pdpa_cleanup['semantic_verifiable']}    INFO
        ELSE
            Log    CASE_SPECIFIC_PDPA_CLEANUP=BEST_EFFORT_WARNING status=${pdpa_cleanup_status} detail=${pdpa_cleanup}    WARN
        END
    END

Run ETB Expected RGI Case
    [Arguments]    ${case_key}    ${handler_keyword}
    ${contract}=    config_loader.Load YAML    ${ETB_CASE_CONTRACT}
    ${profiles}=    config_loader.Load YAML    ${ETB_CASE_PROFILES}
    ${case}=    Set Variable    ${contract['cases']['${case_key}']}
    ${profile_case}=    Set Variable    ${profiles['cases']['${case_key}']}
    ${dob}=    Replace String    ${profile_case['profile']['date_of_birth']}    /    -
    ${flow_status}=    Set Variable    PASS
    ${action_status}=    Set Variable    PASS
    TRY
        ${preparation}=    Prepare CIS State    ${ETB_CASE_PROFILES}    ${case_key}    ${OUTPUT DIR}
        Assert CIS Preparation Ready    ${preparation}
        ${flow_status}    ${flow_result}=    Run Keyword And Ignore Error    Common Onboarding Flow
        ...    ${profile_case['profile']['citizen_id']}    ${dob}    ${profile_case['profile']['mobile_number']}
        IF    '${flow_status}' == 'PASS'
            ${expected_at_profile}=    Run Keyword And Return Status
            ...    Should Be Equal As Strings    ${flow_result}    ${case['expected_error_code']}
            ${normal_destination}=    Run Keyword And Return Status
            ...    Should Be Equal As Strings    ${flow_result}    ${FLOW_STATE_NEXT}
            Should Be True    ${expected_at_profile} or ${normal_destination}
            ...    EXPECTED_RGI_STAGE_MISMATCH expected=${case['expected_error_code']} observed=${flow_result}
            Record ETB Evidence Capture    ${OUTPUT DIR}    ${case_key}_result_before_action
            ${action_status}    ${action_error}=    Run Keyword And Ignore Error    Run Keyword    ${handler_keyword}    ${case['expected_error_code']}
        ELSE
            Fail    ${flow_result}
        END
        Should Be Equal As Strings    ${action_status}    PASS    ${action_error}
    FINALLY
        Record ETB Device Terminal Evidence    ${OUTPUT DIR}    ${case_key}_terminal    ${DEVICE_UDID}
        ${cleanup_status}    ${cleanup}=    Run Keyword And Ignore Error    Cleanup CIS State    ${ETB_CASE_PROFILES}    ${case_key}    ${OUTPUT DIR}
        IF    '${cleanup_status}' != 'PASS'
            Fail    POST_CIS_CLEANUP_AUTOMATION_FAILED=${case_key}
        END
    END
    Assert CIS Cleanup Policy    ${cleanup}
    Log    POST_CIS_CLEAR=${cleanup['cis_clear']} transport=${cleanup_status}    INFO

Run ETB Expected RGI After Laser Code
    [Arguments]    ${case_key}    ${handler_keyword}    ${action_policy}=STANDARD_FIND_BRANCH_CLOSE_APP
    ${contract}=    config_loader.Load YAML    ${ETB_CASE_CONTRACT}
    ${profiles}=    config_loader.Load YAML    ${ETB_CASE_PROFILES}
    ${case}=    Set Variable    ${contract['cases']['${case_key}']}
    ${profile_case}=    Set Variable    ${profiles['cases']['${case_key}']}
    ${dob}=    Replace String    ${profile_case['profile']['date_of_birth']}    /    -

    ${flow_status}=    Set Variable    PASS
    ${action_status}=    Set Variable    PASS
    TRY
        ${preparation}=    Prepare CIS State    ${ETB_CASE_PROFILES}    ${case_key}    ${OUTPUT DIR}
        Assert CIS Preparation Ready    ${preparation}
        ${flow_status}    ${flow_result}=    Run Keyword And Ignore Error    Common Onboarding Flow
        ...    ${profile_case['profile']['citizen_id']}    ${dob}    ${profile_case['profile']['mobile_number']}
        IF    '${flow_status}' == 'PASS'
            # This case expects its error AFTER Laser Code Next, never at Profile.
            Should Be Equal As Strings    ${flow_result}    ${FLOW_STATE_NEXT}
            ...    EXPECTED_RGI_AFTER_LASER_PROFILE_STAGE_MISMATCH
            Wait Until Check DOPA Fill Laser Code Is Displayed
            Input Laser Code    ${profile_case['profile']['laser_code']}
            Wait Until Element Is Visible    ${CHECK_DOPA_FILL_LASER_CODE_BUTTON_NEXT}    ${NCBD_LOADING_TIMEOUT}
            Click Element    ${CHECK_DOPA_FILL_LASER_CODE_BUTTON_NEXT}
            Record ETB Evidence Capture    ${OUTPUT DIR}    ${case_key}_result_before_action
            ${action_status}    ${action_error}=    Run Keyword And Ignore Error    Run Keyword    ${handler_keyword}    ${case['expected_error_code']}    ${NONE}    ${action_policy}
        ELSE
            Fail    ${flow_result}
        END
        Should Be Equal As Strings    ${action_status}    PASS    ${action_error}
    FINALLY
        Record ETB Device Terminal Evidence    ${OUTPUT DIR}    ${case_key}_terminal    ${DEVICE_UDID}
        ${cleanup_status}    ${cleanup}=    Run Keyword And Ignore Error    Cleanup CIS State    ${ETB_CASE_PROFILES}    ${case_key}    ${OUTPUT DIR}
        IF    '${cleanup_status}' != 'PASS'
            Fail    POST_CIS_CLEANUP_AUTOMATION_FAILED=${case_key}
        END
    END
    Assert CIS Cleanup Policy    ${cleanup}
    Log    POST_CIS_CLEAR=${cleanup['cis_clear']} transport=${cleanup_status}    INFO

Reset ETB Application To Landing
    Run Keyword And Ignore Error    Terminate Application    ${APP_PACKAGE}
    Execute Adb Shell    am    force-stop    ${APP_PACKAGE}
    Activate Application    ${APP_PACKAGE}
    ${startup_state}=    Wait For Real Device Startup State
    Should Be Equal As Strings    ${startup_state}    LANDING    Application startup did not reach LANDING.

Reset ETB Regression Application
    Set Suite Variable    ${LANDING_ACTION_RECT}    ${EMPTY}
    ${reset_result}=    Reset Android Application Before Session    ${DEVICE_UDID}    ${APP_PACKAGE}
    Log    ${reset_result}
    ${execution_target}=    Get Environment Variable    ANDROID_EXECUTION_TARGET    DIAGNOSTIC_CONTROL
    IF    '${execution_target}' == 'REAL'
        Open Mobile Application
        Log    APPIUM_SESSION_BEFORE_APP_START=PASS UIAUTOMATOR2_READY_BEFORE_APP_START=PASS    INFO
        ${startup}=    Start And Observe Real Device    ${DEVICE_UDID}    ${APP_PACKAGE}    ${APP_ACTIVITY}    ${OUTPUT DIR}
        Log    ADB_APP_START=${startup['launch_result']}    INFO
        Log    ADB_STARTUP_TERMINAL_STATE=${startup['terminal_state']}    INFO
        Log    APP_PID_AFTER_APP_START=${startup['app_pid_before_attach']}    INFO
        ${attach}=    Verify Real Device Attach    ${DEVICE_UDID}    ${APP_PACKAGE}    ${APP_ACTIVITY}    ${startup['app_pid_before_attach']}
        Log    ${attach}    INFO
    ELSE
        Open Mobile Application
        ${startup_state}=    Wait For Real Device Startup State
        Should Be Equal As Strings    ${startup_state}    LANDING    Authoritative Robot startup did not reach LANDING.
        ${skip}=    Run Keyword And Return Status    Element Should Be Visible Now    ${LANDING_SKIP_BUTTON}
        IF    ${skip}
            ${landing_rect}=    Get Element Rect    ${LANDING_SKIP_BUTTON}
        ELSE
            ${landing_rect}=    Get Element Rect    ${LANDING_READY_BUTTON}
        END
        Set Suite Variable    ${LANDING_ACTION_RECT}    ${landing_rect}
    END

Verify Real Device Attach
    [Arguments]    ${serial}    ${package}    ${activity}    ${pid_before}
    ${pid_after}=    Get App Pid    ${serial}    ${package}
    Should Be Equal As Strings    ${pid_before}    ${pid_after}    REAL_DEVICE_ATTACH_RELAUNCHED_APPLICATION
    ${component}=    Get Foreground Component    ${serial}
    Should Be Equal As Strings    ${component}    ${package}/${activity}    REAL_DEVICE_ATTACH_CURRENT_ACTIVITY_MISMATCH
    ${skip}=    Run Keyword And Return Status    Element Should Be Visible Now    ${LANDING_SKIP_BUTTON}
    ${ready}=    Run Keyword And Return Status    Element Should Be Visible Now    xpath=//*[@resource-id="screenLanding_buttonReady"]
    ${language}=    Run Keyword And Return Status    Element Should Be Visible Now    xpath=//*[@resource-id="screenLanding_languageSwitch"]
    Should Be True    ${skip} or ${ready} or ${language}    REAL_DEVICE_APPIUM_ATTACH_LANDING_NOT_ACCESSIBLE
    IF    ${skip}
        ${landing_rect}=    Get Element Rect    ${LANDING_SKIP_BUTTON}
        Set Suite Variable    ${LANDING_ACTION_RECT}    ${landing_rect}
    ELSE IF    ${ready}
        ${landing_rect}=    Get Element Rect    xpath=//*[@resource-id="screenLanding_buttonReady"]
        Set Suite Variable    ${LANDING_ACTION_RECT}    ${landing_rect}
    END
    RETURN    APP_PID_AFTER_ATTACH=${pid_after} CURRENT_PACKAGE=PASS CURRENT_ACTIVITY=PASS LANDING_SEMANTIC_LOOKUP=PASS NO_SECOND_APP_LAUNCH=YES SESSION_DELETE_OR_HANDOFF_SAFE=YES

Normalize ETB Regression Application
    Run Keyword If Test Failed    Record ETB Evidence Capture    ${OUTPUT DIR}    etb_regression_failure
    ${stop_result}=    Force Stop Android Application    ${DEVICE_UDID}    ${APP_PACKAGE}
    Log    ${stop_result}
    ${close_status}=    Run Keyword And Return Status    Close Application
    Should Be True    ${close_status}    SESSION_CLOSE_FAILED

Safe Close ETB Application
    ${close_status}=    Run Keyword And Return Status    Close Application
    Should Be True    ${close_status}    SESSION_CLOSE_FAILED
