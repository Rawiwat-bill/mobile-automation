*** Settings ***
Library    AppiumLibrary
Library    Collections
Library    OperatingSystem
Library    ../../libraries/adb_device.py
Library    ../../libraries/evidence_scope.py
Resource   app_constants.resource
Resource   ../keywords/appium_expectations.resource


*** Variables ***
${ANDROID_PERMISSION_ALLOW_BUTTON}               xpath=//*[@resource-id="com.android.permissioncontroller:id/permission_allow_foreground_only_button" or @resource-id="com.android.permissioncontroller:id/permission_allow_button"]
${ANDROID_PERMISSION_ALLOW_GENERIC_BUTTON}       xpath=//*[@resource-id="com.android.permissioncontroller:id/permission_allow_button"]
${ANDROID_PERMISSION_ALLOW_FOREGROUND_BUTTON}    xpath=//*[@resource-id="com.android.permissioncontroller:id/permission_allow_foreground_only_button"]
${ANDROID_PERMISSION_DENY_BUTTON}                xpath=//*[@resource-id="com.android.permissioncontroller:id/permission_deny_button"]
${ANDROID_PERMISSION_TIMEOUT}                    5s
${ANDROID_PERMISSION_MAX_PROMPTS}                4
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
            Set To Dictionary    ${capabilities}    appium:noReset=${True}    appium:autoLaunch=${False}    appium:dontStopAppOnReset=${True}    appium:forceAppLaunch=${False}    appium:shouldTerminateApp=${False}    settings[enforceXPath1]=${True}
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
    IF    not ${visible}
        RETURN
    END
    Log    PERMISSION_DIALOG_VISIBLE=TRUE
    ${handled_any}=    Set Variable    ${False}
    FOR    ${permission_index}    IN RANGE    ${ANDROID_PERMISSION_MAX_PROMPTS}
        ${transitioned}=    Run Keyword And Return Status    Permission Transition Should Be Complete
        IF    ${transitioned}
            BREAK
        END
        ${handled}=    Handle One Android Permission Prompt
        Should Be True    ${handled}    PERMISSION_PROMPT_NOT_ACTIONABLE
        ${handled_any}=    Set Variable    ${True}
        Wait Until Keyword Succeeds
        ...    3s
        ...    250ms
        ...    Permission Transition Or Known Prompt Should Be Ready
    END
    IF    ${handled_any}
        Wait Until Keyword Succeeds    10s    500ms    Permission Transition Should Be Complete
        Activate Application    ${APP_PACKAGE}
    END

Handle One Android Permission Prompt
    ${generic_visible}=    Run Keyword And Return Status
    ...    Element Should Be Visible Now    ${ANDROID_PERMISSION_ALLOW_GENERIC_BUTTON}
    IF    ${generic_visible}
        Click Android Permission Prompt And Prove Advance
        ...    ${ANDROID_PERMISSION_ALLOW_GENERIC_BUTTON}
        ...    GENERIC
        RETURN    ${True}
    END
    ${foreground_visible}=    Run Keyword And Return Status
    ...    Element Should Be Visible Now    ${ANDROID_PERMISSION_ALLOW_FOREGROUND_BUTTON}
    IF    ${foreground_visible}
        Click Android Permission Prompt And Prove Advance
        ...    ${ANDROID_PERMISSION_ALLOW_FOREGROUND_BUTTON}
        ...    FOREGROUND
        RETURN    ${True}
    END
    RETURN    ${False}

Click Android Permission Prompt And Prove Advance
    [Arguments]    ${locator}    ${prompt_type}
    Log    PERMISSION_PROMPT_TYPE=${prompt_type}
    ${click_status}=    Run Keyword And Return Status    Click Element    ${locator}
    IF    not ${click_status}
        Log    PERMISSION_CLICK_REACQUIRE=TRUE
        ${reacquired}=    Run Keyword And Return Status
        ...    Wait Until Element Is Visible    ${locator}    ${ANDROID_PERMISSION_TIMEOUT}
        Should Be True    ${reacquired}    PERMISSION_TRANSITION_CLICK_FAILED
        Click Element    ${locator}
    END
    Wait Until Keyword Succeeds
    ...    ${ANDROID_PERMISSION_TIMEOUT}
    ...    250ms
    ...    Android Permission Locator Should Be Gone
    ...    ${locator}

Android Permission Locator Should Be Gone
    [Arguments]    ${locator}
    ${visible}=    Run Keyword And Return Status    Element Should Be Visible Now    ${locator}
    Should Not Be True    ${visible}    PERMISSION_PROMPT_DID_NOT_ADVANCE

Permission Transition Or Known Prompt Should Be Ready
    ${transitioned}=    Run Keyword And Return Status    Permission Transition Should Be Complete
    IF    ${transitioned}
        RETURN
    END
    ${generic_visible}=    Run Keyword And Return Status
    ...    Element Should Be Visible Now    ${ANDROID_PERMISSION_ALLOW_GENERIC_BUTTON}
    ${foreground_visible}=    Run Keyword And Return Status
    ...    Element Should Be Visible Now    ${ANDROID_PERMISSION_ALLOW_FOREGROUND_BUTTON}
    Should Be True
    ...    ${generic_visible} or ${foreground_visible}
    ...    PERMISSION_PROMPT_NOT_READY

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
