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
    ${result_status}    ${center_text}=    Run Keyword And Ignore Error
    ...    Get Text    ${picker_locator}/android.view.ViewGroup/android.widget.ScrollView/android.view.ViewGroup/android.view.ViewGroup[3]/android.widget.TextView
    IF    '${result_status}' == 'PASS'
        ${value}=    Strip String    ${center_text}
        IF    '${value}' != ''
            RETURN    ${value}
        END
    END
    ${value}=    Fetch From Right    ${description}    ,
    ${value}=    Strip String    ${value}
    RETURN    ${value}

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
    [Arguments]    ${picker_locator}    ${target_value}    ${value_kind}
    Wait Until Element Is Visible    ${picker_locator}    ${ANDROID_WHEEL_TIMEOUT}
    FOR    ${index}    IN RANGE    25
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
    Run Keyword And Ignore Error    Record DOB Failure    ${value_kind}    ${target_value}    exhausted 25 attempts
    Run Keyword And Ignore Error    Capture DOB Failure Evidence    ${value_kind}    ${target_value}
    Fail    Could not select DOB picker value '${target_value}' using locator '${picker_locator}'.
