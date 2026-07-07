*** Settings ***
Documentation    Sprint 2.73 real-device Appium health reset.
...              Health check only: clean launch, screenshot, source, optional harmless tap.
Library          AppiumLibrary
Library          OperatingSystem
Library          Process
Resource         ../../resources/app/app_keywords.resource
Resource         ../../resources/pages/onboarding/landing_screen_page.resource


*** Variables ***
${UDID}                   48ZYD25C01422768
${REPORT_DIR}             reports/investigation/real_device_appium_health
${EVIDENCE_DIR}           ${REPORT_DIR}/evidence
${REAL_DEVICE_NAME}       MGA_LX3
${PLATFORM_VERSION}       10
${MAIN_ACTIVITY}          com.bangkokbank.blue.MainActivity
${HEALTH_LOG}             ${EVIDENCE_DIR}/appium_health.log
${SCREENSHOT_PATH}        ${EVIDENCE_DIR}/screenshot.png
${SOURCE_PATH}            ${EVIDENCE_DIR}/source.xml
${HEALTH_STATUS}          NOT_STARTED


*** Test Cases ***
Real Device Appium Health Check
    Create Directory    ${REPORT_DIR}
    Create Directory    ${EVIDENCE_DIR}
    Create File    ${HEALTH_LOG}    Sprint 2.73 Appium health check started.\n    UTF-8
    Run Keyword And Ignore Error    Force Stop App And UiAutomator2
    Open Installed App On Real Device
    Capture Health Evidence
    Log Health Tap Skipped
    Set Test Variable    ${HEALTH_STATUS}    APPIUM_HEALTH_OK
    Append To File    ${HEALTH_LOG}    Health status: ${HEALTH_STATUS}\n    UTF-8
    [Teardown]    Run Keyword And Ignore Error    Close Application


*** Keywords ***
Force Stop App And UiAutomator2
    ${app}=    Run Process    adb    -s    ${UDID}    shell    am    force-stop    ${APP_PACKAGE}
    ...    timeout=15s    on_timeout=terminate
    Should Be Equal As Integers    ${app.rc}    0
    ${server}=    Run Process    adb    -s    ${UDID}    shell    am    force-stop    io.appium.uiautomator2.server
    ...    timeout=15s    on_timeout=terminate
    Should Be Equal As Integers    ${server.rc}    0
    ${test}=    Run Process    adb    -s    ${UDID}    shell    am    force-stop    io.appium.uiautomator2.server.test
    ...    timeout=15s    on_timeout=terminate
    Should Be Equal As Integers    ${test.rc}    0

Open Installed App On Real Device
    Append To File    ${HEALTH_LOG}    Opening Appium session on real device.\n    UTF-8
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
    Append To File    ${HEALTH_LOG}    Session opened.\n    UTF-8

Capture Health Evidence
    Append To File    ${HEALTH_LOG}    Capturing screenshot.\n    UTF-8
    Capture Page Screenshot    ${SCREENSHOT_PATH}
    Append To File    ${HEALTH_LOG}    Screenshot captured.\n    UTF-8
    Append To File    ${HEALTH_LOG}    Capturing page source.\n    UTF-8
    ${source}=    Get Source
    Create File    ${SOURCE_PATH}    ${source}    UTF-8
    Append To File    ${HEALTH_LOG}    Source captured.\n    UTF-8

Log Health Tap Skipped
    Append To File    ${HEALTH_LOG}    Optional visible-element tap skipped to keep health probe bounded.\n    UTF-8
