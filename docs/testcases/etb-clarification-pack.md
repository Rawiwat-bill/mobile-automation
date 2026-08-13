# ETB Regression Business Clarification Pack

Status: OPEN — only executable ambiguities require business resolution before implementation.

Source: `docs/source/testcases/etb/current/QA_TestCase_OPO_ETB Registration_Automation.xlsx`, sheet `Test Cases`.

Canonical interpretation:

1. Pre Condition
2. Expected Result / Expected (PostMMP)
3. Remark / Notes
4. Test Case Name

Worksheet test profiles are presumed prepared for their stated branches. Runtime evidence may reclassify a prepared profile only when the expected branch is not reached, the environment state changes, data expires, or additional setup is proven necessary.

No UI test-data values are reproduced in this document.

## TC-ETB-001 — PDPA title/expected-result conflict (non-blocking interpretation note)

- Workbook row: 4
- Relevant columns: `Testcase`, `Expected Result`
- Official test case: Customer is Pass all registration conditions and answer PDPA clause 6 = Accept
- Sanitized source statements:
  - Testcase states that the customer answers PDPA Clause 6 = Accept.
  - Expected Result says the PDPA screen is not displayed.
- Conflict: The title requires PDPA acceptance while the expected result requires PDPA absence.
- Interpretation: The Test Case Name conflicts with Expected Result. Execution planning follows Expected Result, which says the PDPA screen is not displayed.
- BA/QA question retained: Should the descriptive title be corrected to match the executable Expected Result?
- Implementation impact: The post-OTP assertion must follow Expected Result; this is not a runtime readiness blocker.
- May remain enabled: Yes.

## TC-ETB-003 — Product Selection contradiction

- Workbook row: 6
- Relevant column: `Expected Result`
- Official test case: Customer not have active Savings account
- Sanitized source statements:
  - Expected Result says Select Product is not displayed and is skipped.
  - The same Expected Result also says Select Product is displayed.
- Conflict: One expected-result cell specifies mutually exclusive Product Selection outcomes.
- BA/QA question: For a customer without an active Savings account, is Select Product skipped or displayed, and what downstream screen is expected?
- Implementation impact: Determines whether the shared Product Selection keyword is called or bypassed.
- May remain enabled: Yes; the Select Product wording conflict is an informational
  clarification note, not an execution blocker. Runtime evidence records the
  observed behavior while execution follows Expected Result / Expected (PostMMP).

## TC-ETB-013 — Warning versus terminal rejection (non-blocking precedence note)

- Workbook row: 16
- Relevant columns: `Testcase`, `Expected Result`, `Notes`
- Official test case: Customer is suspect for mule account (Warning)
- Sanitized source statements:
  - Testcase name labels the case as a mule-account Warning.
  - Expected Result specifies full-screen RGI-016, Find a branch, and Close App.
  - Notes contain Result Flag W and Status H.
- Interpretation: Warning terminology and flags conflict with Expected Result. Execution planning follows Expected Result: RGI-016, Find a branch, and Close App.
- BA/QA question retained: Should the descriptive title/remark be corrected to match the executable Expected Result?
- Implementation impact: The terminal-state router follows Expected Result; runtime evidence may reclassify the prepared profile if that branch is not reached.
- May remain enabled: Yes.

## TC-ETB-008 through TC-ETB-011 — 3X disposition note (non-blocking)

| Case | Workbook row | Notes subtype |
|---|---:|---|
| TC-ETB-008 | 11 | 3A |
| TC-ETB-009 | 12 | 3V |
| TC-ETB-010 | 13 | 3U |
| TC-ETB-011 | 14 | 3B |

- Relevant columns: `Testcase`, `Notes`
- Official test case name for all four rows: Customer is high risk (3X, 3U, 3V, 3A, 3B)
- Sanitized source statements:
  - The Testcase title lists five possible subtypes: 3X, 3U, 3V, 3A, and 3B.
  - The four Notes cells identify only 3A, 3V, 3U, and 3B.
- Interpretation: Four rows identify 3A, 3V, 3U, and 3B. The shared Expected Result is executable without inventing a 3X mapping.
- BA/QA question retained: Which prepared profile represents 3X, or is 3X out of scope for this regression pack?
- Implementation impact: Keep subtype notes as supplied; do not create a fifth case without explicit evidence. This is not a readiness blocker for the four existing rows.
- May remain enabled: Yes, subject to runtime evidence.

## Readiness and PDPA reset update

- Worksheet test profiles are presumed prepared for their respective Pre Condition and Expected Result.
- Runtime execution will verify that the prepared state is still effective.
- TC-ETB-002 is held by `PDPA_RESET_CURL_PENDING` because its Pre Condition requires deleting existing PDPA consent.
- The required remark is: Waiting for the team-provided curl command to delete or reset PDPA state.
- TC-ETB-002 is the only case currently held by the missing curl command.
- Non-PDPA cases are not blocked by the missing curl command.
- TC-ETB-001 and TC-ETB-003 through TC-ETB-013 are approved to proceed; wording
  clarifications remain informational and non-blocking.
- The approved DEV shared-default policy makes TC-ETB-002, TC-ETB-003, TC-ETB-004, and TC-ETB-013 UI-data-ready.
- The actual UI values remain only in the ignored local runtime data file. No values are reproduced here.

## Decision gate

The following are required before implementation of the affected branches:

1. Obtain the team-provided PDPA reset curl before executing TC-ETB-002.
2. Retain the TC-ETB-001, TC-ETB-003, TC-ETB-013, and 3X questions as documentation notes; do not block prepared profiles solely on title/remark wording.
3. Capture Appium XML and screenshots for the RGI and positive downstream screens before locator creation.
