*** Settings ***
Documentation    Profile Field Strategy Benchmark
...              
...              Compares interaction strategies for Citizen ID, DOB,
...              and Mobile Number fields on the Profile screen.
...              
...              Each strategy is run with a clean app restart.
...              Metrics: execution time, wait time, scroll time,
...              Appium actions, ADB calls, screenshot count, retry count.
...              
...              Run: python3 -m robot -d reports/benchmark tests/benchmark/profile_field_benchmark.robot
...              
...              Reference: knowledge/benchmark.md

Resource    ../../resources/benchmark/benchmark_strategies.resource
Library     ../../libraries/config_loader.py
Library     Collections

Suite Setup      Set Benchmark Data
Suite Teardown   Close Benchmark Application


*** Variables ***
${CITIZEN_ID}       1111111111111
${DATE_OF_BIRTH}    1990-01-01
${MOBILE_NUMBER}    0811111111


*** Keywords ***
Set Benchmark Data
    ${data}=    Load YAML    ${CURDIR}/../../testdata/onboarding/ntb.example.yaml
    Set Suite Variable    ${CITIZEN_ID}    ${data['profile']['citizen_id']}
    Set Suite Variable    ${DATE_OF_BIRTH}    ${data['profile']['date_of_birth']}
    Set Suite Variable    ${MOBILE_NUMBER}    ${data['profile']['mobile_number']}


*** Test Cases ***
Benchmark Citizen ID Strategies
    [Documentation]    Compare 5 input strategies for Citizen ID field.
    ...                Strategies: Input Text, Input Value, Press Keycodes, Adb Shell, Execute Script
    [Tags]    benchmark    profile    citizen_id

    Start Benchmark    Citizen ID Strategy Comparison

    Run Citizen ID Strategy    ${CITIZEN_ID}    input_text
    Close Benchmark Application
    Run Citizen ID Strategy    ${CITIZEN_ID}    input_value
    Close Benchmark Application
    Run Citizen ID Strategy    ${CITIZEN_ID}    press_keycodes
    Close Benchmark Application
    Run Citizen ID Strategy    ${CITIZEN_ID}    adb_shell
    Close Benchmark Application
    Run Citizen ID Strategy    ${CITIZEN_ID}    execute_script
    Close Benchmark Application

    Log    [BENCHMARK] All Citizen ID strategies completed.

Benchmark DOB Strategies
    [Documentation]    Compare 4 input strategies for Date of Birth field.
    ...                Strategies: Picker Calculated, Input Text, Adb Shell, Input Value
    [Tags]    benchmark    profile    dob

    Start Benchmark    DOB Strategy Comparison

    Run DOB Strategy    ${DATE_OF_BIRTH}    picker_calculated
    Close Benchmark Application
    Run DOB Strategy    ${DATE_OF_BIRTH}    input_text
    Close Benchmark Application
    Run DOB Strategy    ${DATE_OF_BIRTH}    adb_shell
    Close Benchmark Application
    Run DOB Strategy    ${DATE_OF_BIRTH}    input_value
    Close Benchmark Application

    Log    [BENCHMARK] All DOB strategies completed.

Benchmark Mobile Number Strategies
    [Documentation]    Compare 5 input strategies for Mobile Number field.
    ...                Strategies: Input Text, Input Value, Press Keycodes, Adb Shell, Execute Script
    [Tags]    benchmark    profile    mobile_number

    Start Benchmark    Mobile Number Strategy Comparison

    Run Mobile Number Strategy    ${MOBILE_NUMBER}    input_text
    Close Benchmark Application
    Run Mobile Number Strategy    ${MOBILE_NUMBER}    input_value
    Close Benchmark Application
    Run Mobile Number Strategy    ${MOBILE_NUMBER}    press_keycodes
    Close Benchmark Application
    Run Mobile Number Strategy    ${MOBILE_NUMBER}    adb_shell
    Close Benchmark Application
    Run Mobile Number Strategy    ${MOBILE_NUMBER}    execute_script
    Close Benchmark Application

    Log    [BENCHMARK] All Mobile Number strategies completed.
