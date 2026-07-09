*** Settings ***
Documentation    OCR-01 — DEV fresh-state real-device OCR route (investigation; OCR capture unstable).
...              pm clear -> Landing -> Consent -> Profile -> PDPA -> SignUp -> ScanCardIntro ->
...              OCR Camera -> ONE capture -> classify result (DOPA_information / RGI-055 / OCR error / no capture).
...              Stops before OTP. Reuses shared page objects and branch_decision's real-device consent.
...              Evidence-first: each step captures png+xml+activity.
...              Emulator camera has 0-FPS — REAL DEVICE REQUIRED for the capture step.
Library          AppiumLibrary
Library          OperatingSystem
Library          Process
Library          String
Library          ../../libraries/config_loader.py
Resource         ../../resources/app/app_keywords.resource
Resource         ../../resources/pages/onboarding/landing_screen_page.resource
Resource         ../../resources/pages/onboarding/consent_screen_page.resource
Resource         ../../resources/pages/onboarding/profile_screen_page.resource
Resource         ../../resources/pages/onboarding/pdpa_consent_page.resource
Resource         ../../resources/pages/onboarding/sign_up_page.resource
Resource         ../../resources/pages/onboarding/scan_card_intro_page.resource
Resource         ../../resources/pages/onboarding/id_card_camera_capture_page.resource
Resource         ../../resources/pages/onboarding/dopa_information_page.resource


*** Variables ***
${UDID}                48ZYD25C01422768
${REAL_DEVICE_NAME}    MGA_LX3
${PLATFORM_VERSION}    10
${REPORT_DIR}          reports/ocr_runtime
${TESTDATA}            testdata/onboarding/ntb.local.yaml
${TRIAL_TAG}           ocr01
${CLEAR_APP}           ${TRUE}
${CAPTURE_TIMEOUT}     90s
${CID}                 ${EMPTY}
${DOB}                 ${EMPTY}
${MOBILE}              ${EMPTY}


*** Test Cases ***
DEV Fresh State OCR Capture On Real Device
    [Documentation]    Fresh-state DEV route through OCR capture; classifies the post-capture branch.
    Create Directory    ${REPORT_DIR}
    Create Directory    ${REPORT_DIR}/evidence/${TRIAL_TAG}
    Resolve Trial Data
    Run Keyword If    '${CLEAR_APP}' == 'True'    Clear App Data For Fresh Run
    Open Installed App On Real Device
    Capture Step Evidence    launch
    Drive To OCR Camera
    Attempt OCR Capture And Classify
    [Teardown]    Run Keyword And Ignore Error    Close Application


*** Keywords ***
Resolve Trial Data
    ${previous_log_level}=    Set Log Level    NONE
    ${data}=    Load YAML    ${TESTDATA}
    ${cid}=    Set Variable If    '${CID}' == ''    ${data['profile']['citizen_id']}    ${CID}
    ${dob}=    Set Variable If    '${DOB}' == ''    ${data['profile']['date_of_birth']}    ${DOB}
    ${mob}=    Set Variable If    '${MOBILE}' == ''    ${data['profile']['mobile_number']}    ${MOBILE}
    Set Log Level    ${previous_log_level}
    Set Test Variable    ${CID}      ${cid}
    Set Test Variable    ${DOB}      ${dob}
    Set Test Variable    ${MOBILE}   ${mob}
    Log    [OCR-01] Trial=${TRIAL_TAG} fresh_state=${CLEAR_APP}

Clear App Data For Fresh Run
    Log    [OCR-01] Clearing app data (pm clear) for fresh onboarding state
    Run Process    adb    -s    ${UDID}    shell    pm clear    ${APP_PACKAGE}
    ...    timeout=30s    on_timeout=terminate

Open Installed App On Real Device
    Open Application
    ...    ${APPIUM_URL}
    ...    platformName=Android
    ...    automationName=UiAutomator2
    ...    udid=${UDID}
    ...    deviceName=${REAL_DEVICE_NAME}
    ...    platformVersion=${PLATFORM_VERSION}
    ...    appPackage=${APP_PACKAGE}
    ...    appActivity=${APP_ACTIVITY}
    ...    noReset=${TRUE}
    ...    autoGrantPermissions=${TRUE}
    ...    ignoreHiddenApiPolicyError=${TRUE}
    ...    disableWindowAnimation=${TRUE}
    ...    uiautomator2ServerInstallTimeout=120000
    ...    uiautomator2ServerLaunchTimeout=120000
    ...    newCommandTimeout=300

