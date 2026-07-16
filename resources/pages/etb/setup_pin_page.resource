*** Settings ***
Documentation       ETB setup pin page keywords.

Library             String
Library             AppiumLibrary
Resource            ../../../resources/app/app_constants.resource
Resource            ../../../locators/android/etb/setup_pin_locators.resource


*** Keywords ***
Wait Until Setup Pin Screen Is Displayed
    [Documentation]    Wait until the Setup Pin screen is displayed.
    Wait Until Element Is Visible    ${SETUP_PIN_TITLE_TEXT}    ${NCBD_LOADING_TIMEOUT}

Set Up PIN
    [Documentation]    Set up the PIN during the ETB onboarding process.
    [Arguments]    ${pin}    ${re_pin}=${False}
    @{list_pin}=    Split String To Characters    ${pin}
    ${text_checking}=    Set Variable If    not ${re_pin}    ${SETUP_PIN_TITLE_TEXT}    ${RE_ENTER_PIN_TITLE_TEXT}
    Wait Until Element Is Visible    ${text_checking}    ${NCBD_LOADING_TIMEOUT}
    FOR    ${pin}    IN    @{list_pin}
        ${key_pin}=    Replace String    ${SETUP_PIN_KEY_PIN}    {{pin}}    ${pin}
        Click Element    ${key_pin}
    END
