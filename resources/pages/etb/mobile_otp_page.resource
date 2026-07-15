*** Settings ***
Library     String
Library     AppiumLibrary
Library     Collections
Resource    ../../../resources/app/app_constants.resource
Resource    ../../../locators/android/etb/mobile_otp_locators.resource


*** Keywords ***
Wait Until Mobile OTP Screen Is Displayed
    [Documentation]    Wait until the Mobile OTP screen is displayed.
    Wait Until Element Is Visible    ${MOBILE_OTP_TITLE_TEXT}    ${NCBD_LOADING_TIMEOUT}
    Wait Until Element Is Visible    ${MOBILE_OTP_INPUT}    ${NCBD_LOADING_TIMEOUT}

Input OTP
    [Arguments]    ${otp}=999999

    Wait Until Element Is Visible    ${FIELD_OTP0}    ${NCBD_LOADING_TIMEOUT}
    Click Element    ${FIELD_OTP0}
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
