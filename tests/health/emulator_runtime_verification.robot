*** Settings ***
Documentation    Sprint 2.54 — Emulator runtime verification for OCR to NTB_LC transition.
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
${DIR}             reports/investigation/emulator_runtime_verification
${TESTDATA}        testdata/onboarding/ntb.local.yaml
${FRIDA_SCRIPT}    /private/tmp/ntb_lc_contract_runtime.js

*** Test Cases ***
Verify Emulator OCR To NTB LC Runtime
    Create Directory    ${DIR}
    Create Directory    ${DIR}/evidence
    Open Mobile Application For NTB LC Contract
    ${prev}=    Set Log Level    NONE
    ${data}=    Load YAML    ${TESTDATA}
    Set Log Level    ${prev}
    Navigate To Camera For NTB LC Contract    ${data['profile']['citizen_id']}    ${data['profile']['date_of_birth']}    ${data['profile']['mobile_number']}
    Capture Current Screen Evidence    before_ocr
    Run Process    adb    logcat    -c
    Run Process    tools/frida/start_frida_bg.sh    ${FRIDA_SCRIPT}
    Sleep    90s
    Capture Current Screen Evidence    after_ocr
    ${logcat}=    Run Process    adb    logcat    -d    -v    time
    Create File    ${DIR}/evidence/logcat.txt    ${logcat.stdout}    UTF-8
    ${window_dump}=    Run Process    adb    shell    dumpsys    window
    Create File    ${DIR}/evidence/after_ocr_window_dump.txt    ${window_dump.stdout}    UTF-8
    ${frida_log}=    Run Process    cat    /tmp/frida_listener.log
    Create File    ${DIR}/evidence/frida_log.txt    ${frida_log.stdout}    UTF-8
    Close Application

*** Keywords ***
Open Mobile Application For NTB LC Contract
    Open Application
    ...    http://127.0.0.1:4723
    ...    platformName=Android
    ...    automationName=UiAutomator2
    ...    deviceName=Android Emulator
    ...    appPackage=${APP_PACKAGE}
    ...    appActivity=com.bangkokbank.blue.MainActivity
    ...    noReset=true
    ...    autoGrantPermissions=true

Navigate To Camera For NTB LC Contract
    [Arguments]    ${citizen_id}    ${date_of_birth}    ${mobile_number}
    ${on_consent}=    Run Keyword And Return Status
    ...    Wait Until Element Is Visible    ${CONSENT_ACCEPT_BUTTON}    2s
    IF    not ${on_consent}
        Wait Until Landing Screen Is Displayed
        Tap Landing Ready Button
        Allow Android Permission If Visible
        ${still_on_landing}=    Run Keyword And Return Status    Element Should Be Visible    ${LANDING_READY_BUTTON}
        IF    ${still_on_landing}
            Click Element    ${LANDING_READY_BUTTON}
        END
    END
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

Capture Current Screen Evidence
    [Arguments]    ${name}
    ${src}=    Get Source
    Create File    ${DIR}/evidence/${name}.xml    ${src}    UTF-8
    Run Process    sh    -c    adb exec-out screencap -p > ${DIR}/evidence/${name}.png
