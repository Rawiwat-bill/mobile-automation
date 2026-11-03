# ETB Standard Baseline Audit

Audit date: 2026-09-19  
Current status refresh: 2026-09-27  
Project: BBL  
Branch observed: `feature/etb-regression-pack`  
Purpose: map the current ETB implementation to the BBL Automation Standard without changing business behavior.

## 1. Baseline validation evidence

Focused checks executed through IRIS-C:

| Validation | Result |
|---|---|
| `test:etb-traceability-pilot` | PASS — 8/8 |
| `test:etb-run-artifacts` | PASS — 5/5 |
| `test:etb-evidence-isolation` | PASS — 5/5 |
| `test:etb-cleanup` | PASS — 36/36 |

These checks prove focused framework behavior only. They do not replace runtime validation.

## 2. Overall assessment

The current ETB framework already has a strong engineering foundation. The main work is not a framework rewrite.

Priority is to formalize and harden:

1. result trust semantics,
2. full-scope traceability,
3. evidence completeness policy,
4. immutable knowledge binding,
5. CI/CD quality gates.

### Implementation checkpoint — 2026-09-19

Completed in this standards-adoption mission:

- Added additive `failure_origin` to ETB run-result cases.
- Added additive per-case and run-level `result_trust`.
- `PASS` now requires complete evidence plus proven mandatory cleanup to be `TRUSTED`.
- Generic failures remain `UNKNOWN` unless explicit evidence supports a safer classification; the framework does not invent a PRODUCT origin.
- Missing Robot output is explicitly `RESULT_UNAVAILABLE` + `NOT_ASSESSABLE`.
- Added `test:bbl-automation-standard` as a single focused non-device quality gate.
- The full standards gate passed after these changes.

Completed since the original checkpoint:

- full static traceability expanded to TC-ETB-001..013 through `configs/etb_traceability_full.json`,
- immutable Wiki snapshot binding verified and retained by the historical pilot contract,
- result-trust and conservative failure-origin semantics implemented and regression-tested,
- required evidence completeness participates in trust classification,
- the mandatory standards gate includes the current focused contracts.

Still open:

- independent fresh-machine reproducibility proof,
- actual CI pipeline wiring for the standards gate,
- NTB adoption,
- completion of the paused mobile acceptance items recorded in the acceptance snapshot.

## 3. Standards matrix

| Area | Status | Current evidence | Gap / next action |
|---|---|---|---|
| Layered architecture | PASS | test -> business keywords -> pages -> locators; separate contracts/diagnostics/libraries | Preserve boundaries during future changes |
| Canonical case identity | PASS | TC-ETB-001..013 | Keep manifest as authority |
| Test data separation | PASS | committed contract + local approved runtime profiles | Continue security guard |
| Environment readiness | PASS | DEV/SIT/DEV_MOCK preflight and target guard | Expand only when new environments are introduced |
| Business blocker separation | PASS/PARTIAL | BLOCKED classification for known AJI/GOD environment conditions | Generalize failure origin beyond environment-only blocker detection |
| Run identity | PASS | run ID + manifest | Preserve immutable run identity |
| Evidence isolation | PASS | run/case scoped evidence; focused tests 5/5 | Add trust impact for required evidence incompleteness |
| Cleanup | PASS | CIS/PDPA/Appium cleanup dimensions; 36 focused tests pass | Keep cleanup mandatory per policy |
| Missing result handling | PASS | RESULT_UNAVAILABLE when Robot output is absent | Preserve |
| Traceability | PASS (static scope) | full registry covers TC-ETB-001..013; TC003 conflict remains explicit; runtime acceptance remains separate | Preserve full registry and do not convert partial runtime state into a coverage percentage |
| Requirement conflicts | PASS/PARTIAL | TC003 and interpretation notes are preserved | Do not claim coverage for unresolved semantics |
| Wiki/Figma binding | PASS | immutable page-hash manifest and snapshot hash are verified by the traceability contract | Keep design evidence structurally scoped; do not promote it to case-semantic authority |
| Result semantics | PASS | business outcome, blocker, failure origin and result trust are separate dimensions | Preserve conservative classification; UNKNOWN is valid when evidence is insufficient |
| Evidence completeness | PASS | COMPLETE/PARTIAL/INCOMPLETE/NOT_REQUESTED plus evidence index and trust impact are implemented | Preserve run/case isolation and required-evidence trust policy |
| Reproducibility | PARTIAL | tested dependency snapshot + clean candidate proof | independent fresh-machine proof pending |
| CI/CD | GAP | local declared validation scripts exist | create standards-compliance quality gate / pipeline adoption |
| Parallel/device cloud/iOS | OUT OF CURRENT ETB SCOPE | not configured | address when scope requires |

