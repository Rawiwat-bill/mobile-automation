*** Settings ***
Documentation    RD-01 probe — isolate whether Appium Find Element hangs on the real device.
Library          AppiumLibrary
Library          Process
Resource         ../../resources/app/app_constants.resource
Resource         ../../resources/pages/onboarding/landing_screen_page.resource


*** Test Cases ***
Probe Appium Find Element On Landing
    Run Process    adb    -s    48ZYD25C01422768    shell    am force-stop    ${APP_PACKAGE}    timeout=30s
    Run Process    adb    -s    48ZYD25C01422768    shell    pm clear    ${APP_PACKAGE}    timeout=30s
    Open Application
    ...    ${APPIUM_URL}
    ...    platformName=Android
    ...    automationName=UiAutomator2
    ...    udid=48ZYD25C01422768
    ...    deviceName=MGA_LX3
    ...    platformVersion=10
    ...    appPackage=${APP_PACKAGE}
    ...    appActivity=${APP_ACTIVITY}
    ...    noReset=${TRUE}
    ...    autoGrantPermissions=${TRUE}
    ...    ignoreHiddenApiPolicyError=${TRUE}
    ...    newCommandTimeout=60
    Log    PROBE: session opened, waiting 8s for Landing to render
    Sleep    8s
    Log    PROBE: issuing Find Element (LANDING_SKIP_BUTTON, 30s)
    ${s}=    Run Keyword And Return Status    Wait Until Element Is Visible    ${LANDING_SKIP_BUTTON}    30s
    Log    PROBE: skip_visible=${s}
    ${s2}=    Run Keyword And Return Status    Wait Until Element Is Visible    ${LANDING_TITLE_TEXT}    30s
    Log    PROBE: title_visible=${s2}
    [Teardown]    Run Keyword And Ignore Error    Close Application
