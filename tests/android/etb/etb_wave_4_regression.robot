*** Settings ***
Documentation    Data-driven ETB regression case for Wave 4.
Resource         ../../../resources/app/app_keywords.resource
Resource         ../../../resources/keywords/etb/etb_keywords.resource
Resource         ../../../resources/keywords/etb/etb_regression_keywords.resource
Library          ../../../libraries/robot_output_sanitizer.py

Suite Setup      Open Mobile Application
Suite Teardown   Close Application
Test Setup       Reset Wave 4 Application To Landing
Test Teardown    Normalize Wave 4 Application State

*** Test Cases ***
TC-ETB-013 Mule Warning Full-Screen RGI
    Run ETB Expected RGI After Laser Code    etb_tc_013    Handle Expected Full Screen RGI    STANDARD_FIND_BRANCH_CLOSE_APP

*** Keywords ***
Reset Wave 4 Application To Landing
    Run Keyword And Ignore Error    Terminate Application    ${APP_PACKAGE}
    Execute Adb Shell    am    force-stop    ${APP_PACKAGE}
    Activate Application    ${APP_PACKAGE}
    Wait Until Landing Screen Is Displayed

Normalize Wave 4 Application State
    Run Keyword If Test Failed    Capture Page Screenshot    ${OUTPUT DIR}/wave4_failure.png
    Run Keyword And Ignore Error    Execute Adb Shell    am    force-stop    ${APP_PACKAGE}