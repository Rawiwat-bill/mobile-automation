*** Settings ***
Library     AppiumLibrary
Library     OperatingSystem
Library     ../../../libraries/evidence_scope.py
Resource    ../../contracts/flow_states.resource
Resource    ../../diagnostics/etb_observability.resource
Resource    ../../../resources/app/app_constants.resource
Resource    ../../../resources/keywords/scroll_keywords.resource
Resource    ../../../locators/android/common_onboarding/tell_us_about_you_locators.resource
Resource    ../../../locators/android/common_onboarding/terms_and_conditions_locators.resource
Resource    ../../../resources/keywords/appium_expectations.resource


*** Variables ***
${TERMS_CONTENT_READY_MAX_READS}             3
${TERMS_CONTENT_READY_RANGE_END}             4
${TERMS_CONTENT_READY_POLL_INTERVAL}         1s
${TERMS_CONTENT_RECOVERY_MAX_ATTEMPTS}    10
${TERMS_CONTENT_RECOVERY_RANGE_END}       11
${TERMS_CONTENT_RECOVERY_LANDING_PAUSE}   2s
${TERMS_BACK_X_RATIO}                       0.083
${TERMS_BACK_Y_RATIO}                       0.091


*** Keywords ***
Wait Until Terms And Conditions Screen Is Displayed
    [Documentation]    Wait until the Terms and Conditions shell is displayed.
    Wait Until Element Is Visible    ${TERMS_AND_CONDITIONS_WEBVIEW}    ${NCBD_LOADING_TIMEOUT}

Terms Content Should Be Ready
    [Documentation]    Prove hydrated agreement text independently from the bottom acknowledgement marker.
    ${source_status}    ${source}=    Run Keyword And Ignore Error    Get Source
    IF    '${source_status}' != 'PASS'
        Fail    TERMS_SOURCE_READ_FAILED
    END
    ${content_loaded}=    Terms Content Loaded From Source    ${source}
    Should Be True    ${content_loaded}    TERMS_CONTENT_NOT_RENDERED

Wait Until Terms Content Is Ready
    [Documentation]    Read Appium source at most three times; retry only a proven blank Terms WebView.
    FOR    ${read_attempt}    IN RANGE    1    ${TERMS_CONTENT_READY_RANGE_END}
        ${status}    ${error}=    Run Keyword And Ignore Error    Terms Content Should Be Ready
        IF    '${status}' == 'PASS'
            RETURN
        END
        IF    '${error}' == 'TERMS_SOURCE_READ_FAILED'
            Fail    TERMS_SOURCE_READ_FAILED
        END
        IF    '${error}' == 'TERMS_SOURCE_INVALID'
            Fail    TERMS_SOURCE_INVALID
        END
        IF    '${error}' != 'TERMS_CONTENT_NOT_RENDERED'
            Fail    TERMS_CONTENT_CHECK_FAILED
        END
        IF    ${read_attempt} < ${TERMS_CONTENT_READY_MAX_READS}
            Sleep    ${TERMS_CONTENT_READY_POLL_INTERVAL}
        END
    END
    Fail    TERMS_CONTENT_NOT_RENDERED

Tap Terms Back Button For Recovery
    [Documentation]    Navigate back from the visible Terms shell using the responsive in-app back-control position proven on the active layout.
    Wait Until Element Is Visible    ${TERMS_AND_CONDITIONS_WEBVIEW}    ${NCBD_LOADING_TIMEOUT}
    ${width}=    Get Window Width
    ${height}=    Get Window Height
    ${back_x}=    Evaluate    int(${width} * ${TERMS_BACK_X_RATIO})
    ${back_y}=    Evaluate    int(${height} * ${TERMS_BACK_Y_RATIO})
    Execute Adb Shell    input    tap    ${back_x}    ${back_y}
    Log    TERMS_CONTENT_RECOVERY_BACK_TAP=ADB_RATIO x=${back_x} y=${back_y}    INFO

Scroll Down Terms And Conditions
    [Documentation]    Scroll Terms only after hydrated agreement content has been proven.
    Scroll Down Consent Terms With Big Fling

Accept Terms And Conditions
    [Documentation]    Tap Accept with ADB first and use Appium only when navigation is not observed.
    Wait Until Element Is Visible    ${TERMS_AND_CONDITIONS_ACCEPT_BUTTON}    ${NCBD_LOADING_TIMEOUT}
    Wait Until Keyword Succeeds    5s    500ms    Element Should Be Enabled    ${TERMS_AND_CONDITIONS_ACCEPT_BUTTON}
    ${element_rect}=    Get Element Rect    ${TERMS_AND_CONDITIONS_ACCEPT_BUTTON}
    ${center_x}=    Evaluate    int(${element_rect['x']} + (${element_rect['width']} / 2))
    ${center_y}=    Evaluate    int(${element_rect['y']} + (${element_rect['height']} / 2))
    Execute Adb Shell    input    tap    ${center_x}    ${center_y}
    Log    [TERMS] Accept tapped via adb shell at ${center_x},${center_y}

    ${transition}=    Wait For Terms Transition Marker
    IF    '${transition}' == '${FLOW_STATE_NEXT}'
        RETURN    ${FLOW_STATE_NEXT}
    END
    IF    '${transition}' == '${FLOW_STATE_AJI_001}'
        RETURN    ${FLOW_STATE_AJI_001}
    END

    Log    [TERMS] Navigation not observed after ADB tap; trying Appium fallback.    WARN
    Run Keyword And Ignore Error    Click Element    ${TERMS_AND_CONDITIONS_ACCEPT_BUTTON}
    ${transition}=    Wait For Terms Transition Marker
    IF    '${transition}' == '${FLOW_STATE_NEXT}'
        RETURN    ${FLOW_STATE_NEXT}
    END
    IF    '${transition}' == '${FLOW_STATE_AJI_001}'
        RETURN    ${FLOW_STATE_AJI_001}
    END

    Capture Terms Transition Evidence
    Fail    TERMS_TRANSITION_NOT_OBSERVED

Wait For Terms Transition Marker
    [Documentation]    Return NEXT, AJI-001, or NOT_OBSERVED without treating Accept disappearance as success.
    ${observed}=    Run Keyword And Return Status
    ...    Wait Until Keyword Succeeds    10s    500ms    Terms Transition Marker Should Be Visible
    IF    not ${observed}
        RETURN    ${FLOW_STATE_NOT_OBSERVED}
    END
    ${source}=    Get Source
    ${aji}=    Run Keyword And Return Status    Should Contain    ${source}    ${FLOW_STATE_AJI_001}
    IF    ${aji}
        RETURN    ${FLOW_STATE_AJI_001}
    END
    RETURN    ${FLOW_STATE_NEXT}

Terms Transition Marker Should Be Visible
    ${next_visible}=    Run Keyword And Return Status
    ...    Element Should Be Visible Now    ${TELL_US_ABOUT_YOU_TITLE_TEXT}
    ${source}=    Get Source
    ${aji_visible}=    Run Keyword And Return Status    Should Contain    ${source}    ${FLOW_STATE_AJI_001}
    Should Be True    ${next_visible} or ${aji_visible}

Capture Terms Transition Evidence
    [Documentation]    Capture private-local runtime evidence for an unclassified Terms transition.
    ${stamp}=    Evaluate    __import__('time').strftime('%Y%m%d_%H%M%S')
    Record ETB Evidence Capture    ${OUTPUT DIR}    terms_transition_${stamp}
    Log    [TERMS] Transition evidence requested through shared private adapter.    INFO
