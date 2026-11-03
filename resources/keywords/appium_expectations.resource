*** Settings ***
Documentation    Canonical Appium assertions for immediate, non-waiting element probes.
Library          AppiumLibrary


*** Keywords ***
Element Should Be Visible Now
    [Documentation]    Perform exactly one visibility observation without the deprecated Element Should Be Visible keyword.
    [Arguments]    ${locator}
    Wait Until Element Is Visible    ${locator}    0s

Element Is Visible Now
    [Arguments]    ${locator}
    ${status}=    Run Keyword And Return Status    Element Should Be Visible Now    ${locator}
    RETURN    ${status}
