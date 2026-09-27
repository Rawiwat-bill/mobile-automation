# ETB Traceability Matrix — TC001–TC013

Status: FULL STATIC SCOPE  
Updated: 2026-09-27  
Machine-readable source: `configs/etb_traceability_full.json`  
Historical pilot: `configs/etb_traceability_pilot.json`  
Runtime acceptance source: `docs/standards/BBL_ETB_ACCEPTANCE_SNAPSHOT_2026-09-27.md`

## Authority model

Traceability keeps these planes separate:

```text
Requirement
  -> Case contract
  -> Robot testcase
  -> Production assertion source
  -> Expected terminal state
  -> Runtime evidence
  -> Classified result/trust
```

Requirement authority, automation behavior and runtime evidence must not silently overwrite one another. Figma/Wiki design evidence is supporting structural context unless explicitly designated as case-semantic authority.

## Full matrix

| Case | Requirement row | Automation | Expected terminal / error | Runtime state |
|---|---:|---|---|---|
| TC-ETB-001 | 4 | Positive Registration Success | registration success / Control 3C | Current acceptance snapshot does not record a canonical runtime result |
| TC-ETB-002 | 5 | Positive Registration With PDPA Clause 6 | registration success / Control 3C | BLOCKED / DEGRADED — RAI-033 after Profile Next |
| TC-ETB-003 | 6 | Positive Product Selection Variant | registration success / Control 3C | BLOCKED — RAI-033; PDPA clarification remains explicit |
| TC-ETB-004 | 7 | Positive Product Selection Existing Accounts | registration success / Control 3C | BLOCKED — RAI-033 |
| TC-ETB-005 | 8 | Mobile Number Mismatch RGI Popup | RGI-079; popup closed | TRUSTED PASS — `20260927T042429089204Z-p89952` |
| TC-ETB-006 | 9 | DOB Mismatch RGI Popup | RGI-076; popup closed | TRUSTED PASS — `20260926T115141850200Z-p76191` |
| TC-ETB-007 | 10 | Expired Citizen ID Full-Screen RGI | RGI-012; app closed | TRUSTED PASS — `20260926T125124984763Z-p17809` |
| TC-ETB-008 | 11 | High-Risk 3A Full-Screen RGI | RGI-014; app closed | TRUSTED PASS — `20260926T125749592097Z-p22905` |
| TC-ETB-009 | 12 | High-Risk 3V Full-Screen RGI | RGI-014; app closed | TRUSTED PASS — `20260926T130442549114Z-p24890` |
| TC-ETB-010 | 13 | High-Risk 3U Full-Screen RGI | RGI-014; app closed | TRUSTED PASS — `20260927T033120788982Z-p29583` |
| TC-ETB-011 | 14 | High-Risk 3B Full-Screen RGI | RGI-014; app closed | TRUSTED PASS — `20260927T041035604187Z-p75478` |
| TC-ETB-012 | 15 | Low IAL Full-Screen RGI | RGI-013; app closed | TRUSTED PASS — `20260927T041501698390Z-p80301` |
| TC-ETB-013 | 16 | Mule Warning Full-Screen RGI | RGI-016 after Laser Code Next; app closed | OPEN — current profile routes to normal OTP instead of mule branch |

## Important exceptions

### TC-ETB-003

Product Selection `MUST_SKIP` is confirmed, but PDPA visibility remains explicitly unresolved in the case contract. Static traceability is complete; unresolved requirement semantics remain visible and must not be invented by automation.

### TC-ETB-013

The latest runtime run `20260927T050452876260Z-p34690` reached DOPA, submitted Laser Code and then proceeded to the normal OTP screen instead of `RGI-016`. Current classification is backend/test-data mule-profile preparation, not locator failure. Rerun the same automation only after the profile is prepared for the mule/suspicious-account branch.

## Coverage statement

Static traceability scope is 13/13 cases.

Do not publish a runtime pass percentage from this document. Block B mobile acceptance is intentionally paused and current runtime acceptance is incomplete.

## Canonical files

- Requirement/case contract: `testdata/onboarding/etb_cases.yaml`
- Test suite: `tests/android/etb/etb_regression.robot`
- Full machine-readable traceability: `configs/etb_traceability_full.json`
- Historical traceability pilot: `configs/etb_traceability_pilot.json`
- Acceptance snapshot: `docs/standards/BBL_ETB_ACCEPTANCE_SNAPSHOT_2026-09-27.md`
- Remediation status: `docs/standards/BBL_REMEDIATION_CHECKLIST.md`
- Automation standard: `docs/standards/BBL_AUTOMATION_STANDARD.md`
