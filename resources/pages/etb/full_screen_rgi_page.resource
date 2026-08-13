*** Settings ***
Documentation    Shared ETB full-screen RGI Page Object.
Library          AppiumLibrary
Resource         ../../../locators/android/etb/full_screen_rgi_locators.resource
Resource         ../../app/app_constants.resource

*** Keywords ***
Wait Until Full Screen RGI Is Visible
    [Arguments]    ${timeout}=${NCBD_LOADING_TIMEOUT}
    Wait Until Element Is Visible    ${FULL_SCREEN_RGI_CONTAINER}    ${timeout}

Assert Full Screen RGI
    [Arguments]    ${expected_error_code}    ${expected_message}=${NONE}    ${action_policy}=STANDARD_FIND_BRANCH_CLOSE_APP
    Wait Until Full Screen RGI Is Visible
    ${code_locator}=    Set Variable
    ...    xpath=//*[@content-desc="${expected_error_code}" or contains(@text,"${expected_error_code}")]
    Wait Until Element Is Visible    ${code_locator}    ${NCBD_LOADING_TIMEOUT}
    IF    '${action_policy}' == 'STANDARD_FIND_BRANCH_CLOSE_APP'
        Wait Until Element Is Visible    ${FULL_SCREEN_RGI_FIND_BRANCH}    ${NCBD_LOADING_TIMEOUT}
        Wait Until Element Is Visible    ${FULL_SCREEN_RGI_CLOSE_BUTTON}    ${NCBD_LOADING_TIMEOUT}
    ELSE IF    '${action_policy}' == 'ASSERT_ONLY'
        Log    Full-Screen RGI action policy ASSERT_ONLY: standard actions are not required by runtime evidence.
    ELSE
        Fail    Unsupported Full-Screen RGI action policy: ${action_policy}
    END
    IF    $expected_message is not None
        Wait Until Page Contains    ${expected_message}    ${NCBD_LOADING_TIMEOUT}
    END

Tap Full Screen RGI Close App
    Wait Until Element Is Visible    ${FULL_SCREEN_RGI_CLOSE_BUTTON}    ${NCBD_LOADING_TIMEOUT}
    Click Element    ${FULL_SCREEN_RGI_CLOSE_BUTTON}

Handle Expected Full Screen RGI
    [Arguments]    ${expected_error_code}    ${expected_message}=${NONE}    ${action_policy}=STANDARD_FIND_BRANCH_CLOSE_APP
    Assert Full Screen RGI    ${expected_error_code}    ${expected_message}    ${action_policy}
    IF    '${action_policy}' == 'STANDARD_FIND_BRANCH_CLOSE_APP'
        Tap Full Screen RGI Close App
    END
