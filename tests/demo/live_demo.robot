*** Settings ***
Documentation    Live demo: BBL onboarding automation on the real Android device.
...              Reliable autonomous segment: clean launch -> Landing -> Consent.
...              Uses Appium for the session + verification, adb for taps/screenshots
...              (the proven reliable pattern on this Huawei device).
Library          AppiumLibrary
Library          Process
Library          OperatingSystem

*** Variables ***
${UDID}            48ZYD25C01422768
${APP_PACKAGE}     com.bangkokbank.blue.dev
${DEMO_DIR}        ${OUTPUT_DIR}/demo_evidence
${LANDING_SKIP}    xpath=//*[@resource-id="screenLanding_skipButton"]
${CONSENT_TITLE}   xpath=//*[@text="Terms and Conditions"]

*** Test Cases ***
BBL Onboarding Live Demo Landing To Consent
    [Documentation]    Launch BBL, navigate Landing -> Consent, capture a screenshot per step.

    Create Directory    ${DEMO_DIR}
    Run Process    adb    -s    ${UDID}    shell    am    force-stop    ${APP_PACKAGE}
    Sleep    2s
    Log    [DEMO] Device: ${UDID}    WARN
    Log    [DEMO] Step 1 — launching BBL app (clean start)    WARN

    Open Application
    ...    http://127.0.0.1:4723
    ...    platformName=Android
    ...    automationName=UiAutomator2
    ...    udid=${UDID}
    ...    deviceName=MGA_LX3
    ...    platformVersion=10
    ...    appPackage=${APP_PACKAGE}
    ...    appActivity=com.bangkokbank.blue.MainActivity
    ...    noReset=${TRUE}
    ...    autoGrantPermissions=${TRUE}
    ...    ignoreHiddenApiPolicyError=${TRUE}
    ...    disableWindowAnimation=${TRUE}
    ...    newCommandTimeout=300

    Wait Until Page Contains Element    ${LANDING_SKIP}    60s
    Capture Adb Screenshot    01_landing
    Log    [DEMO] Landing reached    WARN

    Log    [DEMO] Step 2 — tap Skip -> Ready page    WARN
    Run Process    adb    -s    ${UDID}    shell    input    tap    360    1511
    Sleep    3s
    Capture Adb Screenshot    02_ready_page

    Log    [DEMO] Step 3 — tap Ready -> Consent    WARN
    Run Process    adb    -s    ${UDID}    shell    input    tap    360    1512
    ${on_consent}=    Wait Until Page Contains Element    ${CONSENT_TITLE}    45s
    Capture Adb Screenshot    03_consent

    Run Keyword If    ${on_consent}
    ...    Log    [DEMO] SUCCESS — Consent screen reached. App is under automation control.    WARN
    Should Be True    ${on_consent}    Demo failed: did not reach Consent screen.
    [Teardown]    Close Application

*** Keywords ***
Capture Adb Screenshot
    [Arguments]    ${name}
    Run Process    sh    -c    adb -s ${UDID} exec-out screencap -p > ${DEMO_DIR}/${name}.png
    Log    [DEMO] Screenshot saved: ${name}.png    WARN
