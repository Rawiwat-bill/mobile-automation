*** Settings ***
Library     String
Library     AppiumLibrary
Resource    ../../../locators/android/etb/check_dopa_fill_laser_code_locator.resource
Resource    ../../../resources/app/app_constants.resource


*** Keywords ***
Wait Until Check DOPA Fill Laser Code Is Displayed
    [Documentation]    Wait until the Check DOPA Fill Laser Code screen is displayed
    Wait Until Element Is Visible    ${CHECK_DOPA_FILL_LASER_CODE_TITLE_TEXT}    ${NCBD_LOADING_TIMEOUT}
    Wait Until Element Is Visible    ${FIELD_LASER_CODE1}    ${NCBD_LOADING_TIMEOUT}

Input Laser Code
    [Documentation]    Input the laser code into the respective fields on the Check DOPA Fill Laser Code screen
    [Arguments]    ${laser_code}
    ${list_laser_code}=    Split String    ${laser_code}    -

    FOR    ${index}    IN RANGE    3
        ${field_number}=    Evaluate    ${index} + 1
        Wait Until Element Is Visible    ${FIELD_LASER_CODE${field_number}}    ${NCBD_LOADING_TIMEOUT}
        Click Element    ${FIELD_LASER_CODE${field_number}}
        Input Text Into Current Element    ${list_laser_code}[${index}]
    END

    Hide Keyboard
    Wait Until Element Is Visible    ${CHECK_DOPA_FILL_LASER_CODE_BUTTON_NEXT}    ${NCBD_LOADING_TIMEOUT}
    Click Element    ${CHECK_DOPA_FILL_LASER_CODE_BUTTON_NEXT}
