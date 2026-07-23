*** Settings ***
Documentation       ETB mobile OTP page keywords.

Library             Collections
Library             String
Library             AppiumLibrary
Resource            ../../../resources/app/app_constants.resource
Resource            ../../../resources/pages/etb/check_pdpa_clause_no_6_page.resource
Resource            ../../../resources/pages/etb/intro_face_scan_page.resource
Resource            ../../../locators/android/etb/mobile_otp_locators.resource


*** Keywords ***
Wait Until Mobile OTP Screen Is Displayed
    [Documentation]    Wait until the Mobile OTP screen is displayed.
    Wait Until Element Is Visible    ${MOBILE_OTP_TITLE_TEXT}    ${NCBD_LOADING_TIMEOUT}
    Wait Until Element Is Visible    ${MOBILE_OTP_INPUT}    ${NCBD_LOADING_TIMEOUT}

Input OTP
    [Documentation]    Input the OTP into the OTP input field.
    [Arguments]    ${otp}

    Wait Until Element Is Visible    ${FIELD_OTP0}    ${NCBD_LOADING_TIMEOUT}
    Click Element    ${FIELD_OTP0}
    Enter OTP By Keycodes    ${otp}

Enter OTP By Keycodes
    [Documentation]    Enter the OTP by sending keycodes for each digit.
    [Arguments]    ${otp}
    ${digits}=    Evaluate    ''.join(ch for ch in """${otp}""" if ch.isdigit())
    ${map}=    Evaluate    {'0': 7, '1': 8, '2': 9, '3': 10, '4': 11, '5': 12, '6': 13, '7': 14, '8': 15, '9': 16}
    ${keycodes}=    Evaluate    [$map[c] for c in $digits]
    FOR    ${keycode}    IN    @{keycodes}
        Press Keycode    ${keycode}
    END

Handle Post OTP Transition
    [Documentation]    Accept the optional PDPA screen after OTP, otherwise wait for face scan.
    ${start_time}=    Evaluate    __import__('time').perf_counter()
    ${post_otp_screen}=    Wait Until Keyword Succeeds    ${NCBD_LOADING_TIMEOUT}    1s    Detect Post OTP Screen
    ${elapsed_seconds}=    Evaluate    round(__import__('time').perf_counter() - $start_time, 3)
    Log To Console    Handle Post OTP Transition took ${elapsed_seconds}s -> ${post_otp_screen}
    Log    Handle Post OTP Transition took ${elapsed_seconds}s -> ${post_otp_screen}
    RETURN    ${post_otp_screen}

Detect Post OTP Screen
    [Documentation]    Detect whether the next screen is PDPA consent or face scan.
    VAR    ${probe_timeout}    2s

    ${pdpa_visible}=    Run Keyword And Return Status
    ...    Wait Until Element Is Visible
    ...    ${CHECK_PDPA_CLAUSE_NO_6_TITLE_TEXT}
    ...    ${probe_timeout}
    IF    ${pdpa_visible}    RETURN    CHECK_PDPA_CLAUSE_NO_6

    ${intro_face_visible}=    Run Keyword And Return Status
    ...    Wait Until Element Is Visible
    ...    ${INTRO_FACE_SCAN_TITLE_TEXT}
    ...    ${probe_timeout}
    IF    ${intro_face_visible}    RETURN    INTRO_FACE_SCAN

    Fail    Post OTP screen not ready yet
