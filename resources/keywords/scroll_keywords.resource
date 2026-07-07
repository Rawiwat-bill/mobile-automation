*** Settings ***
Library    AppiumLibrary
Library    Process


*** Variables ***
${RESPONSIVE_SCROLL_START_Y_RATIO}    0.82
${RESPONSIVE_SCROLL_END_Y_RATIO}      0.18
${RESPONSIVE_SCROLL_X_RATIO}          0.5
${RESPONSIVE_SCROLL_DURATION_MS}      800
${RESPONSIVE_SCROLL_MARKER}           android.widget.TextView
${RESPONSIVE_SCROLL_NO_CHANGE_LIMIT}  3
${CONSENT_BIG_FLING_START_Y_RATIO}    0.87
${CONSENT_BIG_FLING_END_Y_RATIO}      0.12
${CONSENT_BIG_FLING_X_RATIO}          0.5
${CONSENT_BIG_FLING_DURATION_MS}      45
${CONSENT_BIG_FLING_SHORT_PAUSE_S}    0.12
${CONSENT_BIG_FLING_LONG_PAUSE_S}     0.6
${CONSENT_BIG_FLING_LONG_PAUSE_EVERY}  10


*** Keywords ***
Scroll Down Page Responsively
    [Documentation]    Scrolls down using adb swipe coordinates calculated from the active Appium window.
    ...                Intended for React Native/WebView pages where Appium gestures are unreliable.
    ...                ADB uiautomator XML is sampled after each swipe to stop at a bottom marker
    ...                or after repeated no-change dumps.
    [Arguments]    ${max_swipes}=1    ${duration_ms}=${RESPONSIVE_SCROLL_DURATION_MS}    ${bottom_marker}=${EMPTY}    ${no_change_limit}=${RESPONSIVE_SCROLL_NO_CHANGE_LIMIT}
    ${width}=     Get Window Width
    ${height}=    Get Window Height
    ${start_x}=   Evaluate    int(${width} * ${RESPONSIVE_SCROLL_X_RATIO})
    ${start_y}=   Evaluate    int(${height} * ${RESPONSIVE_SCROLL_START_Y_RATIO})
    ${end_y}=     Evaluate    int(${height} * ${RESPONSIVE_SCROLL_END_Y_RATIO})
    ${previous_hash}    ${before_node_count}    ${before_marker_count}    ${bottom_marker_found}=    Dump Current Screen Xml Stats With Adb    ${bottom_marker}
    ${xml_available}=    Evaluate    ${before_node_count} >= 0
    Log    [SCROLL] width=${width} height=${height} start_x=${start_x} start_y=${start_y} end_y=${end_y} duration_ms=${duration_ms}
    Log    [SCROLL] before_marker_count=${before_marker_count}
    Log    [SCROLL] before_node_count=${before_node_count} before_hash=${previous_hash}
    ${swipe_count}=    Set Variable    0
    ${unchanged_count}=    Set Variable    0
    ${bottom_status}=    Set Variable    NOT_REACHED
    FOR    ${index}    IN RANGE    ${max_swipes}
        Execute Adb Shell    input    swipe    ${start_x}    ${start_y}    ${start_x}    ${end_y}    ${duration_ms}
        ${swipe_count}=    Evaluate    ${swipe_count} + 1
        IF    ${xml_available}
            ${current_hash}    ${node_count}    ${marker_count}    ${bottom_marker_found}=    Dump Current Screen Xml Stats With Adb    ${bottom_marker}
            IF    ${node_count} < 0
                ${xml_available}=    Set Variable    ${FALSE}
            END
        ELSE
            ${current_hash}    ${node_count}    ${marker_count}    ${bottom_marker_found}=    Get Current Screenshot Scroll Stats With Adb
        END
        IF    '${current_hash}' == '${previous_hash}'
            ${unchanged_count}=    Evaluate    ${unchanged_count} + 1
        ELSE
            ${unchanged_count}=    Set Variable    0
        END
        Log    [SCROLL] swipe=${swipe_count} node_count=${node_count} marker_count=${marker_count} hash=${current_hash} unchanged_count=${unchanged_count}
        IF    ${bottom_marker_found}
            ${bottom_status}=    Set Variable    MARKER
            BREAK
        END
        IF    ${unchanged_count} >= ${no_change_limit}
            ${bottom_status}=    Set Variable    NO_CHANGE
            BREAK
        END
        ${previous_hash}=    Set Variable    ${current_hash}
    END
    Log    [SCROLL] swipe_count=${swipe_count}
    Log    [SCROLL] bottom_status=${bottom_status}
    Set Test Variable    ${RESPONSIVE_SCROLL_BOTTOM_STATUS}    ${bottom_status}
    Set Test Variable    ${RESPONSIVE_SCROLL_SWIPE_COUNT}    ${swipe_count}
    RETURN    ${swipe_count}

Count Scroll XML Markers
    [Arguments]    ${source}
    ${count}=    Evaluate    str($source).count($RESPONSIVE_SCROLL_MARKER)
    RETURN    ${count}

