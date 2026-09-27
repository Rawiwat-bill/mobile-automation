*** Settings ***
Library     AppiumLibrary
Library     Process
Library     String
Library     OperatingSystem
Resource    ../../../locators/android/onboarding/dopa_information_locators.resource
Resource    ../../keywords/android_wheel_picker.resource
Resource    ../../diagnostics/etb_observability.resource


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
    # adb input tap (OS-level touch) -- the proven RN interaction for DOPA controls
    # Appium Click/Tap intermittently fails to open RN fields; use the configured ADB fallback.
    Execute Adb Shell    input    tap    ${cx}    ${cy}

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
        Wait Until Page Contains Element    ${field_locator}    5s
    END
    Tap DOPA Element Center    ${field_locator}
    ${picker_open}=    Run Keyword And Return Status    Wait Until Page Contains Element    ${DOPA_DATE_PICKER_YEAR}    5s
    IF    ${picker_open}
        DOPA Scroll Picker To Value    ${DOPA_DATE_PICKER_YEAR}    ${year}    number
        DOPA Scroll Picker To Value    ${DOPA_DATE_PICKER_MONTH}    ${month_name}    month
        DOPA Scroll Picker To Value    ${DOPA_DATE_PICKER_DAY}    ${day}    number
        Click Element    ${DOPA_DATE_PICKER_CONFIRM}
        Run Keyword And Return Status    Wait Until Page Does Not Contain Element    ${DOPA_DATE_PICKER_YEAR}    3s
        Log    [DOPA] Date set using the proven DOPA wheel interaction.
    ELSE
        Log    [DOPA] Date picker did not open    WARN
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
    Fail    DOPA wheel picker did not reach the expected value.

DOPA Date Field Should Match
    [Arguments]    ${field_locator}    ${day}    ${month_name}    ${year}
    Wait Until Page Contains Element    ${field_locator}    ${DOPA_FIELD_TIMEOUT}
    ${actual}=    Get Text    ${field_locator}
    ${actual}=    Replace String    ${actual}    .    ${EMPTY}
    ${parts}=    Split String    ${actual}
    ${matches}=    Evaluate
    ...    len($parts) == 3 and int($parts[0]) == int($day) and $parts[1].lower() == $month_name[:3].lower() and int($parts[2]) == int($year)
    Should Be True    ${matches}    Committed DOPA date differs from the expected profile value.

Tap DOPA Next
    Execute Adb Shell    input    keyevent    111
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


Normalize Title
    [Arguments]    ${title}
    ${t}=    Strip String    ${title}
    ${t}=    Replace String    ${t}    .    ${EMPTY}
    ${t}=    Set Variable If    '${t}' == 'Mr'    นาย    ${t}
    ${t}=    Set Variable If    '${t}' == 'Miss'    นางสาว    ${t}
    ${t}=    Set Variable If    '${t}' == 'Mrs'    นาง    ${t}
    RETURN    ${t}


Get DOPA Title Value
    ${status}    ${raw}=    Run Keyword And Ignore Error    Get Text    ${DOPA_TITLE_VALUE}
    Return From Keyword If    '${status}' != 'PASS'    ${EMPTY}
    ${norm}=    Normalize Title    ${raw}
    RETURN    ${norm}


Title Option Candidates
    [Arguments]    ${expected}
    IF    '${expected}' == 'นาย'
        ${candidates}=    Create List    นาย    Mr    Mr.
    ELSE IF    '${expected}' == 'นางสาว'
        ${candidates}=    Create List    นางสาว    Miss    Miss.
    ELSE IF    '${expected}' == 'นาง'
        ${candidates}=    Create List    นาง    Mrs    Mrs.
    ELSE
        ${candidates}=    Create List    ${expected}
    END
    RETURN    ${candidates}


Select DOPA Title Option
    [Arguments]    ${expected}
    ${candidates}=    Title Option Candidates    ${expected}
    FOR    ${candidate}    IN    @{candidates}
        # accessibility_id (content-desc) targets the RN Pressable ROW (resource-id="group-list-press"),
        # not the inner text node. Row is non-clickable/enabled=false in the a11y tree -> adb tap fires onPress
        # Requires Appium's bounded --allow-insecure=uiautomator2:adb_shell permission.
        ${present}=    Run Keyword And Return Status    Page Should Contain Element    accessibility_id=${candidate}    2s
        IF    ${present}
            ${rect}=    Get Element Rect    accessibility_id=${candidate}
            ${cx}=    Evaluate    int(${rect['x']} + (${rect['width']} / 2))
            ${cy}=    Evaluate    int(${rect['y']} + (${rect['height']} / 2))
            Execute Adb Shell    input    tap    ${cx}    ${cy}
            Log    [DOPA] Title option adb-tapped: '${candidate}' row @ (${cx}, ${cy})    WARN
            RETURN    ${TRUE}
        END
    END
    RETURN    ${FALSE}


Capture DOPA Title Dropdown Evidence
    ${ts}=    Get Time    epoch
    Record ETB Evidence Capture    ${OUTPUT DIR}    dopa_title_dropdown_open_${ts}
    Log    [DOPA] Title-dropdown evidence requested through shared private adapter.    WARN


Title Is Accepted Equivalent
    [Arguments]    ${raw}    ${expected}
    # equivalence lives in Normalize Title (Mr/Mr.->นาย etc.); this iterates the
    # explicit accepted list from Title Option Candidates and rejects empty = no selection.
    ${norm}=    Normalize Title    ${raw}
    Should Not Be Empty    ${norm}    DOPA title is empty (no selection registered)
    ${candidates}=    Title Option Candidates    ${expected}
    FOR    ${c}    IN    @{candidates}
        ${cn}=    Normalize Title    ${c}
        IF    '${cn}' == '${norm}'
            RETURN
        END
    END
    Fail    DOPA title '${raw}' not in accepted equivalents ${candidates}


Select DOPA Title If Needed
    [Arguments]    ${expected_title}
    ${expected}=    Normalize Title    ${expected_title}
    ${current}=    Get DOPA Title Value
    IF    '${current}' == '${expected}'
        Log    [DOPA] Title already set correctly: ${current}    WARN
        RETURN
    END
    Log    [DOPA] Title needs selection: current='${current}' expected='${expected}'    WARN
    Tap DOPA Element Center    ${DOPA_TITLE_DROPDOWN}
    Sleep    1s
    Capture DOPA Title Dropdown Evidence
    ${picked}=    Select DOPA Title Option    ${expected}
    Run Keyword And Ignore Error    Hide Keyboard
    Should Be True    ${picked}    DOPA title option not found in dropdown for expected='${expected}'
    Sleep    1s
    ${after}=    Get DOPA Title Value
    Title Is Accepted Equivalent    ${after}    ${expected}
    Log    [DOPA] Title selected and confirmed: ${after}    WARN
