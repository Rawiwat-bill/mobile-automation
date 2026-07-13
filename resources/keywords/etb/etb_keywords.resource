*** Settings ***
Resource    ../../../resources/app/app_keywords.resource
Resource    ../../keywords/common_onboarding/onboarding_keyword.resource


*** Keywords ***
Complete ETB Onboarding
    [Documentation]    Complete the onboarding flow for ETB
    [Arguments]    ${citizen_id}    ${date_of_birth}    ${mobile_number}

    Common Onboarding Flow    ${citizen_id}    ${date_of_birth}    ${mobile_number}
