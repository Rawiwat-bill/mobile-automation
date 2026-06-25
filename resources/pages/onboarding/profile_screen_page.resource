*** Settings ***
Library     AppiumLibrary
Library     Collections
Library     String
Library     OperatingSystem
Resource    ../../../locators/android/onboarding/profile_screen_locators.resource


*** Variables ***
${PROFILE_TIMEOUT}    10s
${DOB_PICKER_TIMEOUT}    3s
${DOB_TRY_DIRECT_INPUT}    ${FALSE}
${PROFILE_INVESTIGATION_DIR}    reports/investigation/profile
${PROFILE_DEBUG_PANEL_BUTTON}    xpath=//*[@content-desc="Open debug panel"]
${PROFILE_BLUR_AFTER_CITIZEN_Y}    780
${PROFILE_BLUR_AFTER_DOB_Y}    1095
${PROFILE_BLUR_AFTER_MOBILE_Y}    1600


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
    ${previous_log_level}=    Set Log Level    NONE
    Enter Digits By Keycodes    ${citizen_id}
    Set Log Level    ${previous_log_level}
    Tap Profile Blank Area    ${PROFILE_BLUR_AFTER_CITIZEN_Y}
    Wait Until Profile Fields Are Blurred

Tap Date Of Birth Field
    Wait Until Element Is Visible    ${PROFILE_DOB_INPUT}    ${PROFILE_TIMEOUT}
    Click Element                    ${PROFILE_DOB_INPUT}
    Log    [PROFILE] DOB field clicked

Input Date Of Birth
    [Arguments]    ${date_of_birth}
    ${dob_start}=    Evaluate    __import__('time').time()
    Log    [PROFILE] DOB start time: ${dob_start}
    Tap Profile Element Center    ${PROFILE_DOB_CONTAINER}
    Log    [PROFILE] DOB field clicked
    Log    [PROFILE] Date picker opened
    ${parts}=    Split String    ${date_of_birth}    -
    ${day}=    Set Variable    ${parts[0]}
    ${month_token}=    Set Variable    ${parts[1]}
    ${year}=    Set Variable    ${parts[2]}
    ${month_map}=    Evaluate    {'01': 'January', '02': 'February', '03': 'March', '04': 'April', '05': 'May', '06': 'June', '07': 'July', '08': 'August', '09': 'September', '10': 'October', '11': 'November', '12': 'December'}
    ${month}=    Set Variable    ${month_token}
    ${has_numeric_month}=    Run Keyword And Return Status    Dictionary Should Contain Key    ${month_map}    ${month_token}
    IF    ${has_numeric_month}
        ${month}=    Get From Dictionary    ${month_map}    ${month_token}
    END
    IF    ${DOB_TRY_DIRECT_INPUT}
        ${direct_strategy}=    Try Direct DOB Input    ${date_of_birth}
        IF    '${direct_strategy}' != ''
            ${dob_end}=    Evaluate    __import__('time').time()
            ${elapsed}=    Evaluate    round(${dob_end} - ${dob_start}, 2)
            Log    [PROFILE] DOB end time: ${dob_end}
            Log    [PROFILE] DOB strategy used: ${direct_strategy}
            Log    [PROFILE] DOB elapsed seconds: ${elapsed}
            RETURN
        END
    END
    ${year_start}=    Evaluate    __import__('time').time()
    Select DOB Picker Value    ${PROFILE_DOB_YEAR_PICKER}    ${year}    number
    ${year_end}=    Evaluate    __import__('time').time()
    ${year_elapsed}=    Evaluate    round(${year_end} - ${year_start}, 2)
    Log    [PROFILE] Year selected
    Log    [PROFILE] Year picker elapsed seconds: ${year_elapsed}
    ${month_start}=    Evaluate    __import__('time').time()
    Select DOB Picker Value    ${PROFILE_DOB_MONTH_PICKER}    ${month}    month
    ${month_end}=    Evaluate    __import__('time').time()
    ${month_elapsed}=    Evaluate    round(${month_end} - ${month_start}, 2)
    Log    [PROFILE] Month selected
    Log    [PROFILE] Month picker elapsed seconds: ${month_elapsed}
    ${day_start}=    Evaluate    __import__('time').time()
    Select DOB Picker Value    ${PROFILE_DOB_DAY_PICKER}    ${day}    number
    ${day_end}=    Evaluate    __import__('time').time()
    ${day_elapsed}=    Evaluate    round(${day_end} - ${day_start}, 2)
    Log    [PROFILE] Day selected
    Log    [PROFILE] Day picker elapsed seconds: ${day_elapsed}
    Click Element    ${PROFILE_DOB_CONFIRM_BUTTON}
    Log    [PROFILE] Date confirmed
    Tap Profile Blank Area    ${PROFILE_BLUR_AFTER_DOB_Y}
    Wait Until Profile Fields Are Blurred
    ${dob_end}=    Evaluate    __import__('time').time()
    ${elapsed}=    Evaluate    round(${dob_end} - ${dob_start}, 2)
    Log    [PROFILE] DOB end time: ${dob_end}
    Log    [PROFILE] DOB strategy used: picker_fallback
    Log    [PROFILE] DOB elapsed seconds: ${elapsed}

