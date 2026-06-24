*** Settings ***
Library     AppiumLibrary
Library     Process
Resource    ../../../locators/android/onboarding/consent_screen_locators.resource


*** Variables ***
${CONSENT_TIMEOUT}    10s


*** Keywords ***
Wait Until Consent Screen Is Displayed
    Wait Until Element Is Visible    ${CONSENT_TITLE_TEXT}    ${CONSENT_TIMEOUT}
    Wait Until Element Is Visible    ${CONSENT_WEBVIEW}       ${CONSENT_TIMEOUT}

Scroll Down Consent Terms
    FOR    ${index}    IN RANGE    80
        ${found_end}=    Run Keyword And Return Status
        ...    Page Should Contain Text
        ...    I have read and understood

        IF    ${found_end}
            BREAK
        END

        Run Process    adb    shell    input    swipe    540    1850    540    800    150
    END

Tap Consent Accept Button
    Wait Until Consent Screen Is Displayed
    Scroll Down Consent Terms
    Wait Until Element Is Visible    ${CONSENT_ACCEPT_BUTTON}    10s
    Click Element                    ${CONSENT_ACCEPT_BUTTON}
    Wait Until Page Does Not Contain Element    ${CONSENT_TITLE_TEXT}    30s
