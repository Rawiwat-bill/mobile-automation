*** Settings ***
Library    AppiumLibrary
Resource   benchmark_base.resource


*** Variables ***
${SCROLL_SWIPE_START_X}      540
${SCROLL_SWIPE_START_Y}      1950
${SCROLL_SWIPE_END_Y}        350
${SCROLL_SWIPE_DURATION}     50


*** Keywords ***
Consent Scroll - Hardcoded Swipe
    [Arguments]    ${max_swipes}=15    ${check_interval}=1
    ${swipe_count}=    Set Variable    0
    ${found_end}=    Set Variable    ${False}
    WHILE    ${swipe_count} < ${max_swipes}
        ${should_check}=    Evaluate    ${swipe_count} % ${check_interval} == 0
        IF    ${should_check}
            ${found_end}=    Run Keyword And Return Status
            ...    Page Should Contain Text    I have read and understood
            IF    ${found_end}
                BREAK
            END
        END
        Execute Adb Shell    input    swipe
        ...    ${SCROLL_SWIPE_START_X}    ${SCROLL_SWIPE_START_Y}
        ...    ${SCROLL_SWIPE_START_X}    ${SCROLL_SWIPE_END_Y}
        ...    ${SCROLL_SWIPE_DURATION}
        Record ADB Call
        Record Scroll    0.3
        ${swipe_count}=    Evaluate    ${swipe_count} + 1
    END
    RETURN    ${found_end}

Consent Scroll - Dynamic Swipe
    [Arguments]    ${max_swipes}=20    ${end_check_interval}=2
    ${result}=    Consent Scroll - Hardcoded Swipe
    ...    max_swipes=${max_swipes}    check_interval=${end_check_interval}
    RETURN    ${result}

Consent Scroll - Scrollbar Drag
    [Arguments]    ${start_x}    ${start_y}    ${end_x}    ${end_y}    ${duration}    ${label}
    Start Phase    scroll_scrollbar_${label}
    Execute Adb Shell    input    swipe    ${start_x}    ${start_y}    ${end_x}    ${end_y}    ${duration}
    Record ADB Call
    Record Scroll    0.3
    ${accept_visible}=    Run Keyword And Return Status
    ...    Element Should Be Visible    ${BENCHMARK_CONSENT_ACCEPT}
    Log    [BENCHMARK] Scrollbar Drag ${label}: accept_visible=${accept_visible}
    End Phase
    RETURN    ${accept_visible}
