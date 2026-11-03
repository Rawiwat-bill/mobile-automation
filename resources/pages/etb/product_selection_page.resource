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

Observe Product Selection Natural Continuation
    [Documentation]    Wait for a visible UI state change after the product list is initially absent.
    ${wait_status}    ${wait_result}=    Run Keyword And Ignore Error
    ...    Wait Until Keyword Succeeds    ${NCBD_LOADING_TIMEOUT}    2s
    ...    Probe Product Selection Natural State
    IF    '${wait_status}' == 'PASS'
        RETURN    ${wait_result}
    END
    Record Product Selection List Not Rendered    ${OUTPUT DIR}
    Log    PRODUCT_LIST_NOT_RENDERED_FINAL    WARN
    RETURN    PRODUCT_LIST_NOT_RENDERED

Probe Product Selection Natural State
    ${source}=    Get Source
    ${rows_visible}=    Run Keyword And Return Status
    ...    Should Contain Any    ${source}
    ...    screenProductSelection_flatListCardsTouchableOpacity_
    ...    screenProductSelection_flatListCardsCheckBox_
    IF    ${rows_visible}
        RETURN    ROWS_AVAILABLE
    END
    ${confirm_visible}=    Run Keyword And Return Status
    ...    Element Should Be Visible Now    ${PRODUCT_SELECTION_CONFIRM}
    IF    ${confirm_visible}
        ${confirm_enabled}=    Run Keyword And Return Status
        ...    Element Should Be Enabled    ${PRODUCT_SELECTION_CONFIRM}
        IF    ${confirm_enabled}
            RETURN    CONFIRM_AVAILABLE_WITHOUT_ITEMS
        END
    END
    ${product_screen_visible}=    Run Keyword And Return Status
    ...    Should Contain Any    ${source}
    ...    screenProductSelection_textTitle
    ...    screenProductSelection_textDescription
    IF    ${product_screen_visible}
        Fail    PRODUCT_LIST_NOT_RENDERED_WAITING
    END
    ${success_visible}=    Run Keyword And Return Status
    ...    Should Contain Any    ${source}
    ...    You're all set!
    ...    You’re all set!
    ...    Let's go
    ...    Let’s go
    IF    ${success_visible}
        RETURN    APP_CONTINUED_WITHOUT_SELECTION
    END
    RETURN    PRODUCT_SELECTION_SCREEN_CHANGED

Complete Product Selection
    [Arguments]    ${expected_product_categories}=${NONE}    ${diagnostic_mode}=${FALSE}    ${category_policy}=ALL
    Wait Until Product Selection Screen Is Displayed
    Record Product Selection Visible    ${OUTPUT DIR}
    ${tc004_diagnostic}=    Get Variable Value    ${ETB_TC004_DIAGNOSTIC}    ${FALSE}
    ${manual_pause}=    Get Environment Variable    ETB_PAUSE_AT_PRODUCT_SELECTION    FALSE
    IF    ${tc004_diagnostic} and '${manual_pause}' == 'TRUE'
        ${settled_state}=    Observe Product Selection Natural Continuation
        Capture Page Screenshot    ${OUTPUT DIR}/product_selection_manual_inspection.png
        Log    TC004_PAUSED_AT_PRODUCT_SELECTION state=${settled_state}    WARN
        Run    python3 -c "input('TC004 paused at Product Selection; press Enter to resume')"
    END
    IF    ${diagnostic_mode}
        ${rows}=    Get Product Selection Rows Safely
        ${row_count}=    Get Length    ${rows}
        IF    ${row_count} == 0
            Record Product Selection List Not Rendered    ${OUTPUT DIR}
            Log    PRODUCT_LIST_NOT_RENDERED    WARN
            ${natural_state}=    Observe Product Selection Natural Continuation
            IF    '${natural_state}' == 'ROWS_AVAILABLE'
                ${rows}=    Get Product Selection Rows Safely
                ${row_count}=    Get Length    ${rows}
                IF    ${row_count} == 0
                    RETURN    PRODUCT_LIST_NOT_RENDERED
                END
            ELSE
                RETURN    ${natural_state}
            END
        END
    END
    Wait Until Product Selection Rows Are Settled
    ${rows}=    Get Product Selection Rows Safely
    Should Not Be Empty    ${rows}    PRODUCT_SELECTION_NO_ELIGIBLE_ITEMS
    Record Product Selection Rows Available    ${OUTPUT DIR}
    Wait Until Keyword Succeeds    ${NCBD_LOADING_TIMEOUT}    500ms
    ...    Assert Expected Product Categories Are Displayed    ${expected_product_categories}    ${category_policy}
    ${selected}=    Run Keyword And Return Status    Product Selection Should Show Selected Items
    Record Product Selection State    ${OUTPUT DIR}
    IF    not ${selected}
        Record Product Selection Action Start    ${OUTPUT DIR}
        ${row}=    Wait Until Keyword Succeeds    ${NCBD_LOADING_TIMEOUT}    500ms    Find First Supported Product Row
        Click Element    ${row}
        Wait Until Keyword Succeeds    ${NCBD_LOADING_TIMEOUT}    500ms    Product Selection Should Show Selected Items
        Record Product Selection Action End    ${OUTPUT DIR}
    END
    ${confirm_locator}=    Wait Until Keyword Succeeds    ${NCBD_LOADING_TIMEOUT}    500ms
    ...    Get Actionable Product Selection Confirm Locator
    Record Product Selection Confirm Available    ${OUTPUT DIR}
    Record Product Selection Confirm Start    ${OUTPUT DIR}
    Click Element    ${confirm_locator}
    Record Product Selection Confirm End    ${OUTPUT DIR}
    RETURN    COMPLETED

