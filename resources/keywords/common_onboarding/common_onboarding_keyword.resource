*** Settings ***
Documentation       ETB Onboarding's Keywords

Resource            ../../../resources/app/app_keywords.resource
Resource            ../../pages/common_onboarding/landing_screen_page.resource
Resource            ../../pages/common_onboarding/terms_and_conditions_page.resource
Resource            ../../pages/common_onboarding/tell_us_about_you_page.resource
Resource            ../../pages/onboarding/profile_screen_page.resource
Resource            ../../keywords/health_check_keywords.resource


*** Keywords ***
Common Onboarding Flow
    [Documentation]    Complete the common onboarding flow for ETB
    [Arguments]    ${citizen_id}    ${date_of_birth}    ${mobile_number}

    Wait Until Landing Screen Is Displayed
    Mark Health Checkpoint    LANDING_VISIBLE
    Switch Landing Language To English
    Tap Landing Ready Button
    Allow Android Permission If Visible
    Wait For Landing Destination    ${TERMS_AND_CONDITIONS_WEBVIEW}    ${NCBD_LOADING_TIMEOUT}
    Mark Health Checkpoint    LANDING_COMPLETED

    Wait Until Terms And Conditions Screen Is Displayed
    Mark Health Checkpoint    TERMS_AND_CONDITIONS_VISIBLE
    Scroll Down Terms And Conditions
    ${terms_result}=    Accept Terms And Conditions
    IF    '${terms_result}' == 'AJI-001'
        Mark Health Checkpoint    ETB_ENVIRONMENT_BACKEND_HANDOFF
        RETURN    AJI-001
    END
    Mark Health Checkpoint    TERMS_AND_CONDITIONS_ACCEPTED

    Wait Until Tell Us About You Screen Is Displayed
    Mark Health Checkpoint    TELL_US_ABOUT_YOU_VISIBLE
    tell_us_about_you_page.Input Citizen ID    ${citizen_id}
    Log    PROFILE_INPUT = COMPLETED
    Select Date Of Birth    ${date_of_birth}
    Log    DOB_INPUT = COMPLETED
    tell_us_about_you_page.Input Mobile Number    ${mobile_number}
    Log    MOBILE_INPUT = COMPLETED
    Wait Until Fields Are Blurred
    ${profile_result}=    Tap Profile Next
    IF    '${profile_result}' == 'GOD-013'
        RETURN    GOD-013
    END
    IF    '${profile_result}' == 'AJI-001'
        RETURN    AJI-001
    END
    IF    '${profile_result}' == 'RGI-104'
        RETURN    RGI-104
    END
    Mark Health Checkpoint    TELL_US_ABOUT_YOU_COMPLETED
    RETURN    NEXT
