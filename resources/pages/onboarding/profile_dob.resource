*** Settings ***
Documentation    Profile Date-of-Birth interaction and picker behavior.
Library          AppiumLibrary
Library          Collections
Library          String
Resource         profile_fields.resource
Resource         ../../../locators/android/onboarding/profile_screen_locators.resource
Resource         ../../keywords/dob_stability_keywords.resource
Resource         ../../keywords/android_wheel_picker.resource
Resource         ../../app/app_constants.resource
Library          ../../../libraries/etb_dob_candidate.py


*** Keywords ***
Verify DOB Field Value
    [Arguments]    ${day}    ${month}    ${year}
    ${dob_strategy}=    Get Variable Value    ${ETB_DOB_STRATEGY}    LEGACY
    IF    $dob_strategy == 'STABLE_V1'
        Verify Committed DOB Exact    ${day}    ${month}    ${year}    ${PROFILE_DOB_INPUT}
        RETURN
    END
    ${field_text}=    Get Text    ${PROFILE_DOB_INPUT}
    ${parts}=    Evaluate    __import__('re').findall(r'[0-9]+|[A-Za-z]+', str($field_text))
    ${part_count}=    Get Length    ${parts}
    Should Be Equal As Integers    ${part_count}    3    DOB_DISPLAY_FORMAT_UNSUPPORTED
    ${actual_day}=    Convert To Integer    ${parts}[0]
    ${actual_month_token}=    Set Variable    ${parts}[1]
    ${actual_year}=    Convert To Integer    ${parts}[2]
    ${actual_month}=    Evaluate    int($actual_month_token) if str($actual_month_token).isdigit() else {'jan':1,'january':1,'feb':2,'february':2,'mar':3,'march':3,'apr':4,'april':4,'may':5,'jun':6,'june':6,'jul':7,'july':7,'aug':8,'august':8,'sep':9,'september':9,'oct':10,'october':10,'nov':11,'november':11,'dec':12,'december':12}[str($actual_month_token).lower()]
    ${expected_day}=    Convert To Integer    ${day}
    ${expected_month}=    Evaluate    int($month) if str($month).isdigit() else {'jan':1,'january':1,'feb':2,'february':2,'mar':3,'march':3,'apr':4,'april':4,'may':5,'jun':6,'june':6,'jul':7,'july':7,'aug':8,'august':8,'sep':9,'september':9,'oct':10,'october':10,'nov':11,'november':11,'dec':12,'december':12}[str($month).lower()]
    ${expected_year}=    Convert To Integer    ${year}
    Should Be Equal As Integers    ${actual_day}    ${expected_day}    DOB day mismatch.
    Should Be Equal As Integers    ${actual_month}    ${expected_month}    DOB month mismatch.
    Should Be Equal As Integers    ${actual_year}    ${expected_year}    DOB year mismatch.
    Log    [PROFILE] complete DOB field verified with masked value.

Tap Date Of Birth Field
    Wait Until Element Is Visible    ${PROFILE_DOB_INPUT}    ${PROFILE_TIMEOUT}
    Click Element                    ${PROFILE_DOB_INPUT}
    Log    [PROFILE] DOB field clicked

Observe Profile DOB Boundary
    [Documentation]    Verify Profile DOB markers from this resource without depending on a caller-only keyword.
    [Arguments]    ${point}
    ${source}=    Get Source
    ${dob_container}=    Run Keyword And Return Status    Should Contain    ${source}    screenProfile_textInputDob-container
    ${dob_input}=    Run Keyword And Return Status    Should Contain    ${source}    screenProfile_textInputDob
    ${mobile_container}=    Run Keyword And Return Status    Should Contain    ${source}    screenProfile_textInputMobileNumber-container
    ${next_button}=    Run Keyword And Return Status    Should Contain    ${source}    screenProfile_buttonNext
    ${activity}=    Get Activity
    ${appium_library}=    Get Library Instance    AppiumLibrary
    ${package}=    Evaluate    $appium_library._current_application().current_package
    Log    [PROFILE_BOUNDARY] ${point} dob-container=${dob_container} dob=${dob_input} mobile-container=${mobile_container} next=${next_button} package=${package} activity=${activity}    WARN
    IF    not ${dob_container} or not ${dob_input}
        ${profile_markers}=    Evaluate    ${mobile_container} or ${next_button}
        IF    ${profile_markers}
            Fail    PROFILE_DOB_MARKER_LOST_AFTER_KEYBOARD_DISMISS
        ELSE
            Fail    PROFILE_STATE_CHANGED_AFTER_KEYBOARD_DISMISS
        END
    END

