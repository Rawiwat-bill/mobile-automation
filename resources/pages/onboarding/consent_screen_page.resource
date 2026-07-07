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
    ${swipe_count}=    Scroll Down Consent Terms With Big Fling    ${max_swipes}
    Log    [PERF] SwipeCount=${swipe_count}

Tap Consent Accept Button
    ${consent_start}=    Evaluate    time.time()    modules=time
    Wait Until Consent Screen Is Displayed
    Scroll Down Consent Terms
    Wait Until Element Is Visible    ${CONSENT_ACCEPT_BUTTON}    3s
    ${accept_tap_time}=    Evaluate    time.time()    modules=time
    ${time_to_accept}=    Evaluate    round(${accept_tap_time} - ${consent_start}, 3)
    Log    [PERF] TimeToAcceptTap=${time_to_accept}
    Click Element                    ${CONSENT_ACCEPT_BUTTON}
    ${transition_passed}=    Run Keyword And Return Status
    ...    Wait Until Page Does Not Contain Element
    ...    ${CONSENT_TITLE_TEXT}
    ...    30s
    Log    [PERF] ConsentTransitionPassed=${transition_passed}
    IF    not ${transition_passed}
        Fail    Consent screen did not transition after tapping Accept.
    END
    ${consent_end}=    Evaluate    time.time()    modules=time
    ${consent_elapsed}=    Evaluate    round(${consent_end} - ${consent_start}, 3)
    Log    [PERF] ConsentElapsed=${consent_elapsed}
