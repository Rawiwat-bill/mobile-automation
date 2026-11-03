*** Settings ***
Library     AppiumLibrary
Library     Collections
Library     String
Resource    ../app/app_constants.resource
Resource    ./dob_stability_keywords.resource


*** Variables ***
${ANDROID_WHEEL_TIMEOUT}             3s


*** Keywords ***
Read Android Wheel Picker Value
    [Arguments]    ${picker_locator}
    Wait Until Element Is Visible    ${picker_locator}    ${ANDROID_WHEEL_TIMEOUT}
    ${description}=    Get Element Attribute    ${picker_locator}    content-desc
    ${description_value}=    Set Variable    ${EMPTY}
    IF    '${description}' != '' and '${description}' != 'None'
        ${description_value}=    Fetch From Right    ${description}    ,
        ${description_value}=    Strip String    ${description_value}
        IF    '${description_value}' != ''
            RETURN    ${description_value}
        END
    END
    Fail    DOB_PICKER_ACCESSIBILITY_VALUE_UNAVAILABLE

Get Android Wheel Picker Index
    [Arguments]    ${value}    ${value_kind}
    IF    $value_kind == 'month'
        # MONTH_INDEXES values are strings in *** Variables ***; coerce to int so the
        # caller's index arithmetic (abs(cur - target)) doesn't hit str-str TypeError.
        ${raw}=    Get From Dictionary    ${MONTH_INDEXES}    ${value}
        ${index}=    Convert To Integer    ${raw}
    ELSE IF    $value_kind == 'number'
        ${index}=    Convert To Integer    ${value}
    ELSE
        Fail    Unsupported Android wheel picker value kind '${value_kind}'.
    END
    RETURN    ${index}

