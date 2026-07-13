*** Variables ***
${TELL_US_ABOUT_YOU_TITLE_TEXT}                 xpath=//android.widget.TextView[@text="Tell us about you"]

${TELL_US_ABOUT_YOU_CITIZEN_ID_CONTAINER}       xpath=//android.view.ViewGroup[@resource-id="cid-container"]
${TELL_US_ABOUT_YOU_CID_INPUT}                  xpath=//android.widget.EditText[@resource-id="cid"]

${TELL_US_ABOUT_YOU_DOB_CONTAINER}              xpath=//*[@resource-id="screenProfile_textInputDob-container"]
${TELL_US_ABOUT_YOU_DOB_INPUT}                  xpath=//android.widget.EditText[@content-desc="profile_screen.dob"]
${TELL_US_ABOUT_YOU_DOB_DATE_PICKER}            xpath=//*[@resource-id="screenProfile_calendarDatePicker-selectedHeaderWrapper"]

${TELL_US_ABOUT_YOU_SEEKBAR_YEAR}               xpath=//android.widget.SeekBar[@resource-id="screenProfile_calendarDatePicker-yearScroll"]
${TELL_US_ABOUT_YOU_SEEKBAR_MONTH}              xpath=//android.widget.SeekBar[@resource-id="screenProfile_calendarDatePicker-monthScroll"]
${TELL_US_ABOUT_YOU_SEEKBAR_DAY}                xpath=//android.widget.SeekBar[@resource-id="screenProfile_calendarDatePicker-dateScroll"]