Input Mobile Number
    [Arguments]    ${mobile_number}
    Tap Profile Element Center    ${PROFILE_MOBILE_NUMBER_CONTAINER}
    Log    [PROFILE] Mobile focused
    ${native_status}=    Run Keyword And Return Status    Enter Mobile Number By Keycodes    ${mobile_number}
    Press Keycode    66
    Tap Profile Blank Area    ${PROFILE_BLUR_AFTER_MOBILE_Y}
    Run Keyword And Ignore Error    Hide Keyboard
    Wait Until Profile Fields Are Blurred
    ${native_populated}=    Run Keyword And Return Status    Wait Until Keyword Succeeds    5x    300ms    Mobile Number Field Should Be Populated    ${mobile_number}
    IF    ${native_status} and ${native_populated}
        Log    [PROFILE] Mobile entered via keyboard
        Log    [PROFILE] Keyboard dismissed
    ELSE
        ${previous_log_level}=    Set Log Level    NONE
        Clear Text    ${PROFILE_MOBILE_NUMBER_INPUT}
        Input Text Into Current Element    ${mobile_number}
        Set Log Level    ${previous_log_level}
        Press Keycode    66
        Tap Profile Blank Area    ${PROFILE_BLUR_AFTER_MOBILE_Y}
        Run Keyword And Ignore Error    Hide Keyboard
        Wait Until Profile Fields Are Blurred
        Wait Until Keyword Succeeds    5x    300ms    Mobile Number Field Should Be Populated    ${mobile_number}
        Log    [PROFILE] Mobile entered via fallback text input
        Log    [PROFILE] Keyboard dismissed
    END

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

Enter Digits By Keycodes
    [Arguments]    ${digits_text}
    ${digits}=    Evaluate    ''.join(ch for ch in """${digits_text}""" if ch.isdigit())
    ${keycodes}=    Evaluate    {'0': 7, '1': 8, '2': 9, '3': 10, '4': 11, '5': 12, '6': 13, '7': 14, '8': 15, '9': 16}
    ${digit_count}=    Get Length    ${digits}
    FOR    ${index}    IN RANGE    ${digit_count}
        ${end_index}=    Evaluate    ${index} + 1
        ${digit}=    Get Substring    ${digits}    ${index}    ${end_index}
        ${keycode}=    Get From Dictionary    ${keycodes}    ${digit}
        Press Keycode    ${keycode}
    END

Enter Mobile Number By Keycodes
    [Arguments]    ${mobile_number}
    Enter Digits By Keycodes    ${mobile_number}
    Press Keycode    66
    Mobile Number Field Should Be Populated    ${mobile_number}

