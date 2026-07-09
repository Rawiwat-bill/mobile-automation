*** Settings ***
Library     AppiumLibrary
Resource    ../../../locators/android/onboarding/dopa_information_locators.resource

*** Variables ***
${DOPA_INFORMATION_TIMEOUT}    35s

*** Keywords ***
Wait Until DOPA Information Screen Is Displayed
    Wait Until Page Contains Element    ${DOPA_INFORMATION_SCREEN}    ${DOPA_INFORMATION_TIMEOUT}
    Log    [DOPA] DOPA information screen visible
