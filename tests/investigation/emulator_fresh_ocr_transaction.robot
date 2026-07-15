*** Settings ***
Documentation    Fresh end-to-end emulator OCR transaction to classify GOD-016 vs stale session.
...              pm clear -> full route -> adb tap Take Photo -> classify result.
...              Investigation only; reuses shared onboarding page keywords.
Library          AppiumLibrary
Library          OperatingSystem
Library          Process
Library          Collections
Library          String
Library          DateTime
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
${REPORT_DIR}       reports/investigation/emulator_fresh_ocr_transaction
${TESTDATA}         testdata/onboarding/ntb.local.yaml
${APP_PATH}         apps/android/app.apk
${MAIN_ACTIVITY}    com.bangkokbank.blue.MainActivity
${EMULATOR_DEVICE}  Android Emulator
${EMULATOR_SERIAL}  ${EMPTY}
${TAP_HELPER}       ${CURDIR}/../../tools/investigation/ocr_tap_classify.py
${ID_CARD_CAMERA_TIMEOUT}    60s


*** Test Cases ***
Fresh Emulator OCR Transaction
    Create Directory    ${REPORT_DIR}
    Resolve Emulator Serial
    Fresh Reset And Record Start
    Open Application On Emulator
    Load Local Onboarding Data
    Process Landing Screen
    Process Consent Screen
    Process CND Screen
    Process PDPA Screen
    Process OCR Intro Screen
    Reach OCR Camera And Record
    Perform Fresh Take Photo Tap
    Wait For And Capture Result
    [Teardown]    Run Keyword And Ignore Error    Close Application


*** Keywords ***
Resolve Emulator Serial
    ${devices}=    Run Process    adb    devices    -l
    ${matches}=    Evaluate    __import__('re').findall(r'^(emulator-\\d+)\\s+device', """${devices.stdout}""", __import__('re').M)
    Should Not Be Empty    ${matches}    No emulator device found.
    Set Test Variable    ${EMULATOR_SERIAL}    ${matches[0]}

Fresh Reset And Record Start
    Run Process    adb    -s    ${EMULATOR_SERIAL}    shell    pm    clear    ${APP_PACKAGE}    timeout=30s    on_timeout=terminate
    Run Process    adb    -s    ${EMULATOR_SERIAL}    install    -r    ${APP_PATH}    timeout=120s    on_timeout=terminate
    Run Process    adb    -s    ${EMULATOR_SERIAL}    logcat    -c    timeout=15s    on_timeout=terminate
    Append To File    ${REPORT_DIR}/route.log    START fresh reset + pm clear @ ${EMPTY}
    ${now}=    Get Current Date
    Append To File    ${REPORT_DIR}/route.log    ${now}\n

Open Application On Emulator
    Open Application    http://127.0.0.1:4723    platformName=Android    automationName=UiAutomator2
    ...    udid=${EMULATOR_SERIAL}    deviceName=${EMULATOR_DEVICE}    appPackage=${APP_PACKAGE}
    ...    appActivity=${MAIN_ACTIVITY}    noReset=${TRUE}    autoGrantPermissions=${TRUE}
    ...    ignoreHiddenApiPolicyError=${TRUE}    newCommandTimeout=300

Load Local Onboarding Data
    ${lvl}=    Set Log Level    NONE
    ${data}=    Load YAML    ${TESTDATA}
    Set Test Variable    ${LOCAL_CITIZEN_ID}    ${data['profile']['citizen_id']}
    Set Test Variable    ${LOCAL_DATE_OF_BIRTH}    ${data['profile']['date_of_birth']}
    Set Test Variable    ${LOCAL_MOBILE_NUMBER}    ${data['profile']['mobile_number']}
    Set Log Level    ${lvl}

Process Landing Screen
    Allow Android Permission If Visible
    ${ok}=    Run Keyword And Return Status    Tap Landing Ready Button
    IF    not ${ok}    Tap Landing Bottom Center
    Allow Android Permission If Visible
    Run Keyword And Ignore Error    Wait Until Consent Screen Is Displayed
    Append To File    ${REPORT_DIR}/route.log    Landing -> Consent done\n

