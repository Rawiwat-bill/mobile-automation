*** Settings ***
Library     String
Library     AppiumLibrary
Resource    ../../../locators/android/etb/check_dopa_fill_laser_code_locators.resource
Resource    ../../../resources/app/app_constants.resource


*** Keywords ***
Wait Until Check DOPA Fill Laser Code Is Displayed
    [Documentation]    Wait until the Check DOPA Fill Laser Code screen is displayed
    Wait Until Element Is Visible    ${CHECK_DOPA_FILL_LASER_CODE_TITLE_TEXT}    ${NCBD_LOADING_TIMEOUT}
    Wait Until Element Is Visible    ${FIELD_LASER_CODE1}    ${NCBD_LOADING_TIMEOUT}

Input Laser Code
    [Documentation]    Input the laser code into the respective fields on the Check DOPA Fill Laser Code screen
    [Arguments]    ${laser_code}
    ${laser_length}=    Get Length    ${laser_code}
    ${laser_valid}=    Evaluate    ${laser_length} == 12 and $laser_code.isalnum()
    Should Be True    ${laser_valid}    INVALID_LASER_CODE_FORMAT
    ${part1}=    Get Substring    ${laser_code}    0    3
    ${part2}=    Get Substring    ${laser_code}    3    10
    ${part3}=    Get Substring    ${laser_code}    10    12
    @{laser_parts}=    Create List    ${part1}    ${part2}    ${part3}

    FOR    ${index}    IN RANGE    3
        ${field_number}=    Evaluate    ${index} + 1
        ${field_locator}=    Set Variable    ${FIELD_LASER_CODE${field_number}}
        Wait Until Element Is Visible    ${field_locator}    ${NCBD_LOADING_TIMEOUT}
        Input Text    ${field_locator}    ${laser_parts}[${index}]
        # React Native may replace the EditText node immediately after input.
        # Reacquire the locator for verification instead of reusing a stale node.
        Wait Until Keyword Succeeds    5x    300ms
        ...    Laser Code Field Should Match Fresh    ${field_locator}    ${laser_parts}[${index}]
    END

    Run Keyword And Ignore Error    Hide Keyboard

Laser Code Field Should Match Fresh
    [Arguments]    ${field_locator}    ${expected}
    Wait Until Element Is Visible    ${field_locator}    2s
    ${field_value}=    Get Text    ${field_locator}
    Should Be Equal As Strings    ${field_value}    ${expected}    INVALID_LASER_CODE_FORMAT

Tap Check DOPA Next
    [Documentation]    Submit the completed laser-code screen.
    Wait Until Element Is Visible    ${CHECK_DOPA_FILL_LASER_CODE_BUTTON_NEXT}    ${NCBD_LOADING_TIMEOUT}
    Click Element    ${CHECK_DOPA_FILL_LASER_CODE_BUTTON_NEXT}

Classify Post Laser Failure State
    [Documentation]    Classify the bounded state after Laser Next without logging profile values or source.
    [Arguments]    ${expected_error_code}
    ${source_status}    ${source}=    Run Keyword And Ignore Error    Get Source
    IF    '${source_status}' != 'PASS'
        RETURN    SOURCE_UNAVAILABLE
    END
    ${codes}=    Get Regexp Matches    ${source}    (?:RGI|GOD|AJI|RAI)-[0-9]{3}
    ${count}=    Get Length    ${codes}
    IF    ${count} > 0
        RETURN    ${codes}[0]
    END
    ${dopa_title}=    Run Keyword And Return Status
    ...    Should Contain    ${source}    screenPersonalInformation_navBarTitleList
    ${laser_field}=    Run Keyword And Return Status
    ...    Should Contain    ${source}    text-input-flat
    IF    ${dopa_title} and ${laser_field}
        RETURN    DOPA_STILL_VISIBLE
    END
    RETURN    UNKNOWN_DESTINATION
