*** Settings ***
Documentation    Sprint 2.74 real-device onboarding resume from healthy Appium baseline.
...              Reuses shared landing, consent, CND, PDPA, OCR intro, and camera keywords.
Library          AppiumLibrary
Library          OperatingSystem
Library          Process
Library          ../../libraries/config_loader.py
Resource         ../../resources/app/app_keywords.resource
Resource         ../../resources/pages/onboarding/landing_screen_page.resource
Resource         ../../resources/pages/onboarding/consent_screen_page.resource
Resource         ../../resources/pages/onboarding/profile_screen_page.resource
Resource         ../../resources/pages/onboarding/pdpa_consent_page.resource
Resource         ../../resources/pages/onboarding/sign_up_page.resource
Resource         ../../resources/pages/onboarding/scan_card_intro_page.resource
Resource         ../../resources/pages/onboarding/id_card_camera_capture_page.resource


*** Variables ***
${UDID}                48ZYD25C01422768
${REPORT_DIR}          reports/investigation/real_device_onboarding_resume
${EVIDENCE_DIR}        ${REPORT_DIR}/evidence
${TESTDATA}            testdata/onboarding/ntb.local.yaml
${REAL_DEVICE_NAME}    MGA_LX3
${PLATFORM_VERSION}    10
${MAIN_ACTIVITY}       com.bangkokbank.blue.MainActivity


*** Test Cases ***
Resume Shared Onboarding Flow On Real Device
    [Documentation]    Landing -> Consent -> CND -> PDPA -> OCR Intro -> Camera, stop at Camera.
    Create Directory    ${REPORT_DIR}
    Create Directory    ${EVIDENCE_DIR}
    Force Stop App For Clean State
    Open Installed App On Real Device
    Load Local Onboarding Data
    Process Landing Screen
    Process Consent Screen
    Process CND Screen
    Process PDPA Screen
    Process OCR Intro Screen
    Process Camera Screen
    [Teardown]    Run Keyword And Ignore Error    Close Application


*** Keywords ***
Force Stop App For Clean State
    ${app}=    Run Process    adb    -s    ${UDID}    shell    am    force-stop    ${APP_PACKAGE}
    ...    timeout=15s    on_timeout=terminate
    Should Be Equal As Integers    ${app.rc}    0
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
    ...    newCommandTimeout=300

Load Local Onboarding Data
    ${previous_log_level}=    Set Log Level    NONE
    ${data}=    Load YAML    ${TESTDATA}
    Set Test Variable    ${LOCAL_CITIZEN_ID}    ${data['profile']['citizen_id']}
    Set Test Variable    ${LOCAL_DATE_OF_BIRTH}    ${data['profile']['date_of_birth']}
    Set Test Variable    ${LOCAL_MOBILE_NUMBER}    ${data['profile']['mobile_number']}
    Set Log Level    ${previous_log_level}

Process Landing Screen
    Capture Screen Evidence    landing    before
    Tap Landing Bottom Center On Real Device
    ${consent_visible}=    Run Keyword And Return Status    Wait Until Consent Screen Is Displayed
    IF    not ${consent_visible}
        Tap Landing Bottom Center On Real Device
        Wait Until Consent Screen Is Displayed
    END
    Record Screen Result    landing    ${FALSE}    ${TRUE}    ${TRUE}    REAL_DEVICE_ONLY    Shared Appium landing locators were not stable on real device; used dynamic bottom-center taps to reach Consent.
    Allow Android Permission If Visible

Process Consent Screen
    Wait Until Consent Screen Is Displayed
    Capture Screen Evidence    consent    before
    ${locator_result}=    Run Keyword And Return Status    Element Should Be Visible    ${CONSENT_ACCEPT_BUTTON}
    ${keyword_result}=    Run Keyword And Return Status    Scroll Down Consent Terms
    Capture Screen Evidence    consent    after_scroll
    ${page_result}=    Run Keyword And Return Status    Tap Consent Accept Button
    Record Screen Result    consent    ${locator_result}    ${keyword_result}    ${page_result}    SHARED    Shared Consent locators and responsive scroll used; Accept transition attempted once.
    Should Be True    ${page_result}    Consent did not transition with shared page object.

Process CND Screen
    Wait Until Profile Screen Is Displayed
    Capture Screen Evidence    cnd    before_input
    ${locator_result}=    Run Keyword And Return Status    Element Should Be Visible    ${PROFILE_CITIZEN_ID_INPUT}
    ${keyword_result}=    Run Keyword And Return Status    Input CND Data With Masked Logs
    ${page_result}=    Run Keyword And Return Status    Tap Profile Next
    Capture Screen Evidence    cnd    after_submit
    Record Screen Result    cnd    ${locator_result}    ${keyword_result}    ${page_result}    SHARED    Shared Profile/CND page object used with masked local data input.
    Should Be True    ${page_result}    CND/Profile did not submit with shared page object.

Input CND Data With Masked Logs
    ${previous_log_level}=    Set Log Level    NONE
    Input Citizen ID    ${LOCAL_CITIZEN_ID}
    Input Date Of Birth    ${LOCAL_DATE_OF_BIRTH}
    Input Mobile Number    ${LOCAL_MOBILE_NUMBER}
    Set Log Level    ${previous_log_level}

