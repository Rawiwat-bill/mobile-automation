*** Settings ***
Library     AppiumLibrary
Library     Collections
Library     String
Library     OperatingSystem
Resource    ../../../locators/android/onboarding/profile_screen_locators.resource
Resource    ../../keywords/dob_stability_keywords.resource
Resource    ../../app/app_constants.resource


*** Variables ***
${PROFILE_TIMEOUT}    10s
${DOB_PICKER_TIMEOUT}    3s
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
    Tap Profile Next Using Adb
    ${profile_closed}=    Run Keyword And Return Status    Wait Until Page Does Not Contain Element    ${PROFILE_TITLE_TEXT}    10s
    ${service_unavailable}=    Run Keyword And Return Status    Wait Until Page Contains Element    xpath=//*[@text="Service is not available now"]    10s
    ${navigated}=    Evaluate    ${profile_closed} or ${service_unavailable}
    IF    not ${navigated}
        Log    [PROFILE] Adb tap did not navigate, falling back to Appium tap
        Tap Profile Element Center    ${PROFILE_NEXT_BUTTON_CONTAINER}
        Log    [PROFILE] Next tapped via Appium
        ${profile_closed}=    Run Keyword And Return Status    Wait Until Page Does Not Contain Element    ${PROFILE_TITLE_TEXT}    10s
        ${service_unavailable}=    Run Keyword And Return Status    Wait Until Page Contains Element    xpath=//*[@text="Service is not available now"]    10s
        ${navigated}=    Evaluate    ${profile_closed} or ${service_unavailable}
    END
    Should Be True    ${navigated}    Profile screen did not navigate after Next tap.
    Log    [PROFILE] Screen after Next: profile_screen_closed

Tap Profile Next
    Tap Profile Next Button

Select DOB Picker Value
    [Arguments]    ${picker_locator}    ${target_value}    ${value_kind}
    Wait Until Element Is Visible    ${picker_locator}    ${DOB_PICKER_TIMEOUT}
    FOR    ${index}    IN RANGE    25
        ${current_value}=    Read DOB Picker Visible Value    ${picker_locator}
        IF    '${current_value}' == '${target_value}'
            RETURN
        END

        IF    '${value_kind}' == 'month'
            ${current_index}=    Get From Dictionary    ${MONTH_INDEXES}    ${current_value}
            ${target_index}=    Get From Dictionary    ${MONTH_INDEXES}    ${target_value}
        ELSE
            ${current_index}=    Convert To Integer    ${current_value}
            ${target_index}=    Convert To Integer    ${target_value}
        END

        ${direction}=    Set Variable If    ${current_index} < ${target_index}    up    down
        Record DOB Picker Attempt    ${value_kind}    ${target_value}    ${current_value}    ${direction}
        ${picker_rect}=    Get Element Rect    ${picker_locator}
        ${center_x}=    Evaluate    int(${picker_rect['x']} + (${picker_rect['width']} / 2))
        ${diff}=    Evaluate    abs(int(${current_index}) - int(${target_index}))
        IF    ${diff} <= 2
            ${top_y}=    Evaluate    int(${picker_rect['y']} + (${picker_rect['height']} * ${DOB_FINE_END_RATIO}))
            ${bottom_y}=    Evaluate    int(${picker_rect['y']} + (${picker_rect['height']} * ${DOB_FINE_START_RATIO}))
        ELSE
            ${top_y}=    Evaluate    int(${picker_rect['y']} + (${picker_rect['height']} * ${DOB_COARSE_END_RATIO}))
            ${bottom_y}=    Evaluate    int(${picker_rect['y']} + (${picker_rect['height']} * ${DOB_COARSE_START_RATIO}))
        END
        IF    '${direction}' == 'up'
            Execute Adb Shell    input    swipe    ${center_x}    ${bottom_y}    ${center_x}    ${top_y}    ${DOB_DRAG_DURATION}
        ELSE
            Execute Adb Shell    input    swipe    ${center_x}    ${top_y}    ${center_x}    ${bottom_y}    ${DOB_DRAG_DURATION}
        END
        Sleep    ${DOB_SETTLE_TIME}s
    END
    Record DOB Failure    ${value_kind}    ${target_value}    exhausted 25 attempts
    Capture DOB Failure Evidence    ${value_kind}    ${target_value}
    Fail    Could not select DOB picker value '${target_value}' using locator '${picker_locator}'.

Read DOB Picker Visible Value
    [Arguments]    ${picker_locator}
    Wait Until Element Is Visible    ${picker_locator}    ${DOB_PICKER_TIMEOUT}
    ${desc}=    Get Element Attribute    ${picker_locator}    content-desc
    ${desc_value}=    Set Variable    ${EMPTY}
    IF    '${desc}' != '' and '${desc}' != 'None'
        ${desc_value}=    Fetch From Right    ${desc}    ,
        ${desc_value}=    Strip String    ${desc_value}
        IF    '${desc_value}' != ''
            RETURN    ${desc_value}
        END
    END
    # Fallback: read the selected value from the center visible TextView in the picker wheel.
    # Structure: SeekBar > ViewGroup[0] > ScrollView(flatlist) > ViewGroup > ViewGroup[3] > TextView
    ${result_status}    ${center_text}=    Run Keyword And Ignore Error
    ...    Get Text    ${picker_locator}/android.view.ViewGroup/android.widget.ScrollView/android.view.ViewGroup/android.view.ViewGroup[3]/android.widget.TextView
    IF    '${result_status}' == 'PASS'
        ${value}=    Strip String    ${center_text}
        IF    '${value}' != ''
            RETURN    ${value}
        END
    END
    # Fallback: parse content-desc from SeekBar
    ${desc}=    Get Element Attribute    ${picker_locator}    content-desc
    ${value}=    Fetch From Right    ${desc}    ,
    ${value}=    Strip String    ${value}
    RETURN    ${value}
