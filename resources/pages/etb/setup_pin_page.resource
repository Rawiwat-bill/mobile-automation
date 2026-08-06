*** Settings ***
Documentation       ETB setup pin page keywords.

Library             String
Library             AppiumLibrary
Resource            ../../../resources/app/app_constants.resource
Resource            ../../../locators/android/etb/setup_pin_locators.resource
Resource            ../../../resources/pages/onboarding/set_pin_page.resource
Resource            ../../../resources/pages/onboarding/confirm_pin_page.resource


*** Keywords ***
Wait Until Setup Pin Screen Is Displayed
    [Documentation]    Wait until the Setup Pin screen is displayed.
    Wait Until Element Is Visible    ${SETUP_PIN_TITLE_TEXT}    ${NCBD_LOADING_TIMEOUT}

Set Up PIN
    [Documentation]    Reuse the runtime-proven NTB custom-keypad interaction for ETB setup and confirmation.
    [Arguments]    ${pin}    ${re_pin}=${False}
    IF    ${re_pin}
        Wait Until Element Is Visible    ${RE_ENTER_PIN_TITLE_TEXT}    ${NCBD_LOADING_TIMEOUT}
        Enter Confirm PIN Using Custom Keypad    ${pin}
    ELSE
        Wait Until Element Is Visible    ${SETUP_PIN_TITLE_TEXT}    ${NCBD_LOADING_TIMEOUT}
        Enter PIN Using Custom Keypad    ${pin}
    END
