*** Settings ***
Resource    ../app/app_keywords.resource
Resource    ../pages/onboarding/landing_screen_page.resource
Resource    ../pages/onboarding/consent_screen_page.resource
Resource    ../pages/onboarding/profile_screen_page.resource
Resource    ../pages/onboarding/pdpa_consent_page.resource
Resource    ../pages/onboarding/sign_up_page.resource
Resource    ../pages/onboarding/scan_card_intro_page.resource
Resource    ../pages/onboarding/id_card_camera_capture_page.resource
Resource    ../pages/onboarding/dopa_information_page.resource
Resource    ../pages/onboarding/verify_mobile_otp_page.resource
Resource    ../pages/onboarding/set_pin_page.resource
Resource    ../pages/onboarding/confirm_pin_page.resource
Resource    ../keywords/health_check_keywords.resource


*** Variables ***
# post-PIN success markers (lowercased before matching). Single source of truth for both
# Stage 1 suites' terminal-state detection -- was duplicated + buggy ($source scope) in the test files.
@{SUCCESS_MARKERS}    success    complete    saved    welcome    congratulations


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

Complete Stage 1 Onboarding
    [Documentation]    Full Stage 1 flow: Landing through Confirm PIN.
    ...                All values come from the testdata dictionary argument.
    [Arguments]    ${data}
    Complete Common Onboarding
    ...    ${data['profile']['citizen_id']}
    ...    ${data['profile']['date_of_birth']}
    ...    ${data['profile']['mobile_number']}
    Capture ID Card Photo
    Wait Until DOPA Information Screen Is Displayed
    Mark Health Checkpoint    DOPA_VISIBLE
    Select DOPA Title If Needed    ${data['dopa']['title']['thai']}
    Wait Until Page Contains Element    xpath=//*[@text="Enter first name in English"]    10s
    Fill DOPA English Names    ${data['dopa']['english']['first_name']}    ${data['dopa']['english']['last_name']}
    ${issue_parts}=    Split String    ${data['dopa']['document']['issue_date']}    -
    ${issue_month}=    Get From Dictionary    ${MONTH_MAP}    ${issue_parts}[1]
    Set DOPA Date Via Picker    ${DOPA_DATE_OF_ISSUE_INPUT}    ${issue_parts}[2]    ${issue_month}    ${issue_parts}[0]
    ${expire_parts}=    Split String    ${data['dopa']['document']['expiry_date']}    -
    ${expire_month}=    Get From Dictionary    ${MONTH_MAP}    ${expire_parts}[1]
    Set DOPA Date Via Picker    ${DOPA_DATE_OF_EXPIRE_INPUT}    ${expire_parts}[2]    ${expire_month}    ${expire_parts}[0]
    Fill DOPA Laser Code    ${data['dopa']['laser']['part1']}    ${data['dopa']['laser']['part2']}    ${data['dopa']['laser']['part3']}
    ${dopa_nav}=    Tap DOPA Next
    Mark Health Checkpoint    DOPA_COMPLETED
    Wait Until OTP Screen Is Displayed
    Mark Health Checkpoint    OTP_VISIBLE
    Enter OTP Code    ${data['otp']['code']}
    Mark Health Checkpoint    OTP_ENTERED
    Wait Until Set PIN Screen Is Displayed
    Mark Health Checkpoint    SET_PIN_VISIBLE
    Enter PIN Using Custom Keypad    ${data['pin']['value']}
    Mark Health Checkpoint    SET_PIN_ENTERED
    Wait Until Confirm PIN Screen Is Displayed
    Mark Health Checkpoint    CONFIRM_PIN_VISIBLE
    Enter Confirm PIN Using Custom Keypad    ${data['pin']['value']}
    Mark Health Checkpoint    CONFIRM_PIN_ENTERED

Detect Post PIN Terminal State
    [Documentation]    Read the page source after Confirm PIN and classify the terminal state.
    ...                Returns one of: SAVED | ENVIRONMENT_BLOCKED | NEXT_SCREEN_UNKNOWN.
    ...                pure-Robot membership via FOR + Should Contain. Avoids Evaluate
    ...                entirely -- Robot $var is not visible inside Evaluate generator scopes, and
    ...                passing a list as an Evaluate namespace kwarg raised a dict-update ValueError.
    ...                Empty source classifies as NEXT_SCREEN_UNKNOWN (never a false pass).
    ${source}=    Get Source
    ${source_lower}=    Convert To Lower Case    ${source}
    ${has_success}=    Set Variable    ${FALSE}
    FOR    ${marker}    IN    @{SUCCESS_MARKERS}
        ${found}=    Run Keyword And Return Status    Should Contain    ${source_lower}    ${marker}
        IF    ${found}
            ${has_success}=    Set Variable    ${TRUE}
        END
    END
    ${has_error}=    Run Keyword And Return Status    Should Contain    ${source_lower}    not available
    ${has_error_aji}=    Run Keyword And Return Status    Should Contain    ${source}    AJI
    ${has_error}=    Set Variable If    ${has_error}    ${TRUE}    ${has_error_aji}
    IF    ${has_success}
        RETURN    SAVED
    ELSE IF    ${has_error}
        RETURN    ENVIRONMENT_BLOCKED
    ELSE
        RETURN    NEXT_SCREEN_UNKNOWN
    END

Accept Terms And Conditions
    Wait Until Consent Screen Is Displayed
    Tap Consent Accept Button
