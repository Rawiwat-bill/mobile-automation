*** Settings ***
Library     AppiumLibrary
Resource    ../../keywords/scroll_keywords.resource
Resource    ../../../locators/android/onboarding/consent_screen_locators.resource


*** Variables ***
${CONSENT_TIMEOUT}    10s
${CONSENT_END_TEXT}    I have read and understood
${CONSENT_MAX_SWIPES}    55


*** Keywords ***
Wait Until Consent Screen Is Displayed
    Wait Until Element Is Visible    ${CONSENT_TITLE_TEXT}    ${CONSENT_TIMEOUT}
    Wait Until Element Is Visible    ${CONSENT_WEBVIEW}       ${CONSENT_TIMEOUT}

Scroll Down Consent Terms
    [Arguments]    ${max_swipes}=${CONSENT_MAX_SWIPES}
    ${accept_visible}=    Run Keyword And Return Status
    ...    Wait Until Element Is Visible    ${CONSENT_ACCEPT_BUTTON}    1s
    IF    ${accept_visible}
        Log    [CONSENT] Native Terms exposes actionable Accept without a readable bottom marker; no scroll required.
        RETURN    0
    END
    ${swipe_count}=    Scroll Down Consent Terms With Big Fling    ${max_swipes}
    Log    [PERF] SwipeCount=${swipe_count}

Tap Consent Accept Button
    ${consent_start}=    Evaluate    time.time()    modules=time
    Wait Until Consent Screen Is Displayed
    Scroll Down Consent Terms
    Wait Until Element Is Visible    ${CONSENT_ACCEPT_BUTTON}    3s
    ${element_rect}=    Get Element Rect    ${CONSENT_ACCEPT_BUTTON}
    ${center_x}=    Evaluate    int(${element_rect['x']} + (${element_rect['width']} / 2))
    ${center_y}=    Evaluate    int(${element_rect['y']} + (${element_rect['height']} / 2))
    ${accept_tap_time}=    Evaluate    time.time()    modules=time
    ${time_to_accept}=    Evaluate    round(${accept_tap_time} - ${consent_start}, 3)
    Log    [PERF] TimeToAcceptTap=${time_to_accept}
    Execute Adb Shell    input    tap    ${center_x}    ${center_y}
    Log    [CONSENT] Accept tapped via adb shell at ${center_x},${center_y}
    ${transition_passed}=    Run Keyword And Return Status
    ...    Wait Until Keyword Succeeds    30s    500ms    Consent Transition Marker Should Be Visible
    IF    not ${transition_passed}
        Log    [CONSENT] Navigation not observed after ADB tap; trying Appium fallback.    WARN
        Run Keyword And Ignore Error    Click Element    ${CONSENT_ACCEPT_BUTTON}
        ${transition_passed}=    Run Keyword And Return Status
        ...    Wait Until Keyword Succeeds    30s    500ms    Consent Transition Marker Should Be Visible
    END
    Log    [PERF] ConsentTransitionPassed=${transition_passed}
    IF    not ${transition_passed}
        Fail    Consent screen did not transition after tapping Accept.
    END
    ${consent_end}=    Evaluate    time.time()    modules=time
    ${consent_elapsed}=    Evaluate    round(${consent_end} - ${consent_start}, 3)
    Log    [PERF] ConsentElapsed=${consent_elapsed}

Consent Transition Marker Should Be Visible
    ${next_visible}=    Run Keyword And Return Status
    ...    Page Should Contain Element    xpath=//*[@text="Tell us about you"]
    ${source}=    Get Source
    ${aji_visible}=    Run Keyword And Return Status    Should Contain    ${source}    AJI-001
    Should Be True    ${next_visible} or ${aji_visible}
