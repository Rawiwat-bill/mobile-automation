*** Settings ***
Documentation       PPI business flow keywords. (example)
...
...                 ไฟล์ตัวอย่างสำหรับทีม PPI — keyword layer ต่อหลาย page
...                 เป็น business flow เดียว ห้ามอ้าง locator ตรงในไฟล์นี้

Resource            ../../app/app_keywords.resource
Resource            ../../pages/ppi/ppi_landing_page.resource
Resource            ../../pages/ppi/ppi_account_page.resource
Resource            ../../pages/ppi/ppi_amount_page.resource
Resource            ../../pages/ppi/ppi_confirm_page.resource
Resource            ../../pages/ppi/ppi_result_page.resource

*** Keywords ***
Complete PPI Transfer
    [Documentation]    Happy path ของ transfer: landing -> เลือกบัญชี -> จำนวนเงิน -> ยืนยัน -> ผลลัพธ์
    [Arguments]    ${account_label}    ${amount}    ${expected_status}

    Wait Until PPI Landing Screen Is Displayed
    Tap PPI Transfer Menu

    Wait Until PPI Account Screen Is Displayed
    Select PPI Account    ${account_label}
    Tap PPI Account Next

    Wait Until PPI Amount Screen Is Displayed
    Input PPI Amount    ${amount}
    Tap PPI Amount Next

    Wait Until PPI Confirm Screen Is Displayed
    Tap PPI Confirm Submit

    Wait Until PPI Result Screen Is Displayed
    PPI Result Status Should Be              ${expected_status}
    PPI Result Reference Should Not Be Empty
    Tap PPI Result Done

Complete PPI Payment
    [Documentation]    Happy path ของ bill payment
    [Arguments]    ${account_label}    ${amount}    ${expected_status}

    Wait Until PPI Landing Screen Is Displayed
    Tap PPI Payment Menu

    Wait Until PPI Account Screen Is Displayed
    Select PPI Account    ${account_label}
    Tap PPI Account Next

    Wait Until PPI Amount Screen Is Displayed
    Input PPI Amount    ${amount}
    Tap PPI Amount Next

    Wait Until PPI Confirm Screen Is Displayed
    Tap PPI Confirm Submit

    Wait Until PPI Result Screen Is Displayed
    PPI Result Status Should Be    ${expected_status}

Submit PPI Transfer Expecting Amount Error
    [Documentation]    Negative path: คาดหวัง error message ที่หน้าจำนวนเงิน
    [Arguments]    ${account_label}    ${amount}

    Wait Until PPI Landing Screen Is Displayed
    Tap PPI Transfer Menu

    Wait Until PPI Account Screen Is Displayed
    Select PPI Account    ${account_label}
    Tap PPI Account Next

    Wait Until PPI Amount Screen Is Displayed
    Input PPI Amount    ${amount}
    Tap PPI Amount Next

    PPI Amount Error Should Be Displayed
