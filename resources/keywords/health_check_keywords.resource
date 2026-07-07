*** Settings ***
Library    Collections
Library    OperatingSystem

*** Variables ***
${HEALTH_CHECK_DIR}    ${OUTPUT_DIR}/health_check
@{HEALTH_CHECK_LIST}

*** Keywords ***
Start Health Check
    Set Suite Variable    ${HEALTH_CHECK_ACTIVE}    ${TRUE}
    ${start}=    Evaluate    __import__('time').time()
    Set Suite Variable    ${HEALTH_CHECK_START}    ${start}
    ${ts}=    Evaluate    __import__('time').strftime('%Y%m%d_%H%M%S')
    Set Suite Variable    ${HEALTH_CHECK_TS}    ${ts}
    Set Suite Variable    @{HEALTH_CHECK_LIST}
    Set Suite Variable    ${HEALTH_CHECK_BLOCKER_CODE}    ${EMPTY}
    Set Suite Variable    ${HEALTH_CHECK_BLOCKER_REASON}    ${EMPTY}
    Set Suite Variable    ${HEALTH_CHECK_BLOCKER_EVIDENCE}    ${EMPTY}
    Log    [HEALTH] Checkpoint tracking started    INFO

Mark Health Checkpoint
    [Arguments]    ${stage}
    ${active}=    Get Variable Value    ${HEALTH_CHECK_ACTIVE}
    IF    $active is None
        RETURN
    END
    IF    not $active
        RETURN
    END
    ${now}=    Evaluate    __import__('time').time()
    ${start}=    Set Variable    ${HEALTH_CHECK_START}
    ${elapsed}=    Evaluate    round(${now} - ${start}, 3)
    ${entry}=    Evaluate    {'stage': '${stage}', 'elapsed': ${elapsed}}
    Append To List    ${HEALTH_CHECK_LIST}    ${entry}
    Set Suite Variable    @{HEALTH_CHECK_LIST}
    ${msg}=    Set Variable    [HEALTH] CHECKPOINT: ${stage}  (${elapsed}s)
    Log    ${msg}    INFO

Set Health Check Blocker
    [Arguments]    ${code}    ${reason}    ${evidence_path}=${EMPTY}
    Set Suite Variable    ${HEALTH_CHECK_BLOCKER_CODE}    ${code}
    Set Suite Variable    ${HEALTH_CHECK_BLOCKER_REASON}    ${reason}
    Set Suite Variable    ${HEALTH_CHECK_BLOCKER_EVIDENCE}    ${evidence_path}
    Log    [HEALTH] BLOCKER: ${code} - ${reason}    WARN
    IF    '${evidence_path}' != '${EMPTY}'
        Log    [HEALTH] Evidence: ${evidence_path}    WARN
    END

End Health Check
    [Arguments]    ${status}=FAIL
    ${active}=    Get Variable Value    ${HEALTH_CHECK_ACTIVE}
    IF    $active is None
        RETURN
    END
    IF    not $active
        RETURN
    END
    Log Health Check Summary    ${status}
    Set Suite Variable    ${HEALTH_CHECK_ACTIVE}    ${FALSE}
    ${msg}=    Set Variable    [HEALTH] Checkpoint tracking ended (status=${status})
    Log    ${msg}    INFO