Dump Current Screen Xml Stats With Adb
    [Arguments]    ${bottom_marker}=${EMPTY}
    ${dump_result}=    Run Process    adb    shell    uiautomator    dump    --compressed    /sdcard/window_dump.xml
    ...    timeout=20s    on_timeout=terminate
    IF    ${dump_result.rc} != 0
        Log    [SCROLL] adb uiautomator dump failed with rc=${dump_result.rc}; using screenshot hash for no-change detection.    WARN
        ${fallback_hash}=    Get Current Screenshot Hash With Adb
        RETURN    ${fallback_hash}    -1    -1    ${FALSE}
    END
    ${hash_result}=    Run Process    adb    shell    toybox    sha256sum    /sdcard/window_dump.xml
    ...    timeout=20s    on_timeout=terminate
    Should Be Equal As Integers    ${hash_result.rc}    0
    ${hash}=    Evaluate    str($hash_result.stdout).split()[0]
    ${node_result}=    Run Process    sh    -c    adb shell "grep -o '<node' /sdcard/window_dump.xml | wc -l"
    ...    timeout=20s    on_timeout=terminate
    Should Be Equal As Integers    ${node_result.rc}    0
    ${node_count}=    Evaluate    int(str($node_result.stdout).strip() or 0)
    ${marker_result}=    Run Process    sh    -c    adb shell "grep -o '${RESPONSIVE_SCROLL_MARKER}' /sdcard/window_dump.xml | wc -l"
    ...    timeout=20s    on_timeout=terminate
    Should Be Equal As Integers    ${marker_result.rc}    0
    ${marker_count}=    Evaluate    int(str($marker_result.stdout).strip() or 0)
    ${bottom_found}=    Set Variable    ${FALSE}
    IF    '${bottom_marker}' != ''
        ${bottom_result}=    Run Process    sh    -c    adb shell "grep -F -c '${bottom_marker}' /sdcard/window_dump.xml"
        ...    timeout=20s    on_timeout=terminate
        ${bottom_count}=    Evaluate    int(str($bottom_result.stdout).strip() or 0)
        ${bottom_found}=    Evaluate    ${bottom_count} > 0
    END
    RETURN    ${hash}    ${node_count}    ${marker_count}    ${bottom_found}

Get Current Screenshot Hash With Adb
    ${shot_result}=    Run Process    adb    shell    screencap    -p    /sdcard/scroll_probe.png
    ...    timeout=20s    on_timeout=terminate
    Should Be Equal As Integers    ${shot_result.rc}    0
    ${hash_result}=    Run Process    adb    shell    toybox    sha256sum    /sdcard/scroll_probe.png
    ...    timeout=20s    on_timeout=terminate
    Should Be Equal As Integers    ${hash_result.rc}    0
    ${hash}=    Evaluate    "screenshot:" + str($hash_result.stdout).split()[0]
    RETURN    ${hash}

Get Current Screenshot Scroll Stats With Adb
    ${hash}=    Get Current Screenshot Hash With Adb
    RETURN    ${hash}    -1    -1    ${FALSE}

Scroll Down Consent Terms With Big Fling
    [Arguments]    ${max_swipes}=55
    ${width}=    Get Window Width
    ${height}=    Get Window Height
    ${start_x}=    Evaluate    int(${width} * ${CONSENT_BIG_FLING_X_RATIO})
    ${start_y}=    Evaluate    int(${height} * ${CONSENT_BIG_FLING_START_Y_RATIO})
    ${end_y}=    Evaluate    int(${height} * ${CONSENT_BIG_FLING_END_Y_RATIO})
    Log    [CONSENT] width=${width} height=${height} start_x=${start_x} start_y=${start_y} end_y=${end_y} duration_ms=${CONSENT_BIG_FLING_DURATION_MS} max_swipes=${max_swipes}
    ${swipe_count}=    Set Variable    0
    FOR    ${index}    IN RANGE    ${max_swipes}
        Execute Adb Shell    input    swipe    ${start_x}    ${start_y}    ${start_x}    ${end_y}    ${CONSENT_BIG_FLING_DURATION_MS}
        ${swipe_count}=    Evaluate    ${swipe_count} + 1
        Log    [CONSENT] fling_swipe=${swipe_count}
        ${is_long_pause}=    Evaluate    ${swipe_count} % ${CONSENT_BIG_FLING_LONG_PAUSE_EVERY} == 0
        IF    ${is_long_pause}
            Sleep    ${CONSENT_BIG_FLING_LONG_PAUSE_S}s
        ELSE
            Sleep    ${CONSENT_BIG_FLING_SHORT_PAUSE_S}s
        END
    END
    Log    [CONSENT] FinalSwipeCount=${swipe_count}
    Set Test Variable    ${CONSENT_BIG_FLING_SWIPE_COUNT}    ${swipe_count}
    RETURN    ${swipe_count}
