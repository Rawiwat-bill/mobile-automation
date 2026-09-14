*** Settings ***
Documentation       ETB onboarding flow keywords.

Resource            ../../../resources/app/app_keywords.resource
Resource            ../../keywords/common_onboarding/common_onboarding_keyword.resource
Resource            ../../pages/etb/check_dopa_fill_laser_code_page.resource
Resource            ../../pages/etb/mobile_otp_page.resource
Resource            ../../pages/etb/setup_pin_page.resource
Resource            ../../pages/etb/rgi_popup_page.resource
Resource            ../../pages/etb/full_screen_rgi_page.resource
Resource            ../../pages/etb/product_selection_page.resource
Resource         ../../pages/etb/three_c_page.resource
Library          ../../../libraries/visual_timeline.py
Library          ../../../libraries/etb_readiness_evidence.py



*** Keywords ***
Complete ETB Onboarding
    [Documentation]    Complete the onboarding flow for ETB
    [Arguments]    ${citizen_id}    ${date_of_birth}    ${mobile_number}    ${laser_code}    ${otp}    ${pin}    ${product_selection_policy}=REQUIRED

    ${common_result}=    Common Onboarding Flow    ${citizen_id}    ${date_of_birth}    ${mobile_number}
    IF    '${common_result}' == 'GOD-013'
        Set Health Check Blocker
        ...    ENVIRONMENT_BACKEND_GOD_013
        ...    Environment/backend service is not available (GOD-013).
        ...    ${OUTPUT DIR}
        Mark Health Checkpoint    ETB_ENVIRONMENT_BACKEND_HANDOFF
        Fail    BLOCKED_BY_ENVIRONMENT_BACKEND_GOD_013: service unavailable before DOPA.
    END
    IF    '${common_result}' == 'AJI-001'
        Set Health Check Blocker
        ...    AJI-001
        ...    Environment/backend handoff: service is not available.
        ...    ${OUTPUT DIR}
        Mark Health Checkpoint    ETB_ENVIRONMENT_BACKEND_HANDOFF
        Persist ETB Readiness Summary
        ...    ${OUTPUT DIR}
        ...    blocker_code=AJI-001
        ...    profile_handoff=PASS
        ...    dopa_reached=${FALSE}
        Fail    BLOCKED_BY_ENVIRONMENT_BACKEND_AJI_001: service unavailable before DOPA.
    END
    Should Be Equal As Strings    ${common_result}    NEXT    ETB_COMMON_ONBOARDING_DID_NOT_REACH_DOPA

    # Check DOPA Fill Laser Code Screen
    Wait Until Check DOPA Fill Laser Code Is Displayed
    Mark Health Checkpoint    CHECK_DOPA_FILL_LASER_CODE_VISIBLE
    Input Laser Code    ${laser_code}
    Log    LASER_INPUT = COMPLETED
    Wait Until Element Is Visible    ${CHECK_DOPA_FILL_LASER_CODE_BUTTON_NEXT}    ${NCBD_LOADING_TIMEOUT}
    Click Element    ${CHECK_DOPA_FILL_LASER_CODE_BUTTON_NEXT}
    Mark Health Checkpoint    CHECK_DOPA_FILL_LASER_CODE_COMPLETED

    # Mobile OTP Screen
    Wait Until Mobile OTP Screen Is Displayed
    Mark Health Checkpoint    MOBILE_OTP_VISIBLE
    Input OTP    ${otp}
    Log    OTP_INPUT = COMPLETED
    Mark Health Checkpoint    MOBILE_OTP_COMPLETED

    ${screen}=    Handle Post OTP Transition
    IF    $screen == 'CHECK_PDPA_CLAUSE_NO_6'
        Wait Until Check PDPA Clause No6 Is Displayed
        Mark Health Checkpoint    CHECK_PDPA_CLAUSE_NO_6_VISIBLE
        Scroll Down PDPA Clause No6
        Accept PDPA Clause No6
        Mark Health Checkpoint    CHECK_PDPA_CLAUSE_NO_6_COMPLETED
    END

    # Intro Face Scan Screen
    Wait Until Intro Face Screen Is Displayed
    Mark Health Checkpoint    INTRO_FACE_SCAN_VISIBLE
    Click Element    ${INTRO_FACE_SCAN_NEXT_BUTTON}
    Allow Android Permission If Visible
    Mark Health Checkpoint    INTRO_FACE_SCAN_COMPLETED

    # Setup Pin Screen
    Wait Until Setup Pin Screen Is Displayed
    Mark Health Checkpoint    SETUP_PIN_VISIBLE
    Set Up PIN    ${pin}
    ${product_selection_completed}=    Set Variable    ${FALSE}
    ${post_pin_state}=    Probe Post First PIN State
    IF    '${post_pin_state}' == 'CONFIRM_PIN'
        Set Up PIN    ${pin}    re_pin=${True}
    ELSE IF    '${post_pin_state}' == 'PRODUCT_SELECTION'
        IF    '${product_selection_policy}' == 'REQUIRED'
            Mark Health Checkpoint    PRODUCT_SELECTION_VISIBLE
            Complete Product Selection
            ${product_selection_completed}=    Set Variable    ${TRUE}
        ELSE
            Fail    PRODUCT_SELECTION_CONTRACT_VIOLATION
        END
    ELSE IF    '${post_pin_state}' == 'COMPLETION_SUCCESS'
        IF    '${product_selection_policy}' == 'REQUIRED'
            Fail    PRODUCT_SELECTION_REQUIRED_BUT_SKIPPED
        END
    ELSE IF    '${post_pin_state}' == 'EXACT_ERROR'
        Fail    TC004_POST_FIRST_PIN_EXACT_ERROR
    ELSE
        Fail    PIN_UNEXPECTED_NAVIGATION
    END
    Log    PIN_INPUT = COMPLETED
    ${destination}=    Wait Until Keyword Succeeds    ${NCBD_LOADING_TIMEOUT}    500ms
    ...    ETB Post PIN Destination Should Be Displayed
    IF    '${destination}' == 'ENVIRONMENT_BACKEND_AJI_001'
        Set Health Check Blocker
        ...    ENVIRONMENT_BACKEND_AJI_001
        ...    Environment/backend handoff after PIN: service is not available.
        ...    ${OUTPUT DIR}
        Mark Health Checkpoint    ETB_ENVIRONMENT_BACKEND_HANDOFF
        RETURN    ${FALSE}
    END
    IF    '${destination}' == 'PRODUCT_SELECTION'
        IF    '${product_selection_policy}' == 'REQUIRED'
            Mark Health Checkpoint    PRODUCT_SELECTION_VISIBLE
            Complete Product Selection
            ${product_selection_completed}=    Set Variable    ${TRUE}
            Wait Until Element Is Visible    ${LABEL_ETB_FINISHED}    ${NCBD_LOADING_TIMEOUT}
        ELSE
            Fail    PRODUCT_SELECTION_CONTRACT_VIOLATION
        END
    ELSE IF    '${destination}' == 'REGISTRATION_SUCCESS' and '${product_selection_policy}' == 'REQUIRED' and not ${product_selection_completed}
        Fail    PRODUCT_SELECTION_REQUIRED_BUT_SKIPPED
    END
    Mark Health Checkpoint    SETUP_PIN_COMPLETED
    Mark Health Checkpoint    SIGN_UP_RESULT_SUCCESS_VISIBLE
    Run Keyword And Ignore Error    Record Visual Timeline Event    SUCCESS0_VISIBLE    REGISTRATION_SUCCESS    ${OUTPUT DIR}/visual_timeline
    Run Keyword And Ignore Error    Record Visual Timeline Event    SUCCESS1_CONTINUE_ACTION_START    REGISTRATION_SUCCESS    ${OUTPUT DIR}/visual_timeline    action=CLICK_SUCCESS_LETS_GO    screenshot=${False}
    Click Element    ${BUTTON_LETGO}
    Run Keyword And Ignore Error    Record Visual Timeline Event    SUCCESS1_CONTINUE_ACTION_END    REGISTRATION_SUCCESS    ${OUTPUT DIR}/visual_timeline    action=CLICK_SUCCESS_LETS_GO_COMPLETED    screenshot=${False}
    Run Keyword And Ignore Error    Record Post Success Visual State    ${OUTPUT DIR}/visual_timeline
    Mark Health Checkpoint    SIGN_UP_RESULT_SUCCESS_COMPLETED
    RETURN    ${TRUE}

