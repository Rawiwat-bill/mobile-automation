*** Settings ***
Documentation    Part D: validate one geometry candidate through the real OCR flow.
...              Drive to OCR Camera, capture before, tap Take Photo, poll FIRST terminal state.
...              RGI-045/DOPA => ACCEPTED, RGI-055 => REJECTED, service/GOD => RUNTIME_ERROR.
...              Stop on first terminal; later GOD never overwrites an earlier RGI.
Library          AppiumLibrary
Library          OperatingSystem
Library          Process
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
${REPORT_DIR}    reports/investigation/geometry_optimizer_safe_fit_v1
${TESTDATA}      testdata/onboarding/ntb.local.yaml
${APP_PATH}      apps/android/app.apk
${MAIN_ACTIVITY}    com.bangkokbank.blue.MainActivity
${EMULATOR_SERIAL}    emulator-5554
${CANDIDATE}     apps/android/mock/derived/ntb_id_card_layout_safe_fit_v1.png


*** Test Cases ***
Validate Safe-Fit Candidate Through OCR Flow
    Create Directory    ${REPORT_DIR}
    Resolve Emulator Serial
    Record Emulator Args
    Fresh Reset
    Open Application    http://127.0.0.1:4723    platformName=Android    automationName=UiAutomator2
    ...    udid=${EMULATOR_SERIAL}    deviceName=Android Emulator    appPackage=${APP_PACKAGE}
    ...    appActivity=${MAIN_ACTIVITY}    noReset=${TRUE}    autoGrantPermissions=${TRUE}
    ...    ignoreHiddenApiPolicyError=${TRUE}    newCommandTimeout=300
    Load Local Onboarding Data
    Append To File    ${REPORT_DIR}/route.log    LANDING first app screen: waiting\n
    # --- route to OCR Camera (proven emulator flow) ---
    Allow Android Permission If Visible
    ${ok}=    Run Keyword And Return Status    Tap Landing Ready Button
    IF    not ${ok}    Tap Landing Bottom Center
    Allow Android Permission If Visible
    Append To File    ${REPORT_DIR}/route.log    Landing done\n
    Run Keyword And Ignore Error    Wait Until Consent Screen Is Displayed
    Run Keyword And Ignore Error    Scroll Down Consent Terms    15
    Tap Consent Accept Button
    Append To File    ${REPORT_DIR}/route.log    Consent done\n
    Wait Until Profile Screen Is Displayed
    ${lvl}=    Set Log Level    NONE
    Run Keyword And Ignore Error    Input Citizen ID    ${LOCAL_CITIZEN_ID}
    Run Keyword And Ignore Error    Input Date Of Birth    ${LOCAL_DATE_OF_BIRTH}
    Run Keyword And Ignore Error    Dismiss DOB Picker If Open
    Run Keyword And Ignore Error    Input Mobile Number    ${LOCAL_MOBILE_NUMBER}
    Set Log Level    ${lvl}
    Tap Profile Next
    Append To File    ${REPORT_DIR}/route.log    Profile/CND done\n
    Wait Until PDPA Consent Screen Is Displayed
    Tap PDPA Consent Accept Button
    Wait Until Sign Up Screen Is Displayed
    Run Keyword And Ignore Error    Tap Sign Up Lets Start Button
    Allow Android Permission If Visible
    Wait Until Scan Card Intro Screen Is Displayed
    Run Keyword And Ignore Error    Tap Scan Card Intro Next
    Allow Android Permission If Visible
    Wait Until ID Card Camera Capture Screen Is Displayed
    Append To File    ${REPORT_DIR}/route.log    OCR Camera reached\n
    Capture Before Evidence
    ${tap_time}=    Get Current Date
    Tap Take Photo Button
    Append To File    ${REPORT_DIR}/route.log    Take Photo tapped @ ${tap_time}\n
    ${cls}=    Poll First Terminal State
    ${final_time}=    Get Current Date
    ${latency}=    Subtract Date From Date    ${final_time}    ${tap_time}    result_separator=,
    Capture Final Evidence
    Write Runtime Result    ${cls}    ${tap_time}    ${final_time}    ${latency}
    [Teardown]    Run Keyword And Ignore Error    Close Application


*** Keywords ***
Resolve Emulator Serial
    ${devices}=    Run Process    adb    devices    -l
    ${matches}=    Evaluate    __import__('re').findall(r'^(emulator-\\d+)\\s+device', """${devices.stdout}""", __import__('re').M)
    Should Not Be Empty    ${matches}    No emulator device found.
    Set Test Variable    ${EMULATOR_SERIAL}    ${matches[0]}

