*** Settings ***
Documentation       PPI Landing page keywords. (example)
...
...                 ไฟล์ตัวอย่างสำหรับทีม PPI — page resource เป็นเจ้าของ
...                 การ interact กับ 1 screen เท่านั้น ห้ามมี business rule

Library             AppiumLibrary
Resource            ../../../locators/android/ppi/ppi_landing_locators.resource

*** Keywords ***
Wait Until PPI Landing Screen Is Displayed
    Wait Until Element Is Visible    ${PPI_LANDING_TITLE}    ${NCBD_LOADING_TIMEOUT}

PPI Landing Screen Should Be Displayed
    Element Should Be Visible    ${PPI_LANDING_TITLE}

Tap PPI Transfer Menu
    Wait Until Element Is Visible    ${PPI_LANDING_TRANSFER_MENU}    ${NCBD_LOADING_TIMEOUT}
    Click Element    ${PPI_LANDING_TRANSFER_MENU}

Tap PPI Payment Menu
    Wait Until Element Is Visible    ${PPI_LANDING_PAYMENT_MENU}    ${NCBD_LOADING_TIMEOUT}
    Click Element    ${PPI_LANDING_PAYMENT_MENU}