Tap Landing Bottom Center
    ${r}=    Run Process    adb    -s    ${EMULATOR_SERIAL}    shell    wm    size    timeout=15s
    ${w}=    Evaluate    int(__import__('re').search(r'(\\d+)x', "${r.stdout}").group(1))
    ${h}=    Evaluate    int(__import__('re').search(r'x(\\d+)', "${r.stdout}").group(1))
    ${ty}=    Evaluate    int(${h} * 0.94)
    Run Process    adb    -s    ${EMULATOR_SERIAL}    shell    input    tap    ${w//2}    ${ty}    timeout=15s
    Sleep    1s

Process Consent Screen
    Wait Until Consent Screen Is Displayed
    Run Keyword And Ignore Error    Scroll Down Consent Terms    15
    Tap Consent Accept Button
    Append To File    ${REPORT_DIR}/route.log    Consent done\n

Process CND Screen
    Wait Until Profile Screen Is Displayed
    ${lvl}=    Set Log Level    NONE
    Run Keyword And Ignore Error    Input Citizen ID    ${LOCAL_CITIZEN_ID}
    Run Keyword And Ignore Error    Input Date Of Birth    ${LOCAL_DATE_OF_BIRTH}
    Dismiss DOB Picker If Open
    Run Keyword And Ignore Error    Input Mobile Number    ${LOCAL_MOBILE_NUMBER}
    Set Log Level    ${lvl}
    Tap Profile Next
    Append To File    ${REPORT_DIR}/route.log    Profile/CND done\n

Dismiss DOB Picker If Open
    ${open}=    Run Keyword And Return Status    Wait Until Element Is Visible    ${PROFILE_DOB_CONFIRM_BUTTON}    2s
    IF    ${open}    Run Keyword And Ignore Error    Click Element    ${PROFILE_DOB_CONFIRM_BUTTON}

Process PDPA Screen
    Wait Until PDPA Consent Screen Is Displayed
    Tap PDPA Consent Accept Button
    Append To File    ${REPORT_DIR}/route.log    PDPA done\n

Process OCR Intro Screen
    Wait Until Sign Up Screen Is Displayed
    Run Keyword And Ignore Error    Tap Sign Up Lets Start Button
    Allow Android Permission If Visible
    Wait Until Scan Card Intro Screen Is Displayed
    Run Keyword And Ignore Error    Tap Scan Card Intro Next
    Allow Android Permission If Visible
    Append To File    ${REPORT_DIR}/route.log    SignUp + ScanCardIntro done\n

Reach OCR Camera And Record
    Wait Until ID Card Camera Capture Screen Is Displayed
    ${now}=    Get Current Date
    Append To File    ${REPORT_DIR}/route.log    OCR Camera reached @ ${now}\n
    Run Process    adb    -s    ${EMULATOR_SERIAL}    logcat    -c    timeout=15s

Perform Fresh Take Photo Tap
    ${now}=    Get Current Date
    Append To File    ${REPORT_DIR}/route.log    Take Photo tapped (adb) @ ${now}\n
    ${r}=    Run Process    python3    ${TAP_HELPER}    ${EMULATOR_SERIAL}    tap    timeout=30s
    Append To File    ${REPORT_DIR}/route.log    tap helper: ${r.stdout}\n
    Log    TAP=${r.stdout}

Wait For And Capture Result
    # Poll for the camera screen to disappear / result screen to appear, up to 180s
    ${gone}=    Set Variable    ${FALSE}
    FOR    ${i}    IN RANGE    36
        Sleep    5s
        ${present}=    Run Keyword And Return Status    Element Should Be Visible    ${ID_CARD_CAMERA_VIEW}    2s
        IF    not ${present}
            ${gone}=    Set Variable    ${TRUE}
            BREAK
        END
    END
    Append To File    ${REPORT_DIR}/route.log    camera screen gone=${gone} after poll\n
    # Capture final evidence
    Run Process    sh    -c    adb -s ${EMULATOR_SERIAL} exec-out screencap -p > ${REPORT_DIR}/final_screen.png    timeout=30s
    Run Process    adb    -s    ${EMULATOR_SERIAL}    shell    uiautomator    dump    /sdcard/f.xml    timeout=30s
    ${xml}=    Run Process    adb    -s    ${EMULATOR_SERIAL}    exec-out    cat    /sdcard/f.xml    timeout=30s
    Create File    ${REPORT_DIR}/final_screen.xml    ${xml.stdout}    UTF-8
    Run Process    sh    -c    adb -s ${EMULATOR_SERIAL} logcat -d -v time > ${REPORT_DIR}/ocr_logcat.txt    timeout=30s
    # Classify
    ${c}=    Run Process    python3    ${TAP_HELPER}    ${EMULATOR_SERIAL}    classify    timeout=30s
    Append To File    ${REPORT_DIR}/route.log    classify: ${c.stdout}\n
    Create File    ${REPORT_DIR}/result.json    {"classification":"${c.stdout.strip().replace(' ','')}"}
    Log    RESULT=${c.stdout}
