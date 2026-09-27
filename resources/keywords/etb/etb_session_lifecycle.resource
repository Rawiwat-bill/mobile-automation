*** Settings ***
Documentation    ETB regression test-session cleanup that guarantees Appium cache purge.
Library          AppiumLibrary
Library          ../../../libraries/adb_device.py
Resource         ../../diagnostics/etb_observability.resource

*** Keywords ***
Finalize ETB Regression Test
    Run Keyword If Test Failed    Capture ETB Failure Evidence For Active State
    ${stop_result}=    Force Stop Android Application    ${DEVICE_UDID}    ${APP_PACKAGE}
    Log    ${stop_result}
    ${close_status}    ${close_error}=    Run Keyword And Ignore Error    Close Application
    ${close_failed}=    Set Variable    ${FALSE}
    IF    $close_status == 'PASS'
        Log    APPIUM_SESSION_CLOSE=PASS    INFO
    ELSE IF    $close_error == 'No application is open'
        Log    APPIUM_SESSION_CLOSE=NOT_REQUIRED    INFO
    ELSE
        ${close_failed}=    Set Variable    ${TRUE}
    END
    ${close_all_status}=    Run Keyword And Return Status    Close All Applications
    Should Be True    ${close_all_status}    SESSION_CLOSE_FAILED
    IF    ${close_failed}
        Fail    SESSION_CLOSE_FAILED
    END

Capture ETB Failure Evidence For Active State
    ${focus_status}    ${foreground}=    Run Keyword And Ignore Error
    ...    Get Foreground Component    ${DEVICE_UDID}
    ${app_active}=    Evaluate    $focus_status == 'PASS' and str($foreground).startswith($APP_PACKAGE + '/')
    IF    ${app_active}
        Record ETB Evidence Capture    ${OUTPUT DIR}    etb_regression_failure
    ELSE
        Record ETB Device Terminal Evidence    ${OUTPUT DIR}    etb_regression_failure_terminal    ${DEVICE_UDID}
        Log    ETB_FAILURE_EVIDENCE_APP_HIERARCHY_NOT_APPLICABLE foreground=${foreground}    WARN
    END
