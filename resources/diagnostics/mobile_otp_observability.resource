*** Settings ***
Documentation    Mobile OTP diagnostic/evidence adapter for unexpected Android resolver capture.
Library          AppiumLibrary
Library          OperatingSystem
Library          ../../libraries/evidence_scope.py


*** Keywords ***
Capture Unexpected Android Resolver Evidence
    [Arguments]    ${output_dir}
    ${evidence_dir}=    Resolve Private Evidence Dir    ${output_dir}
    Capture Page Screenshot    ${evidence_dir}/android_resolver_unexpected.png
    ${source}=    Get Source
    ${sanitized_source}=    Evaluate    __import__('re').sub(r'(?i)(text|content-desc|hint|value|password)="[^"]*"', r'\\1="[REDACTED]"', $source)
    Create File    ${evidence_dir}/android_resolver_unexpected.xml    ${sanitized_source}
