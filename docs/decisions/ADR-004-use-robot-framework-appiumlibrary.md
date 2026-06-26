# ADR-004: Use Robot Framework with AppiumLibrary

## Status
Accepted

## Context
The project required a test automation framework for mobile banking that supports:
- Business-readable test syntax for non-technical stakeholders
- Mobile-specific interaction capabilities (gestures, device control, app management)
- Clear separation of concerns (test data, page objects, locators)
- Cross-platform support (Android first, iOS future)
- CI/CD pipeline compatibility

## Decision
Use Robot Framework as the test automation framework with AppiumLibrary as the mobile automation library.

Rationale:
- Robot Framework provides business-readable keyword-driven syntax
- AppiumLibrary provides Appium client integration for Android and iOS
- Page Object style is naturally supported through resource files
- YAML test data separation via custom Python libraries
- Robot Framework's dryrun and report generation support CI workflows

## Consequences
**Positive:**
- Readable test cases: `Input Citizen ID`, `Tap Profile Next`
- Resource isolation: page keywords, locators, test data each in their own files
- Built-in reporting and logging
- Dryrun validation for syntax checking
- Active community and library ecosystem

**Negative:**
- Robot Framework's variable syntax can conflict with newer versions (RF7+ changes IF expression syntax)
- AppiumLibrary abstracts some Appium details that matter for debugging
- RF's `Run Keyword And Ignore Error` pattern for result handling requires care with RF7+
- Custom Python libraries needed for YAML loading and config management

## Related
- `knowledge/robotframework.md` — Project-specific patterns and conventions
- `docs/principles/engineering-principles.md` — Principle 5: Separation by Concern

## Compliance
- All Robot code must follow documented naming conventions
- Page keywords separated by screen
- Locators outside test files
- Dryrun validation before execution
