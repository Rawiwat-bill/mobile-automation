*** Settings ***
Library     AppiumLibrary
Resource    ../../../locators/android/onboarding/landing_screen_locators.resource


*** Variables ***
${LANDING_TIMEOUT}    10s


*** Keywords ***
Landing Screen Should Be Visible
    Wait Until Element Is Visible    ${LANDING_TITLE_TEXT}          ${LANDING_TIMEOUT}
    Wait Until Element Is Visible    ${LANDING_DESCRIPTION_TEXT}    ${LANDING_TIMEOUT}
    Wait Until Element Is Visible    ${LANDING_INDICATOR}           ${LANDING_TIMEOUT}
    Wait Until Element Is Visible    ${LANDING_SKIP_BUTTON}         ${LANDING_TIMEOUT}

Switch Landing Language To Thai
    Wait Until Element Is Visible    ${LANDING_LANGUAGE_THAI_BUTTON}    ${LANDING_TIMEOUT}
    Click Element                    ${LANDING_LANGUAGE_THAI_BUTTON}

Switch Landing Language To English
    Wait Until Element Is Visible    ${LANDING_LANGUAGE_ENGLISH_BUTTON}    ${LANDING_TIMEOUT}
    Click Element                    ${LANDING_LANGUAGE_ENGLISH_BUTTON}

Skip Landing Screen
    Wait Until Element Is Visible    ${LANDING_SKIP_BUTTON}    ${LANDING_TIMEOUT}
    Click Element                    ${LANDING_SKIP_BUTTON}

Tap Landing Ready Button
    Wait Until Element Is Visible    ${LANDING_READY_BUTTON}    ${LANDING_TIMEOUT}
    Click Element                    ${LANDING_READY_BUTTON}
