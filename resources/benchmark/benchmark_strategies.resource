*** Settings ***
Library    AppiumLibrary
Library    Collections
Library    String
Resource   benchmark_base.resource
Resource   consent_scroll_strategies.resource


*** Keywords ***
# ─── Citizen ID Strategy Executors ─────────────────────────────────────────

Run Citizen ID Strategy
    [Arguments]    ${citizen_id}    ${strategy}
    Navigate To Profile
    Wait For Profile
    Tap Citizen ID Container
    Run Keyword    Run Citizen ID ${strategy}    ${citizen_id}
    Blur Citizen ID
    Log Benchmark Result    citizen_id    ${strategy}

Run Citizen ID input_text
    [Arguments]    ${citizen_id}
    Start Phase    strat_input_text
    Record Appium Action
    Input Text Into Current Element    ${citizen_id}
    End Phase

Run Citizen ID input_value
    [Arguments]    ${citizen_id}
    Start Phase    strat_input_value
    ${previous}=    Set Log Level    NONE
    Input Value    ${BENCHMARK_CITIZEN_INPUT}    ${citizen_id}
    Set Log Level    ${previous}
    Record Appium Action
    End Phase

Run Citizen ID press_keycodes
    [Arguments]    ${citizen_id}
    Start Phase    strat_keycodes
    Enter Digits By Keycodes    ${citizen_id}
    End Phase

Run Citizen ID adb_shell
    [Arguments]    ${citizen_id}
    Start Phase    strat_adb_shell
    Execute Adb Shell    input    text    ${citizen_id}
    Record ADB Call
    End Phase

Run Citizen ID execute_script
    [Arguments]    ${citizen_id}
    Start Phase    strat_execute_script
    Execute Script    document.querySelector('input').value='${citizen_id}'
    Record Appium Action
    End Phase


# ─── DOB Strategy Executors ─────────────────────────────────────────────

Run DOB Strategy
    [Arguments]    ${date_of_birth}    ${strategy}
    Navigate To Profile
    Wait For Profile
    ${previous_log}=    Set Log Level    NONE
    Tap Date Of Birth Container
    Set Log Level    ${previous_log}
    Run Keyword    Run DOB ${strategy}    ${date_of_birth}
    Blur DOB
    Log Benchmark Result    dob    ${strategy}

Run DOB picker_calculated
    [Arguments]    ${date_of_birth}
    Start Phase    strat_picker_calculated
    ${parts}=    Split String    ${date_of_birth}    -
    ${day}=    Set Variable    ${parts[2]}
    ${month_token}=    Set Variable    ${parts[1]}
    ${year}=    Set Variable    ${parts[0]}
    ${month}=    Get From Dictionary    ${MONTH_MAP}    ${month_token}
    Select Benchmark Picker Value    ${BENCHMARK_DOB_YEAR_PICKER}    ${year}    number
    Select Benchmark Picker Value    ${BENCHMARK_DOB_MONTH_PICKER}    ${month}    month
    Select Benchmark Picker Value    ${BENCHMARK_DOB_DAY_PICKER}    ${day}    number
    Click Element    ${BENCHMARK_DOB_CONFIRM}
    Record Appium Action
    End Phase

Run DOB input_text
    [Arguments]    ${date_of_birth}
    Start Phase    strat_input_text
    ${slash_date}=    Replace String    ${date_of_birth}    -    /
    ${previous}=    Set Log Level    NONE
    Clear Text    ${BENCHMARK_DOB_INPUT}
    Input Text    ${BENCHMARK_DOB_INPUT}    ${slash_date}
    Set Log Level    ${previous}
    Record Appium Action
    Record Appium Action
    End Phase

Run DOB adb_shell
    [Arguments]    ${date_of_birth}
    Start Phase    strat_adb_shell
    Execute Adb Shell    input    text    ${date_of_birth}
    Record ADB Call
    End Phase

Run DOB input_value
    [Arguments]    ${date_of_birth}
    Start Phase    strat_input_value
    ${previous}=    Set Log Level    NONE
    Input Value    ${BENCHMARK_DOB_INPUT}    ${date_of_birth}
    Set Log Level    ${previous}
    Record Appium Action
    End Phase


# ─── Mobile Number Strategy Executors ─────────────────────────────────────

Run Mobile Number Strategy
    [Arguments]    ${mobile_number}    ${strategy}
    Navigate To Profile
    Wait For Profile
    Tap Mobile Container
    Run Keyword    Run Mobile ${strategy}    ${mobile_number}
    Blur Mobile
    Log Benchmark Result    mobile_number    ${strategy}

Run Mobile input_text
    [Arguments]    ${mobile_number}
    Start Phase    strat_input_text
    Input Text Into Current Element    ${mobile_number}
    Record Appium Action
    End Phase

Run Mobile input_value
    [Arguments]    ${mobile_number}
    Start Phase    strat_input_value
    ${previous}=    Set Log Level    NONE
    Input Value    ${BENCHMARK_MOBILE_INPUT}    ${mobile_number}
    Set Log Level    ${previous}
    Record Appium Action
    End Phase

Run Mobile press_keycodes
    [Arguments]    ${mobile_number}
    Start Phase    strat_keycodes
    Enter Digits By Keycodes    ${mobile_number}
    End Phase

