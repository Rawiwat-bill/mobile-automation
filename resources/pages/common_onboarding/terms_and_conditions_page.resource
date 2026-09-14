*** Settings ***
Library     AppiumLibrary
Library     OperatingSystem
Library     ../../../libraries/evidence_scope.py
Resource    ../../../resources/app/app_constants.resource
Resource    ../../../resources/keywords/scroll_keywords.resource
Resource    ../../../locators/android/common_onboarding/tell_us_about_you_locators.resource
Resource    ../../../locators/android/common_onboarding/terms_and_conditions_locators.resource


*** Keywords ***
Wait Until Terms And Conditions Screen Is Displayed
    [Documentation]    Wait until the Terms and Conditions screen is displayed.
    Wait Until Element Is Visible    ${TERMS_AND_CONDITIONS_WEBVIEW}    ${NCBD_LOADING_TIMEOUT}

Scroll Down Terms And Conditions
    [Documentation]    Scroll Terms using the repository state-based React Native pattern.
    Scroll Down Consent Terms With Big Fling

Accept Terms And Conditions
    [Documentation]    Tap Accept with ADB first and use Appium only when navigation is not observed.
    Wait Until Element Is Visible    ${TERMS_AND_CONDITIONS_ACCEPT_BUTTON}    ${NCBD_LOADING_TIMEOUT}
    ${element_rect}=    Get Element Rect    ${TERMS_AND_CONDITIONS_ACCEPT_BUTTON}
    ${center_x}=    Evaluate    int(${element_rect['x']} + (${element_rect['width']} / 2))
    ${center_y}=    Evaluate    int(${element_rect['y']} + (${element_rect['height']} / 2))
    Execute Adb Shell    input    tap    ${center_x}    ${center_y}
    Log    [TERMS] Accept tapped via adb shell at ${center_x},${center_y}

    ${transition}=    Wait For Terms Transition Marker
    IF    '${transition}' == 'NEXT'
        RETURN    NEXT
    END
    IF    '${transition}' == 'AJI-001'
        RETURN    AJI-001
    END

    Log    [TERMS] Navigation not observed after ADB tap; trying Appium fallback.    WARN
    Run Keyword And Ignore Error    Click Element    ${TERMS_AND_CONDITIONS_ACCEPT_BUTTON}
    ${transition}=    Wait For Terms Transition Marker
    IF    '${transition}' == 'NEXT'
        RETURN    NEXT
    END
    IF    '${transition}' == 'AJI-001'
        RETURN    AJI-001
    END

    Capture Terms Transition Evidence
    Fail    TERMS_TRANSITION_NOT_OBSERVED

Wait For Terms Transition Marker
    [Documentation]    Return NEXT, AJI-001, or NOT_OBSERVED without treating Accept disappearance as success.
    ${observed}=    Run Keyword And Return Status
    ...    Wait Until Keyword Succeeds    5s    500ms    Terms Transition Marker Should Be Visible
    IF    not ${observed}
        RETURN    NOT_OBSERVED
    END
    ${source}=    Get Source
    ${aji}=    Run Keyword And Return Status    Should Contain    ${source}    AJI-001
    IF    ${aji}
        RETURN    AJI-001
    END
    RETURN    NEXT

Terms Transition Marker Should Be Visible
    ${next_visible}=    Run Keyword And Return Status
    ...    Element Should Be Visible    ${TELL_US_ABOUT_YOU_TITLE_TEXT}
    ${source}=    Get Source
    ${aji_visible}=    Run Keyword And Return Status    Should Contain    ${source}    AJI-001
    Should Be True    ${next_visible} or ${aji_visible}

Capture Terms Transition Evidence
    [Documentation]    Capture private-local runtime evidence for an unclassified Terms transition.
    ${stamp}=    Evaluate    __import__('time').strftime('%Y%m%d_%H%M%S')
    ${private_evidence_dir}=    Resolve Private Evidence Dir    ${OUTPUT DIR}
    ${evidence_dir}=    Set Variable    ${private_evidence_dir}/terms_transition_${stamp}
    Create Directory    ${evidence_dir}
    Run Keyword And Ignore Error    Capture Page Screenshot    ${evidence_dir}/screen.png
    ${source}=    Get Source
    Create File    ${evidence_dir}/page_source.xml    ${source}    UTF-8
    Log    [TERMS] Private-local runtime evidence captured.    INFO