Probe Post First PIN State
    [Documentation]    Classify the immediate post-first-PIN business state using the active Appium session only.
    ${source}=    Get Source
    IF    'screenReEnterPinInput_keyPad' in $source
        RETURN    CONFIRM_PIN
    END
    IF    'screenProductSelection_textTitle' in $source or 'screenProductSelection_textDescription' in $source
        RETURN    PRODUCT_SELECTION
    END
    IF    "You're all set!" in $source or "You’re all set!" in $source or "Let's go" in $source or "Let’s go" in $source
        RETURN    COMPLETION_SUCCESS
    END
    IF    'AJI-001' in $source or 'RGI-' in $source
        RETURN    EXACT_ERROR
    END
    IF    'screenPinInput' in $source or 'loading' in $source.lower()
        RETURN    LOADING_OR_INTERMEDIATE
    END
    RETURN    UNKNOWN

ETB Post PIN Destination Should Be Displayed
    ${product_visible}=    Run Keyword And Return Status
    ...    Product Selection Screen Should Be Displayed
    IF    ${product_visible}
        RETURN    PRODUCT_SELECTION
    END
    ${source}=    Get Source
    IF    'screenProductSelection_textTitle' in $source or 'screenProductSelection_textDescription' in $source
        RETURN    PRODUCT_SELECTION
    END
    ${aji_visible}=    Run Keyword And Return Status
    ...    Should Contain    ${source}    AJI-001
    IF    ${aji_visible}
        RETURN    ENVIRONMENT_BACKEND_AJI_001
    END
    ${finished_visible}=    Run Keyword And Return Status
    ...    Element Should Be Visible    ${LABEL_ETB_FINISHED}
    IF    ${finished_visible}
        RETURN    REGISTRATION_SUCCESS
    END
    IF    "You're all set!" in $source or "You’re all set!" in $source or "Let's go" in $source or "Let’s go" in $source
        RETURN    REGISTRATION_SUCCESS
    END
    Fail    ETB_POST_PIN_DESTINATION_NOT_VISIBLE
