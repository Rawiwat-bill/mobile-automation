*** Settings ***
Documentation    ETB Introduction 3C and Control 3C assertions.
Library          AppiumLibrary
Resource         ../../../locators/android/etb/three_c_locators.resource
Resource         ../../app/app_constants.resource

*** Keywords ***
Assert TC001 Introduction And Control 3C
    [Documentation]    Verify the evidence-backed TC001 post-registration 3C transition.
    Wait Until Element Is Visible    ${THREE_C_INTRODUCTION_GOT_IT}    ${NCBD_LOADING_TIMEOUT}
    Click Element    ${THREE_C_INTRODUCTION_GOT_IT}
    Wait Until Element Is Visible    ${THREE_C_CONTROL_TRANSFER}    ${NCBD_LOADING_TIMEOUT}
    Wait Until Element Is Visible    ${THREE_C_CONTROL_USER_PROFILE}    ${NCBD_LOADING_TIMEOUT}