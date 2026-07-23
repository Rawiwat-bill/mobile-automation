*** Settings ***
Documentation    Consent scroll state investigation probe (v2).
...              Scrolls until no-change (enabled-streak disabled — Accept is always enabled=true in XML).
...              Captures native XML + screenshot per swipe, WebView DOM at initial/bottom.
...              Tests Accept tap at bottom to verify functional enablement.
...              Does NOT modify production consent keywords or swipe params.
...              Reuses production big-fling gesture (45ms, 0.87->0.12 y-ratio, 0.12s pause).
...              Uses Run Process adb (not Execute Adb Shell) to avoid --relaxed-security dependency.
Library          AppiumLibrary
Library          OperatingSystem
Library          Process
Library          String
Resource         ../../resources/app/app_keywords.resource
Resource         ../../resources/pages/onboarding/landing_screen_page.resource
Resource         ../../resources/pages/onboarding/consent_screen_page.resource


*** Variables ***
${EMULATOR_SERIAL}        emulator-5554
${REPORT_DIR}             ${CURDIR}/../../reports/investigation/consent_scroll_locator_research
${MAX_SWIPES}             60
${SWIPE_DURATION_MS}      45
${SHORT_PAUSE_S}          0.12
${NO_CHANGE_LIMIT}        3
${I_HAVE_READ_TEXT}       I have read and understood


*** Test Cases ***
Consent Scroll State Capture
    [Documentation]    Drive to consent, capture per-swipe state until no-change, test Accept tap.
    [Tags]    investigation    consent
    Create Directory    ${REPORT_DIR}
    Create Directory    ${REPORT_DIR}/initial
    Create Directory    ${REPORT_DIR}/bottom
    Clear App Data
    Open Consent App
    Allow Android Permission If Visible
    Drive To Consent Screen
    Capture Full State    initial
    ${bottom_swipe}=    Instrumented Scroll To Bottom
    Capture Full State    bottom
    Create File    ${REPORT_DIR}/bottom_swipe.txt    bottom_swipe=${bottom_swipe}\n    UTF-8
    Log    [INVEST] bottom_reached_at_swipe=${bottom_swipe}    WARN
    Test Accept Tap
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
    Log    [INVEST] Reached Consent screen    WARN

Tap Landing Bottom Center
    ${size_result}=    Run Process    adb    -s    ${EMULATOR_SERIAL}    shell    wm    size
    ...    timeout=15s    on_timeout=terminate
    ${width}=    Evaluate    int(__import__('re').search(r'(\\d+)x(\\d+)', """${size_result.stdout}""").group(1))
    ${height}=    Evaluate    int(__import__('re').search(r'(\\d+)x(\\d+)', """${size_result.stdout}""").group(2))
    ${center_x}=    Evaluate    int(${width} * 0.5)
    ${bottom_y}=    Evaluate    int(${height} * 0.94)
    Run Process    adb    -s    ${EMULATOR_SERIAL}    shell    input    tap    ${center_x}    ${bottom_y}
    ...    timeout=15s    on_timeout=terminate
    Sleep    1s

Capture Full State
    [Arguments]    ${label}
    ${dir}=    Set Variable    ${REPORT_DIR}/${label}
    Create Directory    ${dir}
    ${source}=    Get Source
    Create File    ${dir}/page_source.xml    ${source}    UTF-8
    Capture Page Screenshot    ${dir}/screenshot.png
    Capture Webview Source    ${dir}
    Log    [INVEST] Captured state: ${label}    WARN

Capture Webview Source
    [Arguments]    ${dir}
    ${contexts}=    Get Contexts
    ${webview_ctx}=    Evaluate    next((c for c in $contexts if 'WEBVIEW' in str(c)), None)
    ${has_wv}=    Evaluate    $webview_ctx is not None
    IF    ${has_wv}
        ${switched}=    Run Keyword And Return Status    Switch To Context    ${webview_ctx}
        IF    not ${switched}
            Create File    ${dir}/webview_state.txt    webview_context=${webview_ctx}\nswitch_failed=TRUE\n    UTF-8
            Log    [INVEST] Failed to switch to WebView context (likely no Chromedriver). Continuing with native XML only.    WARN
            RETURN
        END
        ${wv_source}=    Get Source
        Create File    ${dir}/webview_source.html    ${wv_source}    UTF-8
        ${wv_has_read}=    Run Keyword And Return Status    Should Contain    ${wv_source}    ${I_HAVE_READ_TEXT}
        Create File    ${dir}/webview_state.txt    webview_context=${webview_ctx}\nwebview_has_i_have_read=${wv_has_read}\n    UTF-8
        Log    [INVEST] WebView context=${webview_ctx} has_i_have_read=${wv_has_read}    WARN
        Switch To Context    NATIVE_APP
    ELSE
        Create File    ${dir}/webview_state.txt    webview_context=NONE_FOUND\ncontexts=${contexts}\n    UTF-8
        Log    [INVEST] No WEBVIEW context found. Contexts: ${contexts}    WARN
    END