Run Mobile adb_shell
    [Arguments]    ${mobile_number}
    Start Phase    strat_adb_shell
    Execute Adb Shell    input    text    ${mobile_number}
    Record ADB Call
    End Phase

Run Mobile execute_script
    [Arguments]    ${mobile_number}
    Start Phase    strat_execute_script
    Execute Script    document.querySelector('input').value='${mobile_number}'
    Record Appium Action
    End Phase


# ─── Interaction Helpers ──────────────────────────────────────────────────

Tap Citizen ID Container
    Start Phase    tap_citizen_container
    Wait Until Element Is Visible    ${BENCHMARK_CITIZEN_CONTAINER}    10s
    Click Element    ${BENCHMARK_CITIZEN_CONTAINER}
    Record Appium Action
    End Phase

Tap Date Of Birth Container
    Start Phase    tap_dob_container
    Wait Until Element Is Visible    ${BENCHMARK_DOB_CONTAINER}    10s
    Click Element    ${BENCHMARK_DOB_CONTAINER}
    Record Appium Action
    End Phase

Tap Mobile Container
    Start Phase    tap_mobile_container
    Wait Until Element Is Visible    ${BENCHMARK_MOBILE_CONTAINER}    10s
    Click Element    ${BENCHMARK_MOBILE_CONTAINER}
    Record Appium Action
    End Phase

Blur Citizen ID
    Start Phase    blur_citizen
    Tap By Coordinates    540    ${BLUR_AFTER_CITIZEN_Y}
    Run Keyword And Ignore Error    Wait Until Keyword Succeeds    5x    300ms    Field Should Be Blurred    ${BENCHMARK_CITIZEN_INPUT}
    End Phase

Blur DOB
    Start Phase    blur_dob
    Tap By Coordinates    540    ${BLUR_AFTER_DOB_Y}
    Run Keyword And Ignore Error    Wait Until Keyword Succeeds    5x    300ms    Field Should Be Blurred    ${BENCHMARK_DOB_INPUT}
    End Phase

Blur Mobile
    Start Phase    blur_mobile
    Tap By Coordinates    540    ${BLUR_AFTER_MOBILE_Y}
    Run Keyword And Ignore Error    Wait Until Keyword Succeeds    5x    300ms    Field Should Be Blurred    ${BENCHMARK_MOBILE_INPUT}
    End Phase

Field Should Be Blurred
    [Arguments]    ${locator}
    ${focused}=    Get Element Attribute    ${locator}    focused
    Should Be Equal As Strings    ${focused}    false

Tap By Coordinates
    [Arguments]    ${x}    ${y}
    ${tap_point}=    Create List    ${x}    ${y}
    Tap    ${tap_point}
    Record Appium Action

Enter Digits By Keycodes
    [Arguments]    ${digits_text}
    ${digits}=    Evaluate    ''.join(ch for ch in """${digits_text}""" if ch.isdigit())
    ${keycodes}=    Evaluate    {'0': 7, '1': 8, '2': 9, '3': 10, '4': 11, '5': 12, '6': 13, '7': 14, '8': 15, '9': 16}
    ${digit_count}=    Get Length    ${digits}
    ${previous}=    Set Log Level    NONE
    FOR    ${index}    IN RANGE    ${digit_count}
        ${end_index}=    Evaluate    ${index} + 1
        ${digit}=    Get Substring    ${digits}    ${index}    ${end_index}
        ${keycode}=    Get From Dictionary    ${keycodes}    ${digit}
        Press Keycode    ${keycode}
        Record Appium Action
    END
    Set Log Level    ${previous}
    Record ADB Call

Select Benchmark Picker Value
    [Arguments]    ${picker_locator}    ${target_value}    ${value_kind}
    Wait Until Element Is Visible    ${picker_locator}    3s
    ${current_desc}=    Get Element Attribute    ${picker_locator}    content-desc
    ${current_value}=    Fetch From Right    ${current_desc}    ,
    ${current_value}=    Strip String    ${current_value}
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
    ${step_count}=    Evaluate    abs(int(${target_index}) - int(${current_index}))
    IF    ${step_count} == 0
        RETURN
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
        Record Appium Action
    END


# ─── Baseline Fillers (non-target fields use production baseline) ────────

Baseline Fill Citizen ID
    [Arguments]    ${citizen_id}
    Tap Citizen ID Container
    Enter Digits By Keycodes    ${citizen_id}
    Blur Citizen ID

Baseline Fill DOB
    [Arguments]    ${date_of_birth}
    Tap Date Of Birth Container
    ${parts}=    Split String    ${date_of_birth}    -
    ${day}=    Set Variable    ${parts[2]}
    ${month_token}=    Set Variable    ${parts[1]}
    ${year}=    Set Variable    ${parts[0]}
    ${month}=    Get From Dictionary    ${MONTH_MAP}    ${month_token}
    Select Benchmark Picker Value    ${BENCHMARK_DOB_YEAR_PICKER}    ${year}    number
    Select Benchmark Picker Value    ${BENCHMARK_DOB_MONTH_PICKER}    ${month}    month
    Select Benchmark Picker Value    ${BENCHMARK_DOB_DAY_PICKER}    ${day}    number
    Click Element    ${BENCHMARK_DOB_CONFIRM}
    Blur DOB

Baseline Fill Mobile
    [Arguments]    ${mobile_number}
    Tap Mobile Container
    Enter Digits By Keycodes    ${mobile_number}
    Blur Mobile
