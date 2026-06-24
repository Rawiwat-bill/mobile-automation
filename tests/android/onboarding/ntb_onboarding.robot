*** Settings ***
Documentation    NTB Onboarding - Profile Information
Resource         ../../../resources/app/app_keywords.resource
Resource         ../../../resources/pages/onboarding/landing_screen_page.resource
Resource         ../../../resources/pages/onboarding/consent_screen_page.resource
Resource         ../../../resources/pages/onboarding/profile_screen_page.resource
Library          ../../../libraries/config_loader.py

Suite Setup      Open Mobile Application
Suite Teardown   Close Application

*** Variables ***
${NTB_TESTDATA}    testdata/onboarding/ntb.local.yaml

*** Test Cases ***
NTB Onboarding Until Profile Completed

    ${data}=    Load YAML    ${NTB_TESTDATA}

    Wait Until Landing Screen Is Displayed
    Tap Landing Ready Button
    Allow Android Permission If Visible

    Wait Until Consent Screen Is Displayed
    Tap Consent Accept Button

    Wait Until Profile Screen Is Displayed
    Input Citizen ID    ${data['profile']['citizen_id']}
    Tap Date Of Birth Field

    # TODO: Date Picker ยังไม่ได้ Implement

    Input Mobile Number    ${data['profile']['mobile_number']}
    Tap Profile Next Button