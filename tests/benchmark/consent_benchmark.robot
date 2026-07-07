*** Settings ***
Documentation    Consent Screen Scroll Strategy Benchmark
...              
...              Compares scroll strategies for the Consent screen
...              terms acceptance. The Accept button is only enabled
...              after scrolling through the full terms.
...              
...              Experiment: scrollbar drag vs content swipe.
...              Metrics: execution time, scroll time, ADB calls,
...              Appium actions, text found, accept success.
...              
...              Each test case resets benchmark metrics independently.
...              
...              Run: python3 -m robot -d reports/benchmark tests/benchmark/consent_benchmark.robot
...              
...              Reference: knowledge/benchmark.md

Resource    ../../resources/benchmark/benchmark_base.resource
Resource    ../../resources/benchmark/consent_scroll_strategies.resource
Library     Collections

Suite Setup      Log    Consent Benchmark Suite Started
Suite Teardown   Close Benchmark Application


*** Variables ***
${CONSENT_MAX_SWIPES}       12


*** Keywords ***
Navigate To Consent From Start
    Open Benchmark Application
    Allow Android Permission If Visible
    Navigate To Landing
    Tap Landing Ready
    Allow Android Permission If Visible
    Navigate To Consent

Scroll Adb Swipe Hardcoded
    Start Phase    scroll_hardcoded
    ${result}=    Consent Scroll - Hardcoded Swipe    max_swipes=${CONSENT_MAX_SWIPES}
    Log    [BENCHMARK] Adb Swipe Hardcoded: accept_found=${result}
    End Phase

Scroll Adb Swipe Dynamic
    Start Phase    scroll_dynamic
    ${result}=    Consent Scroll - Dynamic Swipe    max_swipes=20    end_check_interval=2
    Log    [BENCHMARK] Adb Swipe Dynamic: accept_found=${result}
    End Phase

Scroll Adb Scrollbar Drag
    [Arguments]    ${start_x}    ${start_y}    ${end_x}    ${end_y}    ${duration}    ${label}
    ${result}=    Consent Scroll - Scrollbar Drag    ${start_x}    ${start_y}    ${end_x}    ${end_y}    ${duration}    ${label}
    RETURN    ${result}

Tap Consent Accept Benchmark With Evidence
    ${accept_visible}=    Run Keyword And Return Status
    ...    Wait Until Element Is Visible    ${BENCHMARK_CONSENT_ACCEPT}    5s
    IF    not ${accept_visible}
        Capture Page Screenshot
        Record Screenshot
        Log    [BENCHMARK] Accept button NOT visible after experiment    WARN
    ELSE
        ${click_ok}=    Run Keyword And Return Status
        ...    Click Element    ${BENCHMARK_CONSENT_ACCEPT}
        Record Appium Action
        IF    not ${click_ok}
            Capture Page Screenshot
            Record Screenshot
            Log    [BENCHMARK] Accept button visible but click FAILED    WARN
        ELSE
            Log    [BENCHMARK] Accept clicked successfully
        END
    END
    RETURN    ${accept_visible}

Tap Consent Accept Benchmark
    Wait Until Element Is Visible    ${BENCHMARK_CONSENT_ACCEPT}    10s
    Click Element    ${BENCHMARK_CONSENT_ACCEPT}
    Record Appium Action

Run Scrollbar Experiment
    [Arguments]    ${start_x}    ${start_y}    ${end_x}    ${end_y}    ${duration}    ${label}
    Start Benchmark    Consent Scroll Strategy
    Navigate To Consent From Start
    ${found}=    Scroll Adb Scrollbar Drag    ${start_x}    ${start_y}    ${end_x}    ${end_y}    ${duration}    ${label}
    Run Keyword And Ignore Error    Tap Consent Accept Benchmark With Evidence
    ${status}=    Set Variable If    ${found}    PASS    FAIL
    Log Benchmark Result    consent    scrollbar_${label}    ${status}
    Close Benchmark Application
    Run Process    adb    shell    am    force-stop    com.bangkokbank.blue.dev


*** Test Cases ***
Baseline Hardcoded Swipe
    [Documentation]    Baseline: content swipe hardcoded (12 max, same coords)
    [Tags]    benchmark    consent    scroll    baseline
    Start Benchmark    Consent Scroll Strategy
    Start Phase    baseline_hardcoded
    Navigate To Consent From Start
    Scroll Adb Swipe Hardcoded
    Tap Consent Accept Benchmark
    End Phase
    Log Benchmark Result    consent    hardcoded    PASS
    Close Benchmark Application
    Run Process    adb    shell    am    force-stop    com.bangkokbank.blue.dev

Baseline Dynamic Swipe
    [Documentation]    Baseline: content swipe dynamic (check every 2 swipes)
    [Tags]    benchmark    consent    scroll    baseline
    Start Benchmark    Consent Scroll Strategy
    Start Phase    baseline_dynamic
    Navigate To Consent From Start
    Scroll Adb Swipe Dynamic
    Tap Consent Accept Benchmark
    End Phase
    Log Benchmark Result    consent    dynamic    PASS
    Close Benchmark Application
    Run Process    adb    shell    am    force-stop    com.bangkokbank.blue.dev

Scrollbar Drag 1060 450 → 1060 1900 300ms
    [Documentation]    Scrollbar drag experiment 1: gesture at x=1060, drag 450→1900, 300ms
    [Tags]    benchmark    consent    scroll    experiment
    Run Scrollbar Experiment    1060    450    1060    1900    300    1060_300

Scrollbar Drag 1040 450 → 1040 1900 300ms
    [Documentation]    Scrollbar drag experiment 2: gesture at x=1040, drag 450→1900, 300ms
    [Tags]    benchmark    consent    scroll    experiment
    Run Scrollbar Experiment    1040    450    1040    1900    300    1040_300

Scrollbar Drag 1040 450 → 1040 1900 150ms
    [Documentation]    Scrollbar drag experiment 3: gesture at x=1040, drag 450→1900, 150ms
    [Tags]    benchmark    consent    scroll    experiment
    Run Scrollbar Experiment    1040    450    1040    1900    150    1040_150

Scrollbar Drag 1030 500 → 1030 1850 150ms
    [Documentation]    Scrollbar drag experiment 4: gesture at x=1030, drag 500→1850, 150ms
    [Tags]    benchmark    consent    scroll    experiment
    Run Scrollbar Experiment    1030    500    1030    1850    150    1030_150