Input Date Of Birth
    [Arguments]    ${date_of_birth}
    ${dob_strategy}=    Get Variable Value    ${ETB_DOB_STRATEGY}    LEGACY
    IF    $dob_strategy == 'STABLE_V1'
        ${dob_metrics}=    Select ETB DOB Exact
        ...    ${date_of_birth}    ${PROFILE_DOB_CONTAINER}
        ...    ${PROFILE_DOB_YEAR_PICKER}    ${PROFILE_DOB_MONTH_PICKER}
        ...    ${PROFILE_DOB_DAY_PICKER}    ${PROFILE_DOB_CONFIRM_BUTTON}
        ...    ${PROFILE_DOB_INPUT}    ${PROFILE_TITLE_TEXT}
        Set Test Variable    ${ETB_DOB_LAST_METRICS}    ${dob_metrics}
        RETURN
    ELSE IF    $dob_strategy != 'LEGACY'
        Fail    DOB_STRATEGY_UNSUPPORTED
    END
    Observe Profile DOB Boundary    P2
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
    ${year_row}=    Set Variable
    ...    xpath=//*[@resource-id="screenProfile_calendarDatePicker-yearScroll"]//*[normalize-space(@text)="${year}" or normalize-space(@content-desc)="${year}" or contains(concat(" ",normalize-space(@content-desc)," ")," ${year} ")]
    ${month_row}=    Set Variable
    ...    xpath=//*[@resource-id="screenProfile_calendarDatePicker-monthScroll"]//*[normalize-space(@text)="${month}" or normalize-space(@content-desc)="${month}"]
    ${day_number}=    Convert To Integer    ${day}
    ${day_row}=    Set Variable
    ...    xpath=//*[@resource-id="screenProfile_calendarDatePicker-dateScroll"]//*[normalize-space(@text)="${day}" or normalize-space(@text)="${day_number}" or normalize-space(@content-desc)="${day}" or normalize-space(@content-desc)="${day_number}"]
    Tap Profile Element Center    ${PROFILE_DOB_CONTAINER}
    Record DOB Picker Visible
    Record DOB Year Start
    ${status}    ${error}=    Run Keyword And Ignore Error
    ...    Select DOB Picker Value    ${PROFILE_DOB_YEAR_PICKER}    ${year}    number    ${year_row}
    IF    '${status}' != 'PASS'
        Record DOB Failure    year    ${year}    ${error}
        Capture DOB Failure Evidence    year    ${year}
        Fail    ${error}
    END
    Record DOB Year End
    Record DOB Month Start
    ${status}    ${error}=    Run Keyword And Ignore Error
    ...    Select DOB Picker Value    ${PROFILE_DOB_MONTH_PICKER}    ${month}    month    ${month_row}
    IF    '${status}' != 'PASS'
        Record DOB Failure    month    ${month}    ${error}
        Capture DOB Failure Evidence    month    ${month}
        Fail    ${error}
    END
    Record DOB Month End
    Record DOB Day Start
    ${status}    ${error}=    Run Keyword And Ignore Error
    ...    Select DOB Picker Value    ${PROFILE_DOB_DAY_PICKER}    ${day}    number    ${day_row}
    IF    '${status}' != 'PASS'
        Record DOB Failure    day    ${day}    ${error}
        Capture DOB Failure Evidence    day    ${day}
        Fail    ${error}
    END
    Record DOB Day End
    Click Element    ${PROFILE_DOB_CONFIRM_BUTTON}
    Tap Profile Focus Dismissal Target    ${BLUR_AFTER_DOB_Y}
    Wait Until Profile Fields Are Blurred
    Verify DOB Field Value    ${day}    ${month_token}    ${year}
    Record DOB Success

Select DOB Picker Value
    [Arguments]    ${picker_locator}    ${target_value}    ${value_kind}    ${target_row_locator}=${EMPTY}
    Select Android Wheel Picker Value    ${picker_locator}    ${target_value}    ${value_kind}    ${target_row_locator}
