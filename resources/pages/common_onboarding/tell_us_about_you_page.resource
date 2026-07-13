*** Settings ***
Library     AppiumLibrary
Library     String
Resource    ../../../locators/android/common_onboarding/tell_us_about_you_locators.resource
Resource    ../../app/app_constants.resource
Resource    ../../keywords/dob_stability_keywords.resource
Resource    ../../keywords/utils/utility_keywords.resource


*** Variables ***
${TELL_US_ABOUT_YOU_TIMEOUT}    5s


*** Keywords ***
Wait Until Tell Us About You Screen Is Displayed
    [Documentation]    Wait until the "Tell us about you" screen is displayed
    Wait Until Element Is Visible    ${TELL_US_ABOUT_YOU_TITLE_TEXT}    timeout=${TELL_US_ABOUT_YOU_TIMEOUT}
    Wait Until Element Is Visible    ${TELL_US_ABOUT_YOU_CITIZEN_ID_CONTAINER}    timeout=${TELL_US_ABOUT_YOU_TIMEOUT}

Wait Until Fields Are Blurred
    [Documentation]    Wait until the fields are blurred (not focused)
    Wait Until Keyword Succeeds    5x    300ms    Fields Should Be Blurred

Fields Should Be Blurred
    [Documentation]    Verify that the fields are blurred (not focused)
    ${citizen_focused}=    Get Element Attribute    ${TELL_US_ABOUT_YOU_CID_INPUT}    focused
    # ${dob_focused}=    Get Element Attribute    ${PROFILE_DOB_INPUT}    focused
    # ${mobile_focused}=    Get Element Attribute    ${PROFILE_MOBILE_NUMBER_INPUT}    focused
    Should Be Equal As Strings    ${citizen_focused}    false
    # Should Be Equal As Strings    ${dob_focused}    false
    # Should Be Equal As Strings    ${mobile_focused}    false

Input Text Field
    [Documentation]    Clear the field, input text, and return the displayed value.
    [Arguments]    ${input_locator}    ${value}
    ${previous_log_level}=    Set Log Level    NONE
    Clear Text    ${input_locator}
    Input Text    ${input_locator}    ${value}
    ${displayed}=    Get Text    ${input_locator}
    Set Log Level    ${previous_log_level}
    RETURN    ${displayed}

Input Citizen ID
    [Documentation]    Input the citizen ID on the "Tell us about you" screen
    [Arguments]    ${citizen_id}

    Wait Until Element Is Visible    ${TELL_US_ABOUT_YOU_CITIZEN_ID_CONTAINER}    ${TELL_US_ABOUT_YOU_TIMEOUT}
    Click Element    ${TELL_US_ABOUT_YOU_CID_INPUT}
    Input Text    ${TELL_US_ABOUT_YOU_CID_INPUT}    ${citizen_id}
    Hide Keyboard Custom
    # ${displayed}=    Input Text Field    ${TELL_US_ABOUT_YOU_CID_INPUT}    ${citizen_id}
    # Run Keyword And Ignore Error    Hide Keyboard
    # Wait Until Fields Are Blurred

Select Date Of Birth
    [Documentation]    Input the date of birth on the "Tell us about you" screen
    [Arguments]    ${date_of_birth}

    Wait Until Element Is Visible    ${TELL_US_ABOUT_YOU_DOB_CONTAINER}    ${TELL_US_ABOUT_YOU_TIMEOUT}
    Click Element    ${TELL_US_ABOUT_YOU_DOB_INPUT}
    Wait Until Element Is Visible    ${TELL_US_ABOUT_YOU_DOB_DATE_PICKER}    ${TELL_US_ABOUT_YOU_TIMEOUT}
    Map Date Of Birth    ${date_of_birth}

Map Date Of Birth
    [Documentation]    Map the date of birth to day, month, and year.
    [Arguments]    ${date_of_birth}

    ${day}    ${month}    ${year}=    Split String    ${date_of_birth}    -
    ${month_int}=    Convert To Integer    ${month}

    Swipe DOB Picker    ${year}    ${month_int}    ${day}

