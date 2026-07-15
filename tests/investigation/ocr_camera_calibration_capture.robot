*** Settings ***
Documentation    Calibration only: drive fresh to OCR Camera, STOP (no Take Photo, no OCR submit).
...              Reuses shared onboarding page keywords with emulator fallbacks.
...              Captures screenshot + XML + display geometry for canvas->screen mapping.
Library          AppiumLibrary
Library          OperatingSystem
Library          Process
Library          DateTime
Library          ../../libraries/config_loader.py
Resource         ../../resources/keywords/onboarding_common.resource
Resource         ../../resources/app/app_keywords.resource
Resource         ../../resources/pages/onboarding/landing_screen_page.resource
Resource         ../../resources/pages/onboarding/consent_screen_page.resource
Resource         ../../resources/pages/onboarding/profile_screen_page.resource
Resource         ../../resources/pages/onboarding/pdpa_consent_page.resource
Resource         ../../resources/pages/onboarding/sign_up_page.resource
Resource         ../../resources/pages/onboarding/scan_card_intro_page.resource
Resource         ../../resources/pages/onboarding/id_card_camera_capture_page.resource


*** Variables ***
${REPORT_DIR}       reports/investigation/ocr_frame_canvas_mapping
${TESTDATA}         testdata/onboarding/ntb.local.yaml
${APP_PATH}         apps/android/app.apk
${MAIN_ACTIVITY}    com.bangkokbank.blue.MainActivity
${EMULATOR_DEVICE}  Android Emulator
${EMULATOR_SERIAL}  emulator-5554
${SCREEN_TIMEOUT}   60s


*** Test Cases ***
Drive To OCR Camera And Capture Geometry
    Create Directory    ${REPORT_DIR}
    Resolve Emulator Serial
    Fresh Reset
    Open Application    http://127.0.0.1:4723    platformName=Android    automationName=UiAutomator2
    ...    udid=${EMULATOR_SERIAL}    deviceName=${EMULATOR_DEVICE}    appPackage=${APP_PACKAGE}
    ...    appActivity=${MAIN_ACTIVITY}    noReset=${TRUE}    autoGrantPermissions=${TRUE}
    ...    ignoreHiddenApiPolicyError=${TRUE}    newCommandTimeout=300
    Load Local Onboarding Data
    # --- route to OCR Camera (mirrors proven emulator flow), STOP before Take Photo ---
    Allow Android Permission If Visible
    ${ok}=    Run Keyword And Return Status    Tap Landing Ready Button
    IF    not ${ok}    Tap Landing Bottom Center
    Allow Android Permission If Visible
    Run Keyword And Ignore Error    Wait Until Consent Screen Is Displayed
    Run Keyword And Ignore Error    Scroll Down Consent Terms    15
    Tap Consent Accept Button
    Wait Until Profile Screen Is Displayed
    ${lvl}=    Set Log Level    NONE
    Run Keyword And Ignore Error    Input Citizen ID    ${LOCAL_CITIZEN_ID}
    Run Keyword And Ignore Error    Input Date Of Birth    ${LOCAL_DATE_OF_BIRTH}
    Run Keyword And Ignore Error    Dismiss DOB Picker If Open
    Run Keyword And Ignore Error    Input Mobile Number    ${LOCAL_MOBILE_NUMBER}
    Set Log Level    ${lvl}
    Tap Profile Next
    Wait Until PDPA Consent Screen Is Displayed
    Tap PDPA Consent Accept Button
    Wait Until Sign Up Screen Is Displayed
    Run Keyword And Ignore Error    Tap Sign Up Lets Start Button
    Allow Android Permission If Visible
    Wait Until Scan Card Intro Screen Is Displayed
    Run Keyword And Ignore Error    Tap Scan Card Intro Next
    Allow Android Permission If Visible
    Wait Until ID Card Camera Capture Screen Is Displayed
    Capture OCR Camera Geometry
    [Teardown]    Run Keyword And Ignore Error    Close Application


