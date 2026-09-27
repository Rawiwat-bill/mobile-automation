*** Settings ***
Library    Collections
Library    OperatingSystem
Library    ../../libraries/failure_evidence.py

*** Variables ***
${STABILITY_DIR}    ${OUTPUT_DIR}/stability
${DOB_STABILITY_FILE}    ${STABILITY_DIR}/stability.json
@{DOB_PICKER_ATTEMPTS}

*** Keywords ***
Initialize DOB Stability Tracking
    Set Suite Variable    @{DOB_PICKER_ATTEMPTS}
    Set Suite Variable    ${DOB_INTERACTION_START}    ${NONE}
    Set Suite Variable    ${DOB_PICKER_VISIBLE}    ${NONE}
    Set Suite Variable    ${DOB_YEAR_START}    ${NONE}
    Set Suite Variable    ${DOB_MONTH_START}    ${NONE}
    Set Suite Variable    ${DOB_DAY_START}    ${NONE}
    Set Suite Variable    ${DOB_YEAR_ELAPSED}    ${NONE}
    Set Suite Variable    ${DOB_MONTH_ELAPSED}    ${NONE}
    Set Suite Variable    ${DOB_DAY_ELAPSED}    ${NONE}
    Set Suite Variable    ${DOB_SUCCESS}    ${FALSE}
    Set Suite Variable    ${DOB_FAILURE_REASON}    ${NONE}
    Set Suite Variable    ${DOB_RETRY_COUNT}    0

Start DOB Interaction
    ${start}=    Evaluate    __import__('time').time()
    Set Suite Variable    ${DOB_INTERACTION_START}    ${start}

Record DOB Picker Visible
    ${now}=    Evaluate    __import__('time').time()
    Set Suite Variable    ${DOB_PICKER_VISIBLE}    ${now}

Record DOB Year Start
    ${now}=    Evaluate    __import__('time').time()
    Set Suite Variable    ${DOB_YEAR_START}    ${now}

Record DOB Year End
    ${now}=    Evaluate    __import__('time').time()
    ${start}=    Set Variable    ${DOB_YEAR_START}
    ${elapsed}=    Evaluate    round(${now} - ${start}, 3)
    Set Suite Variable    ${DOB_YEAR_ELAPSED}    ${elapsed}

Record DOB Month Start
    ${now}=    Evaluate    __import__('time').time()
    Set Suite Variable    ${DOB_MONTH_START}    ${now}

Record DOB Month End
    ${now}=    Evaluate    __import__('time').time()
    ${start}=    Set Variable    ${DOB_MONTH_START}
    ${elapsed}=    Evaluate    round(${now} - ${start}, 3)
    Set Suite Variable    ${DOB_MONTH_ELAPSED}    ${elapsed}

Record DOB Day Start
    ${now}=    Evaluate    __import__('time').time()
    Set Suite Variable    ${DOB_DAY_START}    ${now}

Record DOB Day End
    ${now}=    Evaluate    __import__('time').time()
    ${start}=    Set Variable    ${DOB_DAY_START}
    ${elapsed}=    Evaluate    round(${now} - ${start}, 3)
    Set Suite Variable    ${DOB_DAY_ELAPSED}    ${elapsed}

Record DOB Picker Attempt
    [Arguments]    ${picker_kind}    ${target_value}    ${current_value}    ${direction}
    ${attempt}=    Create Dictionary
    ...    picker=${picker_kind}
    ...    target=${target_value}
    ...    current=${current_value}
    ...    direction=${direction}
    Append To List    ${DOB_PICKER_ATTEMPTS}    ${attempt}

Record DOB Success
    Set Suite Variable    ${DOB_SUCCESS}    ${TRUE}
    ${end}=    Evaluate    __import__('time').time()
    Set Suite Variable    ${DOB_INTERACTION_END}    ${end}