Swipe DOB Picker
    [Documentation]    Swipe the DOB picker to the target dob.
    [Arguments]    ${target_year}    ${target_month}    ${target_day}

    # Get current values from the seekbars
    ${seekbar_year}=    Get Element Attribute
    ...    ${TELL_US_ABOUT_YOU_SEEKBAR_YEAR}
    ...    content-desc
    ${seekbar_month}=    Get Element Attribute
    ...    ${TELL_US_ABOUT_YOU_SEEKBAR_MONTH}
    ...    content-desc
    ${seekbar_day}=    Get Element Attribute
    ...    ${TELL_US_ABOUT_YOU_SEEKBAR_DAY}
    ...    content-desc

    # Evaluate seperate current year
    ${current_year}=    Evaluate
    ...    int('${seekbar_year}'.split(',')[-1].strip())

    # Evaluate seperate current month
    ${month_name}=    Evaluate
    ...    '${seekbar_month}'.split(',')[-1].strip()
    ${current_month}=    Get From Dictionary    ${MONTH_INDEXES}    ${month_name}

    # Evaluate seperate current day
    ${current_day}=    Evaluate
    ...    int('${seekbar_day}'.split(',')[-1].strip())

    # Evaluate steps to move for year, month, and day
    ${steps_year}=    Evaluate    abs(${current_year} - int(${target_year}))
    ${steps_month}=    Evaluate    abs(${current_month} - int(${target_month}))
    ${steps_day}=    Evaluate    abs(${current_day} - int(${target_day}))

    # Get the rects of the seekbars
    ${rect_year}=    Get Element Rect    ${TELL_US_ABOUT_YOU_SEEKBAR_YEAR}
    ${rect_month}=    Get Element Rect    ${TELL_US_ABOUT_YOU_SEEKBAR_MONTH}
    ${rect_day}=    Get Element Rect    ${TELL_US_ABOUT_YOU_SEEKBAR_DAY}

    # Determine the swipe direction for year, month, and day
    ${year_dir}=    Set Variable If    ${current_year} > int(${target_year})    down    up
    ${month_dir}=    Set Variable If    ${current_month} > int(${target_month})    down    up
    ${day_dir}=    Set Variable If    ${current_day} > int(${target_day})    down    up

    # Swipe the year wheel to the target value
    FOR    ${i}    IN RANGE    ${steps_year}
        Swipe DOB Wheel    ${rect_year}    ${year_dir}
    END
    Log    [PERF] DOB Year Picker: current=${current_year}, target=${target_year}, steps=${steps_year}

    # Swipe the month wheel to the target value
    FOR    ${i}    IN RANGE    ${steps_month}
        Swipe DOB Wheel    ${rect_month}    ${month_dir}
    END
    Log    [PERF] DOB Month Picker: current=${current_month}, target=${target_month}, steps=${steps_month}

    # Swipe the day wheel to the target value
    FOR    ${i}    IN RANGE    ${steps_day}
        Swipe DOB Wheel    ${rect_day}    ${day_dir}
    END
    Log    [PERF] DOB Day Picker: current=${current_day}, target=${target_day}, steps=${steps_day}

Swipe DOB Wheel
    [Documentation]    Swipe the DOB wheel in the specified direction.
    [Arguments]    ${rect}    ${direction}

    ${center_x}=    Evaluate    int(${rect['x']} + ${rect['width']} / 2)
    ${center_y}=    Evaluate    int(${rect['y']} + ${rect['height']} / 2)

    ${offset}=    Evaluate    int(${rect['height']} * 0.05)

    ${start_y}=    Evaluate    ${center_y} + ${offset}
    ${end_y}=    Evaluate    ${center_y} - ${offset}
    IF    '${direction}' == 'down'
        Swipe    start_x=${center_x}    start_y=${end_y}    end_x=${center_x}    end_y=${start_y}    duration=200
    ELSE
        Swipe    start_x=${center_x}    start_y=${start_y}    end_x=${center_x}    end_y=${end_y}    duration=200
    END