Select DOB Picker Value
    [Arguments]    ${picker_locator}    ${target_value}    ${value_kind}
    ${month_indexes}=    Evaluate    {'January': 1, 'February': 2, 'March': 3, 'April': 4, 'May': 5, 'June': 6, 'July': 7, 'August': 8, 'September': 9, 'October': 10, 'November': 11, 'December': 12}
    ${calculated_selected}=    Select DOB Picker Value Calculated    ${picker_locator}    ${target_value}    ${value_kind}    ${month_indexes}
    IF    ${calculated_selected}
        RETURN
    END
    Wait Until Element Is Visible    ${picker_locator}    ${DOB_PICKER_TIMEOUT}
    FOR    ${index}    IN RANGE    25
        ${current_desc}=    Get Element Attribute    ${picker_locator}    content-desc
        ${current_value}=    Fetch From Right    ${current_desc}    ,
        ${current_value}=    Strip String    ${current_value}
        IF    '${current_value}' == '${target_value}'
            RETURN
        END

        IF    '${value_kind}' == 'month'
            ${current_index}=    Get From Dictionary    ${month_indexes}    ${current_value}
            ${target_index}=    Get From Dictionary    ${month_indexes}    ${target_value}
        ELSE
            ${current_index}=    Convert To Integer    ${current_value}
            ${target_index}=    Convert To Integer    ${target_value}
        END

        ${direction}=    Set Variable If    ${current_index} < ${target_index}    up    down
        ${picker_rect}=    Get Element Rect    ${picker_locator}
        ${center_x}=    Evaluate    int(${picker_rect['x']} + (${picker_rect['width']} / 2))
        ${top_y}=    Evaluate    int(${picker_rect['y']} + (${picker_rect['height']} * 0.30))
        ${bottom_y}=    Evaluate    int(${picker_rect['y']} + (${picker_rect['height']} * 0.70))
        IF    '${direction}' == 'up'
            Swipe    start_x=${center_x}    start_y=${bottom_y}    end_x=${center_x}    end_y=${top_y}    duration=100ms
        ELSE
            Swipe    start_x=${center_x}    start_y=${top_y}    end_x=${center_x}    end_y=${bottom_y}    duration=100ms
        END
    END
    Fail    Could not select DOB picker value '${target_value}' using locator '${picker_locator}'.

Select DOB Picker Value Calculated
    [Arguments]    ${picker_locator}    ${target_value}    ${value_kind}    ${month_indexes}
    Wait Until Element Is Visible    ${picker_locator}    ${DOB_PICKER_TIMEOUT}
    ${current_desc}=    Get Element Attribute    ${picker_locator}    content-desc
    ${current_value}=    Fetch From Right    ${current_desc}    ,
    ${current_value}=    Strip String    ${current_value}
    IF    '${current_value}' == '${target_value}'
        RETURN    ${TRUE}
    END

    IF    '${value_kind}' == 'month'
        ${current_index}=    Get From Dictionary    ${month_indexes}    ${current_value}
        ${target_index}=    Get From Dictionary    ${month_indexes}    ${target_value}
    ELSE
        ${current_index}=    Convert To Integer    ${current_value}
        ${target_index}=    Convert To Integer    ${target_value}
    END

    ${step_count}=    Evaluate    abs(int(${target_index}) - int(${current_index}))
    IF    ${step_count} == 0
        RETURN    ${TRUE}
    END

    ${direction}=    Set Variable If    ${current_index} < ${target_index}    up    down
    ${picker_rect}=    Get Element Rect    ${picker_locator}
    ${center_x}=    Evaluate    int(${picker_rect['x']} + (${picker_rect['width']} / 2))
    ${top_y}=    Evaluate    int(${picker_rect['y']} + (${picker_rect['height']} * 0.30))
    ${bottom_y}=    Evaluate    int(${picker_rect['y']} + (${picker_rect['height']} * 0.70))
    FOR    ${index}    IN RANGE    ${step_count}
        IF    '${direction}' == 'up'
            Swipe    start_x=${center_x}    start_y=${bottom_y}    end_x=${center_x}    end_y=${top_y}    duration=50ms
        ELSE
            Swipe    start_x=${center_x}    start_y=${top_y}    end_x=${center_x}    end_y=${bottom_y}    duration=50ms
        END
    END

    ${final_desc}=    Get Element Attribute    ${picker_locator}    content-desc
    ${final_value}=    Fetch From Right    ${final_desc}    ,
    ${final_value}=    Strip String    ${final_value}
    IF    '${final_value}' == '${target_value}'
        RETURN    ${TRUE}
    END
    RETURN    ${FALSE}

