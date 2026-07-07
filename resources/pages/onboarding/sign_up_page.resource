*** Settings ***
Library     AppiumLibrary
Resource    ../../../locators/android/onboarding/sign_up_locators.resource

*** Variables ***
${SIGN_UP_TIMEOUT}    10s
${SIGN_UP_TRANSITION_TIMEOUT}    15s

*** Keywords ***
Wait Until Sign Up Screen Is Displayed
    Wait Until Element Is Visible    ${SIGN_UP_LETS_START}    ${SIGN_UP_TIMEOUT}

Tap Sign Up Lets Start Button
    Click Element    ${SIGN_UP_LETS_START}
    Log    [SIGN_UP] Let's start tapped