Record DOB Failure
    [Arguments]    ${picker_kind}    ${target_value}    ${reason}
    Set Suite Variable    ${DOB_SUCCESS}    ${FALSE}
    Set Suite Variable    ${DOB_FAILURE_REASON}    ${picker_kind}=${target_value}: ${reason}
    ${end}=    Evaluate    __import__('time').time()
    Set Suite Variable    ${DOB_INTERACTION_END}    ${end}

Capture DOB Failure Evidence
    [Arguments]    ${picker_kind}    ${target_value}
    Run Keyword And Ignore Error
    ...    Capture ETB Failure Evidence
    ...    ${OUTPUT DIR}
    ...    dob_${picker_kind}_${target_value}

Generate DOB Stability Report
    ${now}=    Evaluate    __import__('time').time()
    ${ts}=    Evaluate    __import__('time').strftime('%Y%m%d_%H%M%S')
    ${start_time}=    Get Variable Value    ${DOB_INTERACTION_START}    0
    ${end_time}=    Get Variable Value    ${DOB_INTERACTION_END}    0
    ${total_elapsed}=    Set Variable    ${0}
    IF    ${start_time} != 0 and ${end_time} != 0
        ${total_elapsed}=    Evaluate    round(${end_time} - ${start_time}, 3)
    END
    ${attempt_count}=    Get Length    ${DOB_PICKER_ATTEMPTS}
    ${success}=    Get Variable Value    ${DOB_SUCCESS}    ${FALSE}
    ${fail_reason}=    Get Variable Value    ${DOB_FAILURE_REASON}    ${NONE}
    ${year_elapsed}=    Get Variable Value    ${DOB_YEAR_ELAPSED}    ${NONE}
    ${month_elapsed}=    Get Variable Value    ${DOB_MONTH_ELAPSED}    ${NONE}
    ${day_elapsed}=    Get Variable Value    ${DOB_DAY_ELAPSED}    ${NONE}
    ${run}=    Create Dictionary
    ...    timestamp=${ts}
    ...    success=${success}
    ...    total_elapsed=${total_elapsed}
    ...    year_elapsed=${year_elapsed}
    ...    month_elapsed=${month_elapsed}
    ...    day_elapsed=${day_elapsed}
    ...    retry_count=${attempt_count}
    ...    failure_reason=${fail_reason}
    Create Directory    ${STABILITY_DIR}
    ${existing}=    Run Keyword And Return Status    File Should Exist    ${DOB_STABILITY_FILE}
    ${runs}=    Create List
    IF    ${existing}
        ${raw}=    Get File    ${DOB_STABILITY_FILE}    UTF-8
        ${data}=    Evaluate    __import__('json').loads($raw)
        ${runs}=    Set Variable    ${data['runs']}
    END
    Append To List    ${runs}    ${run}
    ${pass_count}=    Evaluate    sum(1 for r in $runs if r['success'])
    ${total_count}=    Get Length    ${runs}
    ${pass_rate}=    Evaluate    round(${pass_count} / ${total_count} * 100, 1) if ${total_count} > 0 else 0
    ${avg_time}=    Evaluate    round(sum(r['total_elapsed'] if isinstance(r['total_elapsed'], (int, float)) else 0 for r in $runs) / ${total_count}, 3) if ${total_count} > 0 else 0
    ${avg_retry}=    Evaluate    round(sum(r['retry_count'] for r in $runs) / ${total_count}, 1) if ${total_count} > 0 else 0
    ${dob_summary}=    Create Dictionary
    ...    runs=${total_count}
    ...    pass=${pass_count}
    ...    fail=${total_count - ${pass_count}}
    ...    pass_rate=${pass_rate}
    ...    avg_time=${avg_time}
    ...    avg_retry=${avg_retry}
    ${report}=    Create Dictionary
    ...    dob_picker=${dob_summary}
    ...    runs=${runs}
    ${json}=    Evaluate    __import__('json').dumps($report, indent=2)
    Create File    ${DOB_STABILITY_FILE}    ${json}