Record Emulator Args
    ${boot}=    Run Process    adb    -s    ${EMULATOR_SERIAL}    shell    getprop    sys.boot_completed    timeout=10s
    Append To File    ${REPORT_DIR}/route.log    boot_completed=${boot.stdout.strip()}\n
    ${ps}=    Run Process    sh    -c    ps -ax | grep 'local_android_36' | grep -v grep    timeout=10s
    Create File    ${REPORT_DIR}/emulator_args.txt    ${ps.stdout}\ncandidate=${CANDIDATE}\n

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
    Run Process    adb    -s    ${EMULATOR_SERIAL}    shell    input    tap    ${w//2}    ${h*94//100}    timeout=15s
    Sleep    1s

Dismiss DOB Picker If Open
    ${open}=    Run Keyword And Return Status    Wait Until Element Is Visible    ${PROFILE_DOB_CONFIRM_BUTTON}    2s
    IF    ${open}    Run Keyword And Ignore Error    Click Element    ${PROFILE_DOB_CONFIRM_BUTTON}

Capture Before Evidence
    Run Process    sh    -c    adb -s ${EMULATOR_SERIAL} exec-out screencap -p > ${REPORT_DIR}/before_capture.png    timeout=30s
    Run Process    adb    -s    ${EMULATOR_SERIAL}    shell    uiautomator    dump    /sdcard/b.xml    timeout=30s
    ${xml}=    Run Process    adb    -s    ${EMULATOR_SERIAL}    exec-out    cat    /sdcard/b.xml    timeout=30s
    Create File    ${REPORT_DIR}/before_capture.xml    ${xml.stdout}    UTF-8
    ${act}=    Run Process    adb    -s    ${EMULATOR_SERIAL}    shell    dumpsys    activity    activities    timeout=15s
    Create File    ${REPORT_DIR}/activity_before.txt    ${act.stdout}    UTF-8

Tap Take Photo Button
    # proven adb tap on the round Take Photo button via UI dump (content-desc Take photo)
    Run Process    adb    -s    ${EMULATOR_SERIAL}    shell    uiautomator    dump    /sdcard/tp.xml    timeout=15s
    ${x}=    Run Process    adb    -s    ${EMULATOR_SERIAL}    exec-out    cat    /sdcard/tp.xml    timeout=15s
    ${tgt}=    Evaluate    __import__('re').search(r'content-desc="Take photo"[^>]*bounds="\[(\d+),(\d+)\]\[(\d+),(\d+)\]"', """${x.stdout}""")
    Should Not Be Equal    ${tgt}    ${None}    Take photo button not found
    ${cx}=    Evaluate    (int("${tgt.group(1)}")+int("${tgt.group(3)}"))//2
    ${cy}=    Evaluate    (int("${tgt.group(2)}")+int("${tgt.group(4)}"))//2
    Run Process    adb    -s    ${EMULATOR_SERIAL}    shell    input    tap    ${cx}    ${cy}    timeout=15s
    Append To File    ${REPORT_DIR}/route.log    Take Photo adb tap at ${cx},${cy}\n

Poll First Terminal State
    FOR    ${i}    IN RANGE    30
        Run Process    adb    -s    ${EMULATOR_SERIAL}    shell    uiautomator    dump    /sdcard/t.xml    timeout=10s    on_timeout=terminate
        ${x}=    Run Process    adb    -s    ${EMULATOR_SERIAL}    exec-out    cat    /sdcard/t.xml    timeout=10s
        ${cls}=    Classify Terminal    ${x.stdout}
        Append To File    ${REPORT_DIR}/route.log    poll ${i} -> ${cls}\n
        IF    '${cls}' != 'PENDING'
            RETURN    ${cls}
        END
        Sleep    2s
    END
    [Return]    LAYOUT_TIMEOUT

Classify Terminal
    [Arguments]    ${xml}
    ${low}=    Convert To Lower Case    ${xml}
    ${rgi045}=    Run Keyword And Return Status    Should Contain    ${xml}    RGI-045
    ${rgi055}=    Run Keyword And Return Status    Should Contain    ${xml}    RGI-055
    ${dopa}=    Run Keyword And Return Status    Should Contain    ${xml}    screenDopaInformation
    ${svc}=    Run Keyword And Return Status    Should Contain    ${low}    service is not available
    ${god}=    Run Keyword And Return Status    Should Contain    ${low}    god-
    ${capfail}=    Run Keyword And Return Status    Should Contain    ${low}    capture failure
    ${cls}=    Set Variable If    ${rgi045}    LAYOUT_ACCEPTED_RGI045
    ...    ${rgi055}    LAYOUT_REJECTED_RGI055
    ...    ${dopa}    LAYOUT_ACCEPTED_DOPA
    ...    ${svc}    LAYOUT_RUNTIME_ERROR_SVC
    ...    ${god}    LAYOUT_RUNTIME_ERROR_GOD
    ...    ${capfail}    LAYOUT_RUNTIME_ERROR_CAPFAIL
    ...    PENDING
    [Return]    ${cls}

Capture Final Evidence
    Run Process    sh    -c    adb -s ${EMULATOR_SERIAL} exec-out screencap -p > ${REPORT_DIR}/final_screen.png    timeout=30s
    Run Process    adb    -s    ${EMULATOR_SERIAL}    shell    uiautomator    dump    /sdcard/f.xml    timeout=30s
    ${xml}=    Run Process    adb    -s    ${EMULATOR_SERIAL}    exec-out    cat    /sdcard/f.xml    timeout=30s
    Create File    ${REPORT_DIR}/final_screen.xml    ${xml.stdout}    UTF-8
    Run Process    sh    -c    "adb -s ${EMULATOR_SERIAL} logcat -d -v time > ${REPORT_DIR}/logcat.txt"    timeout=30s

Write Runtime Result
    [Arguments]    ${cls}    ${tap_time}    ${final_time}    ${latency}
    ${final}=    Set Variable If    '${cls}'.startswith('LAYOUT_ACCEPTED')    LAYOUT_ACCEPTED
    ...    '${cls}'.startswith('LAYOUT_REJECTED')    LAYOUT_REJECTED
    ...    '${cls}'.startswith('LAYOUT_RUNTIME_ERROR')    LAYOUT_RUNTIME_ERROR
    ...    '${cls}' == 'LAYOUT_TIMEOUT'    LAYOUT_TIMEOUT
    ...    LAYOUT_UNKNOWN
    Append To File    ${REPORT_DIR}/route.log    FIRST TERMINAL: ${cls} -> ${final}\n
    Create File    ${REPORT_DIR}/runtime_result.json    {"raw_classification":"${cls}","final_classification":"${final}","take_photo_time":"${tap_time}","terminal_time":"${final_time}","latency_seconds":${latency},"candidate":"${CANDIDATE}"}
