# Robot Framework Playbook

## When to Use
- Writing a new test case or test suite
- Creating or modifying Robot Framework keywords
- Organizing resource files
- Debugging Robot Framework syntax or variable issues
- Applying RF7+ compatibility fixes

## Inputs Required
- Test scenario description (from task or feature spec)
- Existing test structure (NTB, ETB, or common)
- Test data values (from YAML data files)

## Evidence Required
- Dryrun output for syntax validation
- Robot log for runtime behavior
- Existing similar tests or keywords as reference

## Step-by-Step Workflow
1. Identify the feature and customer type (NTB, ETB, common).
2. Check existing test files for similar flows that can be extended.
3. Check existing keyword resources for reusable keywords.
4. Write or update test cases:
   - Use business-readable test case names.
   - Keep test cases in the appropriate suite file.
   - Load test data from YAML, never hardcode.
5. Write or update keywords:
   - Screen-level keywords in page resource files.
   - Business flow keywords in keyword resource files.
   - Reuse before create.
6. If RF7+ compatibility is needed:
   - Use `$var[0]` syntax (not `${var}[0]`) in IF conditions.
   - Avoid deprecated `:FOR` loop syntax.
7. Never use `Sleep` — use explicit waits.
8. Never embed locators or test data in test files.
9. Never log sensitive values.

## Validation
- Dry run: `python3 -m robot --dryrun <test_path>`.
- Run focused test: `python3 -m robot -d reports <test_path>` (only when requested).
- Check that all keywords are used, no unused imports.

## Output Format
Summary:
Files Checked:
Files Changed:
Keywords Added:
Validation Command:
Validation Result:
Risk / Note:

## Stop Conditions
- **Evidence missing** — do not change Robot code for flaky tests without screenshots and XML.
- **Manual success not compared** — stop and ask user for manual flow comparison.
- **Test data missing** — stop and ask user for required test data.
- **Broad refactor** — do not refactor broadly without explicit approval.
- **Unrelated files** — do not modify files outside Allowed Files.
