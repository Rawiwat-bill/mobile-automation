*** Settings ***
Documentation    ETB post-PIN state classification and registration-success interactions.
Library          AppiumLibrary
Resource         ../../contracts/flow_states.resource
Resource         product_selection_page.resource
Resource         ../../../resources/app/app_constants.resource
Resource         ../../../locators/android/etb/setup_pin_locators.resource
Resource         ../../../resources/keywords/appium_expectations.resource

*** Variables ***
${ETB_PRESET_SUCCESS_TITLE}    xpath=//*[contains(translate(@text,'ABCDEFGHIJKLMNOPQRSTUVWXYZ','abcdefghijklmnopqrstuvwxyz'),'all set') or contains(translate(@content-desc,'ABCDEFGHIJKLMNOPQRSTUVWXYZ','abcdefghijklmnopqrstuvwxyz'),'all set')]
${ETB_PRESET_PASSKEY}          xpath=//*[contains(translate(@text,'ABCDEFGHIJKLMNOPQRSTUVWXYZ','abcdefghijklmnopqrstuvwxyz'),'passkey') or contains(translate(@content-desc,'ABCDEFGHIJKLMNOPQRSTUVWXYZ','abcdefghijklmnopqrstuvwxyz'),'passkey')]
${ETB_PRESET_ADD_EMAIL}        xpath=//*[contains(translate(@text,'ABCDEFGHIJKLMNOPQRSTUVWXYZ','abcdefghijklmnopqrstuvwxyz'),'add email') or contains(translate(@content-desc,'ABCDEFGHIJKLMNOPQRSTUVWXYZ','abcdefghijklmnopqrstuvwxyz'),'add email')]
${ETB_PRESET_SET_PASSKEY}      xpath=//*[contains(translate(@text,'ABCDEFGHIJKLMNOPQRSTUVWXYZ','abcdefghijklmnopqrstuvwxyz'),'set passkey') or contains(translate(@content-desc,'ABCDEFGHIJKLMNOPQRSTUVWXYZ','abcdefghijklmnopqrstuvwxyz'),'set passkey')]


*** Keywords ***
Probe Post First PIN State
    [Documentation]    Classify the immediate post-first-PIN business state from the active screen.
    ${source}=    Get Source
    IF    '${FLOW_STATE_GOD_005}' in $source
        RETURN    ${FLOW_STATE_GOD_005}
    END
    IF    'screenReEnterPinInput_keyPad' in $source
        RETURN    ${FLOW_STATE_CONFIRM_PIN}
    END
    IF    'screenProductSelection_textTitle' in $source or 'screenProductSelection_textDescription' in $source
        RETURN    ${FLOW_STATE_PRODUCT_SELECTION}
    END
    IF    "You're all set!" in $source or "You’re all set!" in $source or "Let's go" in $source or "Let’s go" in $source
        RETURN    ${FLOW_STATE_COMPLETION_SUCCESS}
    END
    IF    '${FLOW_STATE_AJI_001}' in $source or 'RGI-' in $source
        RETURN    ${FLOW_STATE_EXACT_ERROR}
    END
    IF    'screenPinInput' in $source or 'loading' in $source.lower()
        RETURN    ${FLOW_STATE_LOADING_OR_INTERMEDIATE}
    END
    RETURN    ${FLOW_STATE_UNKNOWN}

Probe Stable Post First PIN State
    [Documentation]    Retry transient loading/unknown states; return only a recognized business state to the caller.
    ${state}=    Probe Post First PIN State
    IF    '${state}' == '${FLOW_STATE_LOADING_OR_INTERMEDIATE}' or '${state}' == '${FLOW_STATE_UNKNOWN}'
        Fail    POST_FIRST_PIN_STATE_NOT_STABLE=${state}
    END
    RETURN    ${state}

ETB Post PIN Destination Should Be Displayed
    [Documentation]    Return the recognized post-PIN destination or fail while retry budget remains.
    ${source}=    Get Source
    IF    '${FLOW_STATE_GOD_005}' in $source
        RETURN    ${FLOW_STATE_GOD_005}
    END
    ${product_visible}=    Run Keyword And Return Status
    ...    Product Selection Screen Should Be Displayed
    IF    ${product_visible}
        RETURN    ${FLOW_STATE_PRODUCT_SELECTION}
    END
    IF    'screenProductSelection_textTitle' in $source or 'screenProductSelection_textDescription' in $source
        RETURN    ${FLOW_STATE_PRODUCT_SELECTION}
    END
    ${aji_visible}=    Run Keyword And Return Status
    ...    Should Contain    ${source}    ${FLOW_STATE_AJI_001}
    IF    ${aji_visible}
        RETURN    ${FLOW_STATE_ENVIRONMENT_BACKEND_AJI_001}
    END
    ${finished_visible}=    Run Keyword And Return Status
    ...    Element Should Be Visible Now    ${LABEL_ETB_FINISHED}
    IF    ${finished_visible}
        RETURN    ${FLOW_STATE_REGISTRATION_SUCCESS}
    END
    IF    "You're all set!" in $source or "You’re all set!" in $source or "Let's go" in $source or "Let’s go" in $source
        RETURN    ${FLOW_STATE_REGISTRATION_SUCCESS}
    END
    Fail    ETB_POST_PIN_DESTINATION_NOT_VISIBLE

Wait Until Registration Success Is Displayed
    Wait Until Element Is Visible    ${LABEL_ETB_FINISHED}    ${NCBD_LOADING_TIMEOUT}

Assert ETB Release Pre-SET
    [Documentation]    Enforce the sourced release-specific Pre-SET contract before continuing.
    ${release}=    Get Variable Value    ${ETB_PRODUCT_RELEASE}    POST_MMP_1
    Wait Until Element Is Visible    ${ETB_PRESET_SUCCESS_TITLE}    ${NCBD_LOADING_TIMEOUT}
    IF    '${release}' == 'MMP_LOT2_V2'
        # The MMP contract forbids the whole visible Passkey section, not only
        # the Post-MMP wording "Set Passkey".
        ${forbidden_visible}=    Run Keyword And Return Status    Element Should Be Visible Now    ${ETB_PRESET_PASSKEY}
        Should Not Be True    ${forbidden_visible}    MMP_PRESET_PASSKEY_MUST_NOT_DISPLAY
    ELSE IF    '${release}' == 'POST_MMP_1'
        Wait Until Element Is Visible    ${ETB_PRESET_PASSKEY}    ${NCBD_LOADING_TIMEOUT}
        Wait Until Element Is Visible    ${ETB_PRESET_ADD_EMAIL}    ${NCBD_LOADING_TIMEOUT}
    ELSE
        Fail    ETB_PRODUCT_RELEASE_INVALID=${release}
    END

Tap Registration Success Continue
    Wait Until Element Is Visible    ${BUTTON_LETGO}    ${NCBD_LOADING_TIMEOUT}
    Click Element    ${BUTTON_LETGO}
