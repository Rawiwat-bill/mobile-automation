*** Settings ***
Library     AppiumLibrary
Resource    ../../../locators/android/common_onboarding/landing_screen_locators.resource


*** Variables ***
${LANDING_TIMEOUT}      60s
${SIGN_UP_TIMEOUT}      10s


*** Keywords ***
Wait Until Landing Screen Is Displayed
    [Documentation]    Wait until the landing screen is displayed
    Landing Screen Should Be Visible

Landing Screen Should Be Visible
    [Documentation]    Verify that the landing screen is visible
    Wait Until Keyword Succeeds    ${LANDING_TIMEOUT}    500ms    Landing Action Should Be Visible

Landing Action Should Be Visible
    [Documentation]    Verify that either the "Skip" or "Ready" button is visible on the landing screen
    ${is_skip_visible}=    Run Keyword And Return Status    Element Should Be Visible    ${LANDING_SKIP_BUTTON}
    IF    ${is_skip_visible}    RETURN
    ${is_ready_visible}=    Run Keyword And Return Status    Element Should Be Visible    ${LANDING_READY_BUTTON}
    Should Be True    ${is_ready_visible}

Switch Landing Language To Thai
    [Documentation]    Switch the landing screen language to Thai
    Wait Until Element Is Visible    ${LANDING_LANGUAGE_THAI_BUTTON}    ${LANDING_TIMEOUT}
    Click Element    ${LANDING_LANGUAGE_THAI_BUTTON}

Switch Landing Language To English
    [Documentation]    Switch the landing screen language to English
    Wait Until Element Is Visible    ${LANDING_LANGUAGE_SWITCH}    ${LANDING_TIMEOUT}
    ${language_description}=    Get Element Attribute    ${LANDING_LANGUAGE_SWITCH}    content-desc
    ${english_selected}=    Run Keyword And Return Status
    ...    Should Contain    ${language_description}    English selected
    IF    ${english_selected}
        RETURN
    END
    ${switch_rect}=    Get Element Rect    ${LANDING_LANGUAGE_SWITCH}
    ${center_x}=    Evaluate    int(${switch_rect['x']} + (${switch_rect['width']} / 2))
    ${center_y}=    Evaluate    int(${switch_rect['y']} + (${switch_rect['height']} / 2))
    Execute Adb Shell    input    tap    ${center_x}    ${center_y}
    Wait Until Element Is Visible
    ...    xpath=//*[@resource-id="screenLanding_languageSwitch" and contains(@content-desc,"English selected")]
    ...    ${LANDING_TIMEOUT}

Skip Landing Screen
    [Documentation]    Skip the landing screen by tapping the "Skip" button
    Wait Until Element Is Visible    ${LANDING_SKIP_BUTTON}    ${LANDING_TIMEOUT}
    Click Element    ${LANDING_SKIP_BUTTON}

Tap Landing Ready Button
    [Documentation]    Tap the "Ready" button on the landing screen
    ${is_ready_visible}=    Run Keyword And Return Status    Element Should Be Visible    ${LANDING_READY_BUTTON}
    IF    ${is_ready_visible}
        Click Element    ${LANDING_READY_BUTTON}
    ELSE
        Skip Landing Screen
        Wait Until Element Is Visible    ${LANDING_READY_BUTTON}    ${LANDING_TIMEOUT}
        Click Element    ${LANDING_READY_BUTTON}
    END
