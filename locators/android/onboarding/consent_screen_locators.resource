*** Variables ***
${CONSENT_TITLE_TEXT}        xpath=//*[@text="Terms and Conditions"]
${CONSENT_WEBVIEW}           xpath=//android.widget.ScrollView[@scrollable="true"]
${CONSENT_ACCEPT_BUTTON}     accessibility_id=Accept
${CONSENT_BOTTOM_MARKER}     xpath=//android.widget.TextView[contains(@text, "I have read and understood")]
