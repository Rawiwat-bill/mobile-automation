*** Settings ***
Documentation    Profile-to-camera real-device resume helper from the current stable checkpoint.
Library          AppiumLibrary
Library          OperatingSystem
Library          Process
Library          ../../libraries/config_loader.py
Resource         ../../resources/app/app_keywords.resource
Resource         ../../resources/pages/onboarding/profile_screen_page.resource
Resource         ../../resources/pages/onboarding/pdpa_consent_page.resource
Resource         ../../resources/pages/onboarding/sign_up_page.resource
Resource         ../../resources/pages/onboarding/scan_card_intro_page.resource
Resource         ../../resources/pages/onboarding/id_card_camera_capture_page.resource


*** Variables ***
${UDID}                48ZYD25C01422768
${REPORT_DIR}          reports/investigation/real_device_profile_resume
${EVIDENCE_DIR}        ${REPORT_DIR}/evidence
${TESTDATA}            testdata/onboarding/ntb.local.yaml
${REAL_DEVICE_NAME}    MGA_LX3
${PLATFORM_VERSION}    10
${MAIN_ACTIVITY}       com.bangkokbank.blue.MainActivity


*** Test Cases ***
Resume Profile To Camera On Real Device
    Create Directory    ${REPORT_DIR}
    Create Directory    ${EVIDENCE_DIR}
    Open Attached App Session On Real Device
    Load Local Onboarding Data
    Wait Until Profile Screen Is Displayed
    Capture Screen Evidence    profile    before_fill
    Input Citizen ID    ${LOCAL_CITIZEN_ID}
    Input Date Of Birth    ${LOCAL_DATE_OF_BIRTH}
    Input Mobile Number    ${LOCAL_MOBILE_NUMBER}
    Capture Screen Evidence    profile    after_fill
    Tap Profile Next
    Capture Screen Evidence    pdpa    before_accept
    Wait Until PDPA Consent Screen Is Displayed
    Tap PDPA Consent Accept Button
    Capture Screen Evidence    pdpa    after_accept
    Wait Until Sign Up Screen Is Displayed
    Tap Sign Up Lets Start Button
    Allow Android Permission If Visible
    Capture Screen Evidence    ocr_intro    sign_up
    Wait Until Scan Card Intro Screen Is Displayed
    Tap Scan Card Intro Next
    Allow Android Permission If Visible
    Capture Screen Evidence    ocr_intro    scan_card_intro
    Wait Until ID Card Camera Capture Screen Is Displayed
    Capture Screen Evidence    camera    before_stop
    [Teardown]    Run Keyword And Ignore Error    Close Application


*** Keywords ***
Open Attached App Session On Real Device
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

Capture Screen Evidence
    [Arguments]    ${screen}    ${label}
    ${screen_dir}=    Set Variable    ${EVIDENCE_DIR}/${screen}
    Create Directory    ${screen_dir}
    ${png}=    Set Variable    ${screen_dir}/${label}.png
    ${xml}=    Set Variable    ${screen_dir}/${label}.xml
    Run Process    sh    -c    adb -s ${UDID} exec-out screencap -p > ${png}
    ...    timeout=30s    on_timeout=terminate
    ${dump_result}=    Run Process    adb    -s    ${UDID}    shell    uiautomator    dump    --compressed    /sdcard/window_dump.xml
    ...    timeout=30s    on_timeout=terminate
    IF    ${dump_result.rc} == 0
        ${xml_result}=    Run Process    adb    -s    ${UDID}    exec-out    cat    /sdcard/window_dump.xml
        ...    timeout=30s    on_timeout=terminate
        Create File    ${xml}    ${xml_result.stdout}    UTF-8
    ELSE
        Create File    ${xml}    XML_CAPTURE_FAILED: ${dump_result.rc}    UTF-8
    END
