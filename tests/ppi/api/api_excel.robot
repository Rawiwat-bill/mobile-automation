*** Settings ***
Library    ${CURDIR}${/}ApiClient.py
Library    ${CURDIR}${/}ExcelHelper.py
Library    Collections

Suite Setup    Load Test Data
Suite Teardown    Save Workbook

*** Variables ***
${EXCEL_FILE}    ${CURDIR}${/}api_list.xlsx
${SHEET_NAME}    APITest


*** Keywords ***
Load Test Data
    Log To Console    ===== Load Test Data =====
    Log To Console    Excel=${EXCEL_FILE}
    Load Workbook    ${EXCEL_FILE}    ${SHEET_NAME}
    ${rows}=    Get Test Rows
    Set Suite Variable    ${ROWS}    ${rows}

Run Single Api Row
    [Arguments]    ${row}

    ${row_no}=    Get From Dictionary    ${row}    _row
    ${method}=    Get From Dictionary    ${row}    Method
    ${url}=    Get From Dictionary    ${row}    URL
    ${payload}=    Get From Dictionary    ${row}    Payload
    ${expected_status}=    Get From Dictionary    ${row}    ExpectedStatus
    ${expected_body}=    Get From Dictionary    ${row}    ExpectedBody

    ${actual_status}    ${actual_body}=    Send Api    ${method}    ${url}    ${payload}

    ${status_ok}=    Run Keyword And Return Status
    ...    Should Be Equal As Integers    ${actual_status}    ${expected_status}

    ${body_ok}    ${body_rule}=    Compare Body    ${expected_body}    ${actual_body}

    ${result}=    Set Variable If    ${status_ok} and ${body_ok}    PASS    FAIL
    ${test_date}=    Get Test Date

    Write Results    ${row_no}    ${actual_status}    ${actual_body}    ${result}    ${test_date}


*** Test Cases ***
Run API Tests From Excel
    FOR    ${row}    IN    @{ROWS}
        Run Single Api Row    ${row}
    END
