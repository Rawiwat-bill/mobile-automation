*** Settings ***
Documentation    Production-flow validation of refactored consent scroll keyword.
...              Exercises: Scroll Down Consent Terms → refactored Scroll Down Consent Terms With Big Fling.
...              Validates marker-based stop + Accept tap + navigation.
Library          AppiumLibrary
Library          Process
Resource         ../../resources/app/app_keywords.resource
Resource         ../../resources/pages/onboarding/landing_screen_page.resource
Resource         ../../resources/pages/onboarding/consent_screen_page.resource


*** Variables ***
${EMULATOR_SERIAL}        emulator-5554
${NEXT_SCREEN_SIGNAL}     accessibility_id=Tell us about you


*** Test Cases ***
Production Consent Refactor Validation
    [Documentation]    Fresh flow: drive to consent, exercise refactored scroll, tap Accept, verify Profile.
    [Tags]    validation    consent    refactor
    Run Process    adb    -s    ${EMULATOR_SERIAL}    shell    pm clear    ${APP_PACKAGE}
    ...    timeout=30s    on_timeout=terminate
    Open Application
    ...    ${APPIUM_URL}
    ...    platformName=Android
    ...    automationName=UiAutomator2
    ...    udid=${EMULATOR_SERIAL}
    ...    deviceName=${DEVICE_NAME}
    ...    appPackage=${APP_PACKAGE}
    ...    appActivity=${APP_ACTIVITY}
    ...    noReset=${TRUE}
    ...    autoGrantPermissions=${TRUE}
    ...    ignoreHiddenApiPolicyError=${TRUE}
    ...    uiautomator2ServerInstallTimeout=120000
    ...    uiautomator2ServerLaunchTimeout=120000
    ...    newCommandTimeout=300
    Allow Android Permission If Visible
    Tap Landing Ready Button
    Allow Android Permission If Visible
    Wait Until Element Is Visible    ${CONSENT_TITLE_TEXT}    20s
    Wait Until Element Is Visible    ${CONSENT_WEBVIEW}    10s
    Log    [REFACTOR] Reached consent screen — exercising refactored keyword    WARN
    ${t0}=    Evaluate    time.time()    modules=time
    Scroll Down Consent Terms
    ${t1}=    Evaluate    time.time()    modules=time
    ${scroll_elapsed}=    Evaluate    round(${t1} - ${t0}, 2)
    ${swipe_count}=    Set Variable    ${CONSENT_BIG_FLING_SWIPE_COUNT}
    Log    [REFACTOR] Scroll: swipes=${swipe_count} elapsed=${scroll_elapsed}s    WARN
    Should Be True    ${swipe_count} > 0    msg=Scroll performed zero swipes
    Should Be True    ${swipe_count} <= 10    msg=Scroll exceeded 10 swipes: ${swipe_count}
    Wait Until Element Is Visible    ${CONSENT_ACCEPT_BUTTON}    5s
    Click Element    ${CONSENT_ACCEPT_BUTTON}
    ${nav_ok}=    Run Keyword And Return Status    Wait Until Element Is Visible    ${NEXT_SCREEN_SIGNAL}    15s
    Log    [REFACTOR] Navigation: ${nav_ok}    WARN
    Should Be True    ${nav_ok}    msg=Navigation to Profile screen failed after Accept tap
    [Teardown]    Run Keyword And Ignore Error    Close Application
