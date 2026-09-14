*** Settings ***
Documentation    ETB regression test-session cleanup that guarantees Appium cache purge.
Library          AppiumLibrary
Library          ../../../libraries/adb_device.py
Library          ../../../libraries/failure_evidence.py

*** Keywords ***
Finalize ETB Regression Test
    Run Keyword If Test Failed    Capture ETB Failure Evidence    ${OUTPUT DIR}    etb_regression_failure
    ${stop_result}=    Force Stop Android Application    ${DEVICE_UDID}    ${APP_PACKAGE}
    Log    ${stop_result}
    ${close_status}    ${close_error}=    Run Keyword And Ignore Error    Close Application
    ${close_failed}=    Set Variable    ${FALSE}
    IF    '${close_status}' == 'PASS'
        Log    APPIUM_SESSION_CLOSE=PASS    INFO
    ELSE IF    '${close_error}' == 'No application is open'
        Log    APPIUM_SESSION_CLOSE=NOT_REQUIRED    INFO
    ELSE
        ${close_failed}=    Set Variable    ${TRUE}
    END
    ${close_all_status}=    Run Keyword And Return Status    Close All Applications
    Should Be True    ${close_all_status}    SESSION_CLOSE_FAILED
    IF    ${close_failed}
        Fail    SESSION_CLOSE_FAILED
    END
