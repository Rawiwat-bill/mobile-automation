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
Resource            ../../pages/etb/three_c_page.resource



*** Keywords ***
Complete ETB Onboarding
    [Documentation]    Complete the onboarding flow for ETB
    [Arguments]    ${citizen_id}    ${date_of_birth}    ${mobile_number}    ${laser_code}    ${otp}    ${pin}

    ${common_result}=    Common Onboarding Flow    ${citizen_id}    ${date_of_birth}    ${mobile_number}
    IF    '${common_result}' == 'AJI-001'
        Set Health Check Blocker
        ...    AJI-001
        ...    Environment/backend handoff: service is not available.
        ...    ${OUTPUT DIR}
        Mark Health Checkpoint    ETB_ENVIRONMENT_BACKEND_HANDOFF
        RETURN    ${FALSE}
    END

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
    Set Up PIN    ${pin}    re_pin=${True}
    Log    PIN_INPUT = COMPLETED
    ${destination}=    Wait Until Keyword Succeeds    ${NCBD_LOADING_TIMEOUT}    500ms
    ...    ETB Post PIN Destination Should Be Displayed
    IF    '${destination}' == 'PRODUCT_SELECTION'
        Mark Health Checkpoint    PRODUCT_SELECTION_VISIBLE
        RETURN    ${TRUE}
    END
    Mark Health Checkpoint    SETUP_PIN_COMPLETED
    Mark Health Checkpoint    SIGN_UP_RESULT_SUCCESS_VISIBLE
    Click Element    ${BUTTON_LETGO}
    Mark Health Checkpoint    SIGN_UP_RESULT_SUCCESS_COMPLETED
    RETURN    ${TRUE}

ETB Post PIN Destination Should Be Displayed
    ${product_visible}=    Run Keyword And Return Status
    ...    Product Selection Screen Should Be Displayed
    IF    ${product_visible}
        RETURN    PRODUCT_SELECTION
    END
    ${finished_visible}=    Run Keyword And Return Status
    ...    Element Should Be Visible    ${LABEL_ETB_FINISHED}
    IF    ${finished_visible}
        RETURN    REGISTRATION_SUCCESS
    END
    Fail    ETB_POST_PIN_DESTINATION_NOT_VISIBLE
