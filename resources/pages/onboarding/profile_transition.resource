*** Settings ***
Documentation    Profile transition interaction and classification.
Library          AppiumLibrary
Library          Collections
Library          String
Resource         ../../contracts/flow_states.resource
Resource         ../../diagnostics/profile_observability.resource
Resource         profile_fields.resource
Resource         ../../../locators/android/onboarding/profile_screen_locators.resource
Resource         ../../../locators/android/etb/check_dopa_fill_laser_code_locators.resource
Resource         ../../../locators/android/etb/rgi_popup_locators.resource
Resource         ../../../locators/android/etb/full_screen_rgi_locators.resource
Resource         ../../app/app_constants.resource
Resource         ../../keywords/appium_expectations.resource


*** Keywords ***
Capture Profile Handoff Snapshot
    [Arguments]    ${snapshot_name}
    Capture Profile Handoff Snapshot Evidence    ${snapshot_name}

Capture Profile Debug Panel Evidence
    [Arguments]    ${snapshot_name}
    Capture Profile Debug Panel Evidence Implementation    ${snapshot_name}

Tap Profile Next Using Adb
    ${element_rect}=    Get Element Rect    ${PROFILE_NEXT_BUTTON_CONTAINER}
    ${center_x}=    Evaluate    int(${element_rect['x']} + (${element_rect['width']} / 2))
    ${center_y}=    Evaluate    int(${element_rect['y']} + (${element_rect['height']} / 2))
    Execute Adb Shell    input    tap    ${center_x}    ${center_y}
    Log    [PROFILE] Next tapped via adb shell at ${center_x},${center_y}

Tap Profile Next Button
    Log    [PROFILE] Profile fields completed
    Run Keyword And Ignore Error    Hide Keyboard
    Log    [PROFILE] Keyboard hidden
    Wait Until Profile Fields Are Blurred
    Wait Until Element Is Visible    ${PROFILE_NEXT_BUTTON_CONTAINER}    ${PROFILE_TIMEOUT}
    ${next_visible}=    Run Keyword And Return Status    Element Should Be Visible Now    ${PROFILE_NEXT_BUTTON_CONTAINER}
    ${next_enabled}=    Run Keyword And Return Status    Element Should Be Enabled    ${PROFILE_NEXT_BUTTON_CONTAINER}
    Log    [PROFILE] Next visible/enabled: ${next_visible}/${next_enabled}
    ${source_before_next}=    Get Source
    Run Keyword And Ignore Error    Capture Profile Exit Evidence Point From Active Session    P0_before_profile_next
    Tap Profile Next Using Adb
    Run Keyword And Ignore Error    Capture Profile Exit Evidence Point From Active Session    P1_after_profile_next
    ${transition_result}=    Wait Until Keyword Succeeds    ${NCBD_LOADING_TIMEOUT}    500ms
    ...    Observe Profile Next Transition    ${source_before_next}
    Run Keyword And Ignore Error    Capture Profile Exit Evidence Point From Active Session    P2_first_recognized_destination
    Run Keyword And Ignore Error    Write Profile Exit Evidence Summary    ${transition_result}
    RETURN    ${transition_result}

Capture Profile Exit Evidence Point
    [Arguments]    ${point_name}
    Record Profile Exit Evidence Point    ${point_name}

Capture Profile Exit Evidence Point From Active Session
    [Arguments]    ${point_name}
    Record Profile Exit Evidence Point    ${point_name}

Write Profile Exit Evidence Summary
    [Arguments]    ${transition_result}
    Record Profile Exit Evidence Summary    ${transition_result}

