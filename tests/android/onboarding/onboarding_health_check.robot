*** Settings ***
Documentation    E2E Onboarding Health Check with ADB logcat API capture
...              and lightweight checkpoint tracking.
...              Supports PASS, FAIL, and BLOCKED status (environment blocker).
Resource         ../../../resources/keywords/onboarding_common.resource
Resource         ../../../resources/keywords/api_capture_keywords.resource
Resource         ../../../resources/keywords/health_check_keywords.resource
Resource         ../../../resources/keywords/dob_stability_keywords.resource
Library          ../../../libraries/config_loader.py
Library          ../../../libraries/robot_output_sanitizer.py
Library          OperatingSystem

Suite Setup      Health Check Suite Setup
Suite Teardown   Health Check Suite Teardown

*** Variables ***
${HEALTH_CHECK_TESTDATA}    ${EMPTY}

*** Keywords ***
Health Check Suite Setup
    Should Not Be Empty    ${HEALTH_CHECK_TESTDATA}    HEALTH_CHECK_TESTDATA must point to an approved local YAML profile.
    File Should Exist    ${HEALTH_CHECK_TESTDATA}    HEALTH_CHECK_TESTDATA file does not exist.
    Initialize DOB Stability Tracking
    Start Health Check
    Open Mobile Application
    Mark Health Checkpoint    APP_OPENED
    Start API Capture

Health Check Suite Teardown
    ${test_status}=    Get Variable Value    ${PREV_TEST_STATUS}
    IF    $test_status is None
        ${test_status}=    Set Variable    FAIL
    END
    ${blocker_code}=    Get Variable Value    ${HEALTH_CHECK_BLOCKER_CODE}    ${EMPTY}
    ${hc_status}=    Set Variable    FAIL
    IF    '${blocker_code}' != '${EMPTY}'
        ${hc_status}=    Set Variable    BLOCKED
    ELSE IF    '${test_status}' == 'PASS'
        ${hc_status}=    Set Variable    PASS
    END
    End Health Check    ${hc_status}
    Generate DOB Stability Report
    ${redacted_log}=    Stop API Capture
    Close Application
    Run Keyword And Ignore Error    Attach API Capture Summary If Available    ${redacted_log}
    ${ts}=    Get Variable Value    ${HEALTH_CHECK_TS}
    Run Keyword If    $ts is not None    Log    [REPORT] Health check report: ${OUTPUT_DIR}/health_check/onboarding_health_check_${ts}.md

*** Keywords ***
Capture After ID Card Photo Evidence
    Sleep    3s
    ${evidence_dir}=    Set Variable    ${OUTPUT_DIR}/private_local/after_id_card_photo
    Create Directory    ${evidence_dir}
    Capture Page Screenshot    ${evidence_dir}/screenshot.png
    ${source}=    Get Source
    Create File    ${evidence_dir}/page_source.xml    ${source}    UTF-8
    Log    [HC] Private-local after-ID-card evidence captured.    INFO

*** Test Cases ***
E2E Onboarding Health Check
    [Documentation]    Completes full NTB onboarding flow while capturing API logs
    ...                and recording checkpoint progress.
    ...                BLOCKED status set when environment blocker is detected.
    ${previous_log_level}=    Set Log Level    NONE
    ${data}=    Load YAML    ${HEALTH_CHECK_TESTDATA}
    Set Log Level    ${previous_log_level}
    ${common_result}=    Complete Common Onboarding    ${data['profile']['citizen_id']}    ${data['profile']['date_of_birth']}    ${data['profile']['mobile_number']}
    Should Be Equal As Strings    ${common_result}    COMMON_ONBOARDING_COMPLETED
    ...    COMMON_ONBOARDING_BLOCKED=${common_result}
    Capture After ID Card Photo Evidence
