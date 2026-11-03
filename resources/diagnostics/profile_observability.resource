*** Settings ***
Documentation    Profile diagnostic/evidence adapter. Page resources call semantic keywords here instead of persisting evidence directly.
Library          AppiumLibrary
Library          OperatingSystem
Library          ../../libraries/profile_exit_evidence.py
Resource         ../app/app_constants.resource
Resource         etb_observability.resource


*** Variables ***
${PROFILE_INVESTIGATION_DIR}    reports/investigation/profile
${PROFILE_DEBUG_PANEL_BUTTON}    xpath=//*[@content-desc="Open debug panel"]


*** Keywords ***
Capture Profile Handoff Snapshot Evidence
    [Arguments]    ${snapshot_name}
    Record ETB Evidence Capture    ${OUTPUT DIR}    profile_${snapshot_name}
    Log    [PROFILE] Handoff snapshot requested through shared private adapter: ${snapshot_name}

Capture Profile Debug Panel Evidence Implementation
    [Arguments]    ${snapshot_name}
    Wait Until Element Is Visible    ${PROFILE_DEBUG_PANEL_BUTTON}    ${PROFILE_TIMEOUT}
    Click Element    ${PROFILE_DEBUG_PANEL_BUTTON}
    Capture Profile Handoff Snapshot Evidence    ${snapshot_name}

Record Profile Exit Evidence Point
    [Arguments]    ${point_name}
    Persist Profile Exit Point    ${point_name}    ${OUTPUT DIR}

Record Profile Exit Evidence Summary
    [Arguments]    ${transition_result}
    ${appium_library}=    Get Library Instance    AppiumLibrary
    ${package}=    Evaluate    $appium_library._current_application().current_package
    ${activity}=    Get Activity
    Persist Profile Exit Evidence Summary    ${OUTPUT DIR}    ${transition_result}    ${package}    ${activity}
