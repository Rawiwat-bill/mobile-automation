*** Settings ***
Documentation    Sprint 2.32.1 — Profile Next Parity Investigation
...              Scenarios A/C/D/E in one file, each independent
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
${DIR}    reports/investigation/manual_vs_automation

*** Keywords ***
Setup Profile Screen
    Create Directory    ${DIR}
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
    RETURN    ${data}

Capture State
    [Arguments]    ${folder}    ${label}
    ${d}=    Set Variable    ${DIR}/${folder}
    Create Directory    ${d}
    # Field values
    ${cid}=    Get Text    xpath=//*[@resource-id="cid"]
    ${dob}=    Get Text    xpath=//*[@resource-id="screenProfile_textInputDob"]
    ${mob}=    Get Text    xpath=//*[@resource-id="screenProfile_textInputMobileNumber"]
    # Focus state
    ${cf}=    Run Keyword And Ignore Error    Get Element Attribute    xpath=//*[@resource-id="cid"]    focused
    ${df}=    Run Keyword And Ignore Error    Get Element Attribute    xpath=//*[@resource-id="screenProfile_textInputDob"]    focused
    ${mf}=    Run Keyword And Ignore Error    Get Element Attribute    xpath=//*[@resource-id="screenProfile_textInputMobileNumber"]    focused
    # Next button
    ${rect}=    Run Keyword And Ignore Error    Get Element Rect    xpath=//*[@resource-id="screenProfile_buttonNext"]
    Log    [STATE:${label}] CID="${cid}" DOB="${dob}" Mob="${mob}"    WARN
    Log    [STATE:${label}] Focus: CID=${cf} DOB=${df} Mob=${mf}    WARN
    Log    [STATE:${label}] Next rect: ${rect}    WARN
    # Save XML + screenshot
    Run Keyword And Ignore Error    ${src}=    Get Source
    Run Keyword And Ignore Error    Create File    ${d}/${label}.xml    ${src}    UTF-8
    Run Process    sh    -c    adb exec-out screencap -p > ${d}/${label}.png    2>/dev/null
    RETURN    ${rect}

Check Result
    [Arguments]    ${folder}
    ${d}=    Set Variable    ${DIR}/${folder}
    Sleep    8s
    Run Keyword And Ignore Error    ${src}=    Get Source
    Run Keyword And Ignore Error    Create File    ${d}/after.xml    ${src}    UTF-8
    Run Process    sh    -c    adb exec-out screencap -p > ${d}/after.png    2>/dev/null
    ${pdpa}=    Run Keyword And Return Status    Page Should Contain Element    accessibility_id=Personal data consent
    ${profile}=    Run Keyword And Return Status    Page Should Contain Element    xpath=//*[@text="Tell us about you"]
    ${landing}=    Run Keyword And Return Status    Page Should Contain Text    A new view to make sense
    Log    [RESULT:${folder}] PDPA=${pdpa} Profile=${profile} Landing=${landing}    WARN
    RETURN    ${pdpa}

*** Test Cases ***
Scenario A — Normal Automation Next
    ${data}=    Setup Profile Screen
    ${rect}=    Capture State    02_automation_next    before
    Log    [A] Tapping Next via standard adb tap    WARN
    ${r}=    Get From Dictionary    ${rect}    value
    ${cx}=    Set Variable    ${r['x']}
    ${cy}=    Set Variable    ${r['y']}
    ${w}=    Set Variable    ${r['width']}
    ${h}=    Set Variable    ${r['height']}
    ${tcx}=    Evaluate    int(${cx} + (${w} / 2))
    ${tcy}=    Evaluate    int(${cy} + (${h} / 2))
    Run Process    adb    shell    input    tap    ${tcx}    ${tcy}
    ${reached}=    Check Result    02_automation_next
    Close Application

Scenario C — Hide Keyboard Then Next
    ${data}=    Setup Profile Screen
    ${rect}=    Capture State    04_hide_keyboard    before
    Log    [C] Hide keyboard + blur + wait    WARN
    Run Keyword And Ignore Error    Hide Keyboard
    Sleep    1s
    Tap Profile Blank Area    1600
    Sleep    3s
    Capture State    04_hide_keyboard    after_blur
    Log    [C] Tapping Next via adb swipe 100ms    WARN
    ${r}=    Get From Dictionary    ${rect}    value
    ${tcx}=    Evaluate    int(${r['x']} + (${r['width']} / 2))
    ${tcy}=    Evaluate    int(${r['y']} + (${r['height']} / 2))
    Run Process    adb    shell    input    swipe    ${tcx}    ${tcy}    ${tcx}    ${tcy}    100
    ${reached}=    Check Result    04_hide_keyboard
    Close Application

Scenario D — Force Blur Then Swipe Next
    ${data}=    Setup Profile Screen
    ${rect}=    Capture State    05_force_blur    before
    Log    [D] Force blur all fields    WARN
    # Tap title area to force blur
    Run Keyword And Ignore Error    Click Element    xpath=//*[@text="Tell us about you"]
    Sleep    1s
    Tap Profile Blank Area    400
    Sleep    2s
    Run Keyword And Ignore Error    Hide Keyboard
    Sleep    2s
    Capture State    05_force_blur    after_blur
    Log    [D] Tapping Next via adb swipe 150ms    WARN
    ${r}=    Get From Dictionary    ${rect}    value
    ${tcx}=    Evaluate    int(${r['x']} + (${r['width']} / 2))
    ${tcy}=    Evaluate    int(${r['y']} + (${r['height']} / 2))
    Run Process    adb    shell    input    swipe    ${tcx}    ${tcy}    ${tcx}    ${tcy}    150
    ${reached}=    Check Result    05_force_blur
    Close Application

Scenario E — Field Value Verification
    ${data}=    Setup Profile Screen
    ${rect}=    Capture State    06_field_verification    before
    Log    [E] Verifying field values    WARN
    ${cid}=    Get Text    xpath=//*[@resource-id="cid"]
    ${dob}=    Get Text    xpath=//*[@resource-id="screenProfile_textInputDob"]
    ${mob}=    Get Text    xpath=//*[@resource-id="screenProfile_textInputMobileNumber"]
    ${cid_n}=    Replace String Using Regexp    ${cid}    [^0-9]    ${EMPTY}
    ${mob_n}=    Replace String Using Regexp    ${mob}    [^0-9]    ${EMPTY}
    Log    [E] CID: "${cid_n}" == "${data['profile']['citizen_id']}"    WARN
    Log    [E] DOB: "${dob}"    WARN
    Log    [E] Mobile: "${mob_n}" == "${data['profile']['mobile_number']}"    WARN
    Should Be Equal As Strings    ${cid_n}    ${data['profile']['citizen_id']}
    Should Be Equal As Strings    ${mob_n}    ${data['profile']['mobile_number']}
    Log    [E] All values verified ✓    WARN
    Close Application
