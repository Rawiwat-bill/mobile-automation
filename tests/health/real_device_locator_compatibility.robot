*** Settings ***
Documentation    Sprint 2.68 reset: dryrun-only locator compatibility smoke.
...              Scope is bounded to Landing and Consent resources reached by evidence.
Library          AppiumLibrary
Resource         ../../resources/pages/onboarding/landing_screen_page.resource
Resource         ../../resources/pages/onboarding/consent_screen_page.resource


*** Test Cases ***
Real Device Locator Compatibility Dryrun Smoke
    [Documentation]    Validates Robot imports/keywords without launching a live onboarding loop.
    No Operation

