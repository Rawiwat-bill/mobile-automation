*** Variables ***
${CHECK_DOPA_FILL_LASER_CODE_TITLE_TEXT}        xpath=//android.widget.TextView[@resource-id="screenPersonalInformation_navBarTitleList"]
${CHECK_DOPA_FILL_LASER_CODE_BUTTON_NEXT}       xpath=//android.widget.Button[@content-desc="Next"]

${FIELD_LASER_CODE1}                            xpath=(//android.widget.TextView[@content-desc="Laser Code"]//parent::android.view.ViewGroup//following-sibling::android.view.ViewGroup//android.widget.EditText[@resource-id="text-input-flat"])[1]
${FIELD_LASER_CODE2}                            xpath=(//android.widget.TextView[@content-desc="Laser Code"]//parent::android.view.ViewGroup//following-sibling::android.view.ViewGroup//android.widget.EditText[@resource-id="text-input-flat"])[2]
${FIELD_LASER_CODE3}                            xpath=(//android.widget.TextView[@content-desc="Laser Code"]//parent::android.view.ViewGroup//following-sibling::android.view.ViewGroup//android.widget.EditText[@resource-id="text-input-flat"])[3]
