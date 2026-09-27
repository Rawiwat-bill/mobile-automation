*** Settings ***
Documentation       ETB mobile OTP page keywords.

Library             Collections
Library             String
Library             AppiumLibrary
Resource    ../../contracts/flow_states.resource
Resource    ../../diagnostics/mobile_otp_observability.resource
Resource            ../../../resources/app/app_constants.resource
Resource            ../../../resources/pages/etb/check_pdpa_clause_no_6_page.resource
Resource            ../../../resources/pages/etb/intro_face_scan_page.resource
Resource            ../../../resources/pages/common_onboarding/landing_screen_page.resource
Resource            ../../../locators/android/etb/mobile_otp_locators.resource


*** Keywords ***
Wait Until Mobile OTP Screen Is Displayed
    [Documentation]    Wait until the Mobile OTP screen is displayed.
    Wait Until Element Is Visible    ${MOBILE_OTP_TITLE_TEXT}    ${NCBD_LOADING_TIMEOUT}
    Wait Until Element Is Visible    ${MOBILE_OTP_INPUT}    ${NCBD_LOADING_TIMEOUT}

Input OTP
    [Documentation]    Input the OTP into the OTP input field.
    [Arguments]    ${otp}

    Wait Until Element Is Visible    ${MOBILE_OTP_INPUT}    ${NCBD_LOADING_TIMEOUT}
    Input Text    ${MOBILE_OTP_INPUT}    ${otp}

Handle Post OTP Transition
    [Documentation]    Resolve the proven Android chooser before detecting the ETB destination.
    ${start_time}=    Evaluate    __import__('time').perf_counter()
    ${post_otp_screen}=    Wait Until Keyword Succeeds    ${NCBD_LOADING_TIMEOUT}    1s    Detect Post OTP Screen
    ${elapsed_seconds}=    Evaluate    round(__import__('time').perf_counter() - $start_time, 3)
    Log To Console    Handle Post OTP Transition took ${elapsed_seconds}s -> ${post_otp_screen}
    Log    Handle Post OTP Transition took ${elapsed_seconds}s -> ${post_otp_screen}
    RETURN    ${post_otp_screen}

Detect Post OTP Screen
    [Documentation]    Detect PDPA, face scan, or an unexpected Android resolver.
    VAR    ${probe_timeout}    2s

    ${resolver_visible}=    Run Keyword And Return Status
    ...    Wait Until Element Is Visible
    ...    ${ANDROID_RESOLVER_TITLE}
    ...    ${probe_timeout}
    IF    ${resolver_visible}
        Capture Unexpected Android Resolver Evidence    ${OUTPUT DIR}
        Fail    ANDROID_RESOLVER_UNEXPECTED_AFTER_ENVIRONMENT_ISOLATION
    END

    ${pdpa_visible}=    Run Keyword And Return Status
    ...    Wait Until Element Is Visible
    ...    ${CHECK_PDPA_CLAUSE_NO_6_TITLE_TEXT}
    ...    ${probe_timeout}
    IF    ${pdpa_visible}    RETURN    ${FLOW_STATE_CHECK_PDPA_CLAUSE_NO_6}

    ${intro_face_visible}=    Run Keyword And Return Status
    ...    Wait Until Element Is Visible
    ...    ${INTRO_FACE_SCAN_TITLE_TEXT}
    ...    ${probe_timeout}
    IF    ${intro_face_visible}    RETURN    ${FLOW_STATE_INTRO_FACE_SCAN}

    Fail    Post OTP screen not ready yet

Detect Post OTP Destination
    ${pdpa_visible}=    Run Keyword And Return Status
    ...    Wait Until Element Is Visible
    ...    ${CHECK_PDPA_CLAUSE_NO_6_TITLE_TEXT}
    ...    2s
    IF    ${pdpa_visible}    RETURN    ${FLOW_STATE_CHECK_PDPA_CLAUSE_NO_6}

    ${intro_face_visible}=    Run Keyword And Return Status
    ...    Wait Until Element Is Visible
    ...    ${INTRO_FACE_SCAN_TITLE_TEXT}
    ...    2s
    IF    ${intro_face_visible}    RETURN    ${FLOW_STATE_INTRO_FACE_SCAN}

    ${landing_visible}=    Run Keyword And Return Status
    ...    Landing Screen Should Be Visible
    IF    ${landing_visible}
        Fail    FRESH_POST_OTP_RESOLVER_TO_LANDING
    END

    Fail    Post OTP destination not ready yet

Resolve ETB Android Resolver
    [Documentation]    Defensive compatibility keyword; resolver selection is forbidden.
    Capture Unexpected Android Resolver Evidence    ${OUTPUT DIR}
    Fail    ANDROID_RESOLVER_UNEXPECTED_AFTER_ENVIRONMENT_ISOLATION

ETB Resolver Target Should Be Foreground
    ${appium_library}=    Get Library Instance    AppiumLibrary
    ${foreground_package}=    Evaluate    $appium_library._current_application().current_package
    Should Be Equal    ${foreground_package}    ${APP_PACKAGE}
