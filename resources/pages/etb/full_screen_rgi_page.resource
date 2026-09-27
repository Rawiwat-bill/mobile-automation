*** Settings ***
Documentation    Shared ETB full-screen RGI Page Object.
Library          AppiumLibrary
Library          ../../../libraries/adb_device.py
Resource         ../../../locators/android/etb/full_screen_rgi_locators.resource
Resource         ../../app/app_constants.resource

*** Variables ***
${FULL_SCREEN_RGI_BRANCH_CLOSE_X_RATIO}    0.917
${FULL_SCREEN_RGI_BRANCH_CLOSE_Y_RATIO}    0.091

*** Keywords ***
Wait Until Full Screen RGI Is Visible
    [Arguments]    ${timeout}=${NCBD_LOADING_TIMEOUT}
    Wait Until Element Is Visible    ${FULL_SCREEN_RGI_CONTAINER}    ${timeout}

Assert Full Screen RGI
    [Arguments]    ${expected_error_code}    ${expected_message}=${NONE}    ${action_policy}=STANDARD_FIND_BRANCH_CLOSE_APP
    Wait Until Full Screen RGI Is Visible
    ${code_locator}=    Set Variable
    ...    xpath=//*[@content-desc="${expected_error_code}" or contains(@text,"${expected_error_code}")]
    Wait Until Element Is Visible    ${code_locator}    ${NCBD_LOADING_TIMEOUT}
    IF    '${action_policy}' == 'STANDARD_FIND_BRANCH_CLOSE_APP'
        Wait Until Element Is Visible    ${FULL_SCREEN_RGI_FIND_BRANCH}    ${NCBD_LOADING_TIMEOUT}
        Wait Until Element Is Visible    ${FULL_SCREEN_RGI_CLOSE_BUTTON}    ${NCBD_LOADING_TIMEOUT}
    ELSE IF    '${action_policy}' == 'ASSERT_ONLY'
        Log    Full-Screen RGI action policy ASSERT_ONLY: standard actions are not required by runtime evidence.
    ELSE
        Fail    Unsupported Full-Screen RGI action policy: ${action_policy}
    END
    IF    $expected_message is not None
        Wait Until Page Contains    ${expected_message}    ${NCBD_LOADING_TIMEOUT}
    END

Tap Full Screen RGI Close App
    Wait Until Element Is Visible    ${FULL_SCREEN_RGI_CLOSE_BUTTON}    ${NCBD_LOADING_TIMEOUT}
    Click Element    ${FULL_SCREEN_RGI_CLOSE_BUTTON}

Open Full Screen RGI Branch And Return
    [Arguments]    ${expected_error_code}
    Wait Until Element Is Visible    ${FULL_SCREEN_RGI_FIND_BRANCH}    ${NCBD_LOADING_TIMEOUT}
    Click Element    ${FULL_SCREEN_RGI_FIND_BRANCH}
    ${destination_mode}=    Wait Until Keyword Succeeds    ${NCBD_LOADING_TIMEOUT}    500ms
    ...    Full Screen RGI Branch Destination Is Open
    Close Full Screen RGI Branch Destination    ${destination_mode}
    Assert Full Screen RGI    ${expected_error_code}

Full Screen RGI Branch Destination Is Open
    ${foreground}=    Get Foreground Component    ${DEVICE_UDID}
    Should Not Be Empty    ${foreground}    FULL_SCREEN_RGI_BRANCH_FOREGROUND_UNKNOWN
    ${external_foreground}=    Evaluate    not str($foreground).startswith($APP_PACKAGE + '/')
    ${source_status}    ${source}=    Run Keyword And Ignore Error    Get Source
    Should Be Equal As Strings    ${source_status}    PASS    FULL_SCREEN_RGI_BRANCH_SOURCE_UNAVAILABLE
    Should Not Be Empty    ${source}    FULL_SCREEN_RGI_BRANCH_SOURCE_EMPTY
    ${webview}=    Run Keyword And Return Status    Should Contain    ${source}    android.webkit.WebView
    Should Be True    ${webview}    FULL_SCREEN_RGI_BRANCH_DESTINATION_UNPROVEN
    ${destination_mode}=    Set Variable If    ${external_foreground}    EXTERNAL_WEBVIEW    IN_APP_WEBVIEW
    Log    FULL_SCREEN_RGI_BRANCH_DESTINATION=PROVEN mode=${destination_mode}    INFO
    RETURN    ${destination_mode}

