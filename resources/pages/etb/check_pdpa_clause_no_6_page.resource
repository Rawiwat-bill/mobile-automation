*** Settings ***
Library     AppiumLibrary
Resource    ../../../resources/app/app_constants.resource
Resource    ../../../locators/android/etb/check_pdpa_clause_no_6_locators.resource


*** Keywords ***
Wait Until Check PDPA Clause No6 Is Displayed
    [Documentation]    Wait until the Check PDPA Clause No6 screen is displayed.]
    Wait Until Element Is Visible    ${CHECK_PDPA_CLAUSE_NO_6_TITLE_TEXT}    ${NCBD_LOADING_TIMEOUT}

Scroll Down PDPA Clause No6
    [Documentation]    Scroll down the Check PDPA Clause No. 6 screen until the last paragraph is visible.

    FOR    ${i}    IN RANGE    1
        Swipe By Percent    50    75    50    10    100ms

        ${found}=    Run Keyword And Return Status
        ...    Page Should Contain Element
        ...    ${CHECK_PDPA_CLAUSE_NO_6_LAST_PARAGRAPH_TEXT}

        IF    ${found}
            Log    [PERF] PDPAClauseNo6SwipeCount=${i}
            BREAK
        END
    END

Accept PDPA Clause No6
    [Documentation]    Tapping the Accept button on the Check PDPA Clause No. 6 screen.
    Click Element    ${CHECK_PDPA_CLAUSE_NO_6_ACCEPT_BUTTON}

    # Go to face scan