Select Android Wheel Picker Value
    [Arguments]    ${picker_locator}    ${target_value}    ${value_kind}    ${target_row_locator}=${EMPTY}
    Wait Until Element Is Visible    ${picker_locator}    ${ANDROID_WHEEL_TIMEOUT}
    ${started}=    Evaluate    __import__('time').monotonic()
    ${no_progress}=    Set Variable    0
    FOR    ${index}    IN RANGE    25
        ${elapsed}=    Evaluate    __import__('time').monotonic() - ${started}
        IF    ${elapsed} > ${DOB_PICKER_MAX_SECONDS}
            Fail    DOB_PICKER_TIMEOUT kind=${value_kind} target=${target_value} elapsed=${elapsed}
        END
        ${current_value}=    Read Android Wheel Picker Value    ${picker_locator}
        IF    '${value_kind}' == 'month'
            ${matched}=    Run Keyword And Return Status    Should Be Equal As Strings    ${current_value}    ${target_value}
        ELSE
            ${matched}=    Run Keyword And Return Status    Should Be Equal As Integers    ${current_value}    ${target_value}
        END
        IF    ${matched}
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
        Run Keyword And Ignore Error    Record DOB Picker Attempt    ${value_kind}    ${target_value}    ${current_value}    ${direction}
        ${picker_rect}=    Get Element Rect    ${picker_locator}
        ${center_x}=    Evaluate    int($picker_rect['x'] + ($picker_rect['width'] / 2))
        ${diff}=    Evaluate    abs(int($current_index) - int($target_index))
        # A visible exact row is actionable even when the numeric distance is
        # two or more; distance alone does not describe the rendered wheel.
        IF    '${target_row_locator}' != ''
            ${target_visible}=    Run Keyword And Return Status
            ...    Wait Until Element Is Visible    ${target_row_locator}    1s
            IF    ${target_visible}
                ${target_lookup_ok}=    Run Keyword And Return Status
                ...    Get WebElements    ${target_row_locator}
                IF    ${target_lookup_ok}
                    ${target_elements}=    Get WebElements    ${target_row_locator}
                    ${target_count}=    Get Length    ${target_elements}
                    IF    ${target_count} == 1
                        ${picker_rect}=    Get Element Rect    ${picker_locator}
                        ${target_rect}=    Get Element Rect    ${target_row_locator}
                        ${target_center_y}=    Evaluate    $target_rect['y'] + ($target_rect['height'] / 2)
                        ${picker_top}=    Evaluate    $picker_rect['y']
                        ${picker_bottom}=    Evaluate    $picker_rect['y'] + $picker_rect['height']
                        ${target_in_picker}=    Evaluate    $picker_top <= $target_center_y <= $picker_bottom
                        IF    ${target_in_picker}
                            ${target_x}=    Evaluate    int($target_rect['x'] + ($target_rect['width'] / 2))
                            ${target_y}=    Evaluate    int($target_rect['y'] + ($target_rect['height'] / 2))
                            ${target_point}=    Create List    ${target_x}    ${target_y}
                            Tap    ${target_point}
                            ${target_selected}=    Run Keyword And Return Status
                            ...    Wait Until Keyword Succeeds    2s    200ms
                            ...    Android Wheel Picker Value Should Be    ${picker_locator}    ${target_value}    ${value_kind}
                            IF    ${target_selected}
                                RETURN
                            END
                        END
                    END
                END
            END
        END
        IF    ${diff} <= 2
            ${top_y}=    Evaluate    int($picker_rect['y'] + ($picker_rect['height'] * 0.35))
            ${bottom_y}=    Evaluate    int($picker_rect['y'] + ($picker_rect['height'] * 0.65))
        ELSE
            ${top_y}=    Evaluate    int($picker_rect['y'] + ($picker_rect['height'] * float($DOB_COARSE_END_RATIO)))
            ${bottom_y}=    Evaluate    int($picker_rect['y'] + ($picker_rect['height'] * float($DOB_COARSE_START_RATIO)))
        END
        IF    '${direction}' == 'up'
            Execute Adb Shell    input    swipe    ${center_x}    ${bottom_y}    ${center_x}    ${top_y}    ${DOB_DRAG_DURATION}
        ELSE
            Execute Adb Shell    input    swipe    ${center_x}    ${top_y}    ${center_x}    ${bottom_y}    ${DOB_DRAG_DURATION}
        END
        ${change_status}    ${next_value}=    Run Keyword And Ignore Error
        ...    Wait Until Keyword Succeeds    3s    200ms
        ...    Android Wheel Picker Value Should Change From    ${picker_locator}    ${current_value}    ${value_kind}
        IF    '${change_status}' != 'PASS'
            ${no_progress}=    Evaluate    ${no_progress} + 1
            IF    ${no_progress} >= ${DOB_PICKER_NO_PROGRESS_LIMIT}
                Fail    DOB_PICKER_NO_PROGRESS kind=${value_kind} target=${target_value} current=${current_value}
            END
        ELSE
            ${no_progress}=    Set Variable    0
            ${target_after_change}=    Run Keyword And Return Status
            ...    Should Be Equal As Integers    ${next_value}    ${target_value}
            IF    '${value_kind}' == 'month'
                ${target_after_change}=    Run Keyword And Return Status
                ...    Should Be Equal As Strings    ${next_value}    ${target_value}
            END
            IF    ${target_after_change}
                RETURN
            END
        END
    END
    Run Keyword And Ignore Error    Record DOB Failure    ${value_kind}    ${target_value}    exhausted 25 attempts
    Fail    Could not select DOB picker value '${target_value}' using locator '${picker_locator}'.

Android Wheel Picker Value Should Be
    [Arguments]    ${picker_locator}    ${target_value}    ${value_kind}
    ${current_value}=    Read Android Wheel Picker Value    ${picker_locator}
    IF    '${value_kind}' == 'month'
        Should Be Equal As Strings    ${current_value}    ${target_value}
    ELSE
        Should Be Equal As Integers    ${current_value}    ${target_value}
    END

Android Wheel Picker Value Should Change From
    [Arguments]    ${picker_locator}    ${previous_value}    ${value_kind}
    ${current_value}=    Read Android Wheel Picker Value    ${picker_locator}
    IF    '${value_kind}' == 'month'
        Should Not Be Equal As Strings    ${current_value}    ${previous_value}
    ELSE
        Should Not Be Equal As Integers    ${current_value}    ${previous_value}
    END
    RETURN    ${current_value}
