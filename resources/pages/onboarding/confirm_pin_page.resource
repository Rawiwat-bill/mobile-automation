*** Settings ***
Library     AppiumLibrary
Library     Collections
Library     OperatingSystem
Resource    ../../../locators/android/onboarding/confirm_pin_locators.resource
Resource    ../../diagnostics/etb_observability.resource
Resource    ../../keywords/appium_expectations.resource


*** Variables ***
${CONFIRM_PIN_TIMEOUT}    60s


*** Keywords ***
Wait Until Confirm PIN Screen Is Displayed
    Wait Until Page Contains Element    ${CONFIRM_PIN_TITLE}    ${CONFIRM_PIN_TIMEOUT}
    Log    [PIN] Confirm PIN screen visible

Confirm PIN Screen Is Active
    [Documentation]    Prove the active re-enter-PIN screen from stable screen-specific markers; retry boundedly across UI transition/rerender without accepting generic security containers.
    ${status}    ${message}=    Run Keyword And Ignore Error
    ...    Wait Until Keyword Succeeds    3s    200ms    Confirm PIN Screen Markers Should Be Visible
    IF    '${status}' != 'PASS'
        Capture Confirm PIN Failure Evidence
        Fail    ${message}
    END

Capture Confirm PIN Failure Evidence
    Record ETB Evidence Capture    ${OUTPUT DIR}    confirm_pin_failure
    Log    [PIN] Confirm PIN failure evidence requested through shared private adapter.    WARN

Confirm PIN Screen Markers Should Be Visible
    ${back_visible}=    Run Keyword And Return Status    Element Should Be Visible Now    ${CONFIRM_PIN_BACK}
    ${zero_locator}=    Get From Dictionary    ${CONFIRM_PIN_KEYPAD}    0
    ${key_visible}=    Run Keyword And Return Status    Element Should Be Visible Now    ${zero_locator}
    Should Be True    ${back_visible} and ${key_visible}    CONFIRM_PIN_SCREEN_NOT_ACTIVE

Enter Confirm PIN Using Custom Keypad
    [Arguments]    ${pin}
    ${digits}=    Evaluate    list($pin)
    ${count}=    Get Length    ${digits}
    Should Be Equal As Integers    ${count}    6    Confirm PIN must be exactly 6 digits
    FOR    ${index}    ${digit}    IN ENUMERATE    @{digits}
        ${locator}=    Get From Dictionary    ${CONFIRM_PIN_KEYPAD}    ${digit}
        Confirm PIN Screen Is Active
        TRY
            ${element}=    Get WebElement    ${locator}
            Click Element    ${element}
        EXCEPT    *StaleElementReferenceException*    type=GLOB
            Confirm PIN Screen Is Active
            # A stale response can arrive after the tap was accepted. Re-clicking
            # the same digit risks duplicating input, so preserve the ambiguity.
            Fail    CONFIRM_PIN_INPUT_ACCEPTANCE_AMBIGUOUS digit_index=${index + 1}
        END
        ${more_digits}=    Evaluate    $index < ($count - 1)
        IF    ${more_digits}
            Confirm PIN Screen Is Active
        END
        Log    [PIN] Confirm digit ${index + 1}/6    WARN
    END
    Log    [PIN] Confirm PIN entry complete    WARN
