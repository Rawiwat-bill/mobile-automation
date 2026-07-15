*** Settings ***
Resource    ../../../resources/app/app_keywords.resource
Resource    ../../keywords/common_onboarding/common_onboarding_keyword.resource
Resource    ../../pages/etb/check_dopa_fill_laser_code_page.resource
Resource    ../../pages/etb/mobile_otp_page.resource


*** Keywords ***
Complete ETB Onboarding
    [Documentation]    Complete the onboarding flow for ETB
    [Arguments]    ${citizen_id}    ${date_of_birth}    ${mobile_number}    ${laser_code}

    Common Onboarding Flow    ${citizen_id}    ${date_of_birth}    ${mobile_number}

    Wait Until Check DOPA Fill Laser Code Is Displayed
    Mark Health Checkpoint    CHECK_DOPA_FILL_LASER_CODE_VISIBLE
    Input Laser Code    ${laser_code}
    Mark Health Checkpoint    CHECK_DOPA_FILL_LASER_CODE_COMPLETED

    Wait Until Mobile OTP Screen Is Displayed
    Mark Health Checkpoint    MOBILE_OTP_VISIBLE
    Input OTP
