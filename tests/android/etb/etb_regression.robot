*** Settings ***
Documentation    Consolidated, data-driven ETB regression cases TC-ETB-001 through TC-ETB-013.
Resource         ../../../resources/keywords/etb/etb_regression_keywords.resource
Resource         ../../../resources/keywords/etb/etb_session_lifecycle.resource
Library          ../../../libraries/robot_output_sanitizer.py
Library          ../../../libraries/startup_state.py

Suite Setup      Prepare ETB Regression Suite
Suite Teardown   No Operation
Test Setup       Reset ETB Regression Application
Test Teardown    Finalize ETB Regression Test

*** Test Cases ***
TC-ETB-001 Positive Registration Success
    [Tags]    etb    regression    positive    smoke
    Run ETB Positive Case    etb_tc_001    assert_3c=${True}

TC-ETB-002 Positive Registration With PDPA Clause 6
    [Tags]    etb    regression    positive    pdpa
    Run ETB TC002 PDPA Case

TC-ETB-003 Positive Product Selection Variant
    [Tags]    etb    regression    positive    product-selection
    Run ETB Positive Case    etb_tc_003    assert_3c=${True}
    Set Suite Variable    ${TC003_CONTROL_HOME_PROVEN}    ${TRUE}

TC-ETB-004 Positive Product Selection Existing Accounts
    [Tags]    etb    regression    positive    product-selection
    Require TC003 Control Home For TC004
    Run ETB Positive Case    etb_tc_004    assert_3c=${True}

TC-ETB-005 Mobile Number Mismatch RGI Popup
    [Tags]    etb    regression    rgi    rgi-popup    smoke
    Run ETB Expected RGI Case    etb_tc_005    Handle Expected RGI Popup

TC-ETB-006 DOB Mismatch RGI Popup
    [Tags]    etb    regression    rgi    rgi-popup
    Run ETB Expected RGI Case    etb_tc_006    Handle Expected RGI Popup

TC-ETB-007 Expired Citizen ID Full-Screen RGI
    [Tags]    etb    regression    rgi    full-screen-rgi
    Run ETB Expected RGI Case    etb_tc_007    Handle Expected Full Screen RGI

TC-ETB-008 High-Risk 3A Full-Screen RGI
    [Tags]    etb    regression    rgi    full-screen-rgi
    Run ETB Expected RGI Case    etb_tc_008    Handle Expected Full Screen RGI

TC-ETB-009 High-Risk 3V Full-Screen RGI
    [Tags]    etb    regression    rgi    full-screen-rgi
    Run ETB Expected RGI Case    etb_tc_009    Handle Expected Full Screen RGI

TC-ETB-010 High-Risk 3U Full-Screen RGI
    [Tags]    etb    regression    rgi    full-screen-rgi
    Run ETB Expected RGI Case    etb_tc_010    Handle Expected Full Screen RGI

TC-ETB-011 High-Risk 3B Full-Screen RGI
    [Tags]    etb    regression    rgi    full-screen-rgi
    Run ETB Expected RGI Case    etb_tc_011    Handle Expected Full Screen RGI

TC-ETB-012 Low IAL Full-Screen RGI
    [Tags]    etb    regression    rgi    full-screen-rgi
    Run ETB Expected RGI Case    etb_tc_012    Handle Expected Full Screen RGI

TC-ETB-013 Mule Warning Full-Screen RGI
    [Tags]    etb    regression    rgi    full-screen-rgi    mule-warning
    Run ETB Expected RGI After Laser Code    etb_tc_013    Handle Expected Full Screen RGI    STANDARD_FIND_BRANCH_CLOSE_APP