Tap Landing Bottom Center On Real Device
    ${size_result}=    Run Process    adb    -s    ${UDID}    shell    wm    size
    ...    timeout=15s    on_timeout=terminate
    Should Be Equal As Integers    ${size_result.rc}    0
    ${width}=    Evaluate    int(__import__('re').search(r'(\\d+)x(\\d+)', """${size_result.stdout}""").group(1))
    ${height}=    Evaluate    int(__import__('re').search(r'(\\d+)x(\\d+)', """${size_result.stdout}""").group(2))
    ${center_x}=    Evaluate    int(${width} * 0.5)
    ${bottom_y}=    Evaluate    int(${height} * 0.94)
    Log    [LANDING] width=${width} height=${height} center_x=${center_x} bottom_y=${bottom_y}
    ${tap_result}=    Run Process    adb    -s    ${UDID}    shell    input    tap    ${center_x}    ${bottom_y}
    ...    timeout=15s    on_timeout=terminate
    Should Be Equal As Integers    ${tap_result.rc}    0
    Sleep    1s

Process PDPA Screen
    Wait Until PDPA Consent Screen Is Displayed
    Capture Screen Evidence    pdpa    before
    ${locator_result}=    Run Keyword And Return Status    Element Should Be Visible    ${PDPA_ACCEPT_BUTTON}
    ${page_result}=    Tap PDPA Consent Accept Button
    ${keyword_result}=    Set Variable    ${page_result}
    Capture Screen Evidence    pdpa    after_accept
    Record Screen Result    pdpa    ${locator_result}    ${keyword_result}    ${page_result}    SHARED    Shared PDPA page object used.
    Should Be True    ${page_result}    PDPA did not transition with shared page object.

Process OCR Intro Screen
    Wait Until Sign Up Screen Is Displayed
    Capture Screen Evidence    ocr_intro    sign_up
    ${sign_up_locator}=    Run Keyword And Return Status    Element Should Be Visible    ${SIGN_UP_LETS_START}
    Tap Sign Up Lets Start Button
    Allow Android Permission If Visible
    Wait Until Scan Card Intro Screen Is Displayed
    Capture Screen Evidence    ocr_intro    scan_card_intro
    ${scan_locator}=    Run Keyword And Return Status    Element Should Be Visible    ${SCAN_CARD_INTRO_STEP_BAR}
    ${page_result}=    Run Keyword And Return Status    Tap Scan Card Intro Next
    Allow Android Permission If Visible
    ${locator_result}=    Evaluate    ${sign_up_locator} and ${scan_locator}
    Record Screen Result    ocr_intro    ${locator_result}    ${page_result}    ${page_result}    SHARED    Shared Sign Up and Scan Card Intro page objects used.
    Should Be True    ${page_result}    OCR intro did not transition with shared page objects.

Process Camera Screen
    Wait Until ID Card Camera Capture Screen Is Displayed
    Capture Screen Evidence    camera    before_take_photo
    ${locator_result}=    Run Keyword And Return Status    Element Should Be Visible    ${ID_CARD_CAMERA_VIEW}
    ${keyword_result}=    Run Keyword And Return Status    Element Should Be Visible    ${ID_CARD_TAKE_PHOTO}
    ${page_result}=    Set Variable    ${keyword_result}
    Record Screen Result    camera    ${locator_result}    ${keyword_result}    ${page_result}    SHARED    Shared camera wait locator resolved; stop at Camera screen.
    Should Be True    ${page_result}    Camera screen did not expose shared Take Photo locator.

Capture Screen Evidence
    [Arguments]    ${screen}    ${label}
    ${screen_dir}=    Set Variable    ${EVIDENCE_DIR}/${screen}
    Create Directory    ${screen_dir}
    ${png}=    Set Variable    ${screen_dir}/${label}.png
    ${xml}=    Set Variable    ${screen_dir}/${label}.xml
    ${activity}=    Set Variable    ${screen_dir}/${label}_activity.txt
    Run Process    sh    -c    adb -s ${UDID} exec-out screencap -p > ${png}
    ...    timeout=30s    on_timeout=terminate
    ${source_status}    ${source}=    Run Keyword And Ignore Error    Get Source
    IF    '${source_status}' == 'PASS'
        Create File    ${xml}    ${source}    UTF-8
    ELSE
        Create File    ${xml}    XML_CAPTURE_FAILED: ${source_status}    UTF-8
    END
    ${activity_result}=    Run Process    adb    -s    ${UDID}    shell    dumpsys    window
    ...    timeout=30s    on_timeout=terminate
    Create File    ${activity}    ${activity_result.stdout}    UTF-8

Record Screen Result
    [Arguments]    ${screen}    ${locator_result}    ${keyword_result}    ${page_result}    ${decision}    ${note}
    ${screen_dir}=    Set Variable    ${EVIDENCE_DIR}/${screen}
    Create Directory    ${screen_dir}
    ${content}=    Catenate    SEPARATOR=\n
    ...    Locator Result: ${locator_result}
    ...    Keyword Result: ${keyword_result}
    ...    Page Object Result: ${page_result}
    ...    Decision: ${decision}
    ...    Code Changes: none
    ...    Note: ${note}
    Create File    ${screen_dir}/result.md    ${content}\n    UTF-8