Drive To OCR Camera
    ${screen}=    Detect Current Screen
    Log    [OCR-01] Starting screen detected: ${screen}
    Capture Step Evidence    start_${screen}

    ${on_landing}=    Run Keyword And Return Status    Wait Until Element Is Visible    ${LANDING_READY_BUTTON}    20s
    IF    ${on_landing}
        Run Keyword And Ignore Error    Tap Landing Ready Button
        Allow Android Permission If Visible
        Capture Step Evidence    after_landing
    END
    ${on_consent}=    Run Keyword And Return Status    Wait Until Element Is Visible    ${CONSENT_TITLE_TEXT}    15s
    IF    ${on_consent}
        Pass Consent Screen Reliably
        Capture Step Evidence    after_consent
    END
    ${on_profile}=    Run Keyword And Return Status    Wait Until Profile Screen Is Displayed
    IF    ${on_profile}
        Fill Profile Fields Masked
        Run Keyword And Ignore Error    Tap Profile Next
        Capture Step Evidence    after_profile_next
    END
    ${on_pdpa}=    Run Keyword And Return Status    Wait Until PDPA Consent Screen Is Displayed
    IF    ${on_pdpa}
        Run Keyword And Ignore Error    Tap PDPA Consent Accept Button
        Capture Step Evidence    after_pdpa
    END
    ${on_signup}=    Run Keyword And Return Status    Wait Until Sign Up Screen Is Displayed
    IF    ${on_signup}
        Run Keyword And Ignore Error    Tap Sign Up Lets Start Button
        Allow Android Permission If Visible
        Capture Step Evidence    after_signup_letsstart
    END
    Wait Until Scan Card Intro Screen Is Displayed
    Capture Step Evidence    scan_card_intro
    Run Keyword And Ignore Error    Tap Scan Card Intro Next
    Allow Android Permission If Visible
    Wait Until ID Card Camera Capture Screen Is Displayed
    Capture Step Evidence    ocr_camera
    Log    [OCR-01] Reached OCR Camera screen — ready for capture

Attempt OCR Capture And Classify
    ${take_visible}=    Run Keyword And Return Status    Element Should Be Visible    ${ID_CARD_TAKE_PHOTO}
    Log    [OCR-01] Take Photo visible=${take_visible}
    Capture Step Evidence    before_capture
    ${tapped}=    Run Keyword And Return Status    Tap Take Photo
    Log    [OCR-01] Take Photo tapped=${tapped}
    ${branch}=    Classify OCR Result
    Capture Step Evidence    result_${branch}
    Log    [OCR-01] RESULT branch=${branch}
    Create File    ${REPORT_DIR}/evidence/${TRIAL_TAG}/OCR_RESULT.txt
    ...    trial=${TRIAL_TAG}\nfresh_state=${CLEAR_APP}\ncapture_tapped=${tapped}\nbranch=${branch}\n
    ...    UTF-8

Classify OCR Result
    ${dopa}=    Run Keyword And Return Status    Wait Until Page Contains Element    ${DOPA_INFORMATION_SCREEN}    ${CAPTURE_TIMEOUT}
    ${rgi}=    Run Keyword And Return Status    Page Should Contain Text    RGI-
    ${god}=    Run Keyword And Return Status    Page Should Contain Text    GOD-
    ${err}=    Run Keyword And Return Status    Wait Until Page Contains Element
    ...    xpath=//*[contains(translate(@resource-id,'ABCDEFGHIJKLMNOPQRSTUVWXYZ','abcdefghijklmnopqrstuvwxyz'),'error') or contains(@text,'not available')]    5s
    ${retake}=    Run Keyword And Return Status    Element Should Be Visible    ${SCAN_CARD_INTRO_STEP_BAR}    5s
    ${branch}=    Set Variable IF
    ...    ${dopa}    DOPA_INFORMATION
    ...    ${rgi}    RGI_055
    ...    ${god}    OCR_ERROR
    ...    ${err}    OCR_ERROR
    ...    ${retake}    NO_CAPTURE
    ...    NO_CAPTURE
    Log    [OCR-01] classify dopa=${dopa} rgi=${rgi} god=${god} err=${err} retake=${retake} -> ${branch}
    RETURN    ${branch}

