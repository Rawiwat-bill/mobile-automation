*** Settings ***
Documentation    Profile screen field interactions shared by onboarding flows.
Library          AppiumLibrary
Library          String
Resource         ../../../locators/android/onboarding/profile_screen_locators.resource
Resource         ../../app/app_constants.resource
Resource         ../../keywords/appium_expectations.resource


*** Variables ***
${PROFILE_TIMEOUT}    10s


*** Keywords ***
Wait Until Profile Screen Is Displayed
    Wait Until Element Is Visible    ${PROFILE_TITLE_TEXT}    30s
    Wait Until Element Is Visible    ${PROFILE_CITIZEN_ID_INPUT}    ${PROFILE_TIMEOUT}
    ${source}=    Get Source
    Should Contain    ${source}    cid-container    PROFILE_SCREEN_SOURCE_MARKER_MISSING
    Should Contain    ${source}    screenProfile_buttonNext    PROFILE_SCREEN_SOURCE_MARKER_MISSING

Tap Profile Element Center
    [Arguments]    ${element_locator}
    Wait Until Element Is Visible    ${element_locator}    ${PROFILE_TIMEOUT}
    ${element_rect}=    Get Element Rect    ${element_locator}
    ${center_x}=    Evaluate    int(${element_rect['x']} + (${element_rect['width']} / 2))
    ${center_y}=    Evaluate    int(${element_rect['y']} + (${element_rect['height']} / 2))
    ${tap_point}=    Create List    ${center_x}    ${center_y}
    Tap    ${tap_point}

Tap Profile Blank Area
    [Arguments]    ${blank_y}
    ${tap_point}=    Create List    540    ${blank_y}
    Tap    ${tap_point}

Tap Profile Focus Dismissal Target
    [Documentation]    Dismiss field focus without a blind keyboard-back action that can leave Profile when the keyboard is already hidden.
    [Arguments]    ${blank_y}
    ${profile_status}    ${profile_message}=    Run Keyword And Ignore Error
    ...    Wait Until Element Is Visible    ${PROFILE_TITLE_TEXT}    5s
    Should Be Equal    ${profile_status}    PASS    PROFILE_DISAPPEARED_BEFORE_FOCUS_DISMISSAL
    ${title_rect}=    Get Element Rect    ${PROFILE_TITLE_TEXT}
    ${center_x}=    Evaluate    int(${title_rect['x']} + (${title_rect['width']} / 2))
    ${center_y}=    Evaluate    int(${title_rect['y']} + (${title_rect['height']} / 2))
    ${tap_point}=    Create List    ${center_x}    ${center_y}
    Tap    ${tap_point}
    ${keyboard_status}    ${keyboard_shown}=    Run Keyword And Ignore Error    Is Keyboard Shown
    IF    '${keyboard_status}' == 'PASS' and ${keyboard_shown}
        Run Keyword And Ignore Error    Hide Keyboard
    END
    ${profile_still_visible}=    Run Keyword And Return Status    Element Should Be Visible Now    ${PROFILE_TITLE_TEXT}
    Should Be True    ${profile_still_visible}    PROFILE_DISAPPEARED_AFTER_FOCUS_DISMISSAL

Wait Until Profile Fields Are Blurred
    Wait Until Keyword Succeeds    5x    300ms    Profile Fields Should Be Blurred

Profile Fields Should Be Blurred
    ${citizen_focused}=    Get Element Attribute    ${PROFILE_CITIZEN_ID_INPUT}    focused
    ${dob_focused}=    Get Element Attribute    ${PROFILE_DOB_INPUT}    focused
    ${mobile_focused}=    Get Element Attribute    ${PROFILE_MOBILE_NUMBER_INPUT}    focused
    Should Be Equal As Strings    ${citizen_focused}    false
    Should Be Equal As Strings    ${dob_focused}    false
    Should Be Equal As Strings    ${mobile_focused}    false

