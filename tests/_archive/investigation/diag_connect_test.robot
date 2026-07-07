*** Settings ***
Documentation    Diagnostic — Connect to running app, navigate to camera, press Take Photo
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
${DIR}    reports/investigation/diag_take_photo/evidence
${TESTDATA}    testdata/onboarding/ntb.local.yaml

*** Test Cases ***
Diagnostic Connect And Navigate
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

    Complete Common Onboarding
    ...    ${data['profile']['citizen_id']}
    ...    ${data['profile']['date_of_birth']}
    ...    ${data['profile']['mobile_number']}
    Log    [FLOW] Camera screen reached    WARN

    Sleep    3s
    Click Element    ${ID_CARD_TAKE_PHOTO}
    Log    [FLOW] Take Photo tapped    WARN

    Sleep    15s
    Log    [FLOW] 15s elapsed — checking Frida log    WARN

    Run Process    sh    -c    adb exec-out screencap -p > ${DIR}/after_take_photo.png

    ${frida_log}=    Run Process    cat    /tmp/frida_listener.log
    Create File    ${DIR}/frida_log.txt    ${frida_log.stdout}    UTF-8

    Run Process    sh    -c    pkill -f "frida -U" 2>/dev/null
    Sleep    2s
    Log    [FLOW] Done    WARN
    Close Application
