*** Settings ***
Library     AppiumLibrary
Library     Process
Resource    ../../../locators/android/onboarding/id_card_camera_capture_locators.resource

*** Variables ***
${ID_CARD_CAMERA_TIMEOUT}    10s
${CAMERA_NAVIGATE_SCRIPT}    ${CURDIR}/../../../tools/emulator/navigate_camera.py
# shutter is a plain ViewGroup (no resource-id/content-desc); accessibility_id=Take photo is its
# NON-clickable text label (resource-id=text) sitting below it. 540,2039 is the proven shutter tap
# Bounds are based on the approved committed mock-card runtime layout. Replace with a stable testID when available.
${ID_CARD_SHUTTER_X}    540
${ID_CARD_SHUTTER_Y}    2039

*** Keywords ***
Wait Until ID Card Camera Capture Screen Is Displayed
    Wait Until Element Is Visible    ${ID_CARD_CAMERA_VIEW}    ${ID_CARD_CAMERA_TIMEOUT}
    Log    [ID_CARD_CAMERA] Camera screen visible

Navigate Virtual Camera To Poster
    ${yaw}=    Get Environment Variable    CAM_YAW    -9
    ${pitch}=    Get Environment Variable    CAM_PITCH    3
    ${fwd}=    Get Environment Variable    CAM_FWD    4
    Run Process    python3    ${CAMERA_NAVIGATE_SCRIPT}    ${yaw}    ${pitch}    ${fwd}
    Run Process    sh    -c    adb exec-out screencap -p > reports/investigation/emulator_camera_calibration/camera_after_nav.png
    Log    [ID_CARD_CAMERA] Virtual camera navigated: yaw=${yaw} pitch=${pitch} fwd=${fwd}

Tap Take Photo
    Click Element    ${ID_CARD_TAKE_PHOTO}
    Log    [ID_CARD_CAMERA] Take photo tapped

Capture ID Card Photo
    [Documentation]    Tap the shutter ViewGroup to capture. accessibility_id=Take photo is a NON-clickable
    ...                text label (resource-id=text) below the shutter; the real shutter is a plain ViewGroup at 540,2039.
    ${on_camera}=    Run Keyword And Return Status    Page Should Contain Element    accessibility_id=Take photo    5s
    IF    ${on_camera}
        Execute Adb Shell    input    tap    ${ID_CARD_SHUTTER_X}    ${ID_CARD_SHUTTER_Y}
        Log    [ID_CARD_CAMERA] Shutter tapped via adb at ${ID_CARD_SHUTTER_X},${ID_CARD_SHUTTER_Y}
    END
