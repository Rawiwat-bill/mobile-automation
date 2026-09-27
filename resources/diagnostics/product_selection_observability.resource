*** Settings ***
Documentation    Product Selection semantic visual-timeline adapter.
Library          ../../libraries/visual_timeline.py
Resource         ../contracts/flow_states.resource


*** Keywords ***
Record Product Selection Visible
    [Arguments]    ${output_dir}
    Run Keyword And Ignore Error    Record Visual Timeline Event    PS0_PRODUCT_SELECTION_VISIBLE    ${FLOW_STATE_PRODUCT_SELECTION}    ${output_dir}/visual_timeline

Record Product Selection Rows Available
    [Arguments]    ${output_dir}
    Run Keyword And Ignore Error    Record Visual Timeline Event    PS1_ROWS_AVAILABLE    ${FLOW_STATE_PRODUCT_SELECTION}    ${output_dir}/visual_timeline    screenshot=${False}

Record Product Selection State
    [Arguments]    ${output_dir}
    Run Keyword And Ignore Error    Record Visual Timeline Event    PS2_SELECTION_STATE    ${FLOW_STATE_PRODUCT_SELECTION}    ${output_dir}/visual_timeline

Record Product Selection Action Start
    [Arguments]    ${output_dir}
    Run Keyword And Ignore Error    Record Visual Timeline Event    PS3_SELECTION_ACTION_START    ${FLOW_STATE_PRODUCT_SELECTION}    ${output_dir}/visual_timeline    action=SELECT_FIRST_ENABLED

Record Product Selection Action End
    [Arguments]    ${output_dir}
    Run Keyword And Ignore Error    Record Visual Timeline Event    PS3_SELECTION_ACTION    ${FLOW_STATE_PRODUCT_SELECTION}    ${output_dir}/visual_timeline    action=SELECT_FIRST_ENABLED_COMPLETED

Record Product Selection Confirm Available
    [Arguments]    ${output_dir}
    Run Keyword And Ignore Error    Record Visual Timeline Event    PS4_CONFIRM_AVAILABLE    ${FLOW_STATE_PRODUCT_SELECTION}    ${output_dir}/visual_timeline    screenshot=${False}

Record Product Selection Confirm Start
    [Arguments]    ${output_dir}
    Run Keyword And Ignore Error    Record Visual Timeline Event    CONFIRM_CLICK_START    ${FLOW_STATE_PRODUCT_SELECTION}    ${output_dir}/visual_timeline    action=CLICK_CONFIRM    screenshot=${False}

Record Product Selection Confirm End
    [Arguments]    ${output_dir}
    Run Keyword And Ignore Error    Record Visual Timeline Event    PS5_CONFIRM_CLICK_END    ${FLOW_STATE_LOADING_OR_INTERMEDIATE}    ${output_dir}/visual_timeline    action=CLICK_CONFIRM_COMPLETED
