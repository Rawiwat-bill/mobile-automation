*** Variables ***
${SETUP_PIN_TITLE_TEXT}         xpath=//android.widget.TextView[@resource-id='screenPinInput_headerText']
${RE_ENTER_PIN_TITLE_TEXT}      xpath=//android.widget.TextView[@content-desc="Re-enter PIN to confirm"]

${SETUP_PIN_KEY_PIN}            xpath=//android.widget.TextView[@text="{{pin}}"]

${SETUP_PIN_FIELD_1}            xpath=//android.widget.ViewGroup[@content-desc="1"]
${SETUP_PIN_FIELD_2}            xpath=//android.widget.ViewGroup[@content-desc="2"]
${SETUP_PIN_FIELD_3}            xpath=//android.widget.ViewGroup[@content-desc="3"]
${SETUP_PIN_FIELD_4}            xpath=//android.widget.ViewGroup[@content-desc="4"]
${SETUP_PIN_FIELD_5}            xpath=//android.widget.ViewGroup[@content-desc="5"]
${SETUP_PIN_FIELD_6}            xpath=//android.widget.ViewGroup[@content-desc="6"]
${SETUP_PIN_FIELD_7}            xpath=//android.widget.ViewGroup[@content-desc="7"]
${SETUP_PIN_FIELD_8}            xpath=//android.widget.ViewGroup[@content-desc="8"]
${SETUP_PIN_FIELD_9}            xpath=//android.widget.ViewGroup[@content-desc="9"]
${SETUP_PIN_FIELD_0}            xpath=//android.widget.ViewGroup[@content-desc="0"]

${SETUP_PIN_FIELD_REMOVE}       xpath=//android.view.ViewGroup[@content-desc="remove"]

${LAYER_LOADING}                xpath=(//android.view.ViewGroup[@resource-id="container"])[2]//android.view.ViewGroup[last()]/android.widget.ImageView

${BUTTON_CONFIRM}               xpath=//android.widget.Button[@content-desc="Confirm"]
${LABEL_ETB_FINISHED}           xpath=//android.widget.TextView[@text="You’re all set!"]
${BUTTON_LETGO}                 xpath=//android.widget.Button[@content-desc="Let’s go"]
