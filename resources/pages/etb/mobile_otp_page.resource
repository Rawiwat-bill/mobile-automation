*** Settings ***
Documentation       ETB mobile OTP page keywords.

Library             Collections
Library             String
Library             AppiumLibrary
Resource            ../../../resources/app/app_constants.resource
Resource            ../../../locators/android/etb/mobile_otp_locators.resource
Resource            ../../../locators/android/etb/check_pdpa_clause_no_6_locators.resource
Resource            ../../../locators/android/etb/intro_face_scan_locators.resource


*** Keywords ***
Wait Until Mobile OTP Screen Is Displayed
    [Documentation]    Wait until the Mobile OTP screen is displayed.
    Wait Until Element Is Visible    ${MOBILE_OTP_TITLE_TEXT}    ${NCBD_LOADING_TIMEOUT}
    Wait Until Element Is Visible    ${MOBILE_OTP_INPUT}    ${NCBD_LOADING_TIMEOUT}

Input OTP
    [Documentation]    Input the OTP into the OTP input field.]
    [Arguments]    ${otp}

    Wait Until Element Is Visible    ${FIELD_OTP0}    ${NCBD_LOADING_TIMEOUT}
    Click Element    ${FIELD_OTP0}
    Enter OTP By Keycodes    ${otp}

Input OTP Fast
    [Documentation]    Input the OTP into the OTP input field.]
    [Arguments]    ${otp}=999999

    Wait Until Element Is Visible    ${FIELD_OTP0}    ${NCBD_LOADING_TIMEOUT}
    Input Text    ${MOBILE_OTP_INPUT}    ${otp}
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
    ${post_otp_screen}=    Wait Until Keyword Succeeds    ${NCBD_LOADING_TIMEOUT}    1s    Detect Post OTP Screen
    IF    '${post_otp_screen}' == 'CHECK_PDPA_CLAUSE_NO_6'
        Wait Until Element Is Visible    ${CHECK_PDPA_CLAUSE_NO_6_TITLE_TEXT}    ${NCBD_LOADING_TIMEOUT}
    ELSE IF    '${post_otp_screen}' == 'INTRO_FACE_SCAN'
        Wait Until Element Is Visible    ${INTRO_FACE_SCAN_TITLE_TEXT}    ${NCBD_LOADING_TIMEOUT}
    END

Detect Post OTP Screen
    [Documentation]    Detect whether the next screen is PDPA consent or face scan.

    ${pdpa_visible}=    Run Keyword And Return Status
    ...    Wait Until Element Is Visible
    ...    ${CHECK_PDPA_CLAUSE_NO_6_TITLE_TEXT}
    ...    ${NCBD_LOADING_TIMEOUT}
    IF    ${pdpa_visible}    RETURN    CHECK_PDPA_CLAUSE_NO_6
