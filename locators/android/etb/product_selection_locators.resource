*** Variables ***
${PRODUCT_SELECTION_TITLE}          id=screenProductSelection_textTitle
${PRODUCT_SELECTION_DESCRIPTION}    id=screenProductSelection_textDescription
${PRODUCT_SELECTION_CHECKBOXES}     xpath=//*[starts-with(@resource-id,"screenProductSelection_flatListCardsCheckBox_")]
${PRODUCT_SELECTION_PRODUCT_NAMES}    xpath=//*[starts-with(@resource-id,"screenProductSelection_flatListCardsTextProductName_")]
${PRODUCT_SELECTION_CONFIRM}        id=screenProductSelection_buttonConfirm
${PRODUCT_SELECTION_CONFIRM_RESOURCE}    xpath=//*[@resource-id="screenProductSelection_buttonConfirm"]
${PRODUCT_SELECTION_CONFIRM_BUTTON}      xpath=//*[@resource-id="screenProductSelection_buttonConfirm-base"]
${PRODUCT_SELECTION_ROWS}           xpath=//*[starts-with(@resource-id,"screenProductSelection_flatListCardsTouchableOpacity_")]
${PRODUCT_SELECTION_ROW_NAME_XPATH}    .//*[starts-with(@resource-id,"screenProductSelection_flatListCardsTextProductName_")]
# Build 208 visible selection summary; no stable resource-id was captured for this label.
${PRODUCT_SELECTION_SELECTED_SUMMARY}    xpath=//*[contains(@text," selected")]
${PRODUCT_SELECTION_RETRIEVAL_ERROR}     xpath=//*[@resource-id="screenProductSelection_textTryAgain"]
${PRODUCT_SELECTION_REFRESH}             xpath=//*[@resource-id="screenProductSelection_buttonRefresh"]
