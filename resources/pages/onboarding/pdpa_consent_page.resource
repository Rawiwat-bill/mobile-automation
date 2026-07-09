*** Settings ***
Library     AppiumLibrary
Library     OperatingSystem
Library     Process
Resource    ../../../locators/android/onboarding/pdpa_consent_locators.resource

*** Variables ***
${PDPA_TIMEOUT}    10s
${PDPA_TRANSITION_TIMEOUT}    15s
${PDPA_INVESTIGATION_DIR}    reports/investigation/after_pdpa
${PDPA_MAX_SWIPES}    12
${PDPA_SWIPE_COUNT}    0

*** Keywords ***
Wait Until PDPA Consent Screen Is Displayed
    Wait Until Element Is Visible    ${PDPA_SCREEN_HEADER}    ${PDPA_TIMEOUT}
    Wait Until Element Is Visible    ${PDPA_ACCEPT_BUTTON}    ${PDPA_TIMEOUT}

Scroll Down PDPA Content
    Set Test Variable    ${PDPA_SWIPE_COUNT}    0
    FOR    ${index}    IN RANGE    ${PDPA_MAX_SWIPES}
        Execute Adb Shell    input    swipe    540    1950    540    350    50
        ${next_count}=    Evaluate    ${PDPA_SWIPE_COUNT} + 1
        Set Test Variable    ${PDPA_SWIPE_COUNT}    ${next_count}
    END
    Log    [PERF] PDPASwipeCount=${PDPA_SWIPE_COUNT}

Tap PDPA Consent Accept Button
    [Documentation]    Scrolls PDPA content to bottom, then taps Accept.
    ...                Returns ${TRUE} if transition detected,
    ...                ${FALSE} if blocked. Captures evidence on blocker.
    Wait Until PDPA Consent Screen Is Displayed
    Scroll Down PDPA Content
    Click Element    ${PDPA_ACCEPT_BUTTON}
    Log    [PDPA] Accept clicked after scrolling PDPA content
    ${transition_passed}=    Run Keyword And Return Status
    ...    Wait Until Page Does Not Contain Element
    ...    ${PDPA_SCREEN_HEADER}
    ...    ${PDPA_TRANSITION_TIMEOUT}
    IF    ${transition_passed}
        Log    [PDPA] PDPA consent accepted, screen transitioned.
        RETURN    ${TRUE}
    END
    Capture PDPA Blocker Evidence
    RETURN    ${FALSE}

Capture PDPA Blocker Evidence
    Create Directory    ${PDPA_INVESTIGATION_DIR}
    Run Keyword And Ignore Error    Capture Page Screenshot    pdpa_blocker.png
    ${source}=    Get Source
    Create File    ${PDPA_INVESTIGATION_DIR}/pdpa_blocker.xml    ${source}    UTF-8
    ${element_count}=    Evaluate    str($source).count('<node')
    Create File    ${PDPA_INVESTIGATION_DIR}/pdpa_blocker_elements.txt
    ...    Total XML nodes: ${element_count}
    Log    [PDPA] Blocker evidence captured to ${PDPA_INVESTIGATION_DIR}/

Capture After PDPA Evidence
    [Arguments]    ${timestamp}
    Create Directory    ${PDPA_INVESTIGATION_DIR}
    ${source}=    Get Source
    Create File    ${PDPA_INVESTIGATION_DIR}/page_source_${timestamp}.xml    ${source}    UTF-8
    ${element_count}=    Evaluate    str($source).count('<node')
    Create File    ${PDPA_INVESTIGATION_DIR}/element_count_${timestamp}.txt
    ...    Total XML nodes: ${element_count}
    Log    [PDPA] After-PDPA evidence captured to ${PDPA_INVESTIGATION_DIR}/
