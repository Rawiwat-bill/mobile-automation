*** Settings ***
Documentation       ETB Product Selection page keywords.

Library             AppiumLibrary
Library             Collections
Library             ../../../libraries/product_selection_contract.py
Resource            ../../diagnostics/product_selection_observability.resource
Resource            ../../../resources/app/app_constants.resource
Resource            ../../../locators/android/etb/product_selection_locators.resource
Resource            ../../../resources/keywords/appium_expectations.resource

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
    Element Should Be Visible Now    ${PRODUCT_SELECTION_TITLE}
    Element Should Be Visible Now    ${PRODUCT_SELECTION_DESCRIPTION}

Complete Product Selection
    [Arguments]    ${expected_product_categories}=${NONE}
    Wait Until Product Selection Screen Is Displayed
    Record Product Selection Visible    ${OUTPUT DIR}
    ${checkboxes}=    Get WebElements    ${PRODUCT_SELECTION_CHECKBOXES}
    Should Not Be Empty    ${checkboxes}    PRODUCT_SELECTION_NO_ELIGIBLE_ITEMS
    Record Product Selection Rows Available    ${OUTPUT DIR}
    Assert Expected Product Categories Are Displayed    ${expected_product_categories}
    ${selected_count}=    Count Selected Product Checkboxes    ${checkboxes}
    Record Product Selection State    ${OUTPUT DIR}
    IF    ${selected_count} == 0
        Record Product Selection Action Start    ${OUTPUT DIR}
        Select First Enabled Product Checkbox    ${checkboxes}
        ${selected_count}=    Count Selected Product Checkboxes    ${checkboxes}
        Record Product Selection Action End    ${OUTPUT DIR}
    END
    Should Be True    ${selected_count} >= 1    PRODUCT_SELECTION_NO_ITEM_SELECTED
    Wait Until Element Is Visible    ${PRODUCT_SELECTION_CONFIRM}    ${NCBD_LOADING_TIMEOUT}
    Record Product Selection Confirm Available    ${OUTPUT DIR}
    Record Product Selection Confirm Start    ${OUTPUT DIR}
    Click Element    ${PRODUCT_SELECTION_CONFIRM}
    Record Product Selection Confirm End    ${OUTPUT DIR}

Assert Expected Product Categories Are Displayed
    [Arguments]    ${expected_categories}
    IF    $expected_categories is None
        RETURN
    END
    ${expected_count}=    Get Length    ${expected_categories}
    IF    ${expected_count} == 0
        RETURN
    END
    ${name_elements}=    Get WebElements    ${PRODUCT_SELECTION_PRODUCT_NAMES}
    Should Not Be Empty    ${name_elements}    PRODUCT_SELECTION_PRODUCT_NAMES_NOT_FOUND
    ${actual_names}=    Create List
    FOR    ${element}    IN    @{name_elements}
        ${name}=    Get Text    ${element}
        Append To List    ${actual_names}    ${name}
    END
    Validate Product Categories    ${actual_names}    ${expected_categories}

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
