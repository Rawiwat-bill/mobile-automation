*** Settings ***
Documentation    Sprint 2.33 — ForgeRock Submission Method Discovery
...              Navigates to camera screen, attaches Frida, enumerates ForgeRock methods
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
${DIR}    reports/investigation/forgerock_submission_discovery
${TESTDATA}    testdata/onboarding/ntb.local.yaml

*** Test Cases ***
ForgeRock Method Discovery
    Create Directory    ${DIR}
    Open Mobile Application
    ${prev}=    Set Log Level    NONE
    ${data}=    Load YAML    ${TESTDATA}
    Set Log Level    ${prev}

    # Navigate to camera screen
    Complete Common Onboarding    ${data['profile']['citizen_id']}    ${data['profile']['date_of_birth']}    ${data['profile']['mobile_number']}
    Log    [FLOW] Reached camera screen    WARN

    # Attach Frida with discovery script
    Log    [FRIDA] Attaching discovery script...    WARN
    ${result}=    Run Process    tools/frida/attach_and_wait.sh    tools/frida/forgerock_method_discovery.js
    ...    timeout=30s    on_timeout=continue
    Log    [FRIDA] ${result.stdout}    WARN

    # Wait for hooks to settle
    Sleep    5s

    # Clear logcat
    Run Process    adb    logcat    -c    2>/dev/null

    # Tap Take Photo to trigger any callback methods
    Log    [ACTION] Tapping Take Photo    WARN
    Run Process    adb    shell    input    tap    540    2196

    # Wait for processing
    Sleep    15s

    # Capture result
    ${src}=    Get Source
    Create File    ${DIR}/after_take_photo.xml    ${src}    UTF-8
    Run Process    sh    -c    adb exec-out screencap -p > ${DIR}/after_take_photo.png

    # Kill Frida and save logs
    Run Process    sh    -c    pkill -f "frida -U" 2>/dev/null
    Sleep    3s

    # Save Frida discovery log
    ${frida_log}=    Run Process    cat    /tmp/frida_attach_live.log
    Create File    ${DIR}/frida_discovery.log    ${frida_log.stdout}    UTF-8

    # Save logcat
    ${logcat}=    Run Process    adb    logcat    -d
    Create File    ${DIR}/logcat.txt    ${logcat.stdout}    UTF-8

    # Check result
    ${has_rvcamera}=    Run Keyword And Return Status    Page Should Contain Element    xpath=//*[@resource-id="RVCamera"]
    Log    [RESULT] Still on camera: ${has_rvcamera}    WARN

    Close Application
