*** Settings ***
Documentation    Sprint 2.45 — Capture OCR Callback Contract
Library    AppiumLibrary
Library    OperatingSystem
Library    Process
Resource   ../../resources/app/app_keywords.resource
Resource   ../../resources/pages/onboarding/landing_screen_page.resource
Resource   ../../resources/pages/onboarding/consent_screen_page.resource
Resource   ../../resources/pages/onboarding/profile_screen_page.resource
Resource   ../../resources/pages/onboarding/pdpa_consent_page.resource
Resource   ../../resources/pages/onboarding/sign_up_page.resource
Resource   ../../resources/pages/onboarding/scan_card_intro_page.resource
Resource   ../../resources/pages/onboarding/id_card_camera_capture_page.resource
Library    ../../libraries/config_loader.py

*** Variables ***
${DIR}    reports/investigation/ocr_callback_contract
${TESTDATA}    testdata/onboarding/ntb.local.yaml

*** Test Cases ***
Capture Bridge Next Contract
    Create Directory    ${DIR}
    Open Mobile Application For Contract Capture
    ${prev}=    Set Log Level    NONE
    ${data}=    Load YAML    ${TESTDATA}
    Set Log Level    ${prev}
    Navigate To Camera Without Photo    ${data['profile']['citizen_id']}    ${data['profile']['date_of_birth']}    ${data['profile']['mobile_number']}
    Log    [FLOW] Camera screen reached without OCR injection    WARN
    Close Application

*** Keywords ***
Open Mobile Application For Contract Capture
    Open Application
    ...    http://127.0.0.1:4723
    ...    platformName=Android
    ...    automationName=UiAutomator2
    ...    deviceName=Android Emulator
    ...    appPackage=${APP_PACKAGE}
    ...    appActivity=com.bangkokbank.blue.MainActivity
    ...    noReset=true
    ...    autoGrantPermissions=true

Navigate To Camera Without Photo
    [Arguments]    ${citizen_id}    ${date_of_birth}    ${mobile_number}
    ${on_consent}=    Run Keyword And Return Status
    ...    Wait Until Element Is Visible
    ...    ${CONSENT_ACCEPT_BUTTON}
    ...    2s
    IF    not ${on_consent}
        Wait Until Landing Screen Is Displayed
        Tap Landing Ready Button
        Allow Android Permission If Visible
        ${still_on_landing}=    Run Keyword And Return Status    Element Should Be Visible    ${LANDING_READY_BUTTON}
        IF    ${still_on_landing}
            Click Element    ${LANDING_READY_BUTTON}
        END
    END
    Accept Consent Terms For Contract Capture
    Wait Until Profile Screen Is Displayed
    Input Citizen ID    ${citizen_id}
    Input Date Of Birth    ${date_of_birth}
    Input Mobile Number    ${mobile_number}
    Tap Profile Next
    Wait Until PDPA Consent Screen Is Displayed
    ${pdpa_accepted}=    Tap PDPA Consent Accept Button
    Should Be True    ${pdpa_accepted}    PDPA did not transition before camera navigation.
    Wait Until Sign Up Screen Is Displayed
    Tap Sign Up Lets Start Button
    Allow Android Permission If Visible
    Wait Until Scan Card Intro Screen Is Displayed
    Tap Scan Card Intro Next
    Allow Android Permission If Visible
    Wait Until ID Card Camera Capture Screen Is Displayed
    Navigate Virtual Camera To Poster

Accept Consent Terms For Contract Capture
    Wait Until Element Is Visible    ${CONSENT_ACCEPT_BUTTON}    15s
    FOR    ${index}    IN RANGE    18
        Swipe Consent Content Area
    END
    Tap Element Center By Adb    ${CONSENT_ACCEPT_BUTTON}
    Wait Until Page Does Not Contain Element    ${CONSENT_ACCEPT_BUTTON}    30s

Swipe Consent Content Area
    ${width}=    Get Window Width
    ${height}=    Get Window Height
    ${x}=    Evaluate    int(${width} * 0.5)
    ${start_y}=    Evaluate    int(${height} * 0.72)
    ${end_y}=    Evaluate    int(${height} * 0.20)
    Run Process    adb    shell    input    swipe    ${x}    ${start_y}    ${x}    ${end_y}    300

Tap Element Center By Adb
    [Arguments]    ${locator}
    ${location}=    Get Element Location    ${locator}
    ${size}=    Get Element Size    ${locator}
    ${x}=    Evaluate    int(${location['x']} + (${size['width']} / 2))
    ${y}=    Evaluate    int(${location['y']} + (${size['height']} / 2))
    Run Process    adb    shell    input    tap    ${x}    ${y}
