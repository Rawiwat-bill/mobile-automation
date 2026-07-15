*** Settings ***
Library     AppiumLibrary
Library     Process
Library     String
Resource    ../../../locators/android/onboarding/dopa_information_locators.resource
Resource    ../../../resources/app/app_constants.resource
Resource    profile_screen_page.resource


*** Variables ***
${DOPA_INFORMATION_TIMEOUT}    35s
${DOPA_FIELD_TIMEOUT}          10s


*** Keywords ***
Wait Until DOPA Information Screen Is Displayed
    Wait Until Page Contains Element    ${DOPA_INFORMATION_SCREEN}    ${DOPA_INFORMATION_TIMEOUT}
    Log    [DOPA] DOPA information screen visible

Tap DOPA Element Center
    [Arguments]    ${locator}
    Wait Until Page Contains Element    ${locator}    ${DOPA_FIELD_TIMEOUT}
    ${rect}=    Get Element Rect    ${locator}
    ${cx}=    Evaluate    int(${rect['x']} + (${rect['width']} / 2))
    ${cy}=    Evaluate    int(${rect['y']} + (${rect['height']} / 2))
    ${tap_point}=    Create List    ${cx}    ${cy}
    Tap    ${tap_point}

Scroll DOPA Down
    ${width}=    Get Window Width
    ${height}=    Get Window Height
    ${cx}=    Evaluate    int(${width} * 0.5)
    ${sy}=    Evaluate    int(${height} * 0.5)
    ${ey}=    Evaluate    int(${height} * 0.29)
    Execute Adb Shell    input    swipe    ${cx}    ${sy}    ${cx}    ${ey}    200

Scroll DOPA To Top
    ${width}=    Get Window Width
    ${height}=    Get Window Height
    ${cx}=    Evaluate    int(${width} * 0.5)
    ${sy}=    Evaluate    int(${height} * 0.21)
    ${ey}=    Evaluate    int(${height} * 0.75)
    FOR    ${i}    IN RANGE    3
        Execute Adb Shell    input    swipe    ${cx}    ${sy}    ${cx}    ${ey}    200
        Sleep    0.1s
    END

Fill DOPA English Names
    [Arguments]    ${first_name}    ${last_name}
    Input Text    ${DOPA_FIRST_NAME_ENG_INPUT}    ${first_name}
    Log    [DOPA] English first name entered: ${first_name}    WARN
    Run Keyword And Ignore Error    Hide Keyboard
    Scroll DOPA Down
    ${last_found}=    Run Keyword And Return Status    Wait Until Page Contains Element    ${DOPA_LAST_NAME_ENG_INPUT}    5s
    IF    ${last_found}
        Input Text    ${DOPA_LAST_NAME_ENG_INPUT}    ${last_name}
        Log    [DOPA] English last name entered: ${last_name}    WARN
        Run Keyword And Ignore Error    Hide Keyboard
    ELSE
        Log    [DOPA] English last name field not found after scroll    WARN
    END

Set DOPA Date Via Picker
    [Arguments]    ${field_locator}    ${day}    ${month_name}    ${year}
    Scroll DOPA Down
    ${found}=    Run Keyword And Return Status    Wait Until Page Contains Element    ${field_locator}    5s
    IF    not ${found}
        Scroll DOPA Down
        ${found}=    Run Keyword And Return Status    Wait Until Page Contains Element    ${field_locator}    5s
    END
    IF    ${found}
        Click Element    ${field_locator}
        ${picker_open}=    Run Keyword And Return Status    Wait Until Page Contains Element    ${DOPA_DATE_PICKER_YEAR}    5s
        IF    ${picker_open}
            DOPA Scroll Picker To Value    ${DOPA_DATE_PICKER_YEAR}    ${year}    number
            DOPA Scroll Picker To Value    ${DOPA_DATE_PICKER_MONTH}    ${month_name}    month
            DOPA Scroll Picker To Value    ${DOPA_DATE_PICKER_DAY}    ${day}    number
            Click Element    ${DOPA_DATE_PICKER_CONFIRM}
            Run Keyword And Return Status    Wait Until Page Does Not Contain Element    ${DOPA_DATE_PICKER_YEAR}    3s
            Log    [DOPA] Date set: ${day} ${month_name} ${year}    WARN
        ELSE
            Log    [DOPA] Date picker did not open    WARN
        END
    ELSE
        Log    [DOPA] Date field not found: ${field_locator}    WARN
    END

