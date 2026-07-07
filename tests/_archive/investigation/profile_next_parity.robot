*** Settings ***
Documentation    Sprint 2.32.1 — Profile Next Parity Check
Library    AppiumLibrary
Library    OperatingSystem
Library    Process
Resource   ../../resources/app/app_keywords.resource
Resource   ../../resources/pages/onboarding/landing_screen_page.resource
Resource   ../../resources/pages/onboarding/consent_screen_page.resource
Resource   ../../resources/pages/onboarding/profile_screen_page.resource
Resource   ../../resources/keywords/onboarding_common.resource
Library    ../../libraries/config_loader.py

*** Variables ***
${DIR}    reports/investigation/manual_vs_automation

*** Test Cases ***
Profile Next Parity Check
    Create Directory    ${DIR}/01_before_next

    Open Mobile Application
    ${prev}=    Set Log Level    NONE
    ${data}=    Load YAML    testdata/onboarding/ntb.local.yaml
    Set Log Level    ${prev}

    # Navigate to Profile
    Wait Until Landing Screen Is Displayed
    Tap Landing Ready Button
    Allow Android Permission If Visible
    Wait Until Consent Screen Is Displayed
    Tap Consent Accept Button
    Wait Until Profile Screen Is Displayed

    # Fill fields
    Input Citizen ID    ${data['profile']['citizen_id']}
    Input Date Of Birth    ${data['profile']['date_of_birth']}
    Input Mobile Number    ${data['profile']['mobile_number']}

    # === CAPTURE STATE BEFORE NEXT ===
    ${cid}=    Get Text    xpath=//*[@resource-id="cid"]
    ${dob}=    Get Text    xpath=//*[@resource-id="screenProfile_textInputDob"]
    ${mobile}=    Get Text    xpath=//*[@resource-id="screenProfile_textInputMobileNumber"]
    ${cid_focus}=    Get Element Attribute    xpath=//*[@resource-id="cid"]    focused
    ${dob_focus}=    Get Element Attribute    xpath=//*[@resource-id="screenProfile_textInputDob"]    focused
    ${mob_focus}=    Get Element Attribute    xpath=//*[@resource-id="screenProfile_textInputMobileNumber"]    focused

    Log    [STATE] CID="${cid}" focus=${cid_focus}    WARN
    Log    [STATE] DOB="${dob}" focus=${dob_focus}    WARN
    Log    [STATE] Mobile="${mobile}" focus=${mob_focus}    WARN

    # Check Next button state
    ${next_rect}=    Get Element Rect    xpath=//*[@resource-id="screenProfile_buttonNext"]
    ${cx}=    Evaluate    int(${next_rect['x']} + (${next_rect['width']} / 2))
    ${cy}=    Evaluate    int(${next_rect['y']} + (${next_rect['height']} / 2))
    Log    [STATE] Next bounds: x=${next_rect['x']} y=${next_rect['y']} w=${next_rect['width']} h=${next_rect['height']}    WARN
    Log    [STATE] Next tap point: ${cx},${cy}    WARN

    # Save XML + screenshot before Next
    ${src}=    Get Source
    Create File    ${DIR}/01_before_next/before_next.xml    ${src}    UTF-8
    Run Process    sh    -c    adb exec-out screencap -p > ${DIR}/01_before_next/before_next.png

    # === SCENARIO C: Hide keyboard + blur + wait ===
    Run Keyword And Ignore Error    Hide Keyboard
    Tap Profile Blank Area    1600
    Sleep    3s

    # Re-read focus state after blur
    ${cid_focus2}=    Get Element Attribute    xpath=//*[@resource-id="cid"]    focused
    ${dob_focus2}=    Get Element Attribute    xpath=//*[@resource-id="screenProfile_textInputDob"]    focused
    ${mob_focus2}=    Get Element Attribute    xpath=//*[@resource-id="screenProfile_textInputMobileNumber"]    focused
    Log    [STATE-AFTER-BLUR] CID focus=${cid_focus2} DOB focus=${dob_focus2} Mobile focus=${mob_focus2}    WARN

    # Tap Next via adb
    Log    [ACTION] Tapping Next at ${cx},${cy}    WARN
    Run Process    adb    shell    input    tap    ${cx}    ${cy}

    # Wait and check result
    Sleep    10s
    ${src2}=    Get Source
    Create File    ${DIR}/01_before_next/after_next.xml    ${src2}    UTF-8
    Run Process    sh    -c    adb exec-out screencap -p > ${DIR}/01_before_next/after_next.png

    # Check what screen we're on
    ${has_profile}=    Run Keyword And Return Status    Page Should Contain Element    xpath=//*[@text="Tell us about you"]
    ${has_pdpa}=    Run Keyword And Return Status    Page Should Contain Element    accessibility_id=Personal data consent
    ${has_landing}=    Run Keyword And Return Status    Page Should Contain Text    A new view to make sense

    Log    [RESULT] Profile=${has_profile} PDPA=${has_pdpa} Landing=${has_landing}    WARN

    Close Application
