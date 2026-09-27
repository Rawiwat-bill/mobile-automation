*** Settings ***
Documentation    Optional app-update prompt handling for the common onboarding path.
Library          AppiumLibrary
Resource         ../../../locators/android/common_onboarding/app_update_prompt_locators.resource
Resource         ../../../locators/android/common_onboarding/landing_screen_locators.resource
Resource         ../../../resources/keywords/appium_expectations.resource


*** Variables ***
${APP_UPDATE_PROMPT_PROBE_TIMEOUT}       2s
${APP_UPDATE_PROMPT_ACTION_TIMEOUT}      5s
${APP_UPDATE_PROMPT_TRANSITION_TIMEOUT}  10s


*** Keywords ***
Dismiss Optional App Update Prompt If Visible
    [Documentation]    Dismiss only the owner-approved optional RGI-109 update branch by choosing Maybe later.
    ${rgi109_visible}=    Run Keyword And Return Status
    ...    Wait Until Element Is Visible    ${APP_UPDATE_RGI109_CODE}    ${APP_UPDATE_PROMPT_PROBE_TIMEOUT}
    IF    not ${rgi109_visible}
        RETURN
    END

    Wait Until Element Is Visible    ${APP_UPDATE_MAYBE_LATER_BUTTON}    ${APP_UPDATE_PROMPT_ACTION_TIMEOUT}
    ${update_app_visible}=    Run Keyword And Return Status
    ...    Element Should Be Visible Now    ${APP_UPDATE_UPDATE_APP_BUTTON}
    IF    ${update_app_visible}
        Log    APP_UPDATE_PROMPT_RGI109_UPDATE_APP_PRESENT=TRUE    INFO
    END

    Click Element    ${APP_UPDATE_MAYBE_LATER_BUTTON}
    Wait Until Keyword Succeeds
    ...    ${APP_UPDATE_PROMPT_TRANSITION_TIMEOUT}
    ...    250ms
    ...    App Update Prompt Should Be Gone
    Log    APP_UPDATE_PROMPT_DISMISSED=RGI-109_ACTION_MAYBE_LATER    INFO

Resolve Optional App Update Or Destination
    [Documentation]    Race the expected destination against exact RGI-109 and known Landing blockers without blind sleeps.
    [Arguments]    ${destination_locator}    ${timeout}
    ${observed}=    Run Keyword And Return Status
    ...    Wait Until Keyword Succeeds
    ...    ${timeout}
    ...    500ms
    ...    App Update Destination Or Blocker Should Be Visible
    ...    ${destination_locator}
    IF    not ${observed}
        Fail    APP_UPDATE_OR_DESTINATION_NOT_OBSERVED
    END

    # A mandatory update wins over a stale/overlapping destination marker.
    # Never let a destination element mask RGI-107.
    ${rgi107_visible}=    Run Keyword And Return Status
    ...    Element Should Be Visible Now    ${APP_UPDATE_RGI107_CODE}
    IF    ${rgi107_visible}
        Fail    APP_UPDATE_REQUIRED_RGI_107
    END

    ${destination_visible}=    Run Keyword And Return Status
    ...    Element Should Be Visible Now    ${destination_locator}
    IF    ${destination_visible}
        RETURN    DESTINATION_READY
    END

    ${rgi109_visible}=    Run Keyword And Return Status
    ...    Element Should Be Visible Now    ${APP_UPDATE_RGI109_CODE}
    ${popup_visible}=    Run Keyword And Return Status
    ...    Element Should Be Visible Now    ${LANDING_POPUP_GUB_CONTAINER}
    IF    ${popup_visible} and not ${rgi109_visible}
        ${rgi109_visible}=    Run Keyword And Return Status
        ...    Wait Until Element Is Visible
        ...    ${APP_UPDATE_RGI109_CODE}
        ...    ${APP_UPDATE_PROMPT_PROBE_TIMEOUT}
    END

    IF    ${rgi109_visible}
        Dismiss Optional App Update Prompt If Visible
        RETURN    UPDATE_DISMISSED
    END

    RETURN    BLOCKER_READY

App Update Destination Or Blocker Should Be Visible
    [Documentation]    Read-only terminal poll for destination, delayed RGI-109, offline, pop-up Gub, or full-screen Gub.
    [Arguments]    ${destination_locator}
    ${destination_visible}=    Run Keyword And Return Status
    ...    Element Should Be Visible Now    ${destination_locator}
    ${rgi109_visible}=    Run Keyword And Return Status
    ...    Element Should Be Visible Now    ${APP_UPDATE_RGI109_CODE}
    ${rgi107_visible}=    Run Keyword And Return Status
    ...    Element Should Be Visible Now    ${APP_UPDATE_RGI107_CODE}
    ${offline_visible}=    Run Keyword And Return Status
    ...    Element Should Be Visible Now    ${LANDING_OFFLINE_MESSAGE}
    ${popup_visible}=    Run Keyword And Return Status
    ...    Element Should Be Visible Now    ${LANDING_POPUP_GUB_CONTAINER}
    ${full_screen_visible}=    Run Keyword And Return Status
    ...    Element Should Be Visible Now    ${LANDING_FULL_SCREEN_GUB_CTA}
    Should Be True
    ...    ${destination_visible} or ${rgi109_visible} or ${rgi107_visible} or ${offline_visible} or ${popup_visible} or ${full_screen_visible}

App Update Prompt Should Be Gone
    ${rgi109_visible}=    Run Keyword And Return Status
    ...    Element Should Be Visible Now    ${APP_UPDATE_RGI109_CODE}
    ${maybe_later_visible}=    Run Keyword And Return Status
    ...    Element Should Be Visible Now    ${APP_UPDATE_MAYBE_LATER_BUTTON}
    Should Not Be True
    ...    ${rgi109_visible} or ${maybe_later_visible}
    ...    APP_UPDATE_PROMPT_RGI109_DID_NOT_CLOSE
