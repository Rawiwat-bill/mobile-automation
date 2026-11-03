*** Settings ***
Library     AppiumLibrary
Resource    ../../../resources/app/app_constants.resource
Resource    ../../../locators/android/etb/intro_face_scan_locators.resource


*** Keywords ***
Wait Until Intro Face Screen Is Displayed
    [Documentation]    Wait until the Intro Face Scan screen is displayed.
    Wait Until Element Is Visible    ${INTRO_FACE_SCAN_TITLE_TEXT}    ${NCBD_LOADING_TIMEOUT}

Continue From Intro Face Scan
    [Documentation]    Advance from the ETB face-scan introduction screen.
    Wait Until Intro Face Screen Is Displayed
    Click Element    ${INTRO_FACE_SCAN_NEXT_BUTTON}
