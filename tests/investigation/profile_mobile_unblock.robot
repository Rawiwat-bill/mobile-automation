*** Settings ***
Documentation    OCR-03 Phase 1 — reproduce mobile input failure on emulator with instrumentation.
...              Attaches to the running app (noReset) on the current Profile screen; does NOT pm clear.
...              Focus only Profile/CND mobile input. No OCR, no camera.
Library          AppiumLibrary
Library          OperatingSystem
Library          Process
Library          String
Library          ../../libraries/config_loader.py
Resource         ../../resources/app/app_keywords.resource
Resource         ../../resources/pages/onboarding/profile_screen_page.resource


*** Variables ***
${UDID}             emulator-5554
${DEVICE_NAME}      Android Emulator
${REPORT_DIR}       reports/ocr_runtime
${EVIDENCE}         ${REPORT_DIR}/evidence/ocr03
${TESTDATA}         testdata/onboarding/ntb.local.yaml


*** Test Cases ***
Reproduce Mobile Input Failure
    Create Directory    ${REPORT_DIR}
    Create Directory    ${EVIDENCE}
    ${mobile}=    Load Mobile From Testdata
    Attach To Running App
    ${on_profile}=    Verify On Profile
    Capture Evidence    before_mobile
    Run Keyword If    not ${on_profile}    Fail    Not on Profile (screen=${EMPTY}); attach did not resume Profile state.
    Instrumented Mobile Input    ${mobile}
    Capture Evidence    after_mobile
    Log Mobile And Next State
    [Teardown]    Run Keyword And Ignore Error    Close Application


*** Keywords ***
Load Mobile From Testdata
    ${previous_log_level}=    Set Log Level    NONE
    ${data}=    Load YAML    ${TESTDATA}
    ${mobile}=    Set Variable    ${data['profile']['mobile_number']}
    Set Log Level    ${previous_log_level}
    Log    [OCR-03] mobile loaded (masked): [MASKED_PHONE]
    RETURN    ${mobile}

Attach To Running App
    Open Application
    ...    ${APPIUM_URL}
    ...    platformName=Android
    ...    automationName=UiAutomator2
    ...    udid=${UDID}
    ...    deviceName=${DEVICE_NAME}
    ...    appPackage=${APP_PACKAGE}
    ...    appActivity=${APP_ACTIVITY}
    ...    noReset=${TRUE}
    ...    dontStopAppOnReset=${TRUE}
    ...    ignoreHiddenApiPolicyError=${TRUE}
    ...    disableWindowAnimation=${TRUE}
    ...    uiautomator2ServerInstallTimeout=120000
    ...    uiautomator2ServerLaunchTimeout=120000
    ...    newCommandTimeout=300

Verify On Profile
    ${status}    ${source}=    Run Keyword And Ignore Error    Get Source
    ${s}=    Set Variable IF    '${status}' == 'PASS'    ${source}    ${EMPTY}
    ${on_profile}=    Run Keyword And Return Status    Should Contain    ${s}    screenProfile_
    Log    [OCR-03] on_profile=${on_profile}
    RETURN    ${on_profile}

Instrumented Mobile Input
    [Arguments]    ${mobile}
    ${tap_ok}=    Run Keyword And Return Status    Tap Profile Element Center    ${PROFILE_MOBILE_NUMBER_CONTAINER}
    Log    [OCR-03] step1 Appium Tap container ok=${tap_ok}
    ${focused_after_tap}=    Read Mobile Focused
    Log    [OCR-03] step2 mobile focused after Appium Tap=${focused_after_tap}
    ${send_status}    ${send_err}=    Run Keyword And Ignore Error    Input Text    ${PROFILE_MOBILE_NUMBER_INPUT}    ${mobile}
    Log    [OCR-03] step3 sendKeys status=${send_status} err=${send_err}
    ${text_after_input}=    Read Mobile Text
    Log    [OCR-03] step4 mobile text after sendKeys=${text_after_input}
    ${blur_ok}=    Run Keyword And Return Status    Tap Profile Blank Area    ${BLUR_AFTER_MOBILE_Y}
    Log    [OCR-03] step5 blur tap ok=${blur_ok} at y=${BLUR_AFTER_MOBILE_Y}
    ${text_after_blur}=    Read Mobile Text
    Log    [OCR-03] step6 mobile text after blur=${text_after_blur}
    Create File    ${EVIDENCE}/mobile_steps.txt
    ...    tap_ok=${tap_ok}\nfocused_after_tap=${focused_after_tap}\nsend_status=${send_status}\nsend_err=${send_err}\ntext_after_input=${text_after_input}\nblur_ok=${blur_ok}\ntext_after_blur=${text_after_blur}\n
    ...    UTF-8

Read Mobile Focused
    ${status}    ${val}=    Run Keyword And Ignore Error    Get Element Attribute    ${PROFILE_MOBILE_NUMBER_INPUT}    focused
    RETURN    ${val}

Read Mobile Text
    ${status}    ${val}=    Run Keyword And Ignore Error    Get Text    ${PROFILE_MOBILE_NUMBER_INPUT}
    ${val}=    Set Variable If    '${status}' == 'PASS'    ${val}    <get_text_failed:${val}>
    RETURN    ${val}

Log Mobile And Next State
    ${mobile_text}=    Read Mobile Text
    ${next_enabled}=    Run Keyword And Return Status    Element Should Be Enabled    ${PROFILE_NEXT_BUTTON_CONTAINER}
    Log    [OCR-03] FINAL mobile_text=${mobile_text} next_enabled=${next_enabled}
    Create File    ${EVIDENCE}/profile_unblock_result.md
    ...    # OCR-03 Phase 1 — mobile input reproduction\n\nmobile_text_final: ${mobile_text}\nnext_enabled: ${next_enabled}\n
    ...    UTF-8

Capture Evidence
    [Arguments]    ${label}
    Run Process    sh    -c    adb -s ${UDID} exec-out screencap -p > ${EVIDENCE}/${label}.png
    ...    timeout=30s    on_timeout=terminate
    ${status}    ${source}=    Run Keyword And Ignore Error    Get Source
    ${body}=    Set Variable IF    '${status}' == 'PASS'    ${source}    XML_CAPTURE_FAILED:${source}
    Create File    ${EVIDENCE}/${label}.xml    ${body}    UTF-8
    ${act}=    Run Process    adb    -s    ${UDID}    shell    dumpsys    window
    ...    timeout=30s    on_timeout=terminate
    Create File    ${EVIDENCE}/${label}_activity.txt    ${act.stdout}    UTF-8
