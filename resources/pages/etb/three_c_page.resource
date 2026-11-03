*** Settings ***
Documentation    ETB Introduction 3C and Control 3C assertions.
Library          AppiumLibrary
Library          ../../../libraries/visual_timeline.py
Resource         ../../../locators/android/etb/three_c_locators.resource
Resource         ../../app/app_constants.resource

*** Keywords ***
Assert TC001 Introduction And Control 3C
    [Documentation]    Verify the evidence-backed TC001 post-registration 3C transition.
    Wait Until Element Is Visible    ${THREE_C_INTRODUCTION_GOT_IT}    ${NCBD_LOADING_TIMEOUT}
    Run Keyword And Ignore Error    Record Visual Timeline Event    3C0_INTRO_VISIBLE    INTRODUCTION_3C    ${OUTPUT DIR}/visual_timeline
    Click Element    ${THREE_C_INTRODUCTION_GOT_IT}
    Run Keyword And Ignore Error    Record Visual Timeline Event    3C1_GOT_IT_CLICKED    INTRODUCTION_3C    ${OUTPUT DIR}/visual_timeline    action=CLICK_INTRO_GOT_IT    screenshot=${False}
    Wait Until Element Is Visible    ${THREE_C_CONTROL_ACCOUNTS}    ${NCBD_LOADING_TIMEOUT}
    Wait Until Element Is Visible    ${THREE_C_CONTROL_USER_PROFILE}    ${NCBD_LOADING_TIMEOUT}
    Run Keyword And Ignore Error    Record Visual Timeline Event    CONTROL0_VISIBLE    CONTROL_HOME    ${OUTPUT DIR}/visual_timeline
    Dismiss Mobile Phone Risk Prompt If Present

Dismiss Mobile Phone Risk Prompt If Present
    [Documentation]    Keep the completed ETB flow on Control when the optional post-registration risk prompt appears.
    ${visible}=    Run Keyword And Return Status
    ...    Wait Until Element Is Visible    ${THREE_C_RISK_MAYBE_LATER}    5s
    IF    ${visible}
        Click Element    ${THREE_C_RISK_MAYBE_LATER}
        Wait Until Page Does Not Contain Element    ${THREE_C_RISK_MAYBE_LATER}    5s
    END
