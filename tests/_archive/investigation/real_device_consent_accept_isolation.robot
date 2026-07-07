*** Settings ***
Documentation    Sprint 2.72 real-device Consent Accept transition isolation.
...              Clean launch, shared navigation, one Accept tap, evidence only.
Library          AppiumLibrary
Library          OperatingSystem
Library          Process
Resource         ../../resources/app/app_keywords.resource
Resource         ../../resources/pages/onboarding/landing_screen_page.resource
Resource         ../../resources/pages/onboarding/consent_screen_page.resource
Resource         ../../locators/android/onboarding/profile_screen_locators.resource


*** Variables ***
${UDID}                   48ZYD25C01422768
${REPORT_DIR}             reports/investigation/real_device_consent_accept_isolation
${EVIDENCE_DIR}           ${REPORT_DIR}/evidence
${REAL_DEVICE_NAME}       MGA_LX3
${PLATFORM_VERSION}       10
${MAIN_ACTIVITY}          com.bangkokbank.blue.MainActivity
${TRANSITION_RESULT}      APP_HUNG
${ACCEPT_VISIBLE}         ${FALSE}
${ACCEPT_ENABLED}         ${FALSE}
${ACCEPT_TAP_STATUS}      NOT_RUN
${PROFILE_REACHED}        ${FALSE}


*** Test Cases ***
Isolate Consent Accept Transition From Clean Real Device Launch
    [Documentation]    Starts from force-stop, reaches Consent, taps Accept exactly once, then stops.
    Create Directory    ${REPORT_DIR}
    Create Directory    ${EVIDENCE_DIR}
    Force Stop App For Clean State
    Open Installed App On Real Device
    Reach Consent Screen With Shared Flow
    Scroll Down Consent Terms
    Verify Accept State
    Capture Consent Accept Evidence    before_accept
    Run Process    adb    -s    ${UDID}    logcat    -c
    ...    timeout=15s    on_timeout=terminate
    Tap Accept Exactly Once If Clickable
    Wait For Consent Accept Transition
    Capture Consent Accept Evidence    after_accept
    Capture Consent Accept Logcat
    Determine Consent Accept Transition Result
    Record Consent Accept Runtime Result
    [Teardown]    Run Keyword And Ignore Error    Close Application


*** Keywords ***
Force Stop App For Clean State
    ${result}=    Run Process    adb    -s    ${UDID}    shell    am    force-stop    ${APP_PACKAGE}
    ...    timeout=15s    on_timeout=terminate
    Should Be Equal As Integers    ${result.rc}    0
    Sleep    2s

Open Installed App On Real Device
    Open Application
    ...    http://127.0.0.1:4723
    ...    platformName=Android
    ...    automationName=UiAutomator2
    ...    udid=${UDID}
    ...    deviceName=${REAL_DEVICE_NAME}
    ...    platformVersion=${PLATFORM_VERSION}
    ...    appPackage=${APP_PACKAGE}
    ...    appActivity=${MAIN_ACTIVITY}
    ...    noReset=${TRUE}
    ...    autoGrantPermissions=${TRUE}
    ...    ignoreHiddenApiPolicyError=${TRUE}
    ...    disableWindowAnimation=${TRUE}
    ...    uiautomator2ServerInstallTimeout=120000
    ...    uiautomator2ServerLaunchTimeout=120000
    ...    newCommandTimeout=120

Reach Consent Screen With Shared Flow
    ${on_consent}=    Run Keyword And Return Status    Wait Until Consent Screen Is Displayed
    IF    ${on_consent}
        RETURN
    END
    ${on_landing}=    Run Keyword And Return Status    Wait Until Landing Screen Is Displayed
    IF    ${on_landing}
        Tap Landing Ready Button
        Allow Android Permission If Visible
        Wait Until Consent Screen Is Displayed
        RETURN
    END
    Fail    Clean launch did not reach Landing or Consent with shared locators.

Verify Accept State
    ${visible}=    Run Keyword And Return Status    Element Should Be Visible    ${CONSENT_ACCEPT_BUTTON}
    ${enabled}=    Run Keyword And Return Status    Element Should Be Enabled    ${CONSENT_ACCEPT_BUTTON}
    Set Test Variable    ${ACCEPT_VISIBLE}     ${visible}
    Set Test Variable    ${ACCEPT_ENABLED}     ${enabled}
    Log    [CONSENT_ACCEPT] visible=${ACCEPT_VISIBLE} enabled=${ACCEPT_ENABLED}

