*** Settings ***
Resource    ../pages/onboarding/consent_screen_page.resource


*** Keywords ***
Accept Terms And Conditions
    Wait Until Consent Screen Is Displayed
    Tap Consent Accept Button
