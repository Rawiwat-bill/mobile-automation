*** Settings ***
Resource    ../app/app_keywords.resource
Resource    ../pages/onboarding/landing_screen_page.resource
Resource    ../pages/onboarding/consent_screen_page.resource
Resource    ../pages/onboarding/profile_screen_page.resource

*** Keywords ***
Complete Common Onboarding
    [Arguments]    ${citizen_id}    ${date_of_birth}    ${mobile_number}
    Wait Until Landing Screen Is Displayed
    Tap Landing Ready Button
    Allow Android Permission If Visible
    Wait Until Consent Screen Is Displayed
    Tap Consent Accept Button
    Wait Until Profile Screen Is Displayed
    Capture Profile Handoff Snapshot    profile_before
    Input Citizen ID    ${citizen_id}
    Input Date Of Birth    ${date_of_birth}
    Input Mobile Number    ${mobile_number}
    Capture Profile Handoff Snapshot    profile_after_input
    Tap Profile Next
