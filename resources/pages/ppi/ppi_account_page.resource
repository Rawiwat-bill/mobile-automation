*** Settings ***
Documentation       PPI Account selection page keywords. (example)

Library             AppiumLibrary
Library             String
Resource            ../../../locators/android/ppi/ppi_account_locators.resource

*** Keywords ***
Wait Until PPI Account Screen Is Displayed
    Wait Until Element Is Visible    ${PPI_ACCOUNT_LIST}    ${NCBD_LOADING_TIMEOUT}

Select PPI Account
    [Documentation]    รับ label จาก test data — ห้าม hardcode เลขบัญชีใน page
    [Arguments]    ${account_label}
    ${locator}=    Format String    ${PPI_ACCOUNT_ITEM_TEMPLATE}    ${account_label}
    Wait Until Element Is Visible    ${locator}    ${NCBD_LOADING_TIMEOUT}
    Click Element    ${locator}

Tap PPI Account Next
    Wait Until Element Is Visible    ${PPI_ACCOUNT_NEXT_BUTTON}    ${NCBD_LOADING_TIMEOUT}
    Click Element    ${PPI_ACCOUNT_NEXT_BUTTON}
