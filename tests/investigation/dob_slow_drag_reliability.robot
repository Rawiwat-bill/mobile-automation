*** Settings ***
Documentation    DOB-02 — calibrated slow-drag reliability for the DOB day wheel.
...              Emulator only, DEV only, DOB picker only. Does NOT modify production Select DOB Picker Value.
...              Phase 1: calibrate 6 swipe geometries (400ms) x 3 attempts, measuring row delta + content-desc lag.
...              Phase 2: auto-pick coarse (~2 rows) + fine (~1 row) geometry.
...              Phase 3: validate landing on day 15 three times -> Done -> verify "15 Jan 1992".
Library          AppiumLibrary
Library          OperatingSystem
Library          Process
Library          String
Library          Collections
Library          ../../libraries/config_loader.py
Resource         ../../resources/app/app_keywords.resource
Resource         ../../resources/pages/onboarding/landing_screen_page.resource
Resource         ../../resources/pages/onboarding/consent_screen_page.resource
Resource         ../../resources/pages/onboarding/profile_screen_page.resource


*** Variables ***
${EMULATOR_SERIAL}     emulator-5554
${EMULATOR_DEVICE}     Android Emulator
${REPORT_DIR}          reports/ocr_runtime
${EVIDENCE}            ${REPORT_DIR}/evidence/dob02
${TESTDATA}            testdata/onboarding/ntb.local.yaml
${TARGET_DAY}          15
${TARGET_YEAR}         1992
${TARGET_MONTH}        January
${DRAG_MS}             400
${SAFE_SLEEP}          0.35
${SETTLE_SLEEP}        0.3
${MAX_ALGO_ITERS}      30
@{GEOMETRIES}          0.70|0.30    0.60|0.40    0.55|0.45    0.52|0.48    0.50|0.42    0.58|0.50


*** Test Cases ***
DOB Slow Drag Reliability
    Create Directory    ${REPORT_DIR}
    Create Directory    ${EVIDENCE}
    ${GEO_DELTAS}=    Create Dictionary
    Set Test Variable    ${GEO_DELTAS}    ${GEO_DELTAS}
    Clear App Data On Emulator
    Open Application On Emulator
    Allow Android Permission If Visible
    Drive To Profile
    Tap Profile Element Center    ${PROFILE_DOB_CONTAINER}
    Wait Until Element Is Visible    ${PROFILE_DOB_DAY_PICKER}    5s
    Run Keyword And Ignore Error    Select DOB Picker Value    ${PROFILE_DOB_YEAR_PICKER}    ${TARGET_YEAR}    number
    Run Keyword And Ignore Error    Select DOB Picker Value    ${PROFILE_DOB_MONTH_PICKER}    ${TARGET_MONTH}    month
    Append To File    ${EVIDENCE}/calibration.csv    geometry,attempt,before,after_immediate,after_settled,delta,lag_observed,elapsed_s\n
    Calibrate All Geometries
    Pick Coarse And Fine
    Validate Algorithm Three Attempts
    [Teardown]    Run Keyword And Ignore Error    Close Application


*** Keywords ***
Clear App Data On Emulator
    Run Process    adb    -s    ${EMULATOR_SERIAL}    shell    pm clear    ${APP_PACKAGE}
    ...    timeout=30s    on_timeout=terminate

Open Application On Emulator
    Open Application
    ...    ${APPIUM_URL}
    ...    platformName=Android
    ...    automationName=UiAutomator2
    ...    udid=${EMULATOR_SERIAL}
    ...    deviceName=${EMULATOR_DEVICE}
    ...    appPackage=${APP_PACKAGE}
    ...    appActivity=${APP_ACTIVITY}
    ...    noReset=${TRUE}
    ...    autoGrantPermissions=${TRUE}
    ...    ignoreHiddenApiPolicyError=${TRUE}
    ...    disableWindowAnimation=${TRUE}
    ...    uiautomator2ServerInstallTimeout=120000
    ...    uiautomator2ServerLaunchTimeout=120000
    ...    newCommandTimeout=300

