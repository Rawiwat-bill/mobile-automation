*** Settings ***
Documentation    PPI bill payment UI test
Library          AppiumLibrary
Library          ../../../libraries/robot_output_sanitizer.py
Resource         ../../../resources/keywords/ppi/ppi_keywords.resource
Variables        ../../../testdata/ppi/ppi_cases.example.yaml

Suite Setup      Open Mobile Application
Suite Teardown   Close Application
Test Teardown    Run Keyword If Test Failed    Capture Page Screenshot

*** Test Cases ***
TC-PPI-UI-003 Bill Payment Success
    [Tags]    ppi    ui    payment    positive    smoke
    Complete PPI Payment
    ...    ${PPI_UC_003}[source_account_label]
    ...    ${PPI_UC_003}[amount]
    ...    ${PPI_UC_003}[expected_status]
