*** Settings ***
Documentation    Compatibility entry point for ETB. Shared onboarding implementation lives in ../common_onboarding.resource.
Resource         ../common_onboarding.resource


*** Keywords ***
Common Onboarding Flow
    [Documentation]    Run the single canonical common onboarding flow for ETB.
    [Arguments]    ${citizen_id}    ${date_of_birth}    ${mobile_number}
    ${result}=    Run Common Onboarding
    ...    ${citizen_id}
    ...    ${date_of_birth}
    ...    ${mobile_number}
    ...    language=ENGLISH
    RETURN    ${result}
