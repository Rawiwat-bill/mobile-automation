*** Settings ***
Library     AppiumLibrary
Resource    ../../../locators/android/onboarding/landing_screen_locators.resource


*** Variables ***
${LANDING_TIMEOUT}    30s


*** Keywords ***
Wait Until Landing Screen Is Displayed
    Landing Screen Should Be Visible

Landing Screen Should Be Visible
    Wait Until Keyword Succeeds    ${LANDING_TIMEOUT}    500ms    Landing Action Should Be Visible

Landing Action Should Be Visible
    ${is_skip_visible}=     Run Keyword And Return Status    Element Should Be Visible    ${LANDING_SKIP_BUTTON}
    IF    ${is_skip_visible}
        RETURN
    END
    ${is_ready_visible}=    Run Keyword And Return Status    Element Should Be Visible    ${LANDING_READY_BUTTON}
    Should Be True    ${is_ready_visible}

Switch Landing Language To Thai
    Wait Until Element Is Visible    ${LANDING_LANGUAGE_THAI_BUTTON}    ${LANDING_TIMEOUT}
    Click Element                    ${LANDING_LANGUAGE_THAI_BUTTON}

Switch Landing Language To English
    Wait Until Element Is Visible    ${LANDING_LANGUAGE_ENGLISH_BUTTON}    ${LANDING_TIMEOUT}
    Click Element                    ${LANDING_LANGUAGE_ENGLISH_BUTTON}

Skip Landing Screen
    Wait Until Element Is Visible    ${LANDING_SKIP_BUTTON}    ${LANDING_TIMEOUT}
    Click Element                    ${LANDING_SKIP_BUTTON}

Tap Landing Ready Button
    ${is_ready_visible}=    Run Keyword And Return Status    Element Should Be Visible    ${LANDING_READY_BUTTON}
    IF    ${is_ready_visible}
        Click Element    ${LANDING_READY_BUTTON}
    ELSE
        Skip Landing Screen
        Wait Until Element Is Visible    ${LANDING_READY_BUTTON}    ${LANDING_TIMEOUT}
        Click Element                    ${LANDING_READY_BUTTON}
    END
