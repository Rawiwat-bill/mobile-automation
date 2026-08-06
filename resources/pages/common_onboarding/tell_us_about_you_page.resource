*** Settings ***
Library     String
Library     AppiumLibrary
Resource    ../../app/app_constants.resource
Resource    ../../keywords/dob_stability_keywords.resource
Resource    ../../keywords/utils/utility_keywords.resource
Resource    ../onboarding/profile_screen_page.resource
Resource    ../../../locators/android/common_onboarding/tell_us_about_you_locators.resource


*** Keywords ***
Wait Until Tell Us About You Screen Is Displayed
    [Documentation]    Wait until the "Tell us about you" screen is displayed
    Wait Until Element Is Visible    ${TELL_US_ABOUT_YOU_TITLE_TEXT}    timeout=${NCBD_LOADING_TIMEOUT}
    Wait Until Element Is Visible    ${TELL_US_ABOUT_YOU_CITIZEN_ID_CONTAINER}    timeout=${NCBD_LOADING_TIMEOUT}

Wait Until Fields Are Blurred
    [Documentation]    Wait until the fields are blurred (not focused)
    Wait Until Keyword Succeeds    5x    300ms    Fields Should Be Blurred

Fields Should Be Blurred
    [Documentation]    Verify that the fields are blurred (not focused)
    ${citizen_focused}=    Get Element Attribute    ${TELL_US_ABOUT_YOU_CID_INPUT}    focused
    ${dob_focused}=    Get Element Attribute    ${TELL_US_ABOUT_YOU_DOB_INPUT}    focused
    ${mobile_focused}=    Get Element Attribute    ${TELL_US_ABOUT_YOU_MOBILE_NUMBER_INPUT}    focused
    Should Be Equal As Strings    ${citizen_focused}    false
    Should Be Equal As Strings    ${dob_focused}    false
    Should Be Equal As Strings    ${mobile_focused}    false

Input Text And Hide Keyboard
    [Documentation]    Input text into a field and hide the keyboard
    [Arguments]    ${input_locator}    ${value}
    ${previous_log_level}=    Set Log Level    NONE
    Clear Text    ${input_locator}
    Input Text    ${input_locator}    ${value}
    Set Log Level    ${previous_log_level}
    Hide Keyboard Custom

Input Citizen ID
    [Documentation]    Input the citizen ID on the "Tell us about you" screen
    [Arguments]    ${citizen_id}

    Wait Until Element Is Visible    ${TELL_US_ABOUT_YOU_CITIZEN_ID_CONTAINER}    ${NCBD_LOADING_TIMEOUT}
    Click Element    ${TELL_US_ABOUT_YOU_CID_INPUT}
    Input Text And Hide Keyboard    ${TELL_US_ABOUT_YOU_CID_INPUT}    ${citizen_id}

Select Date Of Birth
    [Documentation]    Input the date of birth on the "Tell us about you" screen
    [Arguments]    ${date_of_birth}
    profile_screen_page.Input Date Of Birth    ${date_of_birth}
    Capture Date Of Birth Selection State

Capture Date Of Birth Selection State
    [Documentation]    Record only a masked selected-state marker before Next.
    Create File    ${OUTPUT DIR}/dob_selection_state.txt    selected=true
    Log    [DOB] Selected state captured before Next without recording the private value.

Input Mobile Number
    [Documentation]    Input the mobile number on the "Tell us about you" screen
    [Arguments]    ${mobile_number}

    Wait Until Element Is Visible    ${TELL_US_ABOUT_YOU_MOBILE_NUMBER_CONTAINER}    ${NCBD_LOADING_TIMEOUT}
    Click Element    ${TELL_US_ABOUT_YOU_MOBILE_NUMBER_INPUT}
    Input Text And Hide Keyboard    ${TELL_US_ABOUT_YOU_MOBILE_NUMBER_INPUT}    ${mobile_number}

Click Next Button
    [Documentation]    Click the "Next" button on the "Tell us about you" screen
    Wait Until Element Is Visible    ${TELL_US_ABOUT_YOU_BUTTON_NEXT}    ${NCBD_LOADING_TIMEOUT}
    Click Element    ${TELL_US_ABOUT_YOU_BUTTON_NEXT}
