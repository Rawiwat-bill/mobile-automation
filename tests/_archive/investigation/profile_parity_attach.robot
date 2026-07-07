*** Settings ***
Documentation    Sprint 2.32.1 — Profile Parity (attach to running app)
...              Assumes app is already running on Landing screen
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
Attach To Running App
    Open Application
    ...    http://127.0.0.1:4723
    ...    platformName=Android
    ...    automationName=UiAutomator2
    ...    deviceName=Android Emulator
    ...    appPackage=com.bangkokbank.blue.dev
    ...    appActivity=com.bangkokbank.blue.MainActivity
    ...    noReset=true

Navigate To Profile With Fields Filled
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
    RETURN    ${data}

Get Next Button Center
    ${rect}=    Get Element Rect    xpath=//*[@resource-id="screenProfile_buttonNext"]
    ${cx}=    Evaluate    int(${rect['x']} + (${rect['width']} / 2))
    ${cy}=    Evaluate    int(${rect['y']} + (${rect['height']} / 2))
    Log    [NEXT] Button at ${cx},${cy} (rect: x=${rect['x']} y=${rect['y']} w=${rect['width']} h=${rect['height']})    WARN
    RETURN    ${cx}    ${cy}

Save Evidence
    [Arguments]    ${folder}    ${label}
    ${d}=    Set Variable    ${DIR}/${folder}
    Create Directory    ${d}
    Run Keyword And Ignore Error    ${src}=    Get Source
    Run Keyword And Ignore Error    Create File    ${d}/${label}.xml    ${src}    UTF-8
    Run Process    sh    -c    adb exec-out screencap -p > ${d}/${label}.png    2>/dev/null

Check PDPA
    ${pdpa}=    Run Keyword And Return Status    Page Should Contain Element    accessibility_id=Personal data consent
    ${profile}=    Run Keyword And Return Status    Page Should Contain Element    xpath=//*[@text="Tell us about you"]
    Log    [CHECK] PDPA=${pdpa} Profile=${profile}    WARN
    RETURN    ${pdpa}

*** Test Cases ***
Scenario A — ADB Input Tap
    Create Directory    ${DIR}
    Attach To Running App
    ${data}=    Navigate To Profile With Fields Filled
    ${cx}    ${cy}=    Get Next Button Center
    Save Evidence    02_automation_next    before
    Log    [A] Tapping Next via input tap    WARN
    Run Process    adb    shell    input    tap    ${cx}    ${cy}
    Sleep    10s
    Save Evidence    02_automation_next    after
    ${reached}=    Check PDPA
    Run Keyword If    ${reached}    Log    [A] *** REACHED PDPA ***    WARN
    Close Application

Scenario C — Hide Keyboard + Input Swipe
    Attach To Running App
    ${data}=    Navigate To Profile With Fields Filled
    ${cx}    ${cy}=    Get Next Button Center
    Log    [C] Hide keyboard + blur + swipe tap    WARN
    Run Keyword And Ignore Error    Hide Keyboard
    Sleep    1s
    Tap Profile Blank Area    1600
    Sleep    3s
    Save Evidence    04_hide_keyboard    before
    Log    [C] Tapping via input swipe 100ms    WARN
    Run Process    adb    shell    input    swipe    ${cx}    ${cy}    ${cx}    ${cy}    100
    Sleep    10s
    Save Evidence    04_hide_keyboard    after
    ${reached}=    Check PDPA
    Run Keyword If    ${reached}    Log    [C] *** REACHED PDPA ***    WARN
    Close Application

Scenario D — Force Blur + Input Swipe 200ms
    Attach To Running App
    ${data}=    Navigate To Profile With Fields Filled
    ${cx}    ${cy}=    Get Next Button Center
    Log    [D] Force blur + swipe 200ms    WARN
    Run Keyword And Ignore Error    Hide Keyboard
    Sleep    1s
    Tap Profile Blank Area    400
    Sleep    1s
    Tap Profile Blank Area    1600
    Sleep    2s
    Save Evidence    05_force_blur    before
    Log    [D] Tapping via input swipe 200ms    WARN
    Run Process    adb    shell    input    swipe    ${cx}    ${cy}    ${cx}    ${cy}    200
    Sleep    10s
    Save Evidence    05_force_blur    after
    ${reached}=    Check PDPA
    Run Keyword If    ${reached}    Log    [D] *** REACHED PDPA ***    WARN
    Close Application

Scenario E — Field Verification
    Attach To Running App
    ${data}=    Navigate To Profile With Fields Filled
    Save Evidence    06_field_verification    before
    ${cid}=    Get Text    xpath=//*[@resource-id="cid"]
    ${dob}=    Get Text    xpath=//*[@resource-id="screenProfile_textInputDob"]
    ${mob}=    Get Text    xpath=//*[@resource-id="screenProfile_textInputMobileNumber"]
    ${cid_n}=    Replace String Using Regexp    ${cid}    [^0-9]    ${EMPTY}
    ${mob_n}=    Replace String Using Regexp    ${mob}    [^0-9]    ${EMPTY}
    Log    [E] CID: "${cid_n}" expected "${data['profile']['citizen_id']}"    WARN
    Log    [E] DOB: "${dob}"    WARN
    Log    [E] Mobile: "${mob_n}" expected "${data['profile']['mobile_number']}"    WARN
    Save Evidence    06_field_verification    after
    Close Application
