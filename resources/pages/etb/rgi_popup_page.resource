*** Settings ***
Documentation    Shared ETB RGI popup Page Object.
Library          AppiumLibrary
Resource         ../../../locators/android/etb/rgi_popup_locators.resource
Resource         ../../app/app_constants.resource

*** Keywords ***
Wait Until RGI Popup Is Visible
    [Arguments]    ${timeout}=${NCBD_LOADING_TIMEOUT}
    Wait Until Element Is Visible    ${RGI_POPUP_CONTAINER}    ${timeout}

Assert RGI Popup
    [Arguments]    ${expected_error_code}    ${expected_message}=${NONE}
    Wait Until RGI Popup Is Visible
    ${code_locator}=    Set Variable
    ...    xpath=//*[@resource-id="screenProfile_Pop-Up_Gub_SupportCode" and (contains(@text,"${expected_error_code}") or contains(@content-desc,"${expected_error_code}"))]
    Wait Until Element Is Visible    ${code_locator}    ${NCBD_LOADING_TIMEOUT}
    IF    $expected_message is not None
        Wait Until Page Contains    ${expected_message}    ${NCBD_LOADING_TIMEOUT}
    END

Tap RGI Popup OK
    Wait Until RGI Popup Is Visible
    Wait Until Element Is Visible    ${RGI_POPUP_OK_BUTTON}    ${NCBD_LOADING_TIMEOUT}
    Click Element    ${RGI_POPUP_OK_BUTTON}

Wait Until RGI Popup Is Closed
    Wait Until Page Does Not Contain Element    ${RGI_POPUP_CONTAINER}    ${NCBD_LOADING_TIMEOUT}

Handle Expected RGI Popup
    [Arguments]    ${expected_error_code}    ${expected_message}=${NONE}
    Assert RGI Popup    ${expected_error_code}    ${expected_message}
    Tap RGI Popup OK
    Wait Until RGI Popup Is Closed
