*** Settings ***
Library    Process
Library    OperatingSystem
Library    ../../libraries/api_log_redactor.py

*** Variables ***
${APICAPTURE_APP_PACKAGE}    com.bangkokbank.blue.dev
${APICAPTURE_OUTPUT_DIR}    ${OUTPUT_DIR}/api_logs

*** Keywords ***
Start API Capture
    ${result}=    Run Process    adb    shell    pidof    -s    ${APICAPTURE_APP_PACKAGE}
    ${pid}=    Evaluate    '${result.stdout}'.strip()
    IF    '${pid}' == ''
        Log    [API CAPTURE] Could not detect PID for package ${APICAPTURE_APP_PACKAGE} — skipping capture.    WARN
        Set Suite Variable    ${APICAPTURE_LOG_HANDLE}    ${NONE}
        RETURN
    END
    ${raw_dir}=    Set Variable    ${APICAPTURE_OUTPUT_DIR}/raw
    Create Directory    ${raw_dir}
    ${timestamp}=    Evaluate    __import__('time').strftime('%Y%m%d_%H%M%S')
    ${raw_file}=    Set Variable    ${raw_dir}/api_capture_${timestamp}_${pid}.log
    ${handle}=    Start Process    adb    logcat    -b    main    -v    time    --pid    ${pid}    stdout=${raw_file}    stderr=STDOUT    alias=api_logcat
    Set Suite Variable    ${APICAPTURE_LOG_HANDLE}    ${handle}
    Set Suite Variable    ${APICAPTURE_RAW_FILE}    ${raw_file}
    Log    [API CAPTURE] Started logcat capture PID=${pid} → ${raw_file}

Stop API Capture
    ${handle}=    Get Variable Value    ${APICAPTURE_LOG_HANDLE}
    IF    $handle is None
        Log    [API CAPTURE] No active capture handle — skipping stop.
        RETURN    ${NONE}
    END
    Run Keyword And Ignore Error    Terminate Process    ${handle}
    Sleep    1s
    ${exists}=    Run Keyword And Return Status    File Should Exist    ${APICAPTURE_RAW_FILE}
    IF    not ${exists}
        Log    [API CAPTURE] Raw log file not found: ${APICAPTURE_RAW_FILE}
        RETURN    ${NONE}
    END
    ${redacted_dir}=    Set Variable    ${APICAPTURE_OUTPUT_DIR}
    Create Directory    ${redacted_dir}
    ${timestamp}=    Evaluate    __import__('time').strftime('%Y%m%d_%H%M%S')
    ${redacted_file}=    Set Variable    ${redacted_dir}/redacted_api_capture_${timestamp}.log
    ${summary}=    Redact Log    ${APICAPTURE_RAW_FILE}    ${redacted_file}
    ${raw_size}=    Get File Size    ${APICAPTURE_RAW_FILE}
    ${redacted_size}=    Get File Size    ${redacted_file}
    Log    [API CAPTURE] Raw: ${APICAPTURE_RAW_FILE} (${raw_size} bytes)
    Log    [API CAPTURE] Redacted: ${redacted_file} (${redacted_size} bytes)
    Log    [API CAPTURE] Summary: ${summary}
    ${report_dir}=    Set Variable    ${OUTPUT_DIR}/api_logs
    Create Directory    ${report_dir}
    ${summary_file}=    Set Variable    ${report_dir}/api_capture_summary_${timestamp}.log
    ${summary_text}=    Catenate    SEPARATOR=\n
    ...    total_lines: ${summary['total_lines']}
    ...    api_lines: ${summary['api_lines']}
    ...    raw_path: ${summary['raw_path']}
    ...    redacted_path: ${summary['redacted_path']}
    ...    timestamp: ${summary['timestamp']}
    Create File    ${summary_file}    ${summary_text}
    Log    [API CAPTURE] Summary written to ${summary_file}
    RETURN    ${redacted_file}

Attach API Capture Summary If Available
    [Arguments]    ${redacted_path}
    IF    ${redacted_path} is None
        Log    [API CAPTURE] No API capture data available.
        RETURN
    END
    ${exists}=    Run Keyword And Return Status    File Should Exist    ${redacted_path}
    IF    not ${exists}
        Log    [API CAPTURE] Redacted log not found: ${redacted_path}
        RETURN
    END
    Log    [API CAPTURE] Redacted API log available: ${redacted_path}
