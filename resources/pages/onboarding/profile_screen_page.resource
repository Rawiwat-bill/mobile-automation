*** Settings ***
Library     AppiumLibrary
Resource    ../../../locators/android/onboarding/profile_screen_locators.resource


*** Variables ***
${PROFILE_TIMEOUT}    10s


*** Keywords ***
Wait Until Profile Screen Is Displayed
    Wait Until Element Is Visible    ${PROFILE_CITIZEN_ID_INPUT}    30s

Input Citizen ID
    [Arguments]    ${citizen_id}
    Wait Until Element Is Visible    ${PROFILE_CITIZEN_ID_INPUT}    ${PROFILE_TIMEOUT}
    Input Text                       ${PROFILE_CITIZEN_ID_INPUT}    ${citizen_id}

Tap Date Of Birth Field
    Wait Until Element Is Visible    ${PROFILE_DOB_INPUT}    ${PROFILE_TIMEOUT}
    Click Element                    ${PROFILE_DOB_INPUT}

Input Mobile Number
    [Arguments]    ${mobile_number}
    Wait Until Element Is Visible    ${PROFILE_MOBILE_NUMBER_INPUT}    ${PROFILE_TIMEOUT}
    Input Text                       ${PROFILE_MOBILE_NUMBER_INPUT}    ${mobile_number}

Tap Profile Next Button
    Wait Until Element Is Visible    ${PROFILE_NEXT_BUTTON}    ${PROFILE_TIMEOUT}
    Click Element                    ${PROFILE_NEXT_BUTTON}
