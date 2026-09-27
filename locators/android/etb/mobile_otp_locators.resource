*** Variables ***
${MOBILE_OTP_TITLE_TEXT}    xpath=//android.widget.TextView[@resource-id='screenVerifyMobileNumberOTP_textTitle']

${MOBILE_OTP_REF_CODE}      xpath=//android.widget.TextView[contains(@text,"Reference")]

${MOBILE_OTP_INPUT}         xpath=//*[@resource-id="screenVerifyMobileNumberOTP_inputCodeOTP"]
${FIELD_OTP0}               xpath=//android.widget.TextView[@resource-id="input-code-cell-0"]

${ANDROID_RESOLVER_TITLE}    id=android:id/title
${ANDROID_RESOLVER_TARGET_XPATH_TEMPLATE}    //*[@resource-id="android:id/text1" and @text="__ANDROID_RESOLVER_TARGET_LABEL__"]
${ANDROID_RESOLVER_ONCE}    id=android:id/button_once
${ANDROID_RESOLVER_ALWAYS}  id=android:id/button_always
