*** Settings ***
Documentation       ETB onboarding flow keywords.

Resource            ../../contracts/flow_states.resource
Resource            ../../diagnostics/etb_observability.resource
Resource            ../../../resources/app/app_keywords.resource
Resource            ../../keywords/common_onboarding/common_onboarding_keyword.resource
Resource            ../../pages/etb/check_dopa_fill_laser_code_page.resource
Resource            ../../pages/etb/mobile_otp_page.resource
Resource            ../../pages/etb/setup_pin_page.resource
Resource            ../../pages/etb/rgi_popup_page.resource
Resource            ../../pages/etb/full_screen_rgi_page.resource
Resource            ../../pages/etb/product_selection_page.resource
Resource            ../../pages/etb/post_pin_page.resource
Resource         ../../pages/etb/three_c_page.resource



*** Keywords ***
Complete ETB Onboarding
    [Documentation]    Complete the onboarding flow for ETB.
    [Arguments]    ${citizen_id}    ${date_of_birth}    ${mobile_number}    ${laser_code}    ${otp}    ${pin}    ${product_selection_policy}=REQUIRED    ${pdpa_policy}=UNRESOLVED    ${expected_product_categories}=${NONE}    ${confirm_pin_policy}=REQUIRED

    Should Be True    '${confirm_pin_policy}' in ['REQUIRED', 'OPTIONAL']    CONFIRM_PIN_POLICY_INVALID=${confirm_pin_policy}

    ${common_result}=    Common Onboarding Flow    ${citizen_id}    ${date_of_birth}    ${mobile_number}
    IF    '${common_result}' == '${FLOW_STATE_GOD_013}'
        Fail    BLOCKED_BY_ENVIRONMENT_BACKEND_GOD_013: service unavailable before DOPA.
    END
    IF    '${common_result}' == '${FLOW_STATE_AJI_001}'
        Record ETB Readiness Blocker    ${OUTPUT DIR}    ${FLOW_STATE_AJI_001}    ${FALSE}
        Fail    BLOCKED_BY_ENVIRONMENT_BACKEND_AJI_001: service unavailable before DOPA.
    END
    IF    '${common_result}' == 'RAI-033'
        Fail    PROFILE_RESPONSE_UNEXPECTED_RAI_033: observed after Profile Next; root cause unproven; DOPA not reached.
    END
    Should Be Equal As Strings    ${common_result}    ${FLOW_STATE_NEXT}    ETB_COMMON_ONBOARDING_DID_NOT_REACH_DOPA

    Wait Until Check DOPA Fill Laser Code Is Displayed
    Input Laser Code    ${laser_code}
    Log    LASER_INPUT = COMPLETED
    Tap Check DOPA Next

    Wait Until Mobile OTP Screen Is Displayed
    Input OTP    ${otp}
    Log    OTP_INPUT = COMPLETED

    ${screen}=    Handle Post OTP Transition
    IF    '${pdpa_policy}' != 'REQUIRED' and '${pdpa_policy}' != 'MUST_SKIP' and '${pdpa_policy}' != 'UNRESOLVED'
        Fail    PDPA_POLICY_INVALID=${pdpa_policy}
    END
    IF    '${pdpa_policy}' == 'REQUIRED' and '${screen}' != '${FLOW_STATE_CHECK_PDPA_CLAUSE_NO_6}'
        Fail    PDPA_REQUIRED_BUT_SKIPPED
    END
    IF    '${pdpa_policy}' == 'MUST_SKIP' and '${screen}' == '${FLOW_STATE_CHECK_PDPA_CLAUSE_NO_6}'
        Fail    PDPA_MUST_SKIP_BUT_DISPLAYED
    END
    IF    '${screen}' == '${FLOW_STATE_CHECK_PDPA_CLAUSE_NO_6}'
        Wait Until Check PDPA Clause No6 Is Displayed
        Scroll Down PDPA Clause No6
        Accept PDPA Clause No6
    END

    Continue From Intro Face Scan
    Allow Android Permission If Visible

    Wait Until Setup Pin Screen Is Displayed
    Set Up PIN    ${pin}
    ${product_selection_completed}=    Set Variable    ${FALSE}
    ${confirm_pin_completed}=    Set Variable    ${FALSE}
    ${post_pin_state}=    Wait Until Keyword Succeeds    10s    500ms
    ...    Probe Stable Post First PIN State
    IF    '${post_pin_state}' == '${FLOW_STATE_GOD_005}'
        Record ETB Readiness Blocker    ${OUTPUT DIR}    ${FLOW_STATE_GOD_005}    ${TRUE}
        Fail    BLOCKED_BY_ENVIRONMENT_BACKEND_GOD_005: service unavailable after PIN.
    ELSE IF    '${post_pin_state}' == '${FLOW_STATE_CONFIRM_PIN}'
        Set Up PIN    ${pin}    re_pin=${True}
        ${confirm_pin_completed}=    Set Variable    ${TRUE}
    ELSE IF    '${post_pin_state}' == '${FLOW_STATE_PRODUCT_SELECTION}'
        IF    '${confirm_pin_policy}' == 'REQUIRED'
            Fail    CONFIRM_PIN_REQUIRED_BUT_SKIPPED
        END
        IF    '${product_selection_policy}' == 'REQUIRED'
            Complete Product Selection    ${expected_product_categories}
            ${product_selection_completed}=    Set Variable    ${TRUE}
        ELSE
            Fail    PRODUCT_SELECTION_CONTRACT_VIOLATION
        END
    ELSE IF    '${post_pin_state}' == '${FLOW_STATE_COMPLETION_SUCCESS}'
        IF    '${confirm_pin_policy}' == 'REQUIRED'
            Fail    CONFIRM_PIN_REQUIRED_BUT_SKIPPED
        END
        IF    '${product_selection_policy}' == 'REQUIRED'
            Fail    PRODUCT_SELECTION_REQUIRED_BUT_SKIPPED
        END
    ELSE IF    '${post_pin_state}' == '${FLOW_STATE_EXACT_ERROR}'
        Fail    TC004_POST_FIRST_PIN_EXACT_ERROR
    ELSE
        Fail    PIN_UNEXPECTED_NAVIGATION
    END
    IF    '${confirm_pin_policy}' == 'REQUIRED' and not ${confirm_pin_completed}
        Fail    CONFIRM_PIN_COMPLETION_UNPROVEN
    END
    Log    PIN_INPUT = COMPLETED

    ${destination}=    Wait Until Keyword Succeeds    ${NCBD_LOADING_TIMEOUT}    500ms
    ...    ETB Post PIN Destination Should Be Displayed
    IF    '${destination}' == '${FLOW_STATE_GOD_005}'
        Record ETB Readiness Blocker    ${OUTPUT DIR}    ${FLOW_STATE_GOD_005}    ${TRUE}
        Fail    BLOCKED_BY_ENVIRONMENT_BACKEND_GOD_005: service unavailable after PIN.
    ELSE IF    '${destination}' == '${FLOW_STATE_ENVIRONMENT_BACKEND_AJI_001}'
        Record ETB Readiness Blocker    ${OUTPUT DIR}    ${FLOW_STATE_ENVIRONMENT_BACKEND_AJI_001}    ${TRUE}
        Fail    BLOCKED_BY_ENVIRONMENT_BACKEND_AJI_001: service unavailable after PIN.
    END
    IF    '${destination}' == '${FLOW_STATE_PRODUCT_SELECTION}'
        IF    '${product_selection_policy}' == 'REQUIRED'
            Complete Product Selection    ${expected_product_categories}
            ${product_selection_completed}=    Set Variable    ${TRUE}
            Wait Until Registration Success Is Displayed
        ELSE
            Fail    PRODUCT_SELECTION_CONTRACT_VIOLATION
        END
    ELSE IF    '${destination}' == '${FLOW_STATE_REGISTRATION_SUCCESS}' and '${product_selection_policy}' == 'REQUIRED' and not ${product_selection_completed}
        Fail    PRODUCT_SELECTION_REQUIRED_BUT_SKIPPED
    END

    Assert ETB Release Pre-SET
    Record ETB Registration Success Visible    ${OUTPUT DIR}
    Record ETB Registration Continue Start    ${OUTPUT DIR}
    Tap Registration Success Continue
    Record ETB Registration Continue End    ${OUTPUT DIR}
    Record ETB Post Success State    ${OUTPUT DIR}
    RETURN    ${TRUE}