Pass Consent Screen Reliably
    [Documentation]    In-bounds upward swipes (real device is 720x1604; shared scroll uses y=1950 OOB).
    ...                Swipes the WebView to bottom until the end text appears, then taps Accept.
    ${moved}=    Set Variable    ${FALSE}
    FOR    ${i}    IN RANGE    20
        Run Process    adb    -s    ${UDID}    shell    input    swipe    360    1300    360    300    300
        ...    timeout=10s    on_timeout=terminate
        ${at_bottom}=    Run Keyword And Return Status    Page Should Contain Text    I have read and understood
        IF    ${at_bottom}
            ${moved}=    Set Variable    ${TRUE}
            BREAK
        END
    END
    Log    [OCR-01] Consent scroll reached bottom=${moved}
    ${accept_visible}=    Run Keyword And Return Status    Wait Until Element Is Visible    ${CONSENT_ACCEPT_BUTTON}    5s
    IF    ${accept_visible}
        Click Element    ${CONSENT_ACCEPT_BUTTON}
    END
    Run Keyword And Return Status    Wait Until Page Does Not Contain Element    ${CONSENT_TITLE_TEXT}    30s

Fill Profile Fields Masked
    ${previous_log_level}=    Set Log Level    NONE
    Run Keyword And Ignore Error    Input Citizen ID    ${CID}
    Run Keyword And Ignore Error    Input Date Of Birth    ${DOB}
    Run Keyword And Ignore Error    Input Mobile Number    ${MOBILE}
    Set Log Level    ${previous_log_level}

Detect Current Screen
    [Documentation]    Greps page source for known screen markers; returns a label.
    ${status}    ${source}=    Run Keyword And Ignore Error    Get Source
    ${s}=    Set Variable IF    '${status}' == 'PASS'    ${source}    ${EMPTY}
    ${is_landing}=    Run Keyword And Return Status    Should Contain    ${s}    screenLanding_
    ${is_profile}=    Run Keyword And Return Status    Should Contain    ${s}    screenProfile_
    ${is_pdpa}=    Run Keyword And Return Status    Should Contain    ${s}    screenPDPA_
    ${is_signup}=    Run Keyword And Return Status    Should Contain    ${s}    Let’s start
    ${is_scan}=    Run Keyword And Return Status    Should Contain    ${s}    screenScanCardIntro_
    ${is_dopa}=    Run Keyword And Return Status    Should Contain    ${s}    screenDopaInformation_
    ${is_camera}=    Run Keyword And Return Status    Should Contain    ${s}    RVCamera
    ${screen}=    Set Variable If
    ...    ${is_camera}    camera
    ...    ${is_dopa}    dopa
    ...    ${is_scan}    scan
    ...    ${is_signup}    signup
    ...    ${is_pdpa}    pdpa
    ...    ${is_profile}    profile
    ...    ${is_landing}    landing
    ...    consent
    RETURN    ${screen}

Capture Step Evidence
    [Arguments]    ${label}
    ${d}=    Set Variable    ${REPORT_DIR}/evidence/${TRIAL_TAG}
    Create Directory    ${d}
    Run Process    sh    -c    adb -s ${UDID} exec-out screencap -p > ${d}/${label}.png
    ...    timeout=30s    on_timeout=terminate
    ${status}    ${source}=    Run Keyword And Ignore Error    Get Source
    ${body}=    Set Variable IF    '${status}' == 'PASS'    ${source}    XML_CAPTURE_FAILED:${source}
    Create File    ${d}/${label}.xml    ${body}    UTF-8
    ${act}=    Run Process    adb    -s    ${UDID}    shell    dumpsys    window
    ...    timeout=30s    on_timeout=terminate
    Create File    ${d}/${label}_activity.txt    ${act.stdout}    UTF-8