Select DOB Picker Value Direct
    [Arguments]    ${picker_locator}    ${target_value}
    ${selected}=    Run Keyword And Return Status
    ...    Picker Wheel Should Show Value
    ...    ${picker_locator}
    ...    content-desc
    ...    ${target_value}
    RETURN    ${selected}

Picker Wheel Should Show Value
    [Arguments]    ${picker_locator}    ${_attribute}    ${target_value}
    ${current_desc}=    Get Element Attribute    ${picker_locator}    content-desc
    Should Contain    ${current_desc}    ${target_value}

Try Direct DOB Input
    [Arguments]    ${date_of_birth}
    ${parts}=    Split String    ${date_of_birth}    -
    ${day}=    Set Variable    ${parts[0]}
    ${month}=    Set Variable    ${parts[1]}
    ${year}=    Set Variable    ${parts[2]}
    ${slash_date}=    Replace String    ${date_of_birth}    -    /
    @{candidates}=    Create List    ${slash_date}    ${date_of_birth}
    FOR    ${candidate}    IN    @{candidates}
        ${previous_log_level}=    Set Log Level    NONE
        ${clear_status}=    Run Keyword And Return Status    Clear Text    ${PROFILE_DOB_INPUT}
        ${input_text_status}=    Run Keyword And Return Status    Input Text    ${PROFILE_DOB_INPUT}    ${candidate}
        Set Log Level    ${previous_log_level}
        IF    ${input_text_status}
            ${verified}=    Run Keyword And Return Status    DOB Field Should Contain Date    ${day}    ${month}    ${year}
            Run Keyword And Ignore Error    Hide Keyboard
            IF    ${verified}
                Log    [PROFILE] DOB direct input strategy: Input Text
                Run Keyword And Ignore Error    Click Element    ${PROFILE_DOB_CONFIRM_BUTTON}
                RETURN    direct_input_text
            END
        END
        ${previous_log_level}=    Set Log Level    NONE
        ${shell_status}=    Run Keyword And Return Status    Execute Adb Shell    input    text    ${candidate}
        Set Log Level    ${previous_log_level}
        IF    ${shell_status}
            ${verified}=    Run Keyword And Return Status    DOB Field Should Contain Date    ${day}    ${month}    ${year}
            Run Keyword And Ignore Error    Hide Keyboard
            IF    ${verified}
                Log    [PROFILE] DOB direct input strategy: adb shell input text
                Run Keyword And Ignore Error    Click Element    ${PROFILE_DOB_CONFIRM_BUTTON}
                RETURN    direct_input_shell
            END
        END
    END
    Run Keyword And Ignore Error    Hide Keyboard
    RETURN    ${EMPTY}

DOB Field Should Contain Date
    [Arguments]    ${day}    ${month}    ${year}
    ${field_text}=    Get Element Attribute    ${PROFILE_DOB_INPUT}    text
    ${field_desc}=    Get Element Attribute    ${PROFILE_DOB_INPUT}    content-desc
    ${combined}=    Catenate    SEPARATOR= |    ${field_text}    ${field_desc}
    Should Contain    ${combined}    ${day}
    Should Contain    ${combined}    ${month}
    Should Contain    ${combined}    ${year}

Mobile Number Field Should Be Populated
    [Arguments]    ${mobile_number}
    ${field_text}=    Get Element Attribute    ${PROFILE_MOBILE_NUMBER_INPUT}    text
    ${field_desc}=    Get Element Attribute    ${PROFILE_MOBILE_NUMBER_INPUT}    content-desc
    ${combined}=    Catenate    SEPARATOR= |    ${field_text}    ${field_desc}
    ${normalized_field}=    Replace String Using Regexp    ${combined}    [^0-9]    ${EMPTY}
    ${normalized_mobile}=    Replace String Using Regexp    ${mobile_number}    [^0-9]    ${EMPTY}
    Should Contain    ${normalized_field}    ${normalized_mobile}
