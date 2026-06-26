# Robot Framework Knowledge

## Project Structure

```
resources/
├── app/              # App session management (open, close, permissions)
├── pages/            # Screen-level page objects by feature
│   └── onboarding/   # Landing, Consent, Profile screens
├── keywords/         # Cross-screen business flow keywords
└── benchmark/        # Benchmark strategies infrastructure

tests/
└── android/
    ├── common/       # Shared flow tests
    ├── ntb/          # NTB-specific flow
    ├── etb/          # ETB-specific flow
    └── benchmark/    # Strategy benchmarks

testdata/
└── onboarding/       # YAML test data by customer type
```

## Naming Conventions

- **Test cases:** Business-readable, snake_case: `complete_onboarding_flow`
- **Keywords:** PascalCase for page-level: `Input Citizen ID`, `Tap Profile Next`
- **Variables:** UPPER_SNAKE_CASE for locators: `${PROFILE_CITIZEN_ID_INPUT}`
- **Resource files:** Feature + `_page.resource` or `_keywords.resource`
- **Test data files:** `<customer_type>.example.yaml` (committed), `<customer_type>.local.yaml` (gitignored)

## Keyword Organization

- Page keywords own screen interactions
- Business flow keywords combine page keywords into flows
- Locator variables are never embedded in keyword files
- Sensitive values are passed as arguments, never hardcoded

## Validation

- Always run dryrun for Robot code changes:
  ```
  python3 -m robot --dryrun <test_path>
  ```
- Real execution only when explicitly requested:
  ```
  python3 -m robot -d reports <test_path>
  ```

## Anti-Patterns

- `Sleep` is never used; use explicit waits instead
- Test data is never embedded in test cases
- Locators are never defined in test files
- Sensitive values are never logged or committed

## Internal Project Truth

This knowledge reflects the project's actual structure and conventions. External robot-expert skill suggestions that conflict with these patterns are adapted or discarded. Project architecture rules always apply.