Drive To Profile
    Allow Android Permission If Visible
    ${landing_tapped}=    Run Keyword And Return Status    Tap Landing Ready Button
    Allow Android Permission If Visible
    ${consent_visible}=    Run Keyword And Return Status    Wait Until Element Is Visible    ${CONSENT_TITLE_TEXT}    20s
    IF    not ${consent_visible}
        Tap Landing Bottom Center On Emulator
        Allow Android Permission If Visible
        Wait Until Element Is Visible    ${CONSENT_TITLE_TEXT}    20s
    END
    Run Keyword And Ignore Error    Scroll Down Consent Terms    15
    Run Keyword And Ignore Error    Tap Consent Accept Button
    Wait Until Profile Screen Is Displayed
    Log    [DOB-02] Reached Profile screen

Tap Landing Bottom Center On Emulator
    ${size_result}=    Run Process    adb    -s    ${EMULATOR_SERIAL}    shell    wm    size
    ...    timeout=15s    on_timeout=terminate
    ${width}=    Evaluate    int(__import__('re').search(r'(\\d+)x(\\d+)', """${size_result.stdout}""").group(1))
    ${height}=    Evaluate    int(__import__('re').search(r'(\\d+)x(\\d+)', """${size_result.stdout}""").group(2))
    ${center_x}=    Evaluate    int(${width} * 0.5)
    ${bottom_y}=    Evaluate    int(${height} * 0.94)
    Run Process    adb    -s    ${EMULATOR_SERIAL}    shell    input    tap    ${center_x}    ${bottom_y}
    ...    timeout=15s    on_timeout=terminate
    Sleep    1s

Read Day Int
    ${status}    ${cd}=    Run Keyword And Ignore Error    Get Element Attribute    ${PROFILE_DOB_DAY_PICKER}    content-desc
    ${cd}=    Set Variable IF    '${status}' == 'PASS'    ${cd}    Day picker, 0
    ${day_str}=    Fetch From Right    ${cd}    ,
    ${day_str}=    Strip String    ${day_str}
    ${day}=    Convert To Integer    ${day_str}
    RETURN    ${day}

Day Swipe Ratio
    [Arguments]    ${from_ratio}    ${to_ratio}    ${duration_ms}=${DRAG_MS}
    ${rect}=    Get Element Rect    ${PROFILE_DOB_DAY_PICKER}
    ${cx}=    Evaluate    int(${rect['x']} + (${rect['width']} / 2))
    ${y1}=    Evaluate    int(${rect['y']} + (${rect['height']} * ${from_ratio}))
    ${y2}=    Evaluate    int(${rect['y']} + (${rect['height']} * ${to_ratio}))
    Execute Adb Shell    input    swipe    ${cx}    ${y1}    ${cx}    ${y2}    ${duration_ms}

Reset Day To Low
    ${current}=    Read Day Int
    FOR    ${i}    IN RANGE    20
        IF    ${current} <= 3
            BREAK
        END
        Day Swipe Ratio    0.30    0.70    ${DRAG_MS}
        Sleep    ${SAFE_SLEEP}
        ${current}=    Read Day Int
    END
    Log    [DOB-02] reset to day=${current}

Calibrate All Geometries
    FOR    ${geo}    IN    @{GEOMETRIES}
        Reset Day To Low
        Calibrate One Geometry    ${geo}
    END

Calibrate One Geometry
    [Arguments]    ${geo}
    ${parts}=    Split String    ${geo}    |
    ${from}=    Set Variable    ${parts[0]}
    ${to}=    Set Variable    ${parts[1]}
    FOR    ${attempt}    IN RANGE    1    4
        ${before}=    Read Day Int
        ${t0}=    Evaluate    time.time()    modules=time
        Day Swipe Ratio    ${from}    ${to}    ${DRAG_MS}
        ${after_imm}=    Read Day Int
        Sleep    ${SETTLE_SLEEP}
        ${after_settled}=    Read Day Int
        ${t1}=    Evaluate    time.time()    modules=time
        ${lag}=    Evaluate    int(${after_imm} != ${after_settled})
        ${delta}=    Evaluate    ${after_settled} - ${before}
        ${elapsed}=    Evaluate    round(${t1} - ${t0}, 3)
        Append To File    ${EVIDENCE}/calibration.csv    ${geo},${attempt},${before},${after_imm},${after_settled},${delta},${lag},${elapsed}\n
        Log    [DOB-02] geo=${geo} attempt=${attempt} before=${before} after_imm=${after_imm} settled=${after_settled} delta=${delta} lag=${lag} elapsed=${elapsed}
        ${has_geo}=    Run Keyword And Return Status    Dictionary Should Contain Key    ${GEO_DELTAS}    ${geo}
        ${deltas}=    Run Keyword If    ${has_geo}    Get From Dictionary    ${GEO_DELTAS}    ${geo}    ELSE    Create List
        Append To List    ${deltas}    ${delta}
        Set To Dictionary    ${GEO_DELTAS}    ${geo}    ${deltas}
    END

