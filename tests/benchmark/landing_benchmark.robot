*** Settings ***
Documentation    Landing Screen Interaction Benchmark
...              
...              Measures screen detection and navigation timing
...              for the Landing screen. Supports both English and Thai
...              language modes.
...              
...              Each test case resets benchmark metrics independently.
...              
...              Run: python3 -m robot -d reports/benchmark tests/benchmark/landing_benchmark.robot
...              
...              Reference: knowledge/benchmark.md

Resource    ../../resources/benchmark/benchmark_base.resource
Library     Collections

Suite Setup      Log    Landing Benchmark Suite Started
Suite Teardown   Close Benchmark Application


*** Keywords ***
Navigate To Landing From Start
    Open Benchmark Application
    Allow Android Permission If Visible
    Navigate To Landing

Detect Landing Using Skip Button
    Start Phase    detect_skip
    ${found}=    Run Keyword And Return Status
    ...    Wait Until Element Is Visible    ${BENCHMARK_LANDING_SKIP}    30s
    Record Appium Action
    End Phase
    RETURN    ${found}

Detect Landing Using Ready Button
    Start Phase    detect_ready
    ${found}=    Run Keyword And Return Status
    ...    Wait Until Element Is Visible    ${BENCHMARK_LANDING_READY}    30s
    Record Appium Action
    End Phase
    RETURN    ${found}

Detect Landing Using Combined
    Start Phase    detect_combined
    ${found}=    Run Keyword And Return Status
    ...    Wait Until Keyword Succeeds    30s    500ms    Landing Screen Should Be Visible
    Record Appium Action
    End Phase
    RETURN    ${found}


*** Test Cases ***
Benchmark Landing Detection - Skip Button
    [Documentation]    Detect Landing using Skip button locator.
    [Tags]    benchmark    landing    skip
    Start Benchmark    Landing Screen Strategy
    Navigate To Landing From Start
    ${result}=    Detect Landing Using Skip Button
    ${status}=    Set Variable If    ${result}    PASS    FAIL
    Log Benchmark Result    landing    skip    ${status}
    Close Benchmark Application

Benchmark Landing Detection - Ready Button
    [Documentation]    Detect Landing using Ready button locator.
    [Tags]    benchmark    landing    ready
    Start Benchmark    Landing Screen Strategy
    Navigate To Landing From Start
    ${result}=    Detect Landing Using Ready Button
    ${status}=    Set Variable If    ${result}    PASS    FAIL
    Log Benchmark Result    landing    ready    ${status}
    Close Benchmark Application

Benchmark Landing Detection - Combined
    [Documentation]    Detect Landing using combined strategy.
    [Tags]    benchmark    landing    combined
    Start Benchmark    Landing Screen Strategy
    Navigate To Landing From Start
    ${result}=    Detect Landing Using Combined
    ${status}=    Set Variable If    ${result}    PASS    FAIL
    Log Benchmark Result    landing    combined    ${status}
    Close Benchmark Application

Benchmark Landing Ready Navigation
    [Documentation]    Measure end-to-end Ready button tap timing.
    [Tags]    benchmark    landing    navigation
    Start Benchmark    Landing Screen Strategy
    Navigate To Landing From Start
    Tap Landing Ready
    Log Benchmark Result    landing    ready_nav    PASS
    Close Benchmark Application
