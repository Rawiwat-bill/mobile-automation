*** Settings ***
Documentation    Identity Validation - Landing → Consent → Profile → Profile Next
...              
...              Validates the shared onboarding flow then stops.
...              Does NOT continue into OCR or ETB flow.
...              
...              Pass criteria:
...              - Profile screen disappears
...              - OR any next screen appears (service unavailable is acceptable)
Resource         ../../../resources/app/app_keywords.resource
Resource         ../../../resources/keywords/onboarding_common.resource
Library          ../../../libraries/config_loader.py

Suite Setup      Open Mobile Application
Suite Teardown   Close Application

*** Variables ***
${TESTDATA}    testdata/onboarding/ntb.example.yaml

*** Test Cases ***
Identity Validation Flow
    [Documentation]    Run common onboarding and confirm Profile handoff.
    ...                Stops after Profile Next. Does not enter OCR.
    ${previous_log_level}=    Set Log Level    NONE
    ${data}=    Load YAML    ${TESTDATA}
    Set Log Level    ${previous_log_level}
    Complete Common Onboarding    ${data['profile']['citizen_id']}    ${data['profile']['date_of_birth']}    ${data['profile']['mobile_number']}
    Log    Identity validation complete. Profile handoff confirmed.
