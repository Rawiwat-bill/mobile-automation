*** Settings ***
Documentation    Independent validation of state-based consent scrolling.
...              Bottom signal: "I have read and understood" native TextView (virtualized).
...              Validates: marker absent initially → swipe until found → tap Accept → verify navigation.
...              Does NOT modify production code. Uses Run Process adb for swipes (no --relaxed-security).
Library          AppiumLibrary
Library          OperatingSystem
Library          Process
Library          String
Resource         ../../resources/app/app_keywords.resource
Resource         ../../resources/pages/onboarding/landing_screen_page.resource
Resource         ../../resources/pages/onboarding/consent_screen_page.resource


*** Variables ***
${EMULATOR_SERIAL}        emulator-5554
${REPORT_DIR}             ${CURDIR}/../../reports/investigation/consent_state_based_scroll_validation
${MAX_SWIPES}             10
${SWIPE_DURATION_MS}      45
${SETTLE_TIME_S}          0.2
${BOTTOM_MARKER}          xpath=//android.widget.TextView[contains(@text, "I have read and understood")]
${MARKER_TEXT}            I have read and understood
${NEXT_SCREEN_SIGNAL}     accessibility_id=Tell us about you


*** Test Cases ***
Validate State-Based Consent Scroll
    [Documentation]    Fresh consent flow: detect bottom marker → tap Accept → verify navigation.
    [Tags]    investigation    consent    validation
    Create Directory    ${REPORT_DIR}
    ${t0}=    Evaluate    time.time()    modules=time
    ${route}=    Set Variable    [${t0}] Test started
    Clear App Data
    Open Consent App
    Allow Android Permission If Visible
    Drive To Consent Screen
    ${route}=    Set Variable    ${route}\nReached consent screen
    # Capture initial state — check if marker already present
    ${init_hash}    ${init_marker}=    Capture Validation State    initial    0    ${t0}
    ${route}=    Set Variable    ${route}\nInitial: hash=${init_hash} marker=${init_marker}
    ${swipes}=    Set Variable    0
    ${stall_count}=    Set Variable    0
    ${classification}=    Set Variable    PENDING
    ${marker_found}=    Set Variable    ${init_marker}
    ${prev_hash}=    Set Variable    ${init_hash}
    IF    ${init_marker}
        ${classification}=    Set Variable    STATE_BASED_SCROLL_VALIDATED
        ${route}=    Set Variable    ${route}\nMarker present at initial (content already at bottom)
    ELSE
        FOR    ${i}    IN RANGE    ${MAX_SWIPES}
            ${pre_hash}=    Set Variable    ${prev_hash}
            Adb Swipe Consent
            Sleep    ${SETTLE_TIME_S}
            ${swipes}=    Evaluate    ${swipes} + 1
            ${cur_hash}    ${cur_marker}=    Capture Validation State    swipe_${swipes}    ${swipes}    ${t0}
            ${route}=    Set Variable    ${route}\nSwipe ${swipes}: hash=${cur_hash} marker=${cur_marker}
            IF    '${cur_hash}' == '${pre_hash}'
                ${stall_count}=    Evaluate    ${stall_count} + 1
            ELSE
                ${stall_count}=    Set Variable    0
            END
            IF    ${cur_marker}
                ${marker_found}=    Set Variable    ${TRUE}
                ${classification}=    Set Variable    STATE_BASED_SCROLL_VALIDATED
                ${route}=    Set Variable    ${route}\nMarker found at swipe ${swipes}
                BREAK
            END
            IF    ${stall_count} >= 2
                ${classification}=    Set Variable    CONSENT_SCROLL_STALLED
                ${route}=    Set Variable    ${route}\nCONSENT_SCROLL_STALLED at swipe ${swipes} (2 consecutive unchanged hashes)
                BREAK
            END
            ${prev_hash}=    Set Variable    ${cur_hash}
        END
        IF    '${classification}' == 'PENDING'
            ${classification}=    Set Variable    BOTTOM_MARKER_NOT_FOUND
            ${route}=    Set Variable    ${route}\nBOTTOM_MARKER_NOT_FOUND after ${swipes} swipes
        END
    END
    Capture Validation State    bottom    ${swipes}    ${t0}
    ${navigated}=    Set Variable    ${FALSE}
    ${marker_class}=    Set Variable    UNKNOWN
    IF    '${classification}' == 'STATE_BASED_SCROLL_VALIDATED'
        ${marker_class}=    Get Element Attribute    ${BOTTOM_MARKER}    class
        Should Contain    ${marker_class}    TextView    msg=Marker is not a TextView: ${marker_class}
        ${route}=    Set Variable    ${route}\nMarker verified as ${marker_class}
        ${navigated}=    Tap Accept And Verify Navigation
        ${route}=    Set Variable    ${route}\nAccept tap: navigated=${navigated}
        IF    not ${navigated}
            ${classification}=    Set Variable    ACCEPT_NAVIGATION_FAILED
            ${route}=    Set Variable    ${route}\nACCEPT_NAVIGATION_FAILED
        END
    END
    Capture Validation State    after_accept    ${swipes}    ${t0}
    ${t1}=    Evaluate    time.time()    modules=time
    ${duration}=    Evaluate    round(${t1} - ${t0}, 2)
    ${route}=    Set Variable    ${route}\nDuration: ${duration}s\nClassification: ${classification}
    Create File    ${REPORT_DIR}/route.log    ${route}\n    UTF-8
    Write Result Json    ${classification}    ${swipes}    ${marker_found}    ${navigated}    ${duration}    ${marker_class}
    Log    [VALIDATION] classification=${classification} swipes=${swipes} marker_found=${marker_found} navigated=${navigated} duration=${duration}s    WARN
    Run Keyword If    '${classification}' != 'STATE_BASED_SCROLL_VALIDATED'    Fail    Classification: ${classification}
    [Teardown]    Run Keyword And Ignore Error    Close Application


