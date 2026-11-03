# BBL ETB Acceptance Snapshot — 2026-09-27

Purpose: compact source-of-truth snapshot retained before redundant run-artifact cleanup.

## Closed / trusted

| Testcase | Status | Canonical run |
|---|---|---|
| TC-ETB-005 | TRUSTED PASS | 20260927T042429089204Z-p89952 |
| TC-ETB-006 | TRUSTED PASS | 20260926T115141850200Z-p76191 |
| TC-ETB-007 | TRUSTED PASS | 20260926T125124984763Z-p17809 |
| TC-ETB-008 | TRUSTED PASS | 20260926T125749592097Z-p22905 |
| TC-ETB-009 | TRUSTED PASS | 20260926T130442549114Z-p24890 |
| TC-ETB-010 | TRUSTED PASS | 20260927T033120788982Z-p29583 |
| TC-ETB-011 | TRUSTED PASS | 20260927T041035604187Z-p75478 |
| TC-ETB-012 | TRUSTED PASS | 20260927T041501698390Z-p80301 |

All retained canonical trusted runs have complete indexed evidence and no missing expected artifacts according to their accepted evidence-index receipts.

## Still open / not accepted

| Testcase | Current state | Latest evidence |
|---|---|---|
| TC-ETB-002 | BLOCKED / DEGRADED | 20260927T044036405305Z-p8528 — RAI-033 after Profile Next even after owner manual CIS clear; failure origin UNKNOWN |
| TC-ETB-003 | BLOCKED | 20260927T031747603243Z-p15368 — RAI-033 after Profile Next; DOPA not reached |
| TC-ETB-004 | BLOCKED | 20260927T032347728621Z-p21564 — RAI-033 after Profile Next; DOPA not reached |
| TC-ETB-013 | OPEN / DEGRADED | 20260927T050452876260Z-p34690 — after DOPA + Laser Code Next, runtime proceeded to normal OTP (`screenVerifyMobileNumberOTP_*`) instead of RGI-016; backend/test-data mule flag must be prepared before rerun |

## Retention policy used for cleanup

- Preserve this snapshot and docs/standards/BBL_REMEDIATION_CHECKLIST.md.
- Preserve one latest TRUSTED canonical run for each closed testcase TC005–TC012.
- Preserve all currently relevant evidence for open testcases TC002, TC003, TC004 and TC013.
- Remove only redundant historical attempts and legacy per-case artifacts for testcases already closed.
- Do not modify business expectations to match runtime behavior.
