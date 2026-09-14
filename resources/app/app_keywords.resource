*** Settings ***
Library    AppiumLibrary
Library    Collections
Library    OperatingSystem
Library    ../../libraries/adb_device.py
Library    ../../libraries/evidence_scope.py
Resource   app_constants.resource


*** Variables ***
${ANDROID_PERMISSION_ALLOW_BUTTON}    xpath=//*[@resource-id="com.android.permissioncontroller:id/permission_allow_foreground_only_button" or @resource-id="com.android.permissioncontroller:id/permission_allow_button"]
${ANDROID_PERMISSION_DENY_BUTTON}     xpath=//*[@resource-id="com.android.permissioncontroller:id/permission_deny_button"]
${ANDROID_PERMISSION_TIMEOUT}         5s
${DEBUG_MODE}                         False


*** Keywords ***
Open Mobile Application
    [Arguments]    ${no_reset}=${False}
    ${environment}=    Get Environment Variable    ETB_ENVIRONMENT    DEV
    ${environment}=    Convert To Upper Case    ${environment}
    IF    '${environment}' == 'SIT'
        Set Suite Variable    ${APP_PACKAGE}    ${ANDROID_RESOLVER_SIT_PACKAGE}
    ELSE
        Set Suite Variable    ${APP_PACKAGE}    ${ANDROID_RESOLVER_DEV_PACKAGE}
    END
    &{capabilities}=    Create Dictionary
    ...    platformName=Android
    ...    automationName=UiAutomator2
    ...    deviceName=${DEVICE_NAME}
    ...    appPackage=${APP_PACKAGE}
    ...    appActivity=${APP_ACTIVITY}
    ${execution_target}=    Get Environment Variable    ANDROID_EXECUTION_TARGET    DIAGNOSTIC_CONTROL
    IF    '${execution_target}' == 'REAL'
        Set To Dictionary    ${capabilities}    appium:noReset=${True}    appium:autoLaunch=${False}    appium:dontStopAppOnReset=${True}    appium:forceAppLaunch=${False}    appium:shouldTerminateApp=${False}
    ELSE
        ${etb_case_profiles}=    Get Environment Variable    ETB_CASE_PROFILES    ${EMPTY}
        IF    '${etb_case_profiles}' != ''
            Set To Dictionary    ${capabilities}    appium:noReset=${True}    appium:autoLaunch=${False}    appium:dontStopAppOnReset=${True}    appium:forceAppLaunch=${False}    appium:shouldTerminateApp=${False}
        ELSE
            Set To Dictionary    ${capabilities}    noReset=${no_reset}
        END
    END
    IF    $DEVICE_UDID
        Set To Dictionary    ${capabilities}    udid=${DEVICE_UDID}
    END
    IF    '${execution_target}' != 'REAL'
        ${etb_case_profiles_before_session}=    Get Environment Variable    ETB_CASE_PROFILES    ${EMPTY}
        IF    '${etb_case_profiles_before_session}' != ''
            ${etb_startup}=    Start And Observe Real Device    ${DEVICE_UDID}    ${APP_PACKAGE}    ${APP_ACTIVITY}    ${OUTPUT DIR}    timeout=90
            Log    ADB_STARTUP_TERMINAL_STATE=${etb_startup['terminal_state']}    INFO
        END
    END
    Open Application    ${APPIUM_URL}    &{capabilities}

Allow Android Permission If Visible
    ${visible}=    Run Keyword And Return Status
    ...    Wait Until Element Is Visible    ${ANDROID_PERMISSION_ALLOW_BUTTON}    ${ANDROID_PERMISSION_TIMEOUT}
    IF    ${visible}
        Log    PERMISSION_DIALOG_VISIBLE=TRUE
        ${click_status}=    Run Keyword And Return Status
        ...    Click Element    ${ANDROID_PERMISSION_ALLOW_BUTTON}
        IF    not ${click_status}
            ${already_transitioned}=    Run Keyword And Return Status
            ...    Permission Transition Should Be Complete
            IF    not ${already_transitioned}
                Log    PERMISSION_CLICK_REACQUIRE=TRUE
                ${reacquired}=    Run Keyword And Return Status
                ...    Wait Until Element Is Visible    ${ANDROID_PERMISSION_ALLOW_BUTTON}    ${ANDROID_PERMISSION_TIMEOUT}
                IF    not ${reacquired}
                    Fail    PERMISSION_TRANSITION_CLICK_FAILED
                END
                ${retry_status}=    Run Keyword And Return Status
                ...    Click Element    ${ANDROID_PERMISSION_ALLOW_BUTTON}
                IF    not ${retry_status}
                    Fail    PERMISSION_TRANSITION_CLICK_FAILED_AFTER_REACQUIRE
                END
            END
        END
        Wait Until Keyword Succeeds    10s    500ms    Permission Transition Should Be Complete
        Activate Application    ${APP_PACKAGE}
    END

Permission Transition Should Be Complete
    ${activity}=    Get Activity
    ${source}=    Get Source
    ${transitioned}=    Evaluate
    ...    'GrantPermissionsActivity' not in $activity and 'com.google.android.permissioncontroller' not in $source and 'permission_allow_foreground_only_button' not in $source and 'permission_allow_button' not in $source
    Should Be True    ${transitioned}    Permission Controller transition did not complete.

Debug Screenshot
    IF    '${DEBUG_MODE}' == 'True'
        ${evidence_dir}=    Resolve Private Evidence Dir    ${OUTPUT DIR}
        Capture Page Screenshot    ${evidence_dir}/debug_screenshot.png
    END

Debug Log
    [Arguments]    ${message}
    IF    '${DEBUG_MODE}' == 'True'
        Log    ${message}
    END