## 4. Result-semantics status

Implemented.

The run-result model separates Robot execution status, business outcome, blocker, cleanup, evidence, failure origin and result trust.

Supported conservative failure-origin vocabulary includes:

```text
PRODUCT
AUTOMATION
ENVIRONMENT
TEST_DATA
EXECUTION_POLICY
UNKNOWN
```

`UNKNOWN` is preferred over an unsupported PRODUCT claim. Focused run-artifact contracts and the mandatory standards gate protect this behavior.

## 5. Result-trust status

Implemented.

First-class trust states are:

```text
TRUSTED
DEGRADED
UNTRUSTED
NOT_ASSESSABLE
```

Business outcome and result trust remain independent. A PASS is only TRUSTED when mandatory evidence and cleanup policy are satisfied. Missing Robot output becomes RESULT_UNAVAILABLE / NOT_ASSESSABLE rather than an invented business result.

## 6. Traceability status

The historical pilot remains immutable evidence for TC-ETB-001, TC-ETB-002 and TC-ETB-004 plus the explicit TC003 conflict.

The current static traceability source is now:

`configs/etb_traceability_full.json`

It maps all TC-ETB-001..013 through requirement provenance, case identity, Robot testcase, production assertion source, expected terminal/error state and current runtime-evidence binding where available.

Human-readable view:

`docs/standards/ETB_TRACEABILITY_MATRIX.md`

Static traceability is complete for 13/13 cases. Runtime acceptance is intentionally represented separately and must not be converted into a product coverage percentage while Block B is paused.

## 7. Evidence policy status

Implemented for the current ETB baseline.

Evidence is scoped by run, case and checkpoint. `evidence_index.json` distinguishes missing expected artifacts from existing unindexed files and the final trust state reflects required-evidence completeness.

Current policy protects:

- PASS terminal-state evidence,
- expected-RGI code/state evidence,
- blocker evidence,
- diagnostic evidence for automation/application failures when available,
- cleanup evidence,
- artifact security and private-local handling.

The remaining work is operational retention/cleanup policy, not evidence-trust semantics.

## 8. CI/CD gap

The repository already exposes bounded validation scripts. These should become the basis of a standards gate.

Candidate non-device gate:

```text
traceability contract
run artifact contract
evidence isolation
cleanup/lifecycle
artifact security
delivery readiness
Robot dry-run
```

Runtime Android execution should stay in a controlled device/environment lane.

## 9. No-rewrite rule

The standards adoption must not rewrite ETB merely to look more architectural.

Do not change a working layer unless there is a specific standard gap, defect, maintainability issue or safety reason.

Business behavior must remain unchanged unless the authoritative requirement changes.

## 10. Current next implementation sequence

Completed from the original sequence:

- STD-03A Result trust
- STD-03B Failure origin
- STD-03C Full static traceability TC001–TC013
- STD-03D Standards gate
- STD-04 Focused validation / dry-run / artifact-security / delivery-readiness contracts

Still open:

1. Wire the standards gate into the actual CI pipeline.
2. Produce an independent clean-machine fresh-install reproducibility proof.
3. Complete paused mobile acceptance items under Block B when backend/test-data conditions are ready.
4. Apply the standard to NTB without forcing ETB-specific implementation details onto NTB.
