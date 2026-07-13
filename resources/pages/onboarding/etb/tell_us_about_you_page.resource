*** Settings ***
Library     AppiumLibrary
Library     String
Resource    ../../../../locators/android/onboarding/etb/tell_us_about_you_locators.resource
Resource    ../../../app/app_constants.resource
Resource    ../../../keywords/dob_stability_keywords.resource


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
    ${displayed}=    Input Text Field    ${TELL_US_ABOUT_YOU_CID_INPUT}    ${citizen_id}
    Run Keyword And Ignore Error    Hide Keyboard
    Wait Until Fields Are Blurred

Input Date Of Birth
    [Documentation]    Input the date of birth on the "Tell us about you" screen
    [Arguments]    ${date_of_birth}
    # Start DOB Interaction
    Wait Until Element Is Visible    ${TELL_US_ABOUT_YOU_DOB_CONTAINER}    ${TELL_US_ABOUT_YOU_TIMEOUT}
    Click Element    ${TELL_US_ABOUT_YOU_DOB_INPUT}
    Wait Until Element Is Visible    ${TELL_US_ABOUT_YOU_DOB_DATE_PICKER}    ${TELL_US_ABOUT_YOU_TIMEOUT}
    Map Date Of Birth    ${date_of_birth}
    # ${displayed}=    Input Text Field    ${TELL_US_ABOUT_YOU_DOB_INPUT}    ${date_of_birth}
    # Run Keyword And Ignore Error    Hide Keyboard
    # Wait Until Fields Are Blurred

Map Date Of Birth
    [Documentation]    Map the date of birth to day, month, and year.
    [Arguments]    ${date_of_birth}

    ${day}    ${month}    ${year}=    Split String    ${date_of_birth}    -
    ${month_name}=    Get From Dictionary    ${MONTH_MAP}    ${month}

    Set Year Picker    ${year}

Set Year Picker
    [Arguments]    ${target_year}

    ${value}=    Get Element Attribute
    ...    ${TELL_US_ABOUT_YOU_SEEKBAR_YEAR}
    ...    content-desc

    ${current_year}=    Evaluate
    ...    int('${value}'.split(',')[-1].strip())

    ${steps}=    Evaluate    abs(${current_year} - int(${target_year}))

    FOR    ${i}    IN RANGE    ${steps}
        IF    ${current_year} > int(${target_year})
            Swipe    start_x=870    start_y=1450    end_x=870    end_y=1550    duration=200
        ELSE
            Swipe    start_x=870    start_y=1550    end_x=870    end_y=1450    duration=200
        END
    END

    Log    [PERF] DOB Year Picker: current=${current_year}, target=${target_year}, steps=${steps}
