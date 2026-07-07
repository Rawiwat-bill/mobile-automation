*** Settings ***
Documentation    Navigate to camera without Frida, sleep for manual Frida attachment
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
${DIR}    reports/investigation/diag_take_photo/evidence
${TESTDATA}    testdata/onboarding/ntb.local.yaml

*** Test Cases ***
Navigate To Camera And Wait
    Create Directory    ${DIR}
    Open Application
    ...    http://127.0.0.1:4723
    ...    platformName=Android
    ...    automationName=UiAutomator2
    ...    deviceName=Android Emulator
    ...    appPackage=com.bangkokbank.blue.dev
    ...    appActivity=com.bangkokbank.blue.MainActivity
    ...    noReset=true
    ...    dontStopAppOnReset=true
    Log    [FLOW] Connected to running app    WARN

    ${prev}=    Set Log Level    NONE
    ${data}=    Load YAML    ${TESTDATA}
    Set Log Level    ${prev}

    Wait Until Consent Screen Is Displayed
    Tap Consent Accept Button
    Log    [FLOW] Consent done    WARN

    Wait Until Profile Screen Is Displayed
    Input Citizen ID    ${data['profile']['citizen_id']}
    Input Date Of Birth    ${data['profile']['date_of_birth']}
    Input Mobile Number    ${data['profile']['mobile_number']}
    Tap Profile Next
    Log    [FLOW] Profile done    WARN

    Wait Until PDPA Consent Screen Is Displayed
    Tap PDPA Consent Accept Button
    Log    [FLOW] PDPA done    WARN

    Wait Until Sign Up Screen Is Displayed
    Tap Sign Up Lets Start Button
    Allow Android Permission If Visible
    Log    [FLOW] Sign Up done    WARN

    Wait Until Scan Card Intro Screen Is Displayed
    Tap Scan Card Intro Next
    Allow Android Permission If Visible
    Log    [FLOW] Scan Card Intro done    WARN

    Wait Until Element Is Visible    ${ID_CARD_CAMERA_VIEW}
    Log    [FLOW] *** CAMERA SCREEN REACHED ***    WARN

    Log    [FLOW] Sleeping 120s — attach Frida + press Take Photo now    WARN
    Sleep    120s

    Run Process    sh    -c    adb exec-out screencap -p > ${DIR}/after_camera.png
    Log    [FLOW] Done    WARN
    Close Application
