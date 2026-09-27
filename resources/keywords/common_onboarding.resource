*** Settings ***
Documentation    Canonical shared onboarding flow used by NTB and ETB.
...              Owns only the behavior common to both journeys: Landing, Terms, Profile, and Profile Next.
...              Product-specific continuation belongs to NTB/ETB flow resources.
Library          String
Resource         ../contracts/flow_states.resource
Resource         ../app/app_keywords.resource
Resource         ../pages/common_onboarding/landing_screen_page.resource
Resource         ../pages/common_onboarding/app_update_prompt_page.resource
Resource         ../pages/common_onboarding/terms_and_conditions_page.resource
Resource         ../pages/onboarding/profile_screen_page.resource
Resource         appium_expectations.resource


*** Keywords ***
Run Common Onboarding
    [Documentation]    Complete the shared Landing -> Terms -> Profile path.
    ...                Returns NEXT on a proven Profile transition, or the exact known backend/business code.
    [Arguments]    ${citizen_id}    ${date_of_birth}    ${mobile_number}    ${language}=UNCHANGED

    ${language_mode}=    Convert To Upper Case    ${language}
    Dismiss Optional App Update Prompt If Visible
    Wait Until Landing Screen Is Displayed
    IF    '${language_mode}' == 'ENGLISH'
        Switch Landing Language To English
    ELSE IF    '${language_mode}' == 'THAI'
        Switch Landing Language To Thai
    ELSE IF    '${language_mode}' != 'UNCHANGED'
        Fail    UNSUPPORTED_COMMON_ONBOARDING_LANGUAGE=${language}
    END

    Advance Landing To Terms Destination
    Ensure Terms Content Ready With Interim Navigation Retries
    Scroll Down Terms And Conditions
    ${terms_result}=    Accept Terms And Conditions
    IF    '${terms_result}' == '${FLOW_STATE_AJI_001}'
        RETURN    ${FLOW_STATE_AJI_001}
    END
    Should Be Equal As Strings    ${terms_result}    ${FLOW_STATE_NEXT}    COMMON_ONBOARDING_TERMS_DID_NOT_TRANSITION

    Wait Until Profile Screen Is Displayed
    Input Citizen ID    ${citizen_id}
    profile_screen_page.Input Date Of Birth    ${date_of_birth}
    Input Mobile Number    ${mobile_number}
    Verify Current Profile Fields Before Next    ${citizen_id}    ${date_of_birth}    ${mobile_number}
    ${profile_result}=    Tap Profile Next

    IF    '${profile_result}' == '${FLOW_STATE_GOD_013}'
        RETURN    ${FLOW_STATE_GOD_013}
    END
    IF    '${profile_result}' == '${FLOW_STATE_AJI_001}'
        RETURN    ${FLOW_STATE_AJI_001}
    END
    IF    '${profile_result}' == '${FLOW_STATE_RGI_104}'
        RETURN    ${FLOW_STATE_RGI_104}
    END
    ${terminal_code}=    Run Keyword And Return Status
    ...    Should Match Regexp    ${profile_result}    ^(?:RGI|GOD|AJI|RAI)-[0-9]{3}$
    IF    ${terminal_code}
        RETURN    ${profile_result}
    END
    Should Be Equal As Strings
    ...    ${profile_result}
    ...    ${FLOW_STATE_PROFILE_LEFT_OR_NEXT}
    ...    COMMON_ONBOARDING_PROFILE_DID_NOT_TRANSITION
    RETURN    ${FLOW_STATE_NEXT}

Advance Landing To Terms Destination
    [Documentation]    Use one canonical permission -> update/destination race -> Terms-shell sequence while allowing recovery to defer Landing disappearance to that race.
    [Arguments]    ${recovery_mode}=${FALSE}
    IF    ${recovery_mode}
        Tap Landing Ready Button For Destination Race
    ELSE
        Tap Landing Ready Button
    END
    Allow Android Permission If Visible
    ${ready_reappeared}=    Run Keyword And Return Status
    ...    Element Should Be Visible Now    ${LANDING_READY_BUTTON}
    IF    ${ready_reappeared}
        Log    LANDING_READY_REAPPEARED_AFTER_PERMISSION=TRUE    WARN
        Tap Landing Ready Button For Destination Race
    END
    ${update_resolution}=    Resolve Optional App Update Or Destination
    ...    ${TERMS_AND_CONDITIONS_WEBVIEW}
    ...    ${NCBD_LOADING_TIMEOUT}
    Log    APP_UPDATE_DESTINATION_RACE=${update_resolution}    INFO
    Wait For Landing Destination    ${TERMS_AND_CONDITIONS_WEBVIEW}    ${NCBD_LOADING_TIMEOUT}
    Wait Until Terms And Conditions Screen Is Displayed

Ensure Terms Content Ready With Interim Navigation Retries
    [Documentation]    Interim containment: retry the proven in-app Back -> Landing -> Terms navigation until hydrated content appears, bounded by ${TERMS_CONTENT_RECOVERY_MAX_ATTEMPTS} retries.
    ${status}    ${error}=    Run Keyword And Ignore Error    Wait Until Terms Content Is Ready
    IF    '${status}' == 'PASS'
        Log    TERMS_CONTENT_READY=INITIAL    INFO
        RETURN
    END
    IF    '${error}' != 'TERMS_CONTENT_NOT_RENDERED'
        Fail    ${error}
    END

    FOR    ${attempt}    IN RANGE    1    ${TERMS_CONTENT_RECOVERY_RANGE_END}
        Log    TERMS_CONTENT_READY=RETRY_NAVIGATION attempt=${attempt}/${TERMS_CONTENT_RECOVERY_MAX_ATTEMPTS}    WARN
        Tap Terms Back Button For Recovery
        Wait Until Landing Screen Is Displayed
        Sleep    ${TERMS_CONTENT_RECOVERY_LANDING_PAUSE}
        Advance Landing To Terms Destination    recovery_mode=${TRUE}
        ${status}    ${error}=    Run Keyword And Ignore Error    Wait Until Terms Content Is Ready
        IF    '${status}' == 'PASS'
            Log    TERMS_CONTENT_READY=RECOVERED attempt=${attempt}    INFO
            RETURN
        END
        IF    '${error}' != 'TERMS_CONTENT_NOT_RENDERED'
            Fail    ${error}
        END
    END

    Fail    TERMS_CONTENT_NOT_RENDERED_AFTER_${TERMS_CONTENT_RECOVERY_MAX_ATTEMPTS}_RECOVERY_ATTEMPTS