Pick Coarse And Fine
    ${avg}=    Evaluate    {k: round(sum(v)/len(v), 3) for k,v in ${GEO_DELTAS}.items()}
    ${coarse}=    Evaluate    min(${avg}.items(), key=lambda kv: abs(kv[1]-2))[0]
    ${fine}=    Evaluate    min({k:v for k,v in ${avg}.items() if v > 0}.items(), key=lambda kv: abs(kv[1]-1))[0]
    Set Test Variable    ${COARSE_GEO}    ${coarse}
    Set Test Variable    ${FINE_GEO}    ${fine}
    Log    [DOB-02] PICK avg=${avg} -> COARSE=${coarse} FINE=${fine}
    Create File    ${EVIDENCE}/chosen.txt    avg_deltas=${avg}\ncoarse=${coarse}\nfine=${fine}\n    UTF-8

Get Directional Ratios
    [Arguments]    ${current}
    ${diff}=    Evaluate    ${TARGET_DAY} - ${current}
    ${geo}=    Set Variable If    abs(${diff}) > 2    ${COARSE_GEO}    ${FINE_GEO}
    ${parts}=    Split String    ${geo}    |
    ${a}=    Set Variable    ${parts[0]}
    ${b}=    Set Variable    ${parts[1]}
    IF    ${diff} > 0
        ${from}=    Set Variable    ${a}
        ${to}=    Set Variable    ${b}
    ELSE
        ${from}=    Set Variable    ${b}
        ${to}=    Set Variable    ${a}
    END
    RETURN    ${from}    ${to}

Run Algorithm To Target Day
    ${current}=    Read Day Int
    Log    [DOB-02] algo start day=${current}
    FOR    ${i}    IN RANGE    ${MAX_ALGO_ITERS}
        IF    ${current} == ${TARGET_DAY}
            BREAK
        END
        ${from}    ${to}=    Get Directional Ratios    ${current}
        Day Swipe Ratio    ${from}    ${to}    ${DRAG_MS}
        Sleep    ${SAFE_SLEEP}
        ${current}=    Read Day Int
        Log    [DOB-02] algo iter=${i} current=${current} target=${TARGET_DAY}
    END
    ${ok}=    Evaluate    ${current} == ${TARGET_DAY}
    RETURN    ${ok}    ${current}

Validate Algorithm Three Attempts
    Append To File    ${EVIDENCE}/validation.csv    attempt,landed_day,field_text,exact_match,elapsed_s\n
    FOR    ${attempt}    IN RANGE    1    4
        Reset Day To Low
        ${t0}=    Evaluate    time.time()    modules=time
        ${ok}    ${landed}=    Run Algorithm To Target Day
        Run Keyword And Ignore Error    Click Element    ${PROFILE_DOB_CONFIRM_BUTTON}
        Run Keyword And Ignore Error    Wait Until Page Does Not Contain Element    ${PROFILE_DOB_DAY_PICKER}    5s
        ${fstatus}    ${field}=    Run Keyword And Ignore Error    Get Text    ${PROFILE_DOB_INPUT}
        ${field}=    Set Variable IF    '${fstatus}' == 'PASS'    ${field}    <read_failed>
        ${t1}=    Evaluate    time.time()    modules=time
        ${elapsed}=    Evaluate    round(${t1} - ${t0}, 3)
        ${clean}=    Replace String Using Regexp    ${field}    \\.    ${EMPTY}
        ${clean}=    Strip String    ${clean}
        ${exact}=    Evaluate    int('${clean}' == '15 Jan 1992')
        Append To File    ${EVIDENCE}/validation.csv    ${attempt},${landed},${field},${exact},${elapsed}\n
        Log    [DOB-02] VALIDATION attempt=${attempt} landed=${landed} field='${field}' exact=${exact} elapsed=${elapsed}
        Run Keyword And Ignore Error    Tap Profile Element Center    ${PROFILE_DOB_CONTAINER}
        Run Keyword And Ignore Error    Wait Until Element Is Visible    ${PROFILE_DOB_DAY_PICKER}    5s
    END
