*** Settings ***
Library     String
Library     AppiumLibrary
Resource    ../../app/app_constants.resource
Resource    ../../keywords/dob_stability_keywords.resource
Resource    ../../keywords/utils/utility_keywords.resource
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
    [Documentation]    Input the date of birth on the "Tell us about you" screen.
    ...    Uses verified adb swipes with tiered distances for speed and accuracy.
    [Arguments]    ${date_of_birth}

    Wait Until Element Is Visible    ${TELL_US_ABOUT_YOU_DOB_CONTAINER}    ${NCBD_LOADING_TIMEOUT}
    Click Element    ${TELL_US_ABOUT_YOU_DOB_INPUT}
    Wait Until Element Is Visible    ${TELL_US_ABOUT_YOU_DOB_DATE_PICKER}    ${NCBD_LOADING_TIMEOUT}
    ${year}    ${month}    ${day}=    Seperate Date Of Birth    ${date_of_birth}
    # Select in order: Year → Month → Day (year changes can shift day range)
    Select DOB Wheel Value    ${TELL_US_ABOUT_YOU_SEEKBAR_YEAR}    ${year}    number
    Select DOB Wheel Value    ${TELL_US_ABOUT_YOU_SEEKBAR_MONTH}    ${month}    month
    Select DOB Wheel Value    ${TELL_US_ABOUT_YOU_SEEKBAR_DAY}    ${day}    number
    Click Element    ${TELL_US_ABOUT_YOU_DOB_DATE_PICKER_BUTTON_DONE}

Seperate Date Of Birth
    [Documentation]    Map the date of birth to day, month, and year.
    [Arguments]    ${date_of_birth}

    ${day}    ${month}    ${year}=    Split String    ${date_of_birth}    -
    ${day_int}=    Convert To Integer    ${day}
    ${month_int}=    Convert To Integer    ${month}
    ${year_int}=    Convert To Integer    ${year}
    RETURN    ${year_int}    ${month_int}    ${day_int}

Select DOB Wheel Value
    [Documentation]    Swipe a DOB picker wheel to the target value with verification.
    ...    Uses tiered swipe distances (big/coarse/fine) based on distance from target.
    [Arguments]    ${picker_locator}    ${target_value}    ${value_kind}

    Wait Until Element Is Visible    ${picker_locator}    ${NCBD_LOADING_TIMEOUT}
    # Compute geometry once — wheel bounds don't change while picker is open
    ${rect}=    Get Element Rect    ${picker_locator}
    ${center_x}=    Evaluate    int(${rect['x']} + ${rect['width']} / 2)
    ${fine_top_y}=    Evaluate    int(${rect['y']} + ${rect['height']} * ${DOB_FINE_END_RATIO})
    ${fine_bottom_y}=    Evaluate    int(${rect['y']} + ${rect['height']} * ${DOB_FINE_START_RATIO})
    ${coarse_top_y}=    Evaluate    int(${rect['y']} + ${rect['height']} * ${DOB_COARSE_END_RATIO})
    ${coarse_bottom_y}=    Evaluate    int(${rect['y']} + ${rect['height']} * ${DOB_COARSE_START_RATIO})
    ${big_top_y}=    Evaluate    int(${rect['y']} + ${rect['height']} * 0.15)
    ${big_bottom_y}=    Evaluate    int(${rect['y']} + ${rect['height']} * 0.85)

    FOR    ${index}    IN RANGE    40
        # Wait for wheel to settle then read current value
        ${current_value}=    Read DOB Wheel Value    ${picker_locator}
        IF    '${current_value}' == '${target_value}'
            Log    [PERF] DOB ${value_kind} reached target=${target_value} in ${index} swipes
            RETURN
        END
        # Convert to numeric index for comparison
        IF    '${value_kind}' == 'month'
            ${current_index}=    Get From Dictionary    ${MONTH_INDEXES}    ${current_value}
            ${target_index}=    Convert To Integer    ${target_value}
        ELSE
            ${current_index}=    Convert To Integer    ${current_value}
            ${target_index}=    Convert To Integer    ${target_value}
        END
        ${diff}=    Evaluate    abs(${current_index} - ${target_index})
        IF    ${diff} == 0
            Log    [PERF] DOB ${value_kind} reached target=${target_value} in ${index} swipes (index match)
            RETURN
        END
        ${direction}=    Set Variable If    ${current_index} < ${target_index}    up    down
        # Tiered swipe: big (>5 steps), coarse (3-5), fine (1-2)
        IF    ${diff} > 5
            ${top_y}=    Set Variable    ${big_top_y}
            ${bottom_y}=    Set Variable    ${big_bottom_y}
            ${duration}=    Set Variable    50
        ELSE IF    ${diff} > 2
            ${top_y}=    Set Variable    ${coarse_top_y}
            ${bottom_y}=    Set Variable    ${coarse_bottom_y}
            ${duration}=    Set Variable    80
        ELSE
            ${top_y}=    Set Variable    ${fine_top_y}
            ${bottom_y}=    Set Variable    ${fine_bottom_y}
            ${duration}=    Set Variable    120
        END
        IF    '${direction}' == 'up'
            Execute Adb Shell    input    swipe    ${center_x}    ${bottom_y}    ${center_x}    ${top_y}    ${duration}
        ELSE
            Execute Adb Shell    input    swipe    ${center_x}    ${top_y}    ${center_x}    ${bottom_y}    ${duration}
        END
        Sleep    ${DOB_SETTLE_TIME}
    END
    Fail    Could not select DOB ${value_kind} value '${target_value}' after 40 attempts.

Read DOB Wheel Value
    [Documentation]    Read current selected value from a DOB picker wheel via content-desc.
    ...    Polls twice to confirm the wheel has settled (same value on consecutive reads).
    [Arguments]    ${picker_locator}

    ${desc}=    Get Element Attribute    ${picker_locator}    content-desc
    ${value}=    Evaluate    '${desc}'.split(',')[-1].strip() if '${desc}' else ''
    # Quick stability poll — confirm value hasn't changed
    Sleep    0.05s
    ${desc2}=    Get Element Attribute    ${picker_locator}    content-desc
    ${value2}=    Evaluate    '${desc2}'.split(',')[-1].strip() if '${desc2}' else ''
    IF    '${value}' != '${value2}'
        # Wheel still moving — wait longer and re-read
        Sleep    ${DOB_SETTLE_TIME}
        ${desc3}=    Get Element Attribute    ${picker_locator}    content-desc
        ${value}=    Evaluate    '${desc3}'.split(',')[-1].strip() if '${desc3}' else ''
    END
    RETURN    ${value}

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
