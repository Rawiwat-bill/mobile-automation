*** Settings ***
Library     AppiumLibrary
Resource    ../../../resources/app/app_constants.resource
Resource    ../../../locators/android/common_onboarding/sign_up_locators.resource


*** Keywords ***
Wait Until Sign Up Screen Is Displayed
    [Documentation]    Wait until the sign up screen is displayed
    Wait Until Element Is Visible    ${SIGN_UP_LETS_START}    ${NCBD_LOADING_TIMEOUT}

Tap Sign Up Lets Start Button
    [Documentation]    Tap the "Let's start" button on the sign up screen
    Click Element    ${SIGN_UP_LETS_START}
    Log    [SIGN_UP] Let's start tapped
