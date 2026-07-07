*** Settings ***
Documentation    Sprint 2.42 — Exception Capture
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
Resource   ../../resources/keywords/onboarding_common.resource
Library    ../../libraries/config_loader.py

*** Variables ***
${DIR}    reports/investigation/god017_exception_root_cause
${TESTDATA}    testdata/onboarding/ntb.local.yaml

*** Test Cases ***
Exception Capture
    Create Directory    ${DIR}
    Open Mobile Application For Exception Capture
    ${prev}=    Set Log Level    NONE
    ${data}=    Load YAML    ${TESTDATA}
    Set Log Level    ${prev}

    Navigate To Camera Without Photo    ${data['profile']['citizen_id']}    ${data['profile']['date_of_birth']}    ${data['profile']['mobile_number']}
    Log    [FLOW] Camera screen reached before photo capture    WARN

    Run Process    tools/frida/start_frida_bg.sh    tools/frida/exception_capture.js    tools/frida/bridge_authid_inject.js
    Sleep    5s
    Log    [FRIDA] Exception hooks and OCR bridge injection active    WARN

    Sleep    60s
    ${source}=    Get Source
    Create File    ${DIR}/after_injection.xml    ${source}    UTF-8

    Run Process    sh    -c    pkill -f "frida -U" 2>/dev/null
    Sleep    3s
    ${frida_log}=    Run Process    cat    /tmp/frida_listener.log
    Create File    ${DIR}/frida_exception_log.txt    ${frida_log.stdout}    UTF-8

    Close Application

*** Keywords ***
Open Mobile Application For Exception Capture
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
    Wait Until Landing Screen Is Displayed
    Tap Landing Ready Button
    Allow Android Permission If Visible
    ${still_on_landing}=    Run Keyword And Return Status    Element Should Be Visible    ${LANDING_READY_BUTTON}
    IF    ${still_on_landing}
        Click Element    ${LANDING_READY_BUTTON}
    END
    Wait Until Consent Screen Is Displayed
    Tap Consent Accept Button
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
