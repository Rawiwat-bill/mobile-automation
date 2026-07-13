*** Settings ***
Library     AppiumLibrary
Resource    ../../../locators/android/common_onboarding/terms_and_conditions_locators.resource


*** Variables ***
${TERMS_AND_CONDITIONS_TIMEOUT}     5s


*** Keywords ***
Wait Until Terms And Conditions Screen Is Displayed
    [Documentation]    Wait until the Terms and Conditions screen is displayed.
    Wait Until Element Is Visible    ${TERMS_AND_CONDITIONS_TITLE_TEXT}    ${TERMS_AND_CONDITIONS_TIMEOUT}
    Wait Until Element Is Visible    ${TERMS_AND_CONDITIONS_WEBVIEW}    ${TERMS_AND_CONDITIONS_TIMEOUT}

Scroll Down Terms And Conditions
    [Documentation]    Scroll down the Terms and Conditions screen until the last paragraph is visible.

    FOR    ${i}    IN RANGE    5
        Swipe By Percent    50    75    50    10    100ms
        Swipe By Percent    50    75    50    10    100ms
        Swipe By Percent    50    75    50    10    100ms
        Swipe By Percent    50    75    50    10    100ms
        Swipe By Percent    50    75    50    10    100ms

        ${found}=    Run Keyword And Return Status
        ...    Page Should Contain Element
        ...    ${TERMS_AND_CONDITIONS_LAST_PARAGRAPH_TEXT}

        IF    ${found}
            Log    [PERF] TermsAndConditionsSwipeCount=${i}
            BREAK
        END
    END

Accept Terms And Conditions
    [Documentation]    Tapping the Accept button.
    Click Element    ${TERMS_AND_CONDITIONS_ACCEPT_BUTTON}