Get Actionable Product Selection Confirm Locator
    [Documentation]    Re-acquire Confirm after Product Selection loading/re-render instead of relying on one Appium lookup.
    ${candidates}=    Create List
    ...    ${PRODUCT_SELECTION_CONFIRM}
    ...    ${PRODUCT_SELECTION_CONFIRM_RESOURCE}
    ...    ${PRODUCT_SELECTION_CONFIRM_BUTTON}
    FOR    ${locator}    IN    @{candidates}
        ${visible}=    Run Keyword And Return Status    Element Should Be Visible Now    ${locator}
        IF    not ${visible}
            CONTINUE
        END
        ${enabled}=    Run Keyword And Return Status    Element Should Be Enabled    ${locator}
        IF    ${enabled}
            RETURN    ${locator}
        END
    END
    Fail    PRODUCT_SELECTION_CONFIRM_NOT_ACTIONABLE_YET

Get Product Selection Rows Safely
    ${status}    ${result}=    Run Keyword And Ignore Error
    ...    Get WebElements    ${PRODUCT_SELECTION_ROWS}
    IF    '${status}' == 'PASS'
        RETURN    ${result}
    END
    ${empty}=    Create List
    RETURN    ${empty}

Wait Until Product Selection Rows Are Settled
    Wait Until Keyword Succeeds    ${NCBD_LOADING_TIMEOUT}    500ms
    ...    Product Selection Rows Should Be Ready

Product Selection Rows Should Be Ready
    ${name_elements}=    Get WebElements    ${PRODUCT_SELECTION_PRODUCT_NAMES}
    Should Not Be Empty    ${name_elements}    PRODUCT_SELECTION_ROWS_NOT_RENDERED
    FOR    ${element}    IN    @{name_elements}
        ${name}=    Get Text    ${element}
        IF    '${name}' != ''
            RETURN
        END
    END
    Fail    PRODUCT_SELECTION_ROWS_NOT_SETTLED

Assert Expected Product Categories Are Displayed
    [Arguments]    ${expected_categories}    ${category_policy}=ALL
    IF    $expected_categories is None
        RETURN
    END
    ${expected_count}=    Get Length    ${expected_categories}
    IF    '${category_policy}' == 'ALL' and ${expected_count} == 0
        RETURN
    END
    ${name_elements}=    Get WebElements    ${PRODUCT_SELECTION_PRODUCT_NAMES}
    Should Not Be Empty    ${name_elements}    PRODUCT_SELECTION_PRODUCT_NAMES_NOT_FOUND
    ${actual_names}=    Create List
    FOR    ${element}    IN    @{name_elements}
        ${name}=    Get Text    ${element}
        Append To List    ${actual_names}    ${name}
    END
    Validate Product Categories    ${actual_names}    ${expected_categories}    ${category_policy}

Product Selection Should Show Selected Items
    [Documentation]    The visible summary is authoritative; native checkbox attributes stay false on Build 208.
    ${summaries}=    Get WebElements    ${PRODUCT_SELECTION_SELECTED_SUMMARY}
    FOR    ${summary}    IN    @{summaries}
        ${visible}=    Run Keyword And Return Status    Element Should Be Visible Now    ${summary}
        ${text}=    Get Text    ${summary}
        ${positive}=    Run Keyword And Return Status    Should Match Regexp    ${text}    ^[1-9][0-9]* selected$
        IF    ${visible} and ${positive}
            RETURN
        END
    END
    Fail    PRODUCT_SELECTION_NO_ITEM_SELECTED

Find First Supported Product Row
    [Documentation]    Find a real displayed, enabled account row containing a supported product name.
    ${rows}=    Get Product Selection Rows Safely
    ${supported_categories}=    Create List    Saving    e-Saving
    FOR    ${row}    IN    @{rows}
        ${visible}=    Run Keyword And Return Status    Element Should Be Visible Now    ${row}
        ${enabled}=    Get Element Attribute    ${row}    enabled
        IF    not ${visible} or '${enabled}' != 'true'
            CONTINUE
        END
        ${name_elements}=    Call Method    ${row}    find_elements    xpath    ${PRODUCT_SELECTION_ROW_NAME_XPATH}
        FOR    ${element}    IN    @{name_elements}
            ${name}=    Get Text    ${element}
            ${names}=    Create List    ${name}
            ${supported}=    Run Keyword And Return Status    Validate Product Categories    ${names}    ${supported_categories}    ANY_SUPPORTED
            IF    ${supported}
                RETURN    ${row}
            END
        END
    END
    Fail    PRODUCT_SELECTION_NO_ENABLED_SUPPORTED_ROW