*** Keywords ***
Clear App Data
    Run Process    adb    -s    ${EMULATOR_SERIAL}    shell    pm clear    ${APP_PACKAGE}
    ...    timeout=30s    on_timeout=terminate

Open Consent App
    Open Application
    ...    ${APPIUM_URL}
    ...    platformName=Android
    ...    automationName=UiAutomator2
    ...    udid=${EMULATOR_SERIAL}
    ...    deviceName=${DEVICE_NAME}
    ...    appPackage=${APP_PACKAGE}
    ...    appActivity=${APP_ACTIVITY}
    ...    noReset=${TRUE}
    ...    autoGrantPermissions=${TRUE}
    ...    ignoreHiddenApiPolicyError=${TRUE}
    ...    disableWindowAnimation=${TRUE}
    ...    uiautomator2ServerInstallTimeout=120000
    ...    uiautomator2ServerLaunchTimeout=120000
    ...    newCommandTimeout=300

Drive To Consent Screen
    Allow Android Permission If Visible
    ${landing_tapped}=    Run Keyword And Return Status    Tap Landing Ready Button
    Allow Android Permission If Visible
    ${consent_visible}=    Run Keyword And Return Status    Wait Until Element Is Visible    ${CONSENT_TITLE_TEXT}    20s
    IF    not ${consent_visible}
        Tap Landing Bottom Center
        Allow Android Permission If Visible
        Wait Until Element Is Visible    ${CONSENT_TITLE_TEXT}    20s
    END
    Wait Until Element Is Visible    ${CONSENT_WEBVIEW}    10s

Tap Landing Bottom Center
    ${size_result}=    Run Process    adb    -s    ${EMULATOR_SERIAL}    shell    wm    size
    ...    timeout=15s    on_timeout=terminate
    ${width}=    Evaluate    int(__import__('re').search(r'(\\d+)x(\\d+)', """${size_result.stdout}""").group(1))
    ${height}=    Evaluate    int(__import__('re').search(r'(\\d+)x(\\d+)', """${size_result.stdout}""").group(2))
    ${cx}=    Evaluate    int(${width} * 0.5)
    ${cy}=    Evaluate    int(${height} * 0.94)
    Run Process    adb    -s    ${EMULATOR_SERIAL}    shell    input    tap    ${cx}    ${cy}
    ...    timeout=15s    on_timeout=terminate
    Sleep    1s