*** Keywords ***
Resolve Emulator Serial
    ${devices}=    Run Process    adb    devices    -l
    ${matches}=    Evaluate    __import__('re').findall(r'^(emulator-\\d+)\\s+device', """${devices.stdout}""", __import__('re').M)
    Should Not Be Empty    ${matches}    No emulator device found.
    Set Test Variable    ${EMULATOR_SERIAL}    ${matches[0]}

Fresh Reset
    Run Process    adb    -s    ${EMULATOR_SERIAL}    shell    pm    clear    ${APP_PACKAGE}    timeout=30s    on_timeout=terminate
    Run Process    adb    -s    ${EMULATOR_SERIAL}    install    -r    ${APP_PATH}    timeout=120s    on_timeout=terminate
    Run Process    adb    -s    ${EMULATOR_SERIAL}    logcat    -c    timeout=15s    on_timeout=terminate

Load Local Onboarding Data
    ${lvl}=    Set Log Level    NONE
    ${data}=    Load YAML    ${TESTDATA}
    Set Test Variable    ${LOCAL_CITIZEN_ID}    ${data['profile']['citizen_id']}
    Set Test Variable    ${LOCAL_DATE_OF_BIRTH}    ${data['profile']['date_of_birth']}
    Set Test Variable    ${LOCAL_MOBILE_NUMBER}    ${data['profile']['mobile_number']}
    Set Log Level    ${lvl}

Tap Landing Bottom Center
    ${r}=    Run Process    adb    -s    ${EMULATOR_SERIAL}    shell    wm    size    timeout=15s
    ${w}=    Evaluate    int(__import__('re').search(r'(\\d+)x', "${r.stdout}").group(1))
    ${h}=    Evaluate    int(__import__('re').search(r'x(\\d+)', "${r.stdout}").group(1))
    ${ty}=    Evaluate    int(${h} * 0.94)
    Run Process    adb    -s    ${EMULATOR_SERIAL}    shell    input    tap    ${w//2}    ${ty}    timeout=15s
    Sleep    1s

Dismiss DOB Picker If Open
    ${open}=    Run Keyword And Return Status    Wait Until Element Is Visible    ${PROFILE_DOB_CONFIRM_BUTTON}    2s
    IF    ${open}    Run Keyword And Ignore Error    Click Element    ${PROFILE_DOB_CONFIRM_BUTTON}

Capture OCR Camera Geometry
    ${now}=    Get Current Date
    Append To File    ${REPORT_DIR}/capture.log    OCR Camera reached @ ${now}\n
    # display geometry
    ${size}=    Run Process    adb    -s    ${EMULATOR_SERIAL}    shell    wm    size    timeout=15s
    ${density}=    Run Process    adb    -s    ${EMULATOR_SERIAL}    shell    wm    density    timeout=15s
    ${orient}=    Run Process    adb    -s    ${EMULATOR_SERIAL}    shell    getprop    ro.surface_flinger.primary_display_orientation    timeout=15s
    Create File    ${REPORT_DIR}/display_geometry.txt    SIZE:${size.stdout}\nDENSITY:${density.stdout}\nORIENT:${orient.stdout}\n
    # screenshot + xml
    Run Process    sh    -c    adb -s ${EMULATOR_SERIAL} exec-out screencap -p > ${REPORT_DIR}/ocr_camera.png    timeout=30s
    Run Process    adb    -s    ${EMULATOR_SERIAL}    shell    uiautomator    dump    /sdcard/c.xml    timeout=30s
    ${xml}=    Run Process    adb    -s    ${EMULATOR_SERIAL}    exec-out    cat    /sdcard/c.xml    timeout=30s
    Create File    ${REPORT_DIR}/ocr_camera.xml    ${xml.stdout}    UTF-8
    Append To File    ${REPORT_DIR}/capture.log    geometry + screenshot + xml captured\n