Input Citizen ID
    [Arguments]    ${citizen_id}
    Tap Profile Element Center    ${PROFILE_CITIZEN_ID_CONTAINER}
    ${displayed}=    Input Text Field    ${PROFILE_CITIZEN_ID_INPUT}    ${citizen_id}
    Tap Profile Focus Dismissal Target    ${BLUR_AFTER_CITIZEN_Y}
    Wait Until Profile Fields Are Blurred
    Verify Field Value    Citizen ID    ${displayed}    ${citizen_id}

Read Current Profile Field Value
    [Arguments]    ${locator}    ${field_label}
    Wait Until Element Is Visible    ${locator}    ${PROFILE_TIMEOUT}
    ${text_status}    ${text}=    Run Keyword And Ignore Error    Get Text    ${locator}
    IF    '${text_status}' != 'PASS'
        Fail    PROFILE_${field_label}_READ_FAILED
    END
    ${normalized_text}=    Normalize Digits    ${text}
    IF    '${normalized_text}' == ''
        ${value_status}    ${value}=    Run Keyword And Ignore Error
        ...    Get Element Attribute    ${locator}    value
        IF    '${value_status}' != 'PASS'
            Fail    PROFILE_${field_label}_READ_FAILED
        END
        ${normalized_value}=    Normalize Digits    ${value}
        IF    '${normalized_value}' == ''
            Fail    PROFILE_${field_label}_READ_EMPTY
        END
        RETURN    ${value}
    END
    RETURN    ${text}

Verify Current Profile Fields Before Next
    [Arguments]    ${citizen_id}    ${date_of_birth}    ${mobile_number}
    Wait Until Profile Screen Is Displayed
    Wait Until Profile Fields Are Blurred
    ${current_citizen_id}=    Read Current Profile Field Value
    ...    ${PROFILE_CITIZEN_ID_INPUT}    CITIZEN_ID
    Verify Field Value    Citizen ID    ${current_citizen_id}    ${citizen_id}
    ${current_mobile}=    Read Current Profile Field Value
    ...    ${PROFILE_MOBILE_NUMBER_INPUT}    MOBILE
    Verify Field Value    Mobile    ${current_mobile}    ${mobile_number}
    ${parts}=    Split String    ${date_of_birth}    -
    ${expected_day}=    Set Variable    ${parts}[0]
    ${expected_month}=    Set Variable    ${parts}[1]
    ${expected_year}=    Set Variable    ${parts}[2]
    Verify DOB Field Value    ${expected_day}    ${expected_month}    ${expected_year}
    Log    [PROFILE] current visible CID/mobile/DOB verified immediately before Next with masked values.

# ─── TextInput Engine ────────────────────────────────────────────────────

Normalize Digits
    [Arguments]    ${text}
    ${normalized}=    Replace String Using Regexp    ${text}    [^0-9]    ${EMPTY}
    RETURN    ${normalized}

Input Text Field
    [Arguments]    ${input_locator}    ${value}
    ${previous_log_level}=    Set Log Level    NONE
    Clear Text    ${input_locator}
    Input Text    ${input_locator}    ${value}
    ${displayed}=    Get Text    ${input_locator}
    Set Log Level    ${previous_log_level}
    RETURN    ${displayed}

Verify Field Value
    [Arguments]    ${field_label}    ${actual_displayed}    ${expected_raw}
    ${normalized_actual}=    Normalize Digits    ${actual_displayed}
    ${normalized_expected}=    Normalize Digits    ${expected_raw}
    Should Be Equal As Strings    ${normalized_actual}    ${normalized_expected}
    ...    ${field_label} value mismatch.
    Log    [PROFILE] ${field_label} verified with masked value.

# ─── Verification Engine ─────────────────────────────────────────────────

Input Mobile Number
    [Arguments]    ${mobile_number}
    Tap Profile Element Center    ${PROFILE_MOBILE_NUMBER_CONTAINER}
    ${displayed}=    Input Text Field    ${PROFILE_MOBILE_NUMBER_INPUT}    ${mobile_number}
    Tap Profile Focus Dismissal Target    ${BLUR_AFTER_MOBILE_Y}
    Run Keyword And Ignore Error    Hide Keyboard
    Wait Until Profile Fields Are Blurred
    Verify Field Value    Mobile    ${displayed}    ${mobile_number}