Log Health Check Summary
    [Arguments]    ${status}
    Create Directory    ${HEALTH_CHECK_DIR}
    ${ts}=    Set Variable    ${HEALTH_CHECK_TS}
    ${json_path}=    Set Variable    ${HEALTH_CHECK_DIR}/onboarding_health_check_${ts}.json
    ${md_path}=    Set Variable    ${HEALTH_CHECK_DIR}/onboarding_health_check_${ts}.md
    ${count}=    Get Length    ${HEALTH_CHECK_LIST}
    ${last_stage}=    Set Variable    NONE
    IF    ${count} > 0
        ${last}=    Get From List    ${HEALTH_CHECK_LIST}    -1
        ${last_stage}=    Set Variable    ${last['stage']}
    END
    ${checkpoints}=    Create List
    FOR    ${cp}    IN    @{HEALTH_CHECK_LIST}
        ${entry}=    Create Dictionary    stage=${cp['stage']}    elapsed=${cp['elapsed']}
        Append To List    ${checkpoints}    ${entry}
    END
    ${checkpoints_json}=    Evaluate    __import__('json').dumps($checkpoints, indent=2)
    ${blocker_code}=    Get Variable Value    ${HEALTH_CHECK_BLOCKER_CODE}    ${EMPTY}
    ${blocker_reason}=    Get Variable Value    ${HEALTH_CHECK_BLOCKER_REASON}    ${EMPTY}
    ${blocker_evidence}=    Get Variable Value    ${HEALTH_CHECK_BLOCKER_EVIDENCE}    ${EMPTY}
    ${has_blocker}=    Evaluate    '${blocker_code}' != ''
    IF    ${has_blocker}
        ${json_content}=    Catenate    SEPARATOR=\n
        ...    {
        ...      "status": "${status}",
        ...      "last_checkpoint": "${last_stage}",
        ...      "checkpoint_count": ${count},
        ...      "blocker": {
        ...        "code": "${blocker_code}",
        ...        "reason": "${blocker_reason}",
        ...        "evidence": "${blocker_evidence}"
        ...      },
        ...      "checkpoints": ${checkpoints_json}
        ...    }
    ELSE
        ${json_content}=    Catenate    SEPARATOR=\n
        ...    {
        ...      "status": "${status}",
        ...      "last_checkpoint": "${last_stage}",
        ...      "checkpoint_count": ${count},
        ...      "checkpoints": ${checkpoints_json}
        ...    }
    END
    Create File    ${json_path}    ${json_content}
    ${HASH}=    Evaluate    chr(35)
    ${HEADER}=    Catenate    SEPARATOR=\n
    ...    ${HASH} Onboarding Health Check Report
    ...    ${EMPTY}
    ...    **Date:** ${ts}
    ...    **Status:** ${status}
    ...    **Last Checkpoint:** ${last_stage}
    ...    **Checkpoints Reached:** ${count}
    ...    ${EMPTY}
    ${blocker_section}=    Set Variable    ${EMPTY}
    IF    ${has_blocker}
        ${blocker_section}=    Catenate    SEPARATOR=\n
        ...    ${HASH}${HASH} Blocker
        ...    ${EMPTY}
        ...    | Field | Value |
        ...    |-------|-------|
        ...    | **Code** | ${blocker_code} |
        ...    | **Reason** | ${blocker_reason} |
        ...    | **Evidence** | ${blocker_evidence} |
        ...    ${EMPTY}
    END
    ${checkpoints_header}=    Catenate    SEPARATOR=\n
    ...    ${HASH}${HASH} Checkpoints
    ...    ${EMPTY}
    ...    | # | Stage | Elapsed (s) |
    ...    |---|-------|-------------|
    ${md_rows}=    Create List
    ${index}=    Set Variable    1
    FOR    ${cp}    IN    @{HEALTH_CHECK_LIST}
        ${stage}=    Set Variable    ${cp['stage']}
        ${elapsed}=    Set Variable    ${cp['elapsed']}
        ${row}=    Evaluate    '| ' + str(${index}) + ' | ' + '${stage}' + ' | ' + str(${elapsed}) + ' |'
        Append To List    ${md_rows}    ${row}
        ${index}=    Evaluate    ${index} + 1
    END
    ${rows_text}=    Catenate    SEPARATOR=\n    @{md_rows}
    ${md_content}=    Catenate    SEPARATOR=\n    ${HEADER}    ${blocker_section}    ${checkpoints_header}    ${rows_text}
    Create File    ${md_path}    ${md_content}
    ${msg_report}=    Set Variable    [HEALTH] Report written
    ${msg_json}=    Set Variable    [HEALTH]   JSON: ${json_path}
    ${msg_md}=    Set Variable    [HEALTH]   MD:   ${md_path}
    Log    ${msg_report}    INFO
    Log    ${msg_json}    INFO
    Log    ${msg_md}    INFO
