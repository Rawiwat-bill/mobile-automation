*** Settings ***
Documentation       ETB Onboarding's Keywords

Resource            ../../../resources/app/app_keywords.resource
Resource            ../../pages/common_onboarding/landing_screen_page.resource
Resource            ../../pages/common_onboarding/terms_and_conditions_page.resource
Resource            ../../pages/common_onboarding/tell_us_about_you_page.resource
Resource            ../../keywords/health_check_keywords.resource


*** Variables ***
${LOADING_TIMEOUT}      15s


*** Keywords ***
Common Onboarding Flow
    [Documentation]    Complete the common onboarding flow for ETB
    [Arguments]    ${citizen_id}    ${date_of_birth}    ${mobile_number}

    Wait Until Landing Screen Is Displayed
    Mark Health Checkpoint    LANDING_VISIBLE
    Switch Landing Language To English
    Tap Landing Ready Button
    Allow Android Permission If Visible
    Mark Health Checkpoint    LANDING_COMPLETED
    Wait Until Terms And Conditions Screen Is Displayed
    Mark Health Checkpoint    TERMS_AND_CONDITIONS_VISIBLE
    Scroll Down Terms And Conditions
    Accept Terms And Conditions
    Mark Health Checkpoint    TERMS_AND_CONDITIONS_ACCEPTED
    Wait Until Tell Us About You Screen Is Displayed
    Input Citizen ID    ${citizen_id}
    Select Date Of Birth    ${date_of_birth}
    Input Mobile Number    ${mobile_number}
    Wait Until Fields Are Blurred
    Click Next Button
