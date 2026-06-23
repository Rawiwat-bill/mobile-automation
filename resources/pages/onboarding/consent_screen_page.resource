*** Settings ***
Library     AppiumLibrary
Resource    ../../../locators/android/onboarding/consent_screen_locators.resource


*** Variables ***
${CONSENT_TIMEOUT}    10s


*** Keywords ***
Wait Until Consent Screen Is Displayed
    Wait Until Element Is Visible    ${CONSENT_TITLE_TEXT}    ${CONSENT_TIMEOUT}
    Wait Until Element Is Visible    ${CONSENT_WEBVIEW}       ${CONSENT_TIMEOUT}

Tap Consent Accept Button
    Wait Until Element Is Visible    ${CONSENT_ACCEPT_BUTTON}    ${CONSENT_TIMEOUT}
    Click Element                    ${CONSENT_ACCEPT_BUTTON}
