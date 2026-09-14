*** Settings ***
Documentation       ETB Product Selection page keywords.

Library             AppiumLibrary
Library             ../../../libraries/visual_timeline.py
Resource            ../../../resources/app/app_constants.resource
Resource            ../../../locators/android/etb/product_selection_locators.resource

*** Keywords ***
Wait Until Product Selection Screen Is Displayed
    ${title_status}    ${title_error}=    Run Keyword And Ignore Error
    ...    Wait Until Element Is Visible    ${PRODUCT_SELECTION_TITLE}    ${NCBD_LOADING_TIMEOUT}
    IF    '${title_status}' == 'PASS'
        RETURN
    END
    ${source}=    Get Source
    ${source_match}=    Run Keyword And Return Status
    ...    Should Contain Any    ${source}
    ...    screenProductSelection_textTitle
    ...    screenProductSelection_textDescription
    IF    ${source_match}
        RETURN
    END
    Fail    ${title_error}

Product Selection Screen Should Be Displayed
    Element Should Be Visible    ${PRODUCT_SELECTION_TITLE}
    Element Should Be Visible    ${PRODUCT_SELECTION_DESCRIPTION}

Complete Product Selection
    Wait Until Product Selection Screen Is Displayed
    Run Keyword And Ignore Error    Record Visual Timeline Event    PS0_PRODUCT_SELECTION_VISIBLE    PRODUCT_SELECTION    ${OUTPUT DIR}/visual_timeline
    ${checkboxes}=    Get WebElements    ${PRODUCT_SELECTION_CHECKBOXES}
    Should Not Be Empty    ${checkboxes}    PRODUCT_SELECTION_NO_ELIGIBLE_ITEMS
    Run Keyword And Ignore Error    Record Visual Timeline Event    PS1_ROWS_AVAILABLE    PRODUCT_SELECTION    ${OUTPUT DIR}/visual_timeline    screenshot=${False}
    ${selected_count}=    Count Selected Product Checkboxes    ${checkboxes}
    Run Keyword And Ignore Error    Record Visual Timeline Event    PS2_SELECTION_STATE    PRODUCT_SELECTION    ${OUTPUT DIR}/visual_timeline
    IF    ${selected_count} == 0
        Run Keyword And Ignore Error    Record Visual Timeline Event    PS3_SELECTION_ACTION_START    PRODUCT_SELECTION    ${OUTPUT DIR}/visual_timeline    action=SELECT_FIRST_ENABLED
        Select First Enabled Product Checkbox    ${checkboxes}
        ${selected_count}=    Count Selected Product Checkboxes    ${checkboxes}
        Run Keyword And Ignore Error    Record Visual Timeline Event    PS3_SELECTION_ACTION    PRODUCT_SELECTION    ${OUTPUT DIR}/visual_timeline    action=SELECT_FIRST_ENABLED_COMPLETED
    END
    Should Be True    ${selected_count} >= 1    PRODUCT_SELECTION_NO_ITEM_SELECTED
    Wait Until Element Is Visible    ${PRODUCT_SELECTION_CONFIRM}    ${NCBD_LOADING_TIMEOUT}
    Run Keyword And Ignore Error    Record Visual Timeline Event    PS4_CONFIRM_AVAILABLE    PRODUCT_SELECTION    ${OUTPUT DIR}/visual_timeline    screenshot=${False}
    Run Keyword And Ignore Error    Record Visual Timeline Event    CONFIRM_CLICK_START    PRODUCT_SELECTION    ${OUTPUT DIR}/visual_timeline    action=CLICK_CONFIRM    screenshot=${False}
    Click Element    ${PRODUCT_SELECTION_CONFIRM}
    Run Keyword And Ignore Error    Record Visual Timeline Event    PS5_CONFIRM_CLICK_END    LOADING_OR_INTERMEDIATE    ${OUTPUT DIR}/visual_timeline    action=CLICK_CONFIRM_COMPLETED

Count Selected Product Checkboxes
    [Arguments]    ${checkboxes}
    ${selected_count}=    Set Variable    ${0}
    FOR    ${checkbox}    IN    @{checkboxes}
        ${checked}=    Get Element Attribute    ${checkbox}    checked
        ${selected}=    Get Element Attribute    ${checkbox}    selected
        IF    '${checked}' == 'true' or '${selected}' == 'true'
            ${selected_count}=    Evaluate    ${selected_count} + 1
        END
    END
    RETURN    ${selected_count}

Select First Enabled Product Checkbox
    [Arguments]    ${checkboxes}
    FOR    ${checkbox}    IN    @{checkboxes}
        ${enabled}=    Get Element Attribute    ${checkbox}    enabled
        IF    '${enabled}' == 'true'
            Click Element    ${checkbox}
            RETURN
        END
    END
    Fail    PRODUCT_SELECTION_NO_ENABLED_ITEM
