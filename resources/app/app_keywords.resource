*** Settings ***
Library    AppiumLibrary


*** Variables ***
${ANDROID_PERMISSION_ALLOW_BUTTON}    id=com.android.permissioncontroller:id/permission_allow_button
${ANDROID_PERMISSION_DENY_BUTTON}     id=com.android.permissioncontroller:id/permission_deny_button


*** Keywords ***
Allow Android Permission If Visible
    ${is_visible}=    Run Keyword And Return Status    Element Should Be Visible    ${ANDROID_PERMISSION_ALLOW_BUTTON}
    IF    ${is_visible}
        Click Element    ${ANDROID_PERMISSION_ALLOW_BUTTON}
    END
