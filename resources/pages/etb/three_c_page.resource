*** Settings ***
Documentation    ETB Introduction 3C and Control 3C assertions.
Library          AppiumLibrary
Library          ../../../libraries/visual_timeline.py
Resource         ../../../locators/android/etb/three_c_locators.resource
Resource         ../../app/app_constants.resource

*** Keywords ***
Assert TC001 Introduction And Control 3C
    [Documentation]    Verify the evidence-backed TC001 post-registration 3C transition.
    Run Keyword And Ignore Error    Record Visual Timeline Event    3C0_INTRO_VISIBLE    INTRODUCTION_3C    ${OUTPUT DIR}/visual_timeline
    Wait Until Element Is Visible    ${THREE_C_INTRODUCTION_GOT_IT}    ${NCBD_LOADING_TIMEOUT}
    Click Element    ${THREE_C_INTRODUCTION_GOT_IT}
    Run Keyword And Ignore Error    Record Visual Timeline Event    3C1_GOT_IT_CLICKED    CONTROL_HOME    ${OUTPUT DIR}/visual_timeline    action=CLICK_INTRO_GOT_IT    screenshot=${False}
    Wait Until Element Is Visible    ${THREE_C_CONTROL_TRANSFER}    ${NCBD_LOADING_TIMEOUT}
    Wait Until Element Is Visible    ${THREE_C_CONTROL_USER_PROFILE}    ${NCBD_LOADING_TIMEOUT}
    Run Keyword And Ignore Error    Record Visual Timeline Event    CONTROL0_VISIBLE    CONTROL_HOME    ${OUTPUT DIR}/visual_timeline