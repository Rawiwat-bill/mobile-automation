*** Settings ***
Library     AppiumLibrary


*** Keywords ***
Hide Keyboard Custom
    [Documentation]    Hide the keyboard if it is shown, and press the Enter key to dismiss it.
    ${keyboard_found}=    Is Keyboard Shown
    IF    ${keyboard_found}
        Hide Keyboard
        Press Keycode    66
    END
