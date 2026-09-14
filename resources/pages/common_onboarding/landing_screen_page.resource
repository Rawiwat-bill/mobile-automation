*** Settings ***
Library     AppiumLibrary
Library     ../../../libraries/startup_state.py
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

Landing Action Should Be Gone
    [Documentation]    Verify that neither Landing action remains visible after the action tap.
    ${is_skip_visible}=    Run Keyword And Return Status    Element Should Be Visible    ${LANDING_SKIP_BUTTON}
    ${is_ready_visible}=    Run Keyword And Return Status    Element Should Be Visible    ${LANDING_READY_BUTTON}
    Should Not Be True    ${is_skip_visible} or ${is_ready_visible}    LANDING_ACTION_DID_NOT_TRANSITION

Switch Landing Language To Thai
    [Documentation]    Switch the landing screen language to Thai
    Wait Until Element Is Visible    ${LANDING_LANGUAGE_THAI_BUTTON}    ${LANDING_TIMEOUT}
    Click Element    ${LANDING_LANGUAGE_THAI_BUTTON}

Switch Landing Language To English
    [Documentation]    Switch the landing screen language to English
    ${is_sit}=    Evaluate    '${APP_PACKAGE}' == 'com.bangkokbank.blue.sit'
    IF    ${is_sit}
        ${switch_visible}=    Run Keyword And Return Status
        ...    Element Should Be Visible    ${LANDING_LANGUAGE_SWITCH}
        IF    ${switch_visible}
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
            RETURN
        END
        ${english_marker_visible}=    Run Keyword And Return Status
        ...    Element Should Be Visible    ${LANDING_LANGUAGE_ENGLISH_BUTTON}
        ${title_visible}=    Run Keyword And Return Status
        ...    Element Should Be Visible    ${LANDING_TITLE_TEXT}
        ${skip_visible}=    Run Keyword And Return Status
        ...    Element Should Be Visible    ${LANDING_SKIP_BUTTON}
        IF    ${english_marker_visible} and ${title_visible} and ${skip_visible}
            Log    SIT_LANDING_ALREADY_ENGLISH_PARENT_ABSENT
            RETURN
        END
        Fail    SIT_LANGUAGE_STATE_NOT_PROVEN
    END
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
    ${skip_rect}=    Get Element Rect    ${LANDING_SKIP_BUTTON}
    ${skip_x}=    Evaluate    int(${skip_rect['x']} + (${skip_rect['width']} / 2))
    ${skip_y}=    Evaluate    int(${skip_rect['y']} + (${skip_rect['height']} / 2))
    Execute Adb Shell    input    tap    ${skip_x}    ${skip_y}

Tap Landing Ready Button
    [Documentation]    Tap the currently visible Landing action using fresh bounds acquired after any language/layout change.
    ${skip_visible}=    Run Keyword And Return Status    Element Should Be Visible    ${LANDING_SKIP_BUTTON}
    IF    ${skip_visible}
        ${action_rect}=    Get Element Rect    ${LANDING_SKIP_BUTTON}
        ${action_name}=    Set Variable    SKIP
    ELSE
        Wait Until Element Is Visible    ${LANDING_READY_BUTTON}    ${LANDING_TIMEOUT}
        ${action_rect}=    Get Element Rect    ${LANDING_READY_BUTTON}
        ${action_name}=    Set Variable    READY
    END
    Set Suite Variable    ${LANDING_ACTION_RECT}    ${action_rect}
    ${center_x}=    Evaluate    int(${action_rect['x']} + (${action_rect['width']} / 2))
    ${center_y}=    Evaluate    int(${action_rect['y']} + (${action_rect['height']} / 2))
    Execute Adb Shell    input    tap    ${center_x}    ${center_y}
    Log    LANDING_ACTION_TAPPED=ADB_FRESH_BOUNDS action=${action_name}    INFO
    IF    $action_name == 'SKIP'
        Wait Until Keyword Succeeds    10s    500ms    Landing Ready Should Replace Skip
        Log    LANDING_ACTION_TRANSITION=SKIP_TO_READY    INFO
        ${action_rect}=    Get Element Rect    ${LANDING_READY_BUTTON}
        Set Suite Variable    ${LANDING_ACTION_RECT}    ${action_rect}
        ${center_x}=    Evaluate    int(${action_rect['x']} + (${action_rect['width']} / 2))
        ${center_y}=    Evaluate    int(${action_rect['y']} + (${action_rect['height']} / 2))
        Execute Adb Shell    input    tap    ${center_x}    ${center_y}
        Log    LANDING_ACTION_TAPPED=ADB_FRESH_BOUNDS action=READY    INFO
    END
    Wait Until Keyword Succeeds    10s    500ms    Landing Action Should Be Gone

Landing Ready Should Replace Skip
    [Documentation]    Read-only proof of carousel progression; never retry the action tap.
    ${is_skip_visible}=    Run Keyword And Return Status    Element Should Be Visible    ${LANDING_SKIP_BUTTON}
    ${is_ready_visible}=    Run Keyword And Return Status    Element Should Be Visible    ${LANDING_READY_BUTTON}
    Should Not Be True    ${is_skip_visible}    LANDING_SKIP_DID_NOT_REACH_READY
    Should Be True    ${is_ready_visible}    LANDING_SKIP_DID_NOT_REACH_READY

Wait For Landing Destination
    [Documentation]    Prove a caller-supplied destination or fail fast on the exact Landing full-screen Gub state; never tap the unknown CTA.
    [Arguments]    ${destination_locator}    ${timeout}
    ${observed}=    Run Keyword And Return Status
    ...    Wait Until Keyword Succeeds    ${timeout}    500ms    Landing Destination Marker Should Be Visible    ${destination_locator}
    IF    not ${observed}
        Fail    LANDING_DESTINATION_NOT_OBSERVED
    END
    ${full_screen_gub}=    Run Keyword And Return Status
    ...    Element Should Be Visible    ${LANDING_FULL_SCREEN_GUB_CTA}
    IF    ${full_screen_gub}
        Fail    LANDING_FULL_SCREEN_GUB_AFTER_ACTION
    END
    RETURN    NEXT

Landing Destination Marker Should Be Visible
    [Documentation]    Read-only poll that becomes terminal when either the expected destination or exact full-screen Gub marker is visible.
    [Arguments]    ${destination_locator}
    ${destination_visible}=    Run Keyword And Return Status    Element Should Be Visible    ${destination_locator}
    ${full_screen_gub}=    Run Keyword And Return Status
    ...    Element Should Be Visible    ${LANDING_FULL_SCREEN_GUB_CTA}
    Should Be True    ${destination_visible} or ${full_screen_gub}
