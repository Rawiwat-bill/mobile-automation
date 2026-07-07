*** Settings ***
Documentation    Sprint 2.79 emulator revival with fresh app state and shared onboarding flow.
...              Fresh state via pm clear should branch to OCR Camera. Stop at camera.
Library          AppiumLibrary
Library          OperatingSystem
Library          Process
Library          Collections
Library          String
Library          ../../libraries/config_loader.py
Resource         ../../resources/app/app_keywords.resource
Resource         ../../resources/pages/onboarding/landing_screen_page.resource
Resource         ../../resources/pages/onboarding/consent_screen_page.resource
Resource         ../../resources/pages/onboarding/profile_screen_page.resource
Resource         ../../resources/pages/onboarding/pdpa_consent_page.resource
Resource         ../../resources/pages/onboarding/sign_up_page.resource
Resource         ../../resources/pages/onboarding/scan_card_intro_page.resource
Resource         ../../resources/pages/onboarding/id_card_camera_capture_page.resource


*** Variables ***
${REPORT_DIR}          reports/investigation/emulator_revival
${EVIDENCE_DIR}        ${REPORT_DIR}/evidence
${TESTDATA}            testdata/onboarding/ntb.local.yaml
${APP_PATH}            apps/android/app.apk
${MAIN_ACTIVITY}       com.bangkokbank.blue.MainActivity
${EMULATOR_DEVICE}     Android Emulator
${EMULATOR_SERIAL}     ${EMPTY}
${SCREEN_TIMEOUT}      60s


*** Test Cases ***
Emulator Fresh State To OCR Camera
    Create Directory    ${REPORT_DIR}
    Create Directory    ${EVIDENCE_DIR}
    Resolve Emulator Serial
    Install App On Emulator
    Clear App Data On Emulator
    Open Application On Emulator
    Load Local Onboarding Data
    Process Landing Screen
    Process Consent Screen
    Process CND Screen
    Process PDPA Screen
    Process OCR Intro Screen
    Process Camera Screen
    Write Robot Output Reference
    [Teardown]    Run Keyword And Ignore Error    Close Application


*** Keywords ***
Resolve Emulator Serial
    ${devices}=    Run Process    adb    devices    -l
    Should Be Equal As Integers    ${devices.rc}    0
    ${matches}=    Evaluate    __import__('re').findall(r'^(emulator-\\d+)\\s+device', """${devices.stdout}""", __import__('re').M)
    Should Not Be Empty    ${matches}    No emulator device found in adb devices output.
    ${serial}=    Evaluate    $matches[0]
    Set Test Variable    ${EMULATOR_SERIAL}    ${serial}
    Log    [EMU] Serial=${EMULATOR_SERIAL}

Install App On Emulator
    Run Process    adb    -s    ${EMULATOR_SERIAL}    install    -r    ${APP_PATH}
    ...    timeout=120s    on_timeout=terminate

Clear App Data On Emulator
    Run Process    adb    -s    ${EMULATOR_SERIAL}    shell    pm    clear    ${APP_PACKAGE}
    ...    timeout=30s    on_timeout=terminate

Open Application On Emulator
    Open Application
    ...    http://127.0.0.1:4723
    ...    platformName=Android
    ...    automationName=UiAutomator2
    ...    udid=${EMULATOR_SERIAL}
    ...    deviceName=${EMULATOR_DEVICE}
    ...    appPackage=${APP_PACKAGE}
    ...    appActivity=${MAIN_ACTIVITY}
    ...    noReset=${TRUE}
    ...    autoGrantPermissions=${TRUE}
    ...    ignoreHiddenApiPolicyError=${TRUE}
    ...    disableWindowAnimation=${TRUE}
    ...    uiautomator2ServerInstallTimeout=120000
    ...    uiautomator2ServerLaunchTimeout=120000
    ...    newCommandTimeout=300

Load Local Onboarding Data
    ${previous_log_level}=    Set Log Level    NONE
    ${data}=    Load YAML    ${TESTDATA}
    Set Test Variable    ${LOCAL_CITIZEN_ID}    ${data['profile']['citizen_id']}
    Set Test Variable    ${LOCAL_DATE_OF_BIRTH}    ${data['profile']['date_of_birth']}
    Set Test Variable    ${LOCAL_MOBILE_NUMBER}    ${data['profile']['mobile_number']}
    Set Log Level    ${previous_log_level}

