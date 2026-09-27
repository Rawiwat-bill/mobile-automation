*** Settings ***
Documentation    Semantic ETB observability adapter. Business flows call these keywords instead of evidence libraries directly.
Library          ../../libraries/visual_timeline.py
Library          ../../libraries/etb_readiness_evidence.py
Library          ../../libraries/failure_evidence.py
Resource         ../contracts/flow_states.resource


*** Keywords ***
Record ETB Readiness Blocker
    [Arguments]    ${output_dir}    ${blocker_code}    ${dopa_reached}
    Persist ETB Readiness Summary
    ...    ${output_dir}
    ...    blocker_code=${blocker_code}
    ...    profile_handoff=PASS
    ...    dopa_reached=${dopa_reached}

Record ETB Registration Success Visible
    [Arguments]    ${output_dir}
    Run Keyword And Ignore Error
    ...    Record Visual Timeline Event
    ...    SUCCESS0_VISIBLE
    ...    ${FLOW_STATE_REGISTRATION_SUCCESS}
    ...    ${output_dir}/visual_timeline

Record ETB Registration Continue Start
    [Arguments]    ${output_dir}
    Run Keyword And Ignore Error
    ...    Record Visual Timeline Event
    ...    SUCCESS1_CONTINUE_ACTION_START
    ...    ${FLOW_STATE_REGISTRATION_SUCCESS}
    ...    ${output_dir}/visual_timeline
    ...    action=CLICK_SUCCESS_LETS_GO
    ...    screenshot=${False}

Record ETB Registration Continue End
    [Arguments]    ${output_dir}
    Run Keyword And Ignore Error
    ...    Record Visual Timeline Event
    ...    SUCCESS1_CONTINUE_ACTION_END
    ...    ${FLOW_STATE_REGISTRATION_SUCCESS}
    ...    ${output_dir}/visual_timeline
    ...    action=CLICK_SUCCESS_LETS_GO_COMPLETED
    ...    screenshot=${False}

Record ETB Post Success State
    [Arguments]    ${output_dir}
    Run Keyword And Ignore Error    Record Post Success Visual State    ${output_dir}/visual_timeline


Record ETB Evidence Capture
    [Arguments]    ${output_dir}    ${stem}
    ${call_status}    ${result}=    Run Keyword And Ignore Error    Capture ETB Failure Evidence    ${output_dir}    ${stem}
    IF    '${call_status}' != 'PASS'
        Log    AUTOMATION_EVIDENCE_OPERATION_FAILED=${stem}    WARN
        RETURN    ${NONE}
    END
    IF    '${result['capture_status']}' != 'COMPLETE'
        Log    AUTOMATION_EVIDENCE_CAPTURE_STATUS=${stem}:${result['capture_status']}    WARN
    END
    RETURN    ${result}

Record ETB Device Terminal Evidence
    [Arguments]    ${output_dir}    ${stem}    ${serial}
    ${call_status}    ${result}=    Run Keyword And Ignore Error
    ...    Capture ETB Device Terminal Evidence    ${output_dir}    ${stem}    ${serial}
    IF    '${call_status}' != 'PASS'
        Log    AUTOMATION_TERMINAL_EVIDENCE_OPERATION_FAILED=${stem}    WARN
    END
    RETURN    ${result}
