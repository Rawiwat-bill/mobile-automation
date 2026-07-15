*** Settings ***
Library     AppiumLibrary
Library     Process
Resource    ../../../locators/android/onboarding/id_card_camera_capture_locators.resource

*** Variables ***
${ID_CARD_CAMERA_TIMEOUT}    10s
${CAMERA_NAVIGATE_SCRIPT}    ${CURDIR}/../../../tools/emulator/navigate_camera.py

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
    [Documentation]    adb tap fallback when Click Element doesn't trigger RN photo capture.
    ${on_camera}=    Run Keyword And Return Status    Page Should Contain Element    accessibility_id=Take photo    5s
    IF    ${on_camera}
        ${loc}=    Get Element Location    accessibility_id=Take photo
        ${sz}=    Get Element Size    accessibility_id=Take photo
        ${cx}=    Evaluate    int($loc['x'] + $sz['width'] / 2)
        ${cy}=    Evaluate    int($loc['y'] + $sz['height'] / 2)
        Execute Adb Shell    input    tap    ${cx}    ${cy}
        Log    [ID_CARD_CAMERA] Photo captured via adb tap at ${cx},${cy}
    END
