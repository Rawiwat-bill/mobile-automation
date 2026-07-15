*** Settings ***
Library     AppiumLibrary
Resource    ../../../locators/android/onboarding/verify_mobile_otp_locators.resource


*** Variables ***
${OTP_TIMEOUT}    60s


*** Keywords ***
Wait Until OTP Screen Is Displayed
    Wait Until Page Contains Element    ${OTP_SCREEN_MARKER}    ${OTP_TIMEOUT}
    Log    [OTP] OTP screen visible

Enter OTP Code
    [Arguments]    ${code}
    Wait Until Page Contains Element    ${OTP_INPUT}    10s
    Input Text    ${OTP_INPUT}    ${code}
    Log    [OTP] Code entered    WARN