Adb Swipe
    [Arguments]    ${start_x}    ${start_y}    ${end_x}    ${end_y}    ${duration_ms}
    Run Process    adb    -s    ${EMULATOR_SERIAL}    shell    input    swipe
    ...    ${start_x}    ${start_y}    ${end_x}    ${end_y}    ${duration_ms}
    ...    timeout=15s    on_timeout=terminate

Instrumented Scroll To Bottom
    ${width}=    Get Window Width
    ${height}=    Get Window Height
    ${start_x}=    Evaluate    int(${width} * 0.5)
    ${start_y}=    Evaluate    int(${height} * 0.87)
    ${end_y}=    Evaluate    int(${height} * 0.12)
    ${prev_hash}=    Set Variable    init
    ${unchanged}=    Set Variable    0
    FOR    ${i}    IN RANGE    ${MAX_SWIPES}
        Adb Swipe    ${start_x}    ${start_y}    ${start_x}    ${end_y}    ${SWIPE_DURATION_MS}
        Sleep    ${SHORT_PAUSE_S}
        ${swipe_num}=    Evaluate    ${i} + 1
        ${padded}=    Evaluate    f'{${swipe_num}:02d}'
        ${swipe_dir}=    Set Variable    ${REPORT_DIR}/swipe_${padded}
        Create Directory    ${swipe_dir}
        ${source}=    Get Source
        Create File    ${swipe_dir}/page_source.xml    ${source}    UTF-8
        Capture Page Screenshot    ${swipe_dir}/screenshot.png
        ${hash}=    Evaluate    hashlib.sha256($source.encode()).hexdigest()[:16]    modules=hashlib
        ${accept_enabled}=    Run Keyword And Return Status    Element Should Be Enabled    ${CONSENT_ACCEPT_BUTTON}
        ${i_have_read}=    Run Keyword And Return Status    Should Contain    ${source}    ${I_HAVE_READ_TEXT}
        Create File    ${swipe_dir}/state.txt    swipe=${swipe_num}\nhash=${hash}\naccept_enabled=${accept_enabled}\ni_have_read=${i_have_read}\n    UTF-8
        Log    [INVEST] swipe=${swipe_num} hash=${hash} accept_enabled=${accept_enabled} i_have_read=${i_have_read}    WARN
        IF    '${hash}' == '${prev_hash}'
            ${unchanged}=    Evaluate    ${unchanged} + 1
        ELSE
            ${unchanged}=    Set Variable    0
        END
        IF    ${unchanged} >= ${NO_CHANGE_LIMIT}
            Log    [INVEST] CONSENT_SCROLL_STALLED at swipe ${swipe_num} (unchanged=${unchanged})    WARN
            RETURN    -1
        END
        ${prev_hash}=    Set Variable    ${hash}
    END
    Log    [INVEST] Max swipes (${MAX_SWIPES}) reached without no-change    WARN
    RETURN    -1

Test Accept Tap
    [Documentation]    Tap Accept via adb at current (bottom) state, check if consent title disappears.
    ${accept_el}=    Run Keyword And Return Status    Wait Until Element Is Visible    ${CONSENT_ACCEPT_BUTTON}    5s
    IF    not ${accept_el}
        Create File    ${REPORT_DIR}/accept_tap_result.txt    accept_visible=FALSE\n    UTF-8
        Log    [INVEST] Accept button not visible at bottom — cannot test tap    WARN
        RETURN
    END
    ${loc}=    Get Element Location    ${CONSENT_ACCEPT_BUTTON}
    ${sz}=    Get Element Size    ${CONSENT_ACCEPT_BUTTON}
    ${cx}=    Evaluate    int($loc['x'] + $sz['width'] / 2)
    ${cy}=    Evaluate    int($loc['y'] + $sz['height'] / 2)
    Log    [INVEST] Accept tap at (${cx}, ${cy}) location=${loc} size=${sz}    WARN
    Run Process    adb    -s    ${EMULATOR_SERIAL}    shell    input    tap    ${cx}    ${cy}
    ...    timeout=15s    on_timeout=terminate
    Sleep    2s
    ${title_gone}=    Run Keyword And Return Status    Wait Until Page Does Not Contain Element    ${CONSENT_TITLE_TEXT}    10s
    Create File    ${REPORT_DIR}/accept_tap_result.txt    tap_x=${cx}\ntap_y=${cy}\nnavigated=${title_gone}\n    UTF-8
    Log    [INVEST] Accept tap result: navigated=${title_gone}    WARN
