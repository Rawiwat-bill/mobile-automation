*** Settings ***
Documentation    Compatibility facade for Profile screen behavior.
...              Responsibilities are split into field, DOB, and transition/evidence resources.
Resource         profile_fields.resource
Resource         profile_dob.resource
Resource         profile_transition.resource


*** Keywords ***
Input Date Of Birth
    [Documentation]    Backward-compatible facade for callers that namespace DOB through profile_screen_page.
    [Arguments]    ${date_of_birth}
    profile_dob.Input Date Of Birth    ${date_of_birth}
