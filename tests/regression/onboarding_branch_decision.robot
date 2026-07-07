*** Settings ***
Documentation    Sprint 2.78 — Onboarding branch decision discovery (real device).
...              Drives Profile -> PDPA -> SignUp, then STOPs and records which screen
...              appears next: DOPA_information (backend) OR ScanCardIntro/OCR (camera)
...              OR an error. Reuses shared page objects. No OTP, no camera capture.
...              Evidence-first; each step captures png+xml+activity so a stall still yields evidence.
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


*** Variables ***
${UDID}                48ZYD25C01422768
${REAL_DEVICE_NAME}    MGA_LX3
${PLATFORM_VERSION}    10
${REPORT_DIR}          reports/investigation/onboarding_branch_decision
${TESTDATA}            testdata/onboarding/ntb.local.yaml
# Trial knobs (override from CLI: -v CID:... -v TRIAL_TAG:trial_2_alt -v CLEAR_APP:True)
${CID}                 ${EMPTY}
${DOB}                 ${EMPTY}
${MOBILE}              ${EMPTY}
${TRIAL_TAG}           trial
${CLEAR_APP}           ${FALSE}


*** Test Cases ***
Discover Branch After SignUp
    [Documentation]    Runs one onboarding attempt up to SignUp, then records the branch.
    Create Directory    ${REPORT_DIR}
    Create Directory    ${REPORT_DIR}/evidence/${TRIAL_TAG}
    Resolve Trial Data
    Run Keyword If    '${CLEAR_APP}' == 'True'    Clear App Data For Fresh Run
    Open Installed App On Real Device
    Capture Step Evidence    launch
    Drive To SignUp And Record Branch
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
    Log    [BRANCH] Trial=${TRIAL_TAG} CID recognised=${CID == '3872637115880'}

Clear App Data For Fresh Run
    Log    [BRANCH] Clearing app data (pm clear) for fresh onboarding state
    Run Process    adb    -s    ${UDID}    shell    pm clear    ${APP_PACKAGE}
    ...    timeout=30s    on_timeout=terminate

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
    ...    newCommandTimeout=300

Drive To SignUp And Record Branch
    ${screen}=    Detect Current Screen
    Log    [BRANCH] Starting screen detected: ${screen}
    Capture Step Evidence    start_${screen}

    ${on_landing}=    Run Keyword And Return Status    Wait Until Element Is Visible    ${LANDING_READY_BUTTON}    20s
    IF    ${on_landing}
        Run Keyword And Ignore Error    Click Element    ${LANDING_READY_BUTTON}
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
    Record Branch Decision

Pass Consent Screen Reliably
    [Documentation]    In-bounds upward swipes (device is 720x1604; shared keyword uses y=1950 OOB).
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
    Log    [BRANCH] Consent scroll reached bottom=${moved}
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
    ${screen}=    Set Variable If
    ...    ${is_dopa}    dopa
    ...    ${is_scan}    scan
    ...    ${is_signup}    signup
    ...    ${is_pdpa}    pdpa
    ...    ${is_profile}    profile
    ...    ${is_landing}    landing
    ...    consent
    RETURN    ${screen}

Record Branch Decision
    [Documentation]    After SignUp, wait for either DOPA, ScanCardIntro, or an error; record which.
    ${dopa}=    Run Keyword And Return Status    Wait Until Page Contains Element
    ...    xpath=//*[contains(@resource-id,'screenDopaInformation')]    35s
    ${scan}=    Run Keyword And Return Status    Wait Until Page Contains Element
    ...    ${SCAN_CARD_INTRO_STEP_BAR}    8s
    ${err}=    Run Keyword And Return Status    Wait Until Page Contains Element
    ...    xpath=//*[contains(translate(@resource-id,'ABCDEFGHIJKLMNOPQRSTUVWXYZ','abcdefghijklmnopqrstuvwxyz'),'error') or contains(@text,'not available') or contains(@text,'RGI-') or contains(@text,'GOD-')]    5s
    ${branch}=    Set Variable IF    ${dopa}    DOPA_INFORMATION    ${scan}    OCR_CAMERA    ${err}    ERROR    UNKNOWN
    Capture Step Evidence    branch_${branch}
    Log    [BRANCH] RESULT branch=${branch} dopa=${dopa} scan=${scan} error=${err}
    Create File    ${REPORT_DIR}/evidence/${TRIAL_TAG}/BRANCH_RESULT.txt
    ...    trial=${TRIAL_TAG}\ncid_recognised=${CID == '3872637115880'}\nbranch=${branch}\ndopa_reached=${dopa}\nscan_reached=${scan}\nerror_reached=${err}\n
    ...    UTF-8

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
