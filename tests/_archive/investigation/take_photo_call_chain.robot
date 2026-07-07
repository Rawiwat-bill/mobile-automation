*** Settings ***
Documentation    Sprint 2.64 — Take Photo Call Chain Discovery
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
${DIR}    reports/investigation/take_photo_call_chain/evidence
${TESTDATA}    testdata/onboarding/ntb.local.yaml

*** Test Cases ***
Take Photo Call Chain Discovery
    Create Directory    ${DIR}
    Open Mobile Application
    ${prev}=    Set Log Level    NONE
    ${data}=    Load YAML    ${TESTDATA}
    Set Log Level    ${prev}
    Log    [FLOW] App launched    WARN

    Navigate To Camera For Take Photo Chain    ${data['profile']['citizen_id']}    ${data['profile']['date_of_birth']}    ${data['profile']['mobile_number']}
    Wait Until Element Is Visible    ${ID_CARD_CAMERA_VIEW}
    Capture Page Screenshot    ${DIR}/before_tap.png
    ${src_before}=    Get Source
    Create File    ${DIR}/before_tap.xml    ${src_before}    UTF-8
    Log    [FLOW] Camera screen reached    WARN

    Run Process    tools/frida/start_frida_bg.sh    take_photo_call_chain.js
    Sleep    5s
    Log    [FRIDA] Call-chain tracing active    WARN

    Capture Page Screenshot    ${DIR}/before_tap_after_attach.png
    ${src_before_attach}=    Get Source
    Create File    ${DIR}/before_tap_after_attach.xml    ${src_before_attach}    UTF-8

    Log    [ACTION] Tapping Take Photo    WARN
    Click Element    ${ID_CARD_TAKE_PHOTO}
    Log    [ACTION] Take Photo tapped    WARN

    Sleep    20s
    Log    [FLOW] 20s after Take Photo    WARN

    Capture Page Screenshot    ${DIR}/after_tap.png
    ${src_after}=    Get Source
    Create File    ${DIR}/after_tap.xml    ${src_after}    UTF-8

    ${frida_log}=    Run Process    cat    /tmp/frida_listener.log
    Create File    ${DIR}/frida_log.txt    ${frida_log.stdout}    UTF-8

    ${logcat}=    Run Process    adb    logcat    -d    -v    time
    Create File    ${DIR}/logcat.txt    ${logcat.stdout}    UTF-8

    Run Process    sh    -c    pkill -f "frida -U" 2>/dev/null
    Sleep    2s
    Close Application

*** Keywords ***
Navigate To Camera For Take Photo Chain
    [Arguments]    ${citizen_id}    ${date_of_birth}    ${mobile_number}
    ${on_camera}=    Run Keyword And Return Status
    ...    Wait Until Element Is Visible    ${ID_CARD_CAMERA_VIEW}    2s
    IF    ${on_camera}
        Return From Keyword
    END

    ${on_scan_intro}=    Run Keyword And Return Status
    ...    Wait Until Element Is Visible    ${SCAN_CARD_INTRO_STEP_BAR}    2s
    IF    ${on_scan_intro}
        Tap Scan Card Intro Next
        Allow Android Permission If Visible
        Wait Until ID Card Camera Capture Screen Is Displayed
        RETURN
    END

    ${on_signup}=    Run Keyword And Return Status
    ...    Wait Until Element Is Visible    ${SIGN_UP_LETS_START}    2s
    IF    ${on_signup}
        Tap Sign Up Lets Start Button
        Allow Android Permission If Visible
        Wait Until Scan Card Intro Screen Is Displayed
        Tap Scan Card Intro Next
        Allow Android Permission If Visible
        Wait Until ID Card Camera Capture Screen Is Displayed
        RETURN
    END

    ${on_pdpa}=    Run Keyword And Return Status
    ...    Wait Until Element Is Visible    ${PDPA_ACCEPT_BUTTON}    2s
    IF    ${on_pdpa}
        ${pdpa_accepted}=    Tap PDPA Consent Accept Button
        Should Be True    ${pdpa_accepted}    PDPA did not transition before camera navigation.
        Wait Until Sign Up Screen Is Displayed
        Tap Sign Up Lets Start Button
        Allow Android Permission If Visible
        Wait Until Scan Card Intro Screen Is Displayed
        Tap Scan Card Intro Next
        Allow Android Permission If Visible
        Wait Until ID Card Camera Capture Screen Is Displayed
        RETURN
    END

    ${on_profile}=    Run Keyword And Return Status
    ...    Wait Until Element Is Visible    ${PROFILE_TITLE_TEXT}    2s
    IF    ${on_profile}
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
        RETURN
    END

    Wait Until Landing Screen Is Displayed
    Tap Landing Ready Button
    Allow Android Permission If Visible
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
