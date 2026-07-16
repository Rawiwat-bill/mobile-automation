*** Settings ***
Library     AppiumLibrary
Library     Collections
Resource    ../../../locators/android/onboarding/confirm_pin_locators.resource


*** Variables ***
${CONFIRM_PIN_TIMEOUT}    60s


*** Keywords ***
Wait Until Confirm PIN Screen Is Displayed
    Wait Until Page Contains Element    ${CONFIRM_PIN_TITLE}    ${CONFIRM_PIN_TIMEOUT}
    Log    [PIN] Confirm PIN screen visible

Wait Until Enter PIN Screen Is Displayed
    Wait Until Page Contains Element    ${ENTER_PIN_TITLE}    ${CONFIRM_PIN_TIMEOUT}
    Log    [PIN] Enter PIN screen visible

Enter Confirm PIN Using Custom Keypad
    [Arguments]    ${pin}
    ${digits}=    Evaluate    list($pin)
    ${count}=    Get Length    ${digits}
    Should Be Equal As Integers    ${count}    6    Confirm PIN must be exactly 6 digits
    FOR    ${index}    ${digit}    IN ENUMERATE    @{digits}
        ${locator}=    Get From Dictionary    ${CONFIRM_PIN_KEYPAD}    ${digit}
        Click Element    ${locator}
        Log    [PIN] Confirm digit ${index + 1}/6    WARN
        Sleep    0.3s
    END
    Log    [PIN] Confirm PIN entry complete    WARN
