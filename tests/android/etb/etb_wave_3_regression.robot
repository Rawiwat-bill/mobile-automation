*** Settings ***
Documentation    Data-driven ETB full-screen RGI regression cases for Wave 3.
Resource         ../../../resources/app/app_keywords.resource
Resource         ../../../resources/keywords/etb/etb_keywords.resource
Resource         ../../../resources/keywords/etb/etb_regression_keywords.resource
Library          ../../../libraries/robot_output_sanitizer.py

Suite Setup      Open Mobile Application
Suite Teardown   Close Application
Test Setup       Reset Wave 3 Application To Landing
Test Teardown    Normalize Wave 3 Application State

*** Test Cases ***
TC-ETB-008 High-Risk 3A Full-Screen RGI
    Run ETB Expected RGI Case    etb_tc_008    Handle Expected Full Screen RGI

TC-ETB-009 High-Risk 3V Full-Screen RGI
    Run ETB Expected RGI Case    etb_tc_009    Handle Expected Full Screen RGI

TC-ETB-010 High-Risk 3U Full-Screen RGI
    Run ETB Expected RGI Case    etb_tc_010    Handle Expected Full Screen RGI

TC-ETB-011 High-Risk 3B Full-Screen RGI
    Run ETB Expected RGI Case    etb_tc_011    Handle Expected Full Screen RGI

*** Keywords ***
Reset Wave 3 Application To Landing
    Run Keyword And Ignore Error    Terminate Application    ${APP_PACKAGE}
    Execute Adb Shell    am    force-stop    ${APP_PACKAGE}
    Activate Application    ${APP_PACKAGE}
    Wait Until Landing Screen Is Displayed

Normalize Wave 3 Application State
    Run Keyword If Test Failed    Capture Page Screenshot    ${OUTPUT DIR}/wave3_failure.png
    Run Keyword And Ignore Error    Execute Adb Shell    am    force-stop    ${APP_PACKAGE}