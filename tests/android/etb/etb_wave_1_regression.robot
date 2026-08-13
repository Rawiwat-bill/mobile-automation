*** Settings ***
Documentation    Data-driven ETB RGI regression cases for Wave 1.
Resource         ../../../resources/app/app_keywords.resource
Resource         ../../../resources/keywords/etb/etb_keywords.resource
Resource         ../../../resources/keywords/etb/etb_regression_keywords.resource
Library          ../../../libraries/robot_output_sanitizer.py

Test Setup       Open Mobile Application
Test Teardown    Close Application

*** Test Cases ***
TC-ETB-005 Mobile Number Mismatch RGI Popup
    Run ETB Expected RGI Case    etb_tc_005    Handle Expected RGI Popup

TC-ETB-006 DOB Mismatch RGI Popup
    Run ETB Expected RGI Case    etb_tc_006    Handle Expected RGI Popup
