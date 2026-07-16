*** Settings ***
Documentation       ETB onboarding flow keywords.

Resource            ../../../resources/app/app_keywords.resource
Resource            ../../keywords/common_onboarding/common_onboarding_keyword.resource
Resource            ../../pages/etb/check_dopa_fill_laser_code_page.resource
Resource            ../../pages/etb/mobile_otp_page.resource
Resource            ../../pages/etb/check_pdpa_clause_no_6_page.resource
Resource            ../../pages/etb/intro_face_scan_page.resource
Resource            ../../pages/etb/setup_pin_page.resource


*** Keywords ***
Complete ETB Onboarding
    [Documentation]    Complete the onboarding flow for ETB
    [Arguments]    ${citizen_id}    ${date_of_birth}    ${mobile_number}    ${laser_code}    ${otp}    ${pin}

    Common Onboarding Flow    ${citizen_id}    ${date_of_birth}    ${mobile_number}

    # Check DOPA Fill Laser Code Screen
    Wait Until Check DOPA Fill Laser Code Is Displayed
    Mark Health Checkpoint    CHECK_DOPA_FILL_LASER_CODE_VISIBLE
    Input Laser Code    ${laser_code}
    Wait Until Element Is Visible    ${CHECK_DOPA_FILL_LASER_CODE_BUTTON_NEXT}    ${NCBD_LOADING_TIMEOUT}
    Click Element    ${CHECK_DOPA_FILL_LASER_CODE_BUTTON_NEXT}
    Mark Health Checkpoint    CHECK_DOPA_FILL_LASER_CODE_COMPLETED

    # Mobile OTP Screen
    Wait Until Mobile OTP Screen Is Displayed
    Mark Health Checkpoint    MOBILE_OTP_VISIBLE
    Input OTP    ${otp}
    Mark Health Checkpoint    MOBILE_OTP_COMPLETED

    # Check PDPA Clause No6 Screen
    ${post_otp_screen}=    Wait Until Keyword Succeeds    ${NCBD_LOADING_TIMEOUT}    1s    Detect Post OTP Screen
    IF    '${post_otp_screen}' == 'CHECK_PDPA_CLAUSE_NO_6'
        Wait Until Check PDPA Clause No6 Is Displayed
        Mark Health Checkpoint    CHECK_PDPA_CLAUSE_NO_6_VISIBLE
        Scroll Down PDPA Clause No6
        Accept PDPA Clause No6
        Mark Health Checkpoint    CHECK_PDPA_CLAUSE_NO_6_COMPLETED

        # Intro Face Scan Screen
        Wait Until Intro Face Screen Is Displayed
        Mark Health Checkpoint    INTRO_FACE_SCAN_VISIBLE
        Click Element    ${INTRO_FACE_SCAN_NEXT_BUTTON}
        Allow Android Permission If Visible

        # Setup Pin Screen
        Wait Until Setup Pin Screen Is Displayed
        Mark Health Checkpoint    SETUP_PIN_VISIBLE
        Set Up PIN    ${pin}
        Set Up PIN    ${pin}    re_pin=${True}
        Wait Until Page Does Not Contain Element    ${RE_ENTER_PIN_TITLE_TEXT}    ${NCBD_LOADING_TIMEOUT}
        Wait Until Page Does Not Contain Element    ${LAYER_LOADING}    ${NCBD_LOADING_TIMEOUT}
        Click Element    ${BUTTON_CONFIRM}
        Wait Until Element Is Visible    ${LABEL_ETB_FINISHED}    ${NCBD_LOADING_TIMEOUT}
        Click Element    ${BUTTON_LETGO}

        RETURN
    END

    # Intro Face Scan Screen
    Wait Until Intro Face Screen Is Displayed
    Mark Health Checkpoint    INTRO_FACE_SCAN_VISIBLE
    Click Element    ${INTRO_FACE_SCAN_NEXT_BUTTON}
    Allow Android Permission If Visible

    # Setup Pin Screen
    Wait Until Setup Pin Screen Is Displayed
    Mark Health Checkpoint    SETUP_PIN_VISIBLE
    Set Up PIN    ${pin}
    Set Up PIN    ${pin}    re_pin=${True}
    Wait Until Page Does Not Contain Element    ${RE_ENTER_PIN_TITLE_TEXT}    ${NCBD_LOADING_TIMEOUT}
    Wait Until Page Does Not Contain Element    ${LAYER_LOADING}    ${NCBD_LOADING_TIMEOUT}
    Wait Until Element Is Visible    ${LABEL_ETB_FINISHED}    ${NCBD_LOADING_TIMEOUT}
    Click Element    ${BUTTON_LETGO}
