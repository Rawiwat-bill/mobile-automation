# Test Data Pattern

## Problem
Hardcoding test data (Citizen ID, DOB, Mobile Number) in test cases makes tests brittle, difficult to maintain across environments, and insecure when sensitive data is visible in version control.

## Recommended Pattern
- Store test data in YAML files at `testdata/onboarding/<customer_type>.yaml`.
- Committed files contain example data only (clearly non-real).
- Local overrides use `.local.yaml` suffix and are gitignored.
- Load data at runtime via `Load YAML` from `config_loader.py`.
- Test cases reference variables from the loaded data structure.

## Anti-Pattern
- Hardcoding `1111111111111` directly in a test case.
- Storing real customer data in committed YAML files.
- Using `.robot` files for test data storage.
- Mixing multiple customer types in a single data file.

## Example
```robot
# testdata/onboarding/ntb.example.yaml
profile:
  citizen_id: "1111111111111"
  date_of_birth: "1990-01-01"
  mobile_number: "0811111111"

# In test:
${data}=    Load YAML    ${TESTDATA}
Complete Common Onboarding    ${data['profile']['citizen_id']}    ${data['profile']['date_of_birth']}    ${data['profile']['mobile_number']}
```

## When Not to Use
- For configuration values that are the same across environments (Appium caps, device config) — use config files instead.
- For test-specific overrides for a single test case — use local variables with a comment explaining the override.
