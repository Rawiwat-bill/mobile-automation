# ADR-003: Use YAML for Test Data Separation

## Status
Accepted

## Context
Test data (Citizen ID, DOB, Mobile Number) was initially hardcoded in test cases. This made tests brittle, difficult to maintain across environments, and insecure (sensitive data visible in test code). The project needed a data separation pattern.

## Decision
Separate test data into YAML files loaded at runtime via a Python `config_loader`.

Structure:
```
testdata/onboarding/
├── ntb.example.yaml       # Example data (committed, clearly non-real)
├── ntb.local.yaml         # Local overrides (gitignored)
├── etb.example.yaml       # Example data (committed)
└── etb.local.yaml         # Local overrides (gitignored)
```

Loading mechanism:
```robot
${data}=    Load YAML    ${TESTDATA}
${citizen_id}=    Set Variable    ${data['profile']['citizen_id']}
```

## Consequences
**Positive:**
- Test data separated from test logic
- Sensitive data stays in gitignored local files
- Example data in Git is clearly non-real
- Easy to switch environments by changing the YAML file

**Negative:**
- Additional indirection when reading tests
- Data lookup errors only surface at runtime

## Security
- Real PII must never be in committed YAML files
- Local YAML files must be gitignored
- Masked values in examples: `1111111111111`, `0811111111`

## Compliance
- Security agent checks YAML files for real-looking sensitive data
- Review agent rejects hardcoded data in test cases
- Config loader library must not log data values