Tap Accept Exactly Once If Clickable
    IF    not ${ACCEPT_VISIBLE} or not ${ACCEPT_ENABLED}
        Set Test Variable    ${TRANSITION_RESULT}    ACCEPT_NOT_CLICKABLE
        RETURN
    END
    ${status}    ${message}=    Run Keyword And Ignore Error    Click Element    ${CONSENT_ACCEPT_BUTTON}
    Set Test Variable    ${ACCEPT_TAP_STATUS}    ${status}
    Log    [CONSENT_ACCEPT] tap_status=${ACCEPT_TAP_STATUS}
    IF    '${status}' != 'PASS'
        Set Test Variable    ${TRANSITION_RESULT}    ACCEPT_NOT_CLICKABLE
        Log    [CONSENT_ACCEPT] tap_error=${message}    WARN
    END

Wait For Consent Accept Transition
    IF    '${ACCEPT_TAP_STATUS}' != 'PASS'
        RETURN
    END
    ${profile_reached}=    Run Keyword And Return Status
    ...    Wait Until Element Is Visible    ${PROFILE_TITLE_TEXT}    15s
    Set Test Variable    ${PROFILE_REACHED}    ${profile_reached}

Determine Consent Accept Transition Result
    IF    '${TRANSITION_RESULT}' == 'ACCEPT_NOT_CLICKABLE'
        RETURN
    END
    IF    ${PROFILE_REACHED}
        Set Test Variable    ${TRANSITION_RESULT}    ACCEPT_TRANSITIONED_TO_CND
    ELSE IF    '${ACCEPT_TAP_STATUS}' == 'PASS'
        Set Test Variable    ${TRANSITION_RESULT}    ACCEPT_TAPPED_NO_TRANSITION
    ELSE
        Set Test Variable    ${TRANSITION_RESULT}    APP_HUNG
    END

Capture Consent Accept Evidence
    [Arguments]    ${label}
    Capture Screenshot With Adb    ${EVIDENCE_DIR}/${label}.png
    Capture Source With Appium    ${EVIDENCE_DIR}/${label}.xml
    Capture Current Activity    ${label}

Capture Screenshot With Adb
    [Arguments]    ${path}
    ${result}=    Run Process    sh    -c    adb -s ${UDID} exec-out screencap -p > ${path}
    ...    timeout=30s    on_timeout=terminate
    Should Be Equal As Integers    ${result.rc}    0

Capture Source With Appium
    [Arguments]    ${path}
    ${source_status}    ${source}=    Run Keyword And Ignore Error    Get Source
    IF    '${source_status}' == 'PASS'
        Create File    ${path}    ${source}    UTF-8
    ELSE
        Create File    ${path}    XML_CAPTURE_FAILED: ${source}    UTF-8
    END

Capture Current Activity
    [Arguments]    ${label}
    ${activity_result}=    Run Process    adb    -s    ${UDID}    shell    dumpsys    window
    ...    timeout=30s    on_timeout=terminate
    Append To File    ${EVIDENCE_DIR}/current_activity.txt
    ...    \n## ${label}\n${activity_result.stdout}\n    UTF-8

Capture Consent Accept Logcat
    ${result}=    Run Process    adb    -s    ${UDID}    logcat    -d    -v    time
    ...    timeout=30s    on_timeout=terminate
    Create File    ${EVIDENCE_DIR}/logcat.txt    ${result.stdout}    UTF-8

Record Consent Accept Runtime Result
    ${content}=    Catenate    SEPARATOR=\n
    ...    Transition Result: ${TRANSITION_RESULT}
    ...    Accept Visible: ${ACCEPT_VISIBLE}
    ...    Accept Enabled: ${ACCEPT_ENABLED}
    ...    Accept Tap Status: ${ACCEPT_TAP_STATUS}
    ...    Profile Reached: ${PROFILE_REACHED}
    ...    Scroll Bottom Status: ${RESPONSIVE_SCROLL_BOTTOM_STATUS}
    ...    Scroll Swipe Count: ${RESPONSIVE_SCROLL_SWIPE_COUNT}
    Create File    ${EVIDENCE_DIR}/transition_result.txt    ${content}\n    UTF-8
