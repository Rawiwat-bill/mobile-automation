*** Settings ***
Resource    ../../../resources/pages/onboarding/landing_screen_page.resource


*** Test Cases ***
Skip Onboarding From Landing Screen
    Landing Screen Should Be Visible
    Skip Landing Screen
