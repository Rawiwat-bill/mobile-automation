*** Settings ***
Documentation    Sprint 2.32.1 — Profile Next Tap Test
...              Tests input tap vs input swipe for Next button
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
Test Next Button — Input Tap vs Input Swipe
    Create Directory    ${DIR}/02_automation_next
    Create Directory    ${DIR}/04_hide_keyboard

    # Navigate to Profile with fields filled (production keywords)
    Open Mobile Application
    ${prev}=    Set Log Level    NONE
    ${data}=    Load YAML    testdata/onboarding/ntb.local.yaml
    Set Log Level    ${prev}
    Wait Until Landing Screen Is Displayed
    Tap Landing Ready Button
    Allow Android Permission If Visible
    Wait Until Consent Screen Is Displayed
    Tap Consent Accept Button
    Wait Until Profile Screen Is Displayed
    Input Citizen ID    ${data['profile']['citizen_id']}
    Input Date Of Birth    ${data['profile']['date_of_birth']}
    Input Mobile Number    ${data['profile']['mobile_number']}
    Log    [FLOW] Profile fields filled    WARN

    # Get Next button center
    ${rect}=    Get Element Rect    xpath=//*[@resource-id="screenProfile_buttonNext"]
    ${cx}=    Evaluate    int(${rect['x']} + (${rect['width']} / 2))
    ${cy}=    Evaluate    int(${rect['y']} + (${rect['height']} / 2))
    Log    [NEXT] Center: ${cx},${cy}    WARN

    # Verify fields
    ${cid}=    Get Text    xpath=//*[@resource-id="cid"]
    ${dob}=    Get Text    xpath=//*[@resource-id="screenProfile_textInputDob"]
    ${mob}=    Get Text    xpath=//*[@resource-id="screenProfile_textInputMobileNumber"]
    Log    [VERIFY] CID="${cid}" DOB="${dob}" Mob="${mob}"    WARN

    # === APPROACH 1: input tap (current production method) ===
    Log    [TRY-1] input tap ${cx} ${cy}    WARN
    Run Process    adb    shell    input    tap    ${cx}    ${cy}
    Sleep    10s

    # Check result
    ${pdpa1}=    Run Keyword And Return Status    Page Should Contain Element    accessibility_id=Personal data consent
    Log    [TRY-1] PDPA reached: ${pdpa1}    WARN

    # Save evidence
    ${src}=    Get Source
    Create File    ${DIR}/02_automation_next/after_tap.xml    ${src}    UTF-8
    Run Process    sh    -c    adb exec-out screencap -p > ${DIR}/02_automation_next/after_tap.png

    # If input tap didn't work, try input swipe
    IF    not ${pdpa1}
        Log    [TRY-1] Failed. Trying input swipe 100ms    WARN

        # Check if we're still on Profile
        ${still_profile}=    Run Keyword And Return Status    Page Should Contain Element    xpath=//*[@text="Tell us about you"]
        IF    ${still_profile}
            # Try input swipe with 100ms duration
            Log    [TRY-2] input swipe ${cx} ${cy} ${cx} ${cy} 100    WARN
            Run Process    adb    shell    input    swipe    ${cx}    ${cy}    ${cx}    ${cy}    100
            Sleep    10s
            ${pdpa2}=    Run Keyword And Return Status    Page Should Contain Element    accessibility_id=Personal data consent
            Log    [TRY-2] PDPA reached: ${pdpa2}    WARN
        ELSE
            Log    [TRY-2] Not on Profile anymore — can't retry    WARN
        END
    END

    Close Application
