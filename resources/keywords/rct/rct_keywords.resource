*** Settings ***
Documentation       RCT (Reactivate) flow keywords.
...                 Happy case: correct old PIN + PDPA consent = Accept.
...
...                 NOTE: Entry path to the reactivate flow is not yet confirmed.
...                 `Enter Reactivate Flow` is a stub until the navigation
...                 (deep link / menu / post-login path) is provided.

Resource            ../../app/app_keywords.resource
Resource            ../../pages/onboarding/pdpa_consent_page.resource
Resource            ../../keywords/common_onboarding/common_onboarding_keyword.resource
Resource            ../../pages/etb/check_dopa_fill_laser_code_page.resource
Resource            ../../pages/etb/mobile_otp_page.resource
Resource            ../../pages/onboarding/confirm_pin_page.resource
Resource            ../../pages/etb/check_pdpa_clause_no_6_page.resource
Resource            ../../pages/etb/intro_face_scan_page.resource


*** Keywords ***
Enter Reactivate Flow
    [Documentation]    Navigate into the reactivate flow.
    ...                STUB: replace once the entry path is confirmed
    ...                (e.g. deep link, menu item, or login-fail route).
    Log    [RCT] Reactivate entry point not yet implemented. Placeholder executed.

Complete RCT Reactivate
    [Documentation]    Complete the reactivate happy flow:
    ...                1. Common entry (Landing -> Consent -> Profile CID/DOB/Mobile)
    ...                2. Enter reactivate flow
    ...                3. Check DOPA laser code + Mobile OTP
    ...                4. Conditional PDPA consent (reused onboarding PDPA screen;
    ...                   shown only when the user has not yet accepted it,
    ...                   otherwise skipped as already accepted)
    ...                5. Face scan (By pass)
    ...                6. Enter correct old PIN
    [Arguments]    ${citizen_id}    ${date_of_birth}    ${mobile_number}    ${pin}    ${laser_code}

    Common Onboarding Flow    ${citizen_id}    ${date_of_birth}    ${mobile_number}
    Mark Health Checkpoint    RCT_COMMON_ENTRY_COMPLETED

    Enter Reactivate Flow
    Mark Health Checkpoint    RCT_ENTRY

    Wait Until Check DOPA Fill Laser Code Is Displayed
    Mark Health Checkpoint    CHECK_DOPA_FILL_LASER_CODE_VISIBLE
    Input Laser Code    ${laser_code}
    Click Element    ${CHECK_DOPA_FILL_LASER_CODE_BUTTON_NEXT}
    Mark Health Checkpoint    CHECK_DOPA_FILL_LASER_CODE_COMPLETED

    Wait Until Mobile OTP Screen Is Displayed
    Mark Health Checkpoint    MOBILE_OTP_VISIBLE
    Input OTP Fast
    Mark Health Checkpoint    MOBILE_OTP_COMPLETED

    # Check PDPA Clause No6 Screen
    # ${post_otp_screen}=    Wait Until Keyword Succeeds    ${NCBD_LOADING_TIMEOUT}    1s    Detect Post OTP Screen
    # IF    '${post_otp_screen}' == 'CHECK_PDPA_CLAUSE_NO_6'
    #    Wait Until Check PDPA Clause No6 Is Displayed
    #    Mark Health Checkpoint    CHECK_PDPA_CLAUSE_NO_6_VISIBLE
    #    Scroll Down PDPA Clause No6
    #    Accept PDPA Clause No6
    #    Mark Health Checkpoint    CHECK_PDPA_CLAUSE_NO_6_COMPLETED

    #    # RETURN
    # END

    # Intro Face Scan Screen
    Wait Until Intro Face Screen Is Displayed
    Mark Health Checkpoint    INTRO_FACE_SCAN_VISIBLE
    Click Element    ${INTRO_FACE_SCAN_NEXT_BUTTON}
    Allow Android Permission If Visible

    Wait Until Enter PIN Screen Is Displayed
    Mark Health Checkpoint    ENTER_PIN_VISIBLE
    Enter Confirm PIN Using Custom Keypad    ${pin}
    Mark Health Checkpoint    ENTER_PIN_ENTERED
