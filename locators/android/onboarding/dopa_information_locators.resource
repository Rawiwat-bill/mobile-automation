*** Variables ***
${DOPA_INFORMATION_SCREEN}                    xpath=//*[contains(@resource-id,"screenDopaInformation")]
# ponytail: 'dropdown' is a generic id, but it is the only dropdown on the DOPA screen (the Title selector).
${DOPA_TITLE_DROPDOWN}                        xpath=//*[@resource-id="dropdown"]
# displayed value lives in the dropdown's child TextView; the ViewGroup's own text="" (verified via Appium XML).
${DOPA_TITLE_VALUE}                           xpath=//*[@resource-id="dropdown"]//*[@resource-id="text"]
${DOPA_FIRST_NAME_ENG_INPUT}                  xpath=//*[@text="Enter first name in English"]
${DOPA_LAST_NAME_ENG_INPUT}                   xpath=//*[@text="Enter last name in English"]
${DOPA_DATE_OF_ISSUE_INPUT}                   xpath=//android.widget.EditText[contains(@resource-id,"screenDopaInformation_inputDateOfIssue")]
${DOPA_DATE_OF_EXPIRE_INPUT}                  xpath=//android.widget.EditText[contains(@resource-id,"screenDopaInformation_inputDateOfExpire")]
${DOPA_NEXT_BUTTON_CONTAINER}                 xpath=//*[contains(@resource-id,"base-btn-container")]
${DOPA_DATE_PICKER_YEAR}                      xpath=//*[contains(@resource-id,"datePicker-yearScroll")]
${DOPA_DATE_PICKER_MONTH}                     xpath=//*[contains(@resource-id,"datePicker-monthScroll")]
${DOPA_DATE_PICKER_DAY}                       xpath=//*[contains(@resource-id,"datePicker-dateScroll")]
${DOPA_DATE_PICKER_CONFIRM}                   xpath=//*[@content-desc="Done"]
