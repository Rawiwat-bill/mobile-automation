*** Settings ***
Documentation    Data-driven ETB full-screen RGI regression cases for Wave 2.
Resource         ../../../resources/app/app_keywords.resource
Resource         ../../../resources/keywords/etb/etb_keywords.resource
Resource         ../../../resources/keywords/etb/etb_regression_keywords.resource
Library          ../../../libraries/robot_output_sanitizer.py

Test Setup       Open Mobile Application
Test Teardown    Close Application

*** Test Cases ***
TC-ETB-007 Expired Citizen ID Full-Screen RGI
    Run ETB Expected RGI Case    etb_tc_007    Handle Expected Full Screen RGI

TC-ETB-012 Low IAL Full-Screen RGI
    Run ETB Expected RGI Case    etb_tc_012    Handle Expected Full Screen RGI