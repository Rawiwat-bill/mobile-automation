*** Settings ***
Library     AppiumLibrary
Library     Collections
Library     String
Library     OperatingSystem
Resource    ../../../locators/android/onboarding/profile_screen_locators.resource
Resource    ../../keywords/dob_stability_keywords.resource
Resource    ../../keywords/android_wheel_picker.resource
Resource    ../../app/app_constants.resource


*** Variables ***
${PROFILE_TIMEOUT}    10s
${PROFILE_INVESTIGATION_DIR}    reports/investigation/profile
${PROFILE_DEBUG_PANEL_BUTTON}    xpath=//*[@content-desc="Open debug panel"]


*** Keywords ***
Wait Until Profile Screen Is Displayed
    Wait Until Element Is Visible    ${PROFILE_TITLE_TEXT}    30s
    Wait Until Element Is Visible    ${PROFILE_CITIZEN_ID_INPUT}    ${PROFILE_TIMEOUT}

Capture Profile Handoff Snapshot
    [Arguments]    ${snapshot_name}
    Create Directory    ${PROFILE_INVESTIGATION_DIR}
    ${screenshot_path}=    Set Variable    ${PROFILE_INVESTIGATION_DIR}/${snapshot_name}.png
    ${source_path}=    Set Variable    ${PROFILE_INVESTIGATION_DIR}/${snapshot_name}.xml
    Capture Page Screenshot    ${screenshot_path}
    ${page_source}=    Get Source
    Create File    ${source_path}    ${page_source}    UTF-8
    Log    [PROFILE] Captured investigation snapshot: ${snapshot_name}

Capture Profile Debug Panel Evidence
    [Arguments]    ${snapshot_name}
    Wait Until Element Is Visible    ${PROFILE_DEBUG_PANEL_BUTTON}    ${PROFILE_TIMEOUT}
    Click Element    ${PROFILE_DEBUG_PANEL_BUTTON}
    Capture Profile Handoff Snapshot    ${snapshot_name}

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
    Tap Profile Blank Area    ${BLUR_AFTER_CITIZEN_Y}
    Wait Until Profile Fields Are Blurred
    Verify Field Value    Citizen ID    ${displayed}    ${citizen_id}

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

Verify DOB Field Value
    [Arguments]    ${day}    ${year}
    ${field_text}=    Get Text    ${PROFILE_DOB_INPUT}
    ${field_digits}=    Normalize Digits    ${field_text}
    ${expected_digits}=    Set Variable    ${day}${year}
    Should Contain    ${field_digits}    ${expected_digits}
    ...    DOB field value mismatch.
    Log    [PROFILE] DOB field verified with masked value.

Tap Date Of Birth Field
    Wait Until Element Is Visible    ${PROFILE_DOB_INPUT}    ${PROFILE_TIMEOUT}
    Click Element                    ${PROFILE_DOB_INPUT}
    Log    [PROFILE] DOB field clicked

Input Date Of Birth
    [Arguments]    ${date_of_birth}
    Start DOB Interaction
    ${parts}=    Split String    ${date_of_birth}    -
    ${day}=    Set Variable    ${parts[0]}
    ${month_token}=    Set Variable    ${parts[1]}
    ${year}=    Set Variable    ${parts[2]}
    ${month}=    Set Variable    ${month_token}
    ${has_numeric_month}=    Run Keyword And Return Status    Dictionary Should Contain Key    ${MONTH_MAP}    ${month_token}
    IF    ${has_numeric_month}
        ${month}=    Get From Dictionary    ${MONTH_MAP}    ${month_token}
    END
    Tap Profile Element Center    ${PROFILE_DOB_CONTAINER}
    Record DOB Picker Visible
    Record DOB Year Start
    TRY
        Select DOB Picker Value    ${PROFILE_DOB_YEAR_PICKER}    ${year}    number
    EXCEPT    AS    ${error}
        Record DOB Failure    year    ${year}    ${error}
        Capture DOB Failure Evidence    year    ${year}
        Fail    ${error}
    END
    Record DOB Year End
    Record DOB Month Start
    TRY
        Select DOB Picker Value    ${PROFILE_DOB_MONTH_PICKER}    ${month}    month
    EXCEPT    AS    ${error}
        Record DOB Failure    month    ${month}    ${error}
        Capture DOB Failure Evidence    month    ${month}
        Fail    ${error}
    END
    Record DOB Month End
    Record DOB Day Start
    TRY
        Select DOB Picker Value    ${PROFILE_DOB_DAY_PICKER}    ${day}    number
    EXCEPT    AS    ${error}
        Record DOB Failure    day    ${day}    ${error}
        Capture DOB Failure Evidence    day    ${day}
        Fail    ${error}
    END
    Record DOB Day End
    Click Element    ${PROFILE_DOB_CONFIRM_BUTTON}
    Tap Profile Blank Area    ${BLUR_AFTER_DOB_Y}
    Wait Until Profile Fields Are Blurred
    Record DOB Success
    Verify DOB Field Value    ${day}    ${year}