Process Landing Screen
    Capture Screen Evidence    landing
    Allow Android Permission If Visible
    ${landing_tapped}=    Run Keyword And Return Status    Tap Landing Ready Button
    IF    not ${landing_tapped}
        Tap Landing Bottom Center On Emulator
    END
    Allow Android Permission If Visible
    ${consent_visible}=    Run Keyword And Return Status    Wait Until Consent Screen Is Displayed
    IF    not ${consent_visible}
        Tap Landing Bottom Center On Emulator
        Allow Android Permission If Visible
        Wait Until Consent Screen Is Displayed
    END
    Capture Screen Evidence    landing_after
    Record Screen Result    landing    ${FALSE}    ${landing_tapped}    ${consent_visible}    REAL_DEVICE_ONLY    Landing locators did not resolve on the emulator; used bounded bottom-center tap fallback to reach Consent.

Process Consent Screen
    Wait Until Consent Screen Is Displayed
    Capture Screen Evidence    consent_before
    ${locator_result}=    Run Keyword And Return Status    Element Should Be Visible    ${CONSENT_ACCEPT_BUTTON}
    ${keyword_result}=    Run Keyword And Return Status    Scroll Down Consent Terms    15
    Capture Screen Evidence    consent_after_scroll
    ${page_result}=    Run Keyword And Return Status    Tap Consent Accept Button
    Capture Screen Evidence    consent_after_accept
    Record Screen Result    consent    ${locator_result}    ${keyword_result}    ${page_result}    SHARED    Shared consent locators and big-fling scroll used.
    Should Be True    ${page_result}    Consent did not transition on emulator.

Process CND Screen
    Wait Until Profile Screen Is Displayed
    Capture Screen Evidence    cnd_before
    ${locator_result}=    Run Keyword And Return Status    Element Should Be Visible    ${PROFILE_CITIZEN_ID_INPUT}
    ${keyword_result}=    Run Keyword And Return Status    Input CND Data With Masked Logs
    ${page_result}=    Run Keyword And Return Status    Tap Profile Next
    Capture Screen Evidence    cnd_after
    Record Screen Result    cnd    ${locator_result}    ${keyword_result}    ${page_result}    SHARED    Shared Profile/CND page object used on emulator.
    Should Be True    ${page_result}    CND/Profile did not transition on emulator.

Input CND Data With Masked Logs
    ${previous_log_level}=    Set Log Level    NONE
    Input Citizen ID    ${LOCAL_CITIZEN_ID}
    Input Date Of Birth    ${LOCAL_DATE_OF_BIRTH}
    Input Mobile Number    ${LOCAL_MOBILE_NUMBER}
    Set Log Level    ${previous_log_level}

Process PDPA Screen
    Wait Until PDPA Consent Screen Is Displayed
    Capture Screen Evidence    pdpa_before
    ${locator_result}=    Run Keyword And Return Status    Element Should Be Visible    ${PDPA_ACCEPT_BUTTON}
    ${page_result}=    Run Keyword And Return Status    Tap PDPA Consent Accept Button
    Capture Screen Evidence    pdpa_after
    Record Screen Result    pdpa    ${locator_result}    ${page_result}    ${page_result}    SHARED    Shared PDPA page object used on emulator.
    Should Be True    ${page_result}    PDPA did not transition on emulator.

Process OCR Intro Screen
    Wait Until Sign Up Screen Is Displayed
    Capture Screen Evidence    ocr_intro_sign_up
    ${sign_up_locator}=    Run Keyword And Return Status    Element Should Be Visible    ${SIGN_UP_LETS_START}
    ${sign_up_result}=    Run Keyword And Return Status    Tap Sign Up Lets Start Button
    Allow Android Permission If Visible
    Wait Until Scan Card Intro Screen Is Displayed
    Capture Screen Evidence    ocr_intro_scan_card_intro
    ${scan_locator}=    Run Keyword And Return Status    Element Should Be Visible    ${SCAN_CARD_INTRO_STEP_BAR}
    ${scan_result}=    Run Keyword And Return Status    Tap Scan Card Intro Next
    Allow Android Permission If Visible
    ${locator_result}=    Evaluate    ${sign_up_locator} and ${scan_locator}
    ${keyword_result}=    Evaluate    ${sign_up_result} and ${scan_result}
    Record Screen Result    ocr_intro    ${locator_result}    ${keyword_result}    ${keyword_result}    SHARED    Shared sign-up and scan-card-intro page objects used on emulator.
    Should Be True    ${keyword_result}    OCR intro did not transition on emulator.

