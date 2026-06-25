*** Settings ***
Library     AppiumLibrary
Library     Process
Resource    ../../../locators/android/onboarding/consent_screen_locators.resource


*** Variables ***
${CONSENT_TIMEOUT}    10s
${CONSENT_SWIPE_COUNT}    0
${CONSENT_END_CHECK_COUNT}    0
${CONSENT_END_TEXT}    I have read and understood
${CONSENT_MAX_SWIPES}    12
${CONSENT_FIRST_END_CHECK_AT}    4
${CONSENT_END_CHECK_INTERVAL}    2


*** Keywords ***
Wait Until Consent Screen Is Displayed
    Wait Until Element Is Visible    ${CONSENT_TITLE_TEXT}    ${CONSENT_TIMEOUT}
    Wait Until Element Is Visible    ${CONSENT_WEBVIEW}       ${CONSENT_TIMEOUT}

Scroll Down Consent Terms
    Set Test Variable    ${CONSENT_SWIPE_COUNT}    0
    Set Test Variable    ${CONSENT_END_CHECK_COUNT}    0
    FOR    ${index}    IN RANGE    ${CONSENT_MAX_SWIPES}
        Run Process    adb    shell    input    swipe    540    1950    540    350    50
        ${next_count}=    Evaluate    ${CONSENT_SWIPE_COUNT} + 1
        Set Test Variable    ${CONSENT_SWIPE_COUNT}    ${next_count}
        ${past_first_check}=    Evaluate    ${CONSENT_SWIPE_COUNT} >= ${CONSENT_FIRST_END_CHECK_AT}
        ${on_check_interval}=    Evaluate    (${CONSENT_SWIPE_COUNT} - ${CONSENT_FIRST_END_CHECK_AT}) % ${CONSENT_END_CHECK_INTERVAL} == 0
        IF    ${past_first_check} and ${on_check_interval}
            ${next_check_count}=    Evaluate    ${CONSENT_END_CHECK_COUNT} + 1
            Set Test Variable    ${CONSENT_END_CHECK_COUNT}    ${next_check_count}
            ${found_end}=    Run Keyword And Return Status
            ...    Page Should Contain Text
            ...    ${CONSENT_END_TEXT}
            IF    ${found_end}
                BREAK
            END
        END
    END
    Log    [PERF] SwipeCount=${CONSENT_SWIPE_COUNT}
    Log    [PERF] EndTextChecks=${CONSENT_END_CHECK_COUNT}

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