Read Visible Profile Error Codes
    [Arguments]    ${elements}
    ${codes}=    Create List
    FOR    ${element}    IN    @{elements}
        ${visible_status}=    Run Keyword And Return Status    Element Should Be Visible Now    ${element}
        IF    not ${visible_status}
            CONTINUE
        END
        ${text_status}    ${text}=    Run Keyword And Ignore Error    Get Element Attribute    ${element}    text
        IF    '${text_status}' == 'PASS'
            ${match_status}    ${matches}=    Run Keyword And Ignore Error
            ...    Get Regexp Matches    ${text}    (?:RGI|GOD|AJI|RAI)-[0-9]{3}
            IF    '${match_status}' == 'PASS'
                FOR    ${match}    IN    @{matches}
                    Append To List    ${codes}    ${match}
                END
            END
        END
        ${desc_status}    ${content_desc}=    Run Keyword And Ignore Error
        ...    Get Element Attribute    ${element}    content-desc
        IF    '${desc_status}' == 'PASS'
            ${match_status}    ${matches}=    Run Keyword And Ignore Error
            ...    Get Regexp Matches    ${content_desc}    (?:RGI|GOD|AJI|RAI)-[0-9]{3}
            IF    '${match_status}' == 'PASS'
                FOR    ${match}    IN    @{matches}
                    Append To List    ${codes}    ${match}
                END
            END
        END
    END
    ${codes}=    Remove Duplicates    ${codes}
    RETURN    ${codes}

Observe Profile Next Transition
    [Arguments]    ${source_before_next}
    ${source_after_next}=    Get Source
    ${popup_visible}=    Run Keyword And Return Status    Element Should Be Visible Now    ${RGI_POPUP_CONTAINER}
    IF    ${popup_visible}
        ${popup_lookup_status}    ${elements}=    Run Keyword And Ignore Error
        ...    Get WebElements    ${RGI_POPUP_CODE_ELEMENTS}
        IF    '${popup_lookup_status}' == 'PASS'
            ${codes}=    Read Visible Profile Error Codes    ${elements}
            ${count}=    Get Length    ${codes}
            IF    ${count} == 1
                RETURN    ${codes[0]}
            ELSE IF    ${count} > 1
                Fail    PROFILE_POPUP_CODE_AMBIGUOUS
            END
        END
        # Do not fall back to Get Text on a generic locator.  That read can
        # aggregate hidden descendants or return an exception string from a
        # stale lookup; only individually visible, successfully-read elements
        # are authoritative evidence of a popup code.
        Fail    PROFILE_POPUP_CODE_UNPROVEN
    END
    # The generic security-error-container is also present on normal DOPA and
    # Profile hierarchies. Prefer the screen-specific destination marker.
    ${dopa_visible}=    Run Keyword And Return Status
    ...    Element Should Be Visible Now    xpath=//*[@resource-id="screenPersonalInformation_navBarTitleList"]
    IF    ${dopa_visible}
        RETURN    ${FLOW_STATE_PROFILE_LEFT_OR_NEXT}
    END
    ${full_screen_visible}=    Run Keyword And Return Status
    ...    Element Should Be Visible Now    ${FULL_SCREEN_RGI_CONTAINER}
    IF    ${full_screen_visible}
        # Read only the active error container's descendants.  Do not search
        # the complete hierarchy, where hidden/unrelated codes can win.
        ${screen_lookup_status}    ${elements}=    Run Keyword And Ignore Error
        ...    Get WebElements    xpath=//*[@resource-id="security-error-container"]//*
        IF    '${screen_lookup_status}' == 'PASS'
            ${screen_codes}=    Read Visible Profile Error Codes    ${elements}
            ${screen_code_count}=    Get Length    ${screen_codes}
            IF    ${screen_code_count} == 1
                RETURN    ${screen_codes[0]}
            ELSE IF    ${screen_code_count} > 1
                Fail    PROFILE_FULL_SCREEN_CODE_AMBIGUOUS
            END
        END
        # Continue classification; the wrapper alone is not an error state.
    END
    ${profile_visible}=    Run Keyword And Return Status    Element Should Be Visible Now    ${PROFILE_TITLE_TEXT}
    IF    ${profile_visible}
        Fail    PROFILE_NEXT_DESTINATION_UNPROVEN_PROFILE_STILL_VISIBLE
    END
    Fail    PROFILE_NEXT_DESTINATION_UNPROVEN

Tap Profile Next
    ${transition_result}=    Tap Profile Next Button
    RETURN    ${transition_result}