Adb Swipe Consent
    ${width}=    Get Window Width
    ${height}=    Get Window Height
    ${sx}=    Evaluate    int(${width} * 0.5)
    ${sy}=    Evaluate    int(${height} * 0.87)
    ${ey}=    Evaluate    int(${height} * 0.12)
    Run Process    adb    -s    ${EMULATOR_SERIAL}    shell    input    swipe
    ...    ${sx}    ${sy}    ${sx}    ${ey}    ${SWIPE_DURATION_MS}
    ...    timeout=15s    on_timeout=terminate

Capture Validation State
    [Arguments]    ${label}    ${swipe_num}    ${t0}
    ${dir}=    Set Variable    ${REPORT_DIR}/${label}
    Create Directory    ${dir}
    ${source}=    Get Source
    Create File    ${dir}/page_source.xml    ${source}    UTF-8
    Capture Page Screenshot    ${dir}/screenshot.png
    ${hash}=    Evaluate    hashlib.sha256($source.encode()).hexdigest()[:16]    modules=hashlib
    ${elapsed}=    Evaluate    round(time.time() - $t0, 2)    modules=time
    ${marker}=    Run Keyword And Return Status    Should Contain    ${source}    ${MARKER_TEXT}
    Create File    ${dir}/state.txt    swipe=${swipe_num}\nhash=${hash}\nmarker=${marker}\nelapsed=${elapsed}\n    UTF-8
    Log    [STATE] ${label}: swipe=${swipe_num} hash=${hash} marker=${marker} elapsed=${elapsed}s    WARN
    RETURN    ${hash}    ${marker}

Tap Accept And Verify Navigation
    ${accept_visible}=    Run Keyword And Return Status    Wait Until Element Is Visible    ${CONSENT_ACCEPT_BUTTON}    5s
    IF    not ${accept_visible}
        Log    [VALIDATION] Accept button not visible    WARN
        RETURN    ${FALSE}
    END
    ${loc}=    Get Element Location    ${CONSENT_ACCEPT_BUTTON}
    ${sz}=    Get Element Size    ${CONSENT_ACCEPT_BUTTON}
    ${cx}=    Evaluate    int($loc['x'] + $sz['width'] / 2)
    ${cy}=    Evaluate    int($loc['y'] + $sz['height'] / 2)
    Log    [VALIDATION] Tapping Accept at (${cx}, ${cy})    WARN
    Run Process    adb    -s    ${EMULATOR_SERIAL}    shell    input    tap    ${cx}    ${cy}
    ...    timeout=15s    on_timeout=terminate
    Sleep    2s
    ${navigated}=    Run Keyword And Return Status    Wait Until Element Is Visible    ${NEXT_SCREEN_SIGNAL}    10s
    Log    [VALIDATION] Navigation: navigated=${navigated} (next_screen=${NEXT_SCREEN_SIGNAL})    WARN
    RETURN    ${navigated}

Write Result Json
    [Arguments]    ${classification}    ${swipes}    ${marker_found}    ${navigated}    ${duration}    ${marker_class}
    ${result}=    Evaluate    json.dumps({"classification": $classification, "swipes_to_marker": $swipes, "marker_found": $marker_found, "marker_class": $marker_class, "navigated": $navigated, "duration_s": $duration, "next_screen_signal": "accessibility_id=Tell us about you", "bottom_marker_locator": "xpath=//android.widget.TextView[contains(@text, 'I have read and understood')]", "max_swipes": 10}, indent=2)    modules=json
    Create File    ${REPORT_DIR}/result.json    ${result}    UTF-8