Close Full Screen RGI Branch Destination
    [Arguments]    ${destination_mode}
    IF    '${destination_mode}' == 'IN_APP_WEBVIEW'
        ${width}=    Get Window Width
        ${height}=    Get Window Height
        ${controls}=    Get WebElements    xpath=//*[@resource-id="security-error-container"]//android.view.ViewGroup[@clickable="true"]
        ${header_controls}=    Evaluate    [e for e in $controls if e.rect['x'] >= int(float($width) * 0.75) and e.rect['y'] < int(float($height) * 0.2)]
        ${control_count}=    Get Length    ${header_controls}
        Should Be True    ${control_count} >= 1    FULL_SCREEN_RGI_BRANCH_CLOSE_CONTROL_UNPROVEN
        ${close_control}=    Evaluate    max($header_controls, key=lambda e: e.rect['x'])
        ${close_rect}=    Evaluate    $close_control.rect
        ${close_x}=    Evaluate    int(${close_rect['x']} + (${close_rect['width']} / 2))
        ${close_y}=    Evaluate    int(${close_rect['y']} + (${close_rect['height']} / 2))
        Execute Adb Shell    input    tap    ${close_x}    ${close_y}
        Wait Until Keyword Succeeds    5s    300ms    Full Screen RGI In-App Branch WebView Should Be Closed
        Log    FULL_SCREEN_RGI_BRANCH_RETURN=IN_APP_CLOSE_CONTROL    INFO
    ELSE IF    '${destination_mode}' == 'EXTERNAL_WEBVIEW'
        Execute Adb Shell    input    keyevent    4
        Log    FULL_SCREEN_RGI_BRANCH_RETURN=ANDROID_BACK    INFO
    ELSE
        Fail    FULL_SCREEN_RGI_BRANCH_DESTINATION_MODE_UNSUPPORTED
    END

Full Screen RGI In-App Branch WebView Should Be Closed
    ${source_status}    ${source}=    Run Keyword And Ignore Error    Get Source
    Should Be Equal As Strings    ${source_status}    PASS    FULL_SCREEN_RGI_BRANCH_RETURN_SOURCE_UNAVAILABLE
    Should Not Be Empty    ${source}    FULL_SCREEN_RGI_BRANCH_RETURN_SOURCE_EMPTY
    ${webview}=    Run Keyword And Return Status    Should Contain    ${source}    android.webkit.WebView
    Should Not Be True    ${webview}    FULL_SCREEN_RGI_BRANCH_WEBVIEW_STILL_OPEN

Tap Full Screen RGI Close App And Verify
    Tap Full Screen RGI Close App
    Wait Until Keyword Succeeds    ${NCBD_LOADING_TIMEOUT}    500ms    Full Screen RGI App Is Closed

Full Screen RGI App Is Closed
    ${foreground}=    Get Foreground Component    ${DEVICE_UDID}
    Should Not Be Empty    ${foreground}    FULL_SCREEN_RGI_CLOSE_APP_FOREGROUND_UNKNOWN
    ${closed}=    Evaluate    not str($foreground).startswith($APP_PACKAGE + '/')
    Should Be True    ${closed}    FULL_SCREEN_RGI_CLOSE_APP_DID_NOT_LEAVE_APP

Handle Expected Full Screen RGI
    [Arguments]    ${expected_error_code}    ${expected_message}=${NONE}    ${action_policy}=STANDARD_FIND_BRANCH_CLOSE_APP
    Assert Full Screen RGI    ${expected_error_code}    ${expected_message}    ${action_policy}
    IF    '${action_policy}' == 'STANDARD_FIND_BRANCH_CLOSE_APP'
        Open Full Screen RGI Branch And Return    ${expected_error_code}
        Tap Full Screen RGI Close App And Verify
    END
