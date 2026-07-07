*** Settings ***
Documentation    Sprint 2.32.1 — Manual vs Automation Parity Investigation
...              Tests why Profile → Next fails in automation but works manually
Library    AppiumLibrary
Library    OperatingSystem
Library    Process
Library    Collections
Resource   ../../resources/app/app_keywords.resource
Resource   ../../resources/pages/onboarding/landing_screen_page.resource
Resource   ../../resources/pages/onboarding/consent_screen_page.resource
Resource   ../../resources/pages/onboarding/profile_screen_page.resource
Resource   ../../resources/keywords/onboarding_common.resource
Library    ../../libraries/config_loader.py

*** Variables ***
${BASE}       reports/investigation/manual_vs_automation
${TESTDATA}   testdata/onboarding/ntb.local.yaml

*** Keywords ***
Save Evidence
    [Arguments]    ${folder}    ${label}
    ${dir}=    Set Variable    ${BASE}/${folder}
    Create Directory    ${dir}
    ${source}=    Get Source
    Create File    ${dir}/${label}.xml    ${source}    UTF-8
    Run Process    sh    -c    adb exec-out screencap -p > ${dir}/${label}.png
    Log    [EVIDENCE] Saved ${folder}/${label}

Read Field Values
    ${cid}=    Get Text    ${PROFILE_CITIZEN_ID_INPUT}
    ${dob}=    Get Text    ${PROFILE_DOB_INPUT}
    ${mobile}=    Get Text    ${PROFILE_MOBILE_NUMBER_INPUT}
    ${cid_focused}=    Get Element Attribute    ${PROFILE_CITIZEN_ID_INPUT}    focused
    ${dob_focused}=    Get Element Attribute    ${PROFILE_DOB_INPUT}    focused
    ${mobile_focused}=    Get Element Attribute    ${PROFILE_MOBILE_NUMBER_INPUT}    focused
    ${next_rect}=    Get Element Rect    ${PROFILE_NEXT_BUTTON_CONTAINER}
    ${center_x}=    Evaluate    int(${next_rect['x']} + (${next_rect['width']} / 2))
    ${center_y}=    Evaluate    int(${next_rect['y']} + (${next_rect['height']} / 2))
    Log    [STATE] CID="${cid}" focused=${cid_focused}    WARN
    Log    [STATE] DOB="${dob}" focused=${dob_focused}    WARN
    Log    [STATE] Mobile="${mobile}" focused=${mobile_focused}    WARN
    Log    [STATE] Next button: x=${next_rect['x']} y=${next_rect['y']} w=${next_rect['width']} h=${next_rect['height']}    WARN
    Log    [STATE] Next center: ${center_x},${center_y}    WARN
    ${all}=    Create List    ${cid}    ${dob}    ${mobile}    ${cid_focused}    ${dob_focused}    ${mobile_focused}    ${center_x}    ${center_y}
    RETURN    ${all}

Navigate To Profile
    Open Mobile Application
    ${previous_log_level}=    Set Log Level    NONE
    ${data}=    Load YAML    ${TESTDATA}
    Set Log Level    ${previous_log_level}
    Wait Until Landing Screen Is Displayed
    Tap Landing Ready Button
    Allow Android Permission If Visible
    Wait Until Consent Screen Is Displayed
    Tap Consent Accept Button
    Wait Until Profile Screen Is Displayed
    [Return]    ${data}

Fill Profile Fields
    [Arguments]    ${data}
    Input Citizen ID    ${data['profile']['citizen_id']}
    Input Date Of Birth    ${data['profile']['date_of_birth']}
    Input Mobile Number    ${data['profile']['mobile_number']}

Check Result
    [Arguments]    ${folder}
    Sleep    8s
    Save Evidence    ${folder}    after_next
    ${has_profile}=    Run Keyword And Return Status
    ...    Page Should Contain Element    ${PROFILE_TITLE_TEXT}
    ${has_pdpa}=    Run Keyword And Return Status
    ...    Page Should Contain Element    accessibility_id=Personal data consent
    Log    [RESULT] ${folder}: Profile=${has_profile} PDPA=${has_pdpa}    WARN
    RETURN    ${has_pdpa}

*** Test Cases ***
Scenario C — Hide Keyboard Wait Then Next
    Create Directory    ${BASE}
    ${data}=    Navigate To Profile
    Fill Profile Fields    ${data}
    Save Evidence    01_before_next    state_before
    ${fields}=    Read Field Values

    # Scenario C: Hide keyboard, tap outside, wait
    Run Keyword And Ignore Error    Hide Keyboard
    Tap Profile Blank Area    ${PROFILE_BLUR_AFTER_MOBILE_Y}
    Sleep    3s
    Save Evidence    04_hide_keyboard    before_next
    ${fields2}=    Read Field Values

    # Tap Next via adb
    Tap Profile Next Using Adb
    ${reached_pdpa}=    Check Result    04_hide_keyboard
    Run Keyword If    ${reached_pdpa}    Log    [RESULT] *** SCENARIO C PASSED — reached PDPA ***    WARN
    Close Application

Scenario E — Verify Field Values
    Create Directory    ${BASE}
    ${data}=    Navigate To Profile
    Fill Profile Fields    ${data}

    # Read actual values
    ${cid}=    Get Text    ${PROFILE_CITIZEN_ID_INPUT}
    ${dob}=    Get Text    ${PROFILE_DOB_INPUT}
    ${mobile}=    Get Text    ${PROFILE_MOBILE_NUMBER_INPUT}

    # Normalize and compare
    ${cid_digits}=    Replace String Using Regexp    ${cid}    [^0-9]    ${EMPTY}
    ${mobile_digits}=    Replace String Using Regexp    ${mobile}    [^0-9]    ${EMPTY}
    ${expected_cid}=    Set Variable    ${data['profile']['citizen_id']}
    ${expected_mobile}=    Set Variable    ${data['profile']['mobile_number']}

    Log    [VERIFY] CID: actual="${cid_digits}" expected="${expected_cid}" match=${cid_digits}==${expected_cid}    WARN
    Log    [VERIFY] DOB: actual="${dob}"    WARN
    Log    [VERIFY] Mobile: actual="${mobile_digits}" expected="${expected_mobile}" match=${mobile_digits}==${expected_mobile}    WARN

    # Check DOB contains day and year from test data
    ${parts}=    Split String    ${data['profile']['date_of_birth']}    -
    ${day}=    Set Variable    ${parts[0]}
    ${year}=    Set Variable    ${parts[2]}
    ${dob_has_day}=    Run Keyword And Return Status    Should Contain    ${dob}    ${day}
    ${dob_has_year}=    Run Keyword And Return Status    Should Contain    ${dob}    ${year}
    Log    [VERIFY] DOB has day=${day}: ${dob_has_day}, year=${year}: ${dob_has_year}    WARN

    Save Evidence    06_field_verification    verification
    Close Application
