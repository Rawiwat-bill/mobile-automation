*** Settings ***
Library     AppiumLibrary
Resource    ../../../locators/android/onboarding/scan_card_intro_locators.resource

*** Variables ***
${SCAN_CARD_INTRO_TIMEOUT}    10s

*** Keywords ***
Wait Until Scan Card Intro Screen Is Displayed
    Wait Until Element Is Visible    ${SCAN_CARD_INTRO_STEP_BAR}    ${SCAN_CARD_INTRO_TIMEOUT}

Tap Scan Card Intro Next
    Click Element    ${SCAN_CARD_INTRO_NEXT}
    Log    [SCAN_CARD_INTRO] Next tapped
