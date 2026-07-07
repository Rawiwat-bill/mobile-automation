*** Settings ***
Documentation    Sprint 2.70 bounded real-device validation for responsive consent scroll.
...              No reinstall, no Frida, no full onboarding loop.
Library          AppiumLibrary
Library          OperatingSystem
Library          Process
Resource         ../../resources/app/app_keywords.resource
Resource         ../../resources/pages/onboarding/landing_screen_page.resource
Resource         ../../resources/pages/onboarding/consent_screen_page.resource


*** Variables ***
${UDID}                48ZYD25C01422768
${EVIDENCE_DIR}        reports/investigation/responsive_scroll/evidence
${REAL_DEVICE_NAME}    MGA_LX3
${PLATFORM_VERSION}    10


*** Test Cases ***
Bounded Real Device Consent Responsive Scroll
    [Documentation]    Opens installed app, reaches Consent if needed, captures XML before/after five responsive swipes.
    Create Directory    ${EVIDENCE_DIR}
    Open Installed App On Real Device
    Reach Consent Screen Without Full Loop
    Capture Source To File    ${EVIDENCE_DIR}/before_scroll.xml
    Scroll Down Consent Terms    5
    Capture Source With Adb    ${EVIDENCE_DIR}/after_scroll.xml
    [Teardown]    Close Application


*** Keywords ***
Open Installed App On Real Device
    Open Application
    ...    http://127.0.0.1:4723
    ...    platformName=Android
    ...    automationName=UiAutomator2
    ...    udid=${UDID}
    ...    deviceName=${REAL_DEVICE_NAME}
    ...    platformVersion=${PLATFORM_VERSION}
    ...    appPackage=${APP_PACKAGE}
    ...    appActivity=com.bangkokbank.blue.MainActivity
    ...    noReset=${TRUE}
    ...    autoGrantPermissions=${TRUE}
    ...    ignoreHiddenApiPolicyError=${TRUE}
    ...    disableWindowAnimation=${TRUE}
    ...    uiautomator2ServerInstallTimeout=120000
    ...    uiautomator2ServerLaunchTimeout=120000
    ...    newCommandTimeout=120

Reach Consent Screen Without Full Loop
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
    Fail    Test must start from Landing or Consent for bounded responsive scroll validation.

Capture Source To File
    [Arguments]    ${path}
    ${source}=    Get Source
    Create File    ${path}    ${source}    UTF-8

Capture Source With Adb
    [Arguments]    ${path}
    Run Keyword And Ignore Error
    ...    Run Process    adb    -s    ${UDID}    shell    uiautomator    dump    /sdcard/window_dump.xml
    ...    timeout=30s    on_timeout=terminate
    ${result}=    Run Process    sh    -c    adb -s ${UDID} exec-out cat /sdcard/window_dump.xml > ${path}
    ...    timeout=30s    on_timeout=terminate
    Should Be Equal As Integers    ${result.rc}    0
