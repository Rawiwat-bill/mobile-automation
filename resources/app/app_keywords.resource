*** Settings ***
Library    AppiumLibrary


*** Variables ***
${ANDROID_PERMISSION_ALLOW_BUTTON}    xpath=//*[@resource-id="com.android.permissioncontroller:id/permission_allow_button" or @resource-id="com.android.permissioncontroller:id/permission_allow_foreground_only_button"]
${ANDROID_PERMISSION_DENY_BUTTON}     xpath=//*[@resource-id="com.android.permissioncontroller:id/permission_deny_button"]
${ANDROID_PERMISSION_TIMEOUT}         5s
${DEBUG_MODE}                         False
${APP_PACKAGE}                        com.bangkokbank.blue.dev


*** Keywords ***
Open Mobile Application
    Open Application
    ...    http://127.0.0.1:4723
    ...    platformName=Android
    ...    automationName=UiAutomator2
    ...    deviceName=Android Emulator
    ...    app=${CURDIR}/../../apps/android/app.apk
    ...    appPackage=${APP_PACKAGE}
    ...    appActivity=com.bangkokbank.blue.MainActivity
    ...    noReset=false

Allow Android Permission If Visible
    ${is_visible}=    Run Keyword And Return Status
    ...    Wait Until Element Is Visible    ${ANDROID_PERMISSION_ALLOW_BUTTON}    ${ANDROID_PERMISSION_TIMEOUT}
    IF    ${is_visible}
        Click Element    ${ANDROID_PERMISSION_ALLOW_BUTTON}
        Activate Application    ${APP_PACKAGE}
    END

Debug Screenshot
    IF    '${DEBUG_MODE}' == 'True'
        Capture Page Screenshot
    END

Debug Log
    [Arguments]    ${message}
    IF    '${DEBUG_MODE}' == 'True'
        Log    ${message}
    END