Input Mobile Number
    [Arguments]    ${mobile_number}
    Tap Profile Element Center    ${PROFILE_MOBILE_NUMBER_CONTAINER}
    ${displayed}=    Input Text Field    ${PROFILE_MOBILE_NUMBER_INPUT}    ${mobile_number}
    Tap Profile Blank Area    ${BLUR_AFTER_MOBILE_Y}
    Run Keyword And Ignore Error    Hide Keyboard
    Wait Until Profile Fields Are Blurred
    Verify Field Value    Mobile    ${displayed}    ${mobile_number}

Tap Profile Next Using Adb
    ${element_rect}=    Get Element Rect    ${PROFILE_NEXT_BUTTON_CONTAINER}
    ${center_x}=    Evaluate    int(${element_rect['x']} + (${element_rect['width']} / 2))
    ${center_y}=    Evaluate    int(${element_rect['y']} + (${element_rect['height']} / 2))
    Execute Adb Shell    input    tap    ${center_x}    ${center_y}
    Log    [PROFILE] Next tapped via adb shell at ${center_x},${center_y}

Tap Profile Next Button
    Log    [PROFILE] Profile fields completed
    Run Keyword And Ignore Error    Hide Keyboard
    Log    [PROFILE] Keyboard hidden
    Wait Until Profile Fields Are Blurred
    Wait Until Element Is Visible    ${PROFILE_NEXT_BUTTON_CONTAINER}    ${PROFILE_TIMEOUT}
    ${next_visible}=    Run Keyword And Return Status    Element Should Be Visible    ${PROFILE_NEXT_BUTTON_CONTAINER}
    ${next_enabled}=    Run Keyword And Return Status    Element Should Be Enabled    ${PROFILE_NEXT_BUTTON_CONTAINER}
    Log    [PROFILE] Next visible/enabled: ${next_visible}/${next_enabled}
    ${source_before_next}=    Get Source
    Tap Profile Next Using Adb
    ${transition_result}=    Wait Until Keyword Succeeds    10s    500ms
    ...    Observe Profile Next Transition    ${source_before_next}
    RETURN    ${transition_result}

Observe Profile Next Transition
    [Arguments]    ${source_before_next}
    ${profile_visible}=    Run Keyword And Return Status    Element Should Be Visible    ${PROFILE_TITLE_TEXT}
    ${service_unavailable}=    Run Keyword And Return Status
    ...    Page Should Contain Element    xpath=//*[@text="Service is not available now"]
    IF    ${service_unavailable}
        RETURN    SERVICE_ERROR_VISIBLE
    END
    IF    not ${profile_visible}
        RETURN    PROFILE_LEFT_OR_NEXT_STATE_VISIBLE
    END
    ${source_after_next}=    Get Source
    ${source_changed}=    Evaluate    $source_after_next != $source_before_next
    IF    ${source_changed}
        ${loading_visible}=    Run Keyword And Return Status
        ...    Should Contain    ${source_after_next}    android.widget.ImageView
        IF    not ${loading_visible}
            RETURN    PROFILE_LEFT_OR_NEXT_STATE_VISIBLE
        END
    END
    Fail    PROFILE_NEXT_LOADING_TIMEOUT

Tap Profile Next
    Tap Profile Next Button

Select DOB Picker Value
    [Arguments]    ${picker_locator}    ${target_value}    ${value_kind}
    Select Android Wheel Picker Value    ${picker_locator}    ${target_value}    ${value_kind}
