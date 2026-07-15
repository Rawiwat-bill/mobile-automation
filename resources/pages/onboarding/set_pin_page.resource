*** Settings ***
Library     AppiumLibrary
Library     Collections
Resource    ../../../locators/android/onboarding/set_pin_locators.resource


*** Variables ***
${SET_PIN_TIMEOUT}    60s


*** Keywords ***
Wait Until Set PIN Screen Is Displayed
    Wait Until Page Contains Element    ${SET_PIN_SCREEN_MARKER}    ${SET_PIN_TIMEOUT}
    Log    [PIN] Set PIN screen visible

Enter PIN Using Custom Keypad
    [Arguments]    ${pin}
    ${digits}=    Evaluate    list($pin)
    ${count}=    Get Length    ${digits}
    Should Be Equal As Integers    ${count}    6    PIN must be exactly 6 digits
    FOR    ${index}    ${digit}    IN ENUMERATE    @{digits}
        ${locator}=    Get From Dictionary    ${SET_PIN_KEYPAD}    ${digit}
        Click Element    ${locator}
        Log    [PIN] Entered digit ${index + 1}/6    WARN
        Sleep    0.3s
    END
    Log    [PIN] PIN entry complete    WARN
