*** Settings ***
Resource    ../app/app_keywords.resource
Resource    ../pages/onboarding/landing_screen_page.resource
Resource    ../pages/onboarding/consent_screen_page.resource
Resource    ../pages/onboarding/profile_screen_page.resource
Resource    ../pages/onboarding/pdpa_consent_page.resource
Resource    ../pages/onboarding/sign_up_page.resource
Resource    ../pages/onboarding/scan_card_intro_page.resource
Resource    ../pages/onboarding/id_card_camera_capture_page.resource
Resource    ../keywords/health_check_keywords.resource

*** Keywords ***
Complete Common Onboarding
    [Arguments]    ${citizen_id}    ${date_of_birth}    ${mobile_number}
    Wait Until Landing Screen Is Displayed
    Mark Health Checkpoint    LANDING_VISIBLE
    Tap Landing Ready Button
    Allow Android Permission If Visible
    Mark Health Checkpoint    LANDING_COMPLETED
    Wait Until Consent Screen Is Displayed
    Mark Health Checkpoint    CONSENT_VISIBLE
    Tap Consent Accept Button
    Mark Health Checkpoint    CONSENT_ACCEPTED
    Wait Until Profile Screen Is Displayed
    Mark Health Checkpoint    PROFILE_VISIBLE
    Capture Profile Handoff Snapshot    profile_before
    Input Citizen ID    ${citizen_id}
    Input Date Of Birth    ${date_of_birth}
    Input Mobile Number    ${mobile_number}
    Capture Profile Handoff Snapshot    profile_after_input
    Tap Profile Next
    Mark Health Checkpoint    PROFILE_COMPLETED
    Wait Until PDPA Consent Screen Is Displayed
    Mark Health Checkpoint    PDPA_CONSENT_VISIBLE
    ${pdpa_accepted}=    Tap PDPA Consent Accept Button
    Mark Health Checkpoint    PDPA_CONSENT_ACCEPT_ATTEMPTED
    IF    not ${pdpa_accepted}
        Set Health Check Blocker
        ...    PDPA_ACCEPT_NO_TRANSITION
        ...    PDPA Accept click succeeded but no screen transition. Backend/environment dependency.
        ...    reports/investigation/after_pdpa/
        Mark Health Checkpoint    PDPA_ACCEPT_NO_TRANSITION
        RETURN
    END
    Wait Until Sign Up Screen Is Displayed
    Mark Health Checkpoint    SIGN_UP_VISIBLE
    Tap Sign Up Lets Start Button
    Allow Android Permission If Visible
    Mark Health Checkpoint    SIGN_UP_STARTED
    Wait Until Scan Card Intro Screen Is Displayed
    Mark Health Checkpoint    SCAN_CARD_INTRO_VISIBLE
    Tap Scan Card Intro Next
    Allow Android Permission If Visible
    Mark Health Checkpoint    SCAN_CARD_INTRO_COMPLETED
    Wait Until ID Card Camera Capture Screen Is Displayed
    Mark Health Checkpoint    ID_CARD_CAMERA_CAPTURE_VISIBLE
    Navigate Virtual Camera To Poster
    Tap Take Photo
    Mark Health Checkpoint    ID_CARD_PHOTO_CAPTURED
