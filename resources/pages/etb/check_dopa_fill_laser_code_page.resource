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
        Wait Until Element Is Visible    ${FIELD_LASER_CODE${field_number}}    ${NCBD_LOADING_TIMEOUT}
        Input Text    ${FIELD_LASER_CODE${field_number}}    ${laser_parts}[${index}]
        ${field_value}=    Get Text    ${FIELD_LASER_CODE${field_number}}
        ${field_matches}=    Run Keyword And Return Status    Should Be Equal As Strings    ${field_value}    ${laser_parts}[${index}]
        Should Be True    ${field_matches}    INVALID_LASER_CODE_FORMAT
    END

    Hide Keyboard

Tap Check DOPA Next
    [Documentation]    Submit the completed laser-code screen.
    Wait Until Element Is Visible    ${CHECK_DOPA_FILL_LASER_CODE_BUTTON_NEXT}    ${NCBD_LOADING_TIMEOUT}
    Click Element    ${CHECK_DOPA_FILL_LASER_CODE_BUTTON_NEXT}
