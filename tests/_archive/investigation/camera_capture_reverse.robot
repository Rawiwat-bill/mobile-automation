*** Settings ***
Documentation    Sprint 2.25 — Camera Capture Reverse Engineering
...              Observes filesystem, logcat, and XML changes during Take Photo
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
${EVIDENCE_DIR}    reports/investigation/camera_capture_flow
${TESTDATA}        testdata/onboarding/ntb.local.yaml

*** Keywords ***
Snapshot Filesystem
    [Arguments]    ${label}
    ${ts}=    Evaluate    __import__('time').strftime('%H%M%S')
    ${files}=    Run Process    adb    shell    find    /data/data/com.bangkokbank.blue.dev/    -type    f    2>/dev/null
    Create File    ${EVIDENCE_DIR}/fs_${label}.txt    ${files.stdout}    UTF-8
    ${count}=    Get Length    ${files.stdout.splitlines()}
    Log    [FS] ${label}: ${count} files
    RETURN    ${count}

Snapshot MediaStore
    [Arguments]    ${label}
    ${result}=    Run Process    adb    shell    content    query    --uri    content://media/external/images/media/    2>/dev/null
    Create File    ${EVIDENCE_DIR}/mediastore_${label}.txt    ${result.stdout}    UTF-8
    Log    [MS] ${label}: MediaStore captured

Snapshot ExternalCache
    [Arguments]    ${label}
    ${result}=    Run Process    adb    shell    ls    -laR    /sdcard/Android/data/com.bangkokbank.blue.dev/    2>/dev/null
    Create File    ${EVIDENCE_DIR}/extcache_${label}.txt    ${result.stdout}    UTF-8
    Log    [EC] ${label}: External cache captured

Snapshot All
    [Arguments]    ${label}
    Snapshot Filesystem    ${label}
    Snapshot MediaStore    ${label}
    Snapshot ExternalCache    ${label}

*** Test Cases ***
Camera Capture Reverse Engineering
    Create Directory    ${EVIDENCE_DIR}
    Open Mobile Application
    ${previous_log_level}=    Set Log Level    NONE
    ${data}=    Load YAML    ${TESTDATA}
    Set Log Level    ${previous_log_level}

    # Navigate to camera screen
    Complete Common Onboarding    ${data['profile']['citizen_id']}    ${data['profile']['date_of_birth']}    ${data['profile']['mobile_number']}

    # Now on camera screen
    Sleep    2s

    # Snapshot BEFORE Take Photo
    Log    [CAPTURE] === BEFORE Take Photo ===    WARN
    Snapshot All    before

    # Capture XML before
    ${source}=    Get Source
    Create File    ${EVIDENCE_DIR}/xml_before.xml    ${source}    UTF-8

    # Start logcat capture
    Run Process    adb    logcat    -c    2>/dev/null

    # Tap Take Photo
    Log    [CAPTURE] === TAPPING Take Photo ===    WARN
    Click Element    accessibility_id=Take photo

    # Wait for capture to process
    Sleep    8s

    # Stop logcat and save
    Log    [CAPTURE] === AFTER Take Photo ===    WARN
    ${logcat}=    Run Process    adb    logcat    -d
    Create File    ${EVIDENCE_DIR}/logcat_during_capture.txt    ${logcat.stdout}    UTF-8

    # Snapshot AFTER Take Photo
    Snapshot All    after

    # Capture XML after
    ${source}=    Get Source
    Create File    ${EVIDENCE_DIR}/xml_after.xml    ${source}    UTF-8

    # Take another screenshot of current state
    Capture Page Screenshot    ${EVIDENCE_DIR}/screen_after_photo.png

    Close Application
