*** Settings ***
Documentation    Sprint 2.32.1 — Profile Next Parity (robust version)
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
Profile Next Parity
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
    Log    [FLOW] Reached Profile screen    WARN

    # Fill fields
    Input Citizen ID    ${data['profile']['citizen_id']}
    Input Date Of Birth    ${data['profile']['date_of_birth']}
    Input Mobile Number    ${data['profile']['mobile_number']}
    Log    [FLOW] All fields filled    WARN

    # === CAPTURE STATE ===
    ${cid}=    Get Text    xpath=//*[@resource-id="cid"]
    ${dob}=    Get Text    xpath=//*[@resource-id="screenProfile_textInputDob"]
    ${mobile}=    Get Text    xpath=//*[@resource-id="screenProfile_textInputMobileNumber"]
    ${cid_f}=    Get Element Attribute    xpath=//*[@resource-id="cid"]    focused
    ${dob_f}=    Get Element Attribute    xpath=//*[@resource-id="screenProfile_textInputDob"]    focused
    ${mob_f}=    Get Element Attribute    xpath=//*[@resource-id="screenProfile_textInputMobileNumber"]    focused

    Log    [STATE] CID="${cid}" focused=${cid_f}    WARN
    Log    [STATE] DOB="${dob}" focused=${dob_f}    WARN
    Log    [STATE] Mobile="${mobile}" focused=${mob_f}    WARN

    # Next button location
    ${rect}=    Get Element Rect    xpath=//*[@resource-id="screenProfile_buttonNext"]
    ${cx}=    Evaluate    int(${rect['x']} + (${rect['width']} / 2))
    ${cy}=    Evaluate    int(${rect['y']} + (${rect['height']} / 2))
    Log    [STATE] Next button: x=${rect['x']} y=${rect['y']} w=${rect['width']} h=${rect['height']}    WARN
    Log    [STATE] Next tap target: ${cx},${cy}    WARN

    # Save evidence
    ${src}=    Get Source
    Create File    ${DIR}/01_before_next/before.xml    ${src}    UTF-8
    Run Process    sh    -c    adb exec-out screencap -p > ${DIR}/01_before_next/before.png

    # === APPROACH 1: Appium Click Element (not adb tap) ===
    Log    [TRY-1] Click Element via Appium    WARN
    Run Keyword And Ignore Error    Click Element    xpath=//*[@resource-id="screenProfile_buttonNext"]
    Sleep    8s

    ${has_pdpa}=    Run Keyword And Return Status    Page Should Contain Element    accessibility_id=Personal data consent
    Log    [TRY-1] PDPA reached: ${has_pdpa}    WARN

    IF    not ${has_pdpa}
        # === APPROACH 2: adb tap at calculated center ===
        Log    [TRY-2] ADB tap at ${cx},${cy}    WARN
        Run Process    adb    shell    input    tap    ${cx}    ${cy}
        Sleep    8s
        ${has_pdpa}=    Run Keyword And Return Status    Page Should Contain Element    accessibility_id=Personal data consent
        Log    [TRY-2] PDPA reached: ${has_pdpa}    WARN
    END

    IF    not ${has_pdpa}
        # === APPROACH 3: Hide keyboard + blur + Appium click ===
        Log    [TRY-3] Hide keyboard + blur + click    WARN
        Run Keyword And Ignore Error    Hide Keyboard
        Sleep    1s
        # Tap blank area to force blur
        ${tap_point}=    Create List    540    400
        Tap    ${tap_point}
        Sleep    2s
        # Re-check focus
        ${cid_f2}=    Get Element Attribute    xpath=//*[@resource-id="cid"]    focused
        ${dob_f2}=    Get Element Attribute    xpath=//*[@resource-id="screenProfile_textInputDob"]    focused
        ${mob_f2}=    Get Element Attribute    xpath=//*[@resource-id="screenProfile_textInputMobileNumber"]    focused
        Log    [TRY-3] After blur: CID=${cid_f2} DOB=${dob_f2} Mobile=${mob_f2}    WARN
        # Click Next via Appium
        Run Keyword And Ignore Error    Click Element    xpath=//*[@resource-id="base-btn"]
        Sleep    8s
        ${has_pdpa}=    Run Keyword And Return Status    Page Should Contain Element    accessibility_id=Personal data consent
        Log    [TRY-3] PDPA reached: ${has_pdpa}    WARN
    END

    # Capture final state
    ${src2}=    Get Source
    Create File    ${DIR}/01_before_next/after.xml    ${src2}    UTF-8
    Run Process    sh    -c    adb exec-out screencap -p > ${DIR}/01_before_next/after.png

    # Check what screen we ended on
    ${has_profile}=    Run Keyword And Return Status    Page Should Contain Element    xpath=//*[@text="Tell us about you"]
    ${has_landing}=    Run Keyword And Return Status    Page Should Contain Text    A new view to make sense
    Log    [FINAL] Profile=${has_profile} PDPA=${has_pdpa} Landing=${has_landing}    WARN

    Close Application