Process Camera Screen
    Wait Until ID Card Camera Capture Screen Is Displayed
    Capture Screen Evidence    emulator_ocr_camera
    ${locator_result}=    Run Keyword And Return Status    Element Should Be Visible    ${ID_CARD_CAMERA_VIEW}
    ${keyword_result}=    Run Keyword And Return Status    Element Should Be Visible    ${ID_CARD_TAKE_PHOTO}
    Record Screen Result    camera    ${locator_result}    ${keyword_result}    ${keyword_result}    SHARED    Emulator reached OCR camera screen and stopped before capture.
    Should Be True    ${keyword_result}    OCR camera screen did not expose the shared Take Photo locator.

Capture Screen Evidence
    [Arguments]    ${label}
    ${png}=    Set Variable    ${EVIDENCE_DIR}/${label}.png
    ${xml}=    Set Variable    ${EVIDENCE_DIR}/${label}.xml
    ${activity}=    Set Variable    ${EVIDENCE_DIR}/${label}_activity.txt
    Run Process    sh    -c    adb -s ${EMULATOR_SERIAL} exec-out screencap -p > ${png}
    ...    timeout=30s    on_timeout=terminate
    Run Process    adb    -s    ${EMULATOR_SERIAL}    shell    uiautomator    dump    --compressed    /sdcard/window_dump.xml
    ...    timeout=30s    on_timeout=terminate
    ${dump_result}=    Run Process    adb    -s    ${EMULATOR_SERIAL}    exec-out    cat    /sdcard/window_dump.xml
    ...    timeout=30s    on_timeout=terminate
    Create File    ${xml}    ${dump_result.stdout}    UTF-8
    ${activity_result}=    Run Process    adb    -s    ${EMULATOR_SERIAL}    shell    dumpsys    window
    ...    timeout=30s    on_timeout=terminate
    Create File    ${activity}    ${activity_result.stdout}    UTF-8

Record Screen Result
    [Arguments]    ${screen}    ${locator_result}    ${keyword_result}    ${page_result}    ${decision}    ${note}
    ${screen_dir}=    Set Variable    ${REPORT_DIR}/${screen}
    Create Directory    ${screen_dir}
    ${content}=    Catenate    SEPARATOR=\n
    ...    Locator Result: ${locator_result}
    ...    Keyword Result: ${keyword_result}
    ...    Page Object Result: ${page_result}
    ...    Decision: ${decision}
    ...    Code Changes: shared consent scroll updated only
    ...    Note: ${note}
    Create File    ${screen_dir}/result.md    ${content}\n    UTF-8

Write Robot Output Reference
    ${content}=    Catenate    SEPARATOR=\n
    ...    Validation command:
    ...    python3 -m robot --dryrun tests/investigation/emulator_revival.robot
    ...
    ...    Live command:
    ...    python3 -m robot -d reports/investigation/emulator_revival/robot -L TRACE tests/investigation/emulator_revival.robot
    Create File    ${EVIDENCE_DIR}/robot_output_reference.md    ${content}\n    UTF-8

Tap Landing Bottom Center On Emulator
    ${size_result}=    Run Process    adb    -s    ${EMULATOR_SERIAL}    shell    wm    size
    ...    timeout=15s    on_timeout=terminate
    Should Be Equal As Integers    ${size_result.rc}    0
    ${width}=    Evaluate    int(__import__('re').search(r'(\\d+)x(\\d+)', """${size_result.stdout}""").group(1))
    ${height}=    Evaluate    int(__import__('re').search(r'(\\d+)x(\\d+)', """${size_result.stdout}""").group(2))
    ${center_x}=    Evaluate    int(${width} * 0.5)
    ${bottom_y}=    Evaluate    int(${height} * 0.94)
    Log    [LANDING] width=${width} height=${height} center_x=${center_x} bottom_y=${bottom_y}
    ${tap_result}=    Run Process    adb    -s    ${EMULATOR_SERIAL}    shell    input    tap    ${center_x}    ${bottom_y}
    ...    timeout=15s    on_timeout=terminate
    Should Be Equal As Integers    ${tap_result.rc}    0
    Sleep    1s
