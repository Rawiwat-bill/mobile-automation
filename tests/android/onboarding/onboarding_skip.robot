*** Settings ***
Library    AppiumLibrary

*** Test Cases ***
Open Application Test

    Open Application
    ...    http://127.0.0.1:4723
    ...    platformName=Android
    ...    automationName=UiAutomator2
    ...    deviceName=Android Emulator
    ...    appPackage=com.bangkokbank.blue.dev
    ...    appActivity=com.bangkokbank.blue.MainActivity
    ...    noReset=true

    Capture Page Screenshot

    Close Application