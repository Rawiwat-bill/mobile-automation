*** Variables ***
${TERMS_AND_CONDITIONS_TITLE_TEXT}              xpath=//android.widget.TextView[@text="Terms and Conditions"]
${TERMS_AND_CONDITIONS_WEBVIEW}                 xpath=//android.webkit.WebView
${TERMS_AND_CONDITIONS_LAST_PARAGRAPH_TEXT}     xpath=//android.widget.TextView[@text="I have read and understood the terms and conditions set forth above, and agreed to be bound by such terms and conditions as from the date I indicated my acceptance by pressing the ‘Accept’ button. "]
${TERMS_AND_CONDITIONS_ACCEPT_BUTTON}           xpath=//android.widget.Button[(@content-desc="Accept" or @text="Accept")]
