*** Settings ***
Documentation    Real device demo smoke for the shared onboarding flow.
...              Clean launch, landing, consent, evidence capture, stop.
Library          AppiumLibrary
Library          OperatingSystem
Library          Process
Library          ../../libraries/config_loader.py
Resource         ../../resources/app/app_keywords.resource
Resource         ../../resources/pages/onboarding/landing_screen_page.resource
Resource         ../../resources/pages/onboarding/consent_screen_page.resource


*** Variables ***
${UDID}                48ZYD25C01422768
${REPORT_DIR}          reports/investigation/real_device_demo
${EVIDENCE_DIR}        ${REPORT_DIR}/evidence
${REAL_DEVICE_NAME}    MGA_LX3
${PLATFORM_VERSION}    10
${MAIN_ACTIVITY}       com.bangkokbank.blue.MainActivity


*** Test Cases ***
Real Device Demo To Consent
    Create Directory    ${REPORT_DIR}
    Create Directory    ${EVIDENCE_DIR}
    Force Stop App For Clean State
    Open Installed App On Real Device
    Wait Until Landing Screen Is Displayed
    Capture Screen Evidence    landing    before
    Tap Landing Ready Button
    Allow Android Permission If Visible
    Wait Until Consent Screen Is Displayed
    Capture Screen Evidence    consent    before
    Scroll Down Consent Terms
    Capture Screen Evidence    consent    after_scroll
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

Capture Screen Evidence
    [Arguments]    ${screen}    ${label}
    ${screen_dir}=    Set Variable    ${EVIDENCE_DIR}/${screen}
    Create Directory    ${screen_dir}
    ${png}=    Set Variable    ${screen_dir}/${label}.png
    ${xml}=    Set Variable    ${screen_dir}/${label}.xml
    Run Process    sh    -c    adb -s ${UDID} exec-out screencap -p > ${png}
    ...    timeout=30s    on_timeout=terminate
    ${source}=    Get Source
    Create File    ${xml}    ${source}    UTF-8