DOPA Scroll Picker To Value
    [Arguments]    ${picker_locator}    ${target_value}    ${value_kind}
    FOR    ${i}    IN RANGE    25
        ${cd}=    Get Element Attribute    ${picker_locator}    content-desc
        ${current}=    Fetch From Right    ${cd}    ,
        ${current}=    Strip String    ${current}
        IF    '${current}' == '${target_value}'
            RETURN
        END
        ${rect}=    Get Element Rect    ${picker_locator}
        ${cx}=    Evaluate    int(${rect['x']} + (${rect['width']} / 2))
        IF    '${value_kind}' == 'month'
            ${cur_idx}=    Get From Dictionary    ${MONTH_INDEXES}    ${current}
            ${tgt_idx}=    Get From Dictionary    ${MONTH_INDEXES}    ${target_value}
        ELSE
            ${cur_idx}=    Convert To Integer    ${current}
            ${tgt_idx}=    Convert To Integer    ${target_value}
        END
        ${diff}=    Evaluate    abs(int(${cur_idx}) - int(${tgt_idx}))
        IF    ${diff} <= 2
            ${top_y}=    Evaluate    int(${rect['y']} + (${rect['height']} * ${DOB_FINE_END_RATIO}))
            ${bot_y}=    Evaluate    int(${rect['y']} + (${rect['height']} * ${DOB_FINE_START_RATIO}))
        ELSE
            ${top_y}=    Evaluate    int(${rect['y']} + (${rect['height']} * ${DOB_COARSE_END_RATIO}))
            ${bot_y}=    Evaluate    int(${rect['y']} + (${rect['height']} * ${DOB_COARSE_START_RATIO}))
        END
        IF    ${cur_idx} < ${tgt_idx}
            Execute Adb Shell    input    swipe    ${cx}    ${bot_y}    ${cx}    ${top_y}    ${DOB_DRAG_DURATION}
        ELSE
            Execute Adb Shell    input    swipe    ${cx}    ${top_y}    ${cx}    ${bot_y}    ${DOB_DRAG_DURATION}
        END
        Sleep    ${DOB_SETTLE_TIME}s
    END

Tap DOPA Next
    Run Keyword And Ignore Error    Hide Keyboard
    Sleep    0.2s
    Scroll DOPA To Top
    ${nav}=    Set Variable    ${FALSE}
    ${by_acc}=    Run Keyword And Return Status    Wait Until Page Contains Element    accessibility_id=Next    3s
    IF    ${by_acc} and not ${nav}
        Click Element    accessibility_id=Next
        ${nav}=    Run Keyword And Return Status    Wait Until Page Does Not Contain Element    ${DOPA_INFORMATION_SCREEN}    10s
        Log    [DOPA] Next via accessibility_id: navigated=${nav}    WARN
    END
    IF    not ${nav}
        ${btn}=    Run Keyword And Return Status    Wait Until Page Contains Element    ${DOPA_NEXT_BUTTON_CONTAINER}    3s
        IF    ${btn}
            ${rect}=    Get Element Rect    ${DOPA_NEXT_BUTTON_CONTAINER}
            ${cx}=    Evaluate    int(${rect['x']} + (${rect['width']} / 2))
            ${cy}=    Evaluate    int(${rect['y']} + (${rect['height']} / 2))
            Execute Adb Shell    input    tap    ${cx}    ${cy}
            ${nav}=    Run Keyword And Return Status    Wait Until Page Does Not Contain Element    ${DOPA_INFORMATION_SCREEN}    10s
            Log    [DOPA] Next via adb tap: navigated=${nav}    WARN
        END
    END
    RETURN    ${nav}

Fill DOPA Laser Code
    [Arguments]    ${part1}    ${part2}    ${part3}
    Scroll DOPA Down
    Scroll DOPA Down
    ${p1}=    Run Keyword And Return Status    Wait Until Page Contains Element    xpath=//*[@text="${part1}"]    5s
    IF    ${p1}
        Input Text    xpath=//*[@text="${part1}"]    ${part1}
        Log    [DOPA] Laser part1 filled: ${part1}    WARN
    END
    ${p2}=    Run Keyword And Return Status    Wait Until Page Contains Element    xpath=//*[@text="${part2}"]    5s
    IF    ${p2}
        Input Text    xpath=//*[@text="${part2}"]    ${part2}
        Log    [DOPA] Laser part2 filled: ${part2}    WARN
    END
    ${p3}=    Run Keyword And Return Status    Wait Until Page Contains Element    xpath=//*[@text="${part3}"]    5s
    IF    ${p3}
        Input Text    xpath=//*[@text="${part3}"]    ${part3}
        Log    [DOPA] Laser part3 filled: ${part3}    WARN
    END
    Run Keyword And Ignore Error    Hide Keyboard
