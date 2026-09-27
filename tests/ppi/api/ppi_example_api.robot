*** Settings ***
Documentation    PPI bill payment และ account inquiry API test
Library          RequestsLibrary
Library          Collections
Library          OperatingSystem
Library          ../../../libraries/robot_output_sanitizer.py
Variables        ../../../testdata/ppi/ppi_cases.example.yaml

Suite Setup      Open PPI API Session
Suite Teardown   Delete All Sessions

*** Variables ***
${PPI_SESSION}      ppi
${API_TIMEOUT}      30

*** Test Cases ***
TC-PPI-API-003 Bill Payment Returns Success
    [Tags]    ppi    api    payment    positive    smoke
    &{payload}=     Create Dictionary
    ...    sourceAccount=${PPI_API}[source_account]
    ...    billerId=${PPI_API}[biller_id]
    ...    amount=${PPI_UC_003}[amount]
    ...    currency=${PPI_UC_003}[currency]
    ${response}=    POST On Session    ${PPI_SESSION}    ${PPI_API}[payment_path]
    ...    json=${payload}    expected_status=any
    Should Be Equal As Integers    ${response.status_code}    200
    ${body}=    Set Variable       ${response.json()}
    Should Be Equal As Strings     ${body}[status]    ${PPI_UC_003}[expected_status]

TC-PPI-API-004 Account Inquiry Returns Expected Fields
    [Tags]    ppi    api    inquiry    positive
    ${response}=    GET On Session    ${PPI_SESSION}
    ...    ${PPI_API}[account_path]/${PPI_API}[source_account]    expected_status=any
    Should Be Equal As Integers    ${response.status_code}    200
    ${body}=    Set Variable       ${response.json()}
    Dictionary Should Contain Key  ${body}    availableBalance
    Dictionary Should Contain Key  ${body}    currency

TC-PPI-API-005 Request Without Credential Is Rejected
    [Tags]    ppi    api    negative    auth
    Create Session    ppi_noauth    %{PPI_API_BASE_URL}    timeout=${API_TIMEOUT}
    ${response}=    GET On Session    ppi_noauth
    ...    ${PPI_API}[account_path]/${PPI_API}[source_account]    expected_status=any
    Should Be Equal As Integers    ${response.status_code}    401

*** Keywords ***
Open PPI API Session
    [Documentation]    อ่าน endpoint และ token จาก environment แบบ fail-fast โดยไม่ log ค่า
    ${base_url}=    Get Environment Variable    PPI_API_BASE_URL    ${EMPTY}
    ${token}=       Get Environment Variable    PPI_API_TOKEN       ${EMPTY}
    IF    '${base_url}' == '${EMPTY}'
        Fail    Required environment variable is not set: PPI_API_BASE_URL
    END
    IF    '${token}' == '${EMPTY}'
        Fail    Required environment variable is not set: PPI_API_TOKEN
    END
    &{headers}=    Create Dictionary
    ...    Accept=application/json
    ...    Content-Type=application/json
    ...    Authorization=Bearer ${token}
    Create Session    ${PPI_SESSION}    ${base_url}    headers=${headers}    timeout=${API_TIMEOUT}
