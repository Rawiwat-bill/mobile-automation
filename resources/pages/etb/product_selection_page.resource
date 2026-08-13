*** Settings ***
Documentation       ETB Product Selection page keywords.

Library             AppiumLibrary
Resource            ../../../locators/android/etb/product_selection_locators.resource

*** Keywords ***
Wait Until Product Selection Screen Is Displayed
    Wait Until Element Is Visible    ${PRODUCT_SELECTION_TITLE}    ${NCBD_LOADING_TIMEOUT}
    Wait Until Element Is Visible    ${PRODUCT_SELECTION_DESCRIPTION}    ${NCBD_LOADING_TIMEOUT}

Product Selection Screen Should Be Displayed
    Element Should Be Visible    ${PRODUCT_SELECTION_TITLE}
    Element Should Be Visible    ${PRODUCT_SELECTION_DESCRIPTION}
