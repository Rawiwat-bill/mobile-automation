# BBL Remediation Checklist

Updated: 2026-09-27 (ICT)
Scope: /Users/RARW/BBL
Policy: Restore trustworthy test baseline before final project cleanup. Owner-authorized selective cleanup may remove redundant artifacts for already-accepted cases while canonical evidence and all open-case evidence remain preserved.

## Block B — Test Trust

- [x] B-F04.1 Confirm PIN isolated harness repaired.
  - Change: stubbed the production failure-evidence callback in the isolated stale-transition harness.
  - Production business behavior changed: NO.
  - Validation: `test:confirm-pin-transition`
  - Job: `c6158a87-897b-4131-8e40-e801d27f45d5`
  - Result: PASS (1/1).

- [x] B-F04.2 Product Selection isolated harness repaired.
  - Change: added the production `Probe Stable Post First PIN State` wrapper dependency to the synthetic harness.
  - Production business behavior changed: NO.
  - Validation: `test:etb-product-selection-state`
  - Job: `718f90c0-e706-4528-a187-5a9b73574e58`
  - Result: PASS (4/4 Python tests; 8/8 embedded Robot scenarios).

- [x] B-F04.3 Consent/Landing stale harness assertion repaired.
  - Change: aligned the harness with current bounded fresh-element-rect recovery and no blind duplicate Ready tap.
  - Production business behavior changed: NO.
  - Validation: `test:consent-scroll`
  - Job: `a616b630-7e70-4a83-9cb3-d92b28c02286`
  - Result: PASS (8/8).

- [x] B-F04.4 Mandatory standard gate now includes Confirm PIN and Product Selection focused contracts.
  - Change: added `test:confirm-pin-transition` and `test:etb-product-selection-state` to `test:bbl-automation-standard`.
  - Purpose: prevent future mobile execution baseline from silently bypassing these focused regressions.
  - Production business behavior changed: NO.

- [x] B-F04.5 Full mandatory offline automation gate is green after repairs.
  - Validation: `test:bbl-automation-standard`
  - Job: `4f23a48a-7f58-4429-b4ed-e6cd6ca334fa`
  - Result: PASS, exit 0.
  - Mobile execution: NO.
  - Cleanup performed: NO.

- [x] B-F05 Evidence discovery/index is deterministic by run, testcase and checkpoint.
  - Change: added reference-only `evidence_index.json` generation during ETB finalization. It indexes run/case/checkpoint artifact references, Robot `output.xml` / `log.html` / `report.html`, run manifest/result status, and distinguishes `missing_expected` from `existing_unindexed` without copying artifact contents.
  - Coverage: includes the TC003-style case where a screenshot physically exists even when no producer metadata registered it.
  - Validation: `test:etb-evidence-index`
  - Job: `c19a2b8f-f84c-4d88-bbc1-6a7bbbb0146a`
  - Result: PASS (2/2).
  - Validation: `test:etb-run-artifacts`
  - Job: `49ca4c47-77c8-4d31-8648-a024da7f0264`
  - Result: PASS (18/18); evidence index produced for normal finalization and RESULT_UNAVAILABLE paths.
  - Production business behavior changed: NO.

- [x] B-F06 Evidence capture is consolidated through the shared private ETB adapter for the remediated checkpoint/failure paths.
  - Change: routed Confirm PIN failure, PDPA blocker/after-state, DOPA title checkpoint, Terms transition and Profile handoff snapshot capture through `Record ETB Evidence Capture`; collapsed Profile exit evidence into the canonical run/case private scope.
  - Failure semantics: shared adapter is best-effort; evidence capture failure does not mask the original automation failure.
  - Validation: `test:etb-evidence-capture-consolidation`
  - Job: `4b169f09-bba3-48e2-9e05-e907f88997f7`
  - Result: PASS (2/2), including synthetic proof that `ORIGINAL_AUTOMATION_FAILURE` remains terminal when evidence capture fails.
  - Validation: `test:confirm-pin-transition`
  - Job: `f4178840-c5a3-47f2-9948-0a0c08038f16`
  - Result: PASS (1/1).
  - Validation: `test:consent-scroll`
  - Job: `0df05f9f-1f5e-4e40-be2a-033f830afb25`
  - Result: PASS (8/8).
  - Validation: `test:etb-evidence-isolation`
  - Job: `ff626915-422d-4c9a-aad8-50f211e8104c`
  - Result: PASS (5/5), including Robot dry-run.
  - Validation: `test:etb-artifact-security`
  - Job: `07b73132-b230-4327-ae10-ae0250070a68`
  - Result: PASS (5/5).
  - Production business behavior changed: NO.

- [x] B-F06.1 Synthetic offline runner fixtures include the new evidence-index dependency.
  - Change: updated only isolated `test_etb_profile_contract.py` and `test_etb_target_guard.py` sandboxes so copied `etb_runtime.py` can import `libraries/evidence_index.py`; CIS/ADB boundaries remain mocked/stubbed.
  - Validation: `test:etb-profile-contract`
  - Job: `b40097a4-d936-4649-9787-f89d8b781ab6`
  - Result: PASS (17/17).
  - Validation: `test:etb-target-guard`
  - Job: `4754af87-3ca4-4d25-8537-c38e5f2976b1`
  - Result: PASS (39/39).
  - Production business behavior changed: NO.

- [x] B-F06.2 Full mandatory offline BBL automation gate is green after F05/F06.
  - Validation: `test:bbl-automation-standard`
  - Job: `d5a714e7-668b-46a5-9b4f-d2d9a8d61941`
  - Result: PASS, exit 0.
  - Intermediate validation history: jobs `10968183-c519-4b1e-beba-a58996421a1f` and `8a5c3541-a9dd-450f-be75-173c3b7416bd` exposed stale synthetic sandbox dependency wiring only; both were remediated before the accepted final gate.
  - Production business behavior changed: NO.
  - Mobile execution: NO.
  - Cleanup performed: NO.

- [ ] B-Mobile Acceptance preflight is currently blocked before testcase execution.
  - Target/device/build validation: `maint:diagnose-dev-target`
  - Job: `6aa335e2-9ee1-4fc5-858a-29cd0887a61c`
  - Result: PASS; emulator target, boot/QEMU/AVD, UI dump, DEV package, exact Build191 package identity and launcher all pass.
  - POST binding validation: `test:etb-target-guard`
  - Job: `4754af87-3ca4-4d25-8537-c38e5f2976b1`
  - Result: PASS (39/39); Build191 is accepted for `POST_MMP_1` and rejected for the MMP release binding.
  - Proxy validation: `maint:etb-align-proxy`
  - Job: `9297a307-31cd-469c-823a-1e9d0b640b8e`
  - Result: PASS; emulator-5556 HTTP proxy aligned to the existing bounded configuration.
  - Appium validation: temporary declared `maint:appium-check` bridge to `tools/appium_server.py --check`.
  - Job: `8be3083d-cb7b-4d17-a143-79b6cc0ba26f`
  - Result: PASS; UiAutomator2, Android SDK, managed runtime receipt and Appium status are ready. Temporary package-script bridge was removed afterward and `package.json` returned to the mandatory-gate-validated hash.
  - CIS readiness: `maint:etb-dev-cis-ready`
  - Job: `adeea6de-83e8-4a8b-967a-000743b7b1ee`
  - Result: BLOCKED, exit 3; `DNS_RESOLUTION_FAILURE`.
  - Fresh recheck job: `f0ce46ab-ed03-4553-bf2c-b6b51fcbe28d` — same `DNS_RESOLUTION_FAILURE`.
  - Sanitized DNS differential diagnostic job: `3bf0677c-eb6b-448c-92f0-0c1ac8ebb23a`.
  - DNS diagnosis: public DNS PASS, CIS internal DNS FAIL, CA bundle present, resolver configuration present, no system VPN connection detected; classified `INTERNAL_SPLIT_DNS_UNAVAILABLE`.
  - Required resume condition: restore the RARW corporate VPN/split-DNS path, then rerun CIS readiness. Do not run or clear a testcase while CIS DNS is unresolved.
  - Evidence/index readiness: covered by green F05/F06 focused validation and mandatory BBL automation gate.
  - Testcase execution: NO. Do not clear CIS or run TC005/TC002 while CIS DNS remains unresolved.
  - Production business behavior changed: NO.
  - Cleanup performed: NO.

- [x] B-Mobile TC005 canonical smoke is trusted after Profile focus-dismissal race remediation.
  - First runtime job: `5a6e4daf-387c-4995-9c69-ebfb3bce5789`, run `20260926T104754860768Z-p21377`.
  - First result: FAIL before the expected business assertion with `PROFILE_DISAPPEARED_BEFORE_FOCUS_DISMISSAL`; run evidence was complete and CIS pre/post cleanup passed.
  - Visual diagnosis: failure screenshot showed the app had navigated back to Terms while dismissing focus from the Profile mobile field; Citizen ID focus dismissal had passed, and the failure occurred in `Input Mobile Number -> Tap Profile Focus Dismissal Target`.
  - Root cause classification: automation interaction race / blind keyboard-back behavior, not RGI-079 business behavior and not environment readiness.
  - Change: Profile focus dismissal now proves Profile first, taps a Profile-safe title target, checks `Is Keyboard Shown`, and calls `Hide Keyboard` only when the keyboard is actually shown; fail-closed Profile guards remain.
  - Production business behavior changed: NO.
  - Focused validation: `test:profile-focus-dismissal` job `566606f4-cc98-4f00-9f75-5bd5211c2fd1` — PASS (3/3 focused Profile contracts).
  - Profile runner contract: `test:etb-profile-contract` job `c0f4fa68-3512-4e45-a6f8-4db9f08fa9a5` — PASS (17/17).
  - Mandatory gate: `test:bbl-automation-standard` job `59e8e66d-6d19-4cf2-94eb-9d4724b85f51` — PASS, exit 0.
  - Accepted TC005 rerun: job `7ca0cf57-0c36-4efa-9ad5-efcf73bccd9c`, run `20260926T110748263481Z-p56010` — PASS (1/1), `ETB_RUN_RESULT=PASS`, result trust `TRUSTED`.
  - Runtime evidence: expected popup visually confirmed as `Mobile number doesn’t match`, help code `RGI-079`, action `OK`; `ETB_TC_005_RESULT_BEFORE_ACTION` capture COMPLETE.
  - Terminal/evidence integrity: evidence COMPLETE, missing expected = 0, existing unindexed = 0, Robot output/log/report present.
  - CIS post-test cleanup: PASS / already cleared / reusable.
  - Cleanup performed: NO.

- [ ] B-Mobile TC002 is DEFERRED by owner decision; do not retry for now.
  - Initial controlled job: `cc75c9b2-585d-4bc0-94b6-8c5305a3ed3b` reached Profile flow but failed on a focus-dismissal transition assertion.
  - Later runtime evidence: run `20260926T112737311493Z-p59783` reached Profile Next and observed `RAI-033`.
  - CIS PRE_TEST: PASS / `ALREADY_CLEARED` / state ready / reusable.
  - CIS POST_TEST: PASS / `ALREADY_CLEARED` / state ready / reusable.
  - Marker evidence: P0/P1/P2 Profile markers present; first recognized destination `RAI-033`.
  - Evidence capture: COMPLETE; Robot output/log/report and evidence index present.
  - Current decision: defer TC002; do not alter expected behavior and do not retry until explicitly resumed.
  - Cleanup performed: NO.

- [x] B-Mobile TC006 DOB mismatch acceptance is TRUSTED.
  - Job: `767ffb99-75ec-4126-9dbc-2266f3366cb2`.
  - Run: `20260926T115141850200Z-p76191`.
  - Runtime: DEV / Build191 / `POST_MMP_1` / emulator-5556.
  - Result: PASS (1/1), `ETB_RUN_RESULT=PASS`, result trust `TRUSTED`.
  - Runtime evidence: expected popup visually confirmed as `Incorrect citizen ID or date of birth`, help code `RGI-076`, action `OK`.
  - Marker evidence: P0/P1/P2 Profile markers present; first recognized destination `RGI-076`.
  - Evidence: COMPLETE; before-action screenshot/page source and terminal evidence present.
  - CIS post-test cleanup: PASS / `ALREADY_CLEARED` / state ready / reusable.
  - Production business behavior changed: NO.
  - Cleanup performed: NO.

- [x] B-Mobile TC007 expired-CID full-screen RGI acceptance is TRUSTED.
  - Expected contract: `RGI-012` full-screen → `Find a branch` → return → `Close app` → app closed.
  - Diagnostic run `20260926T120813748798Z-p78740`, job `7cbc8e5c-468b-4d09-aedd-c33321063bc2`: business screen was correct, but automation falsely required the branch destination to leave the BBL package; visual evidence proved an in-app Bangkok Bank WebView opened.
  - Second diagnostic job `9c959d7e-ed05-4ed7-90c2-e23f42a0ee02`: branch destination proof passed, but generic return did not reliably close the in-app WebView.
  - Change: branch destination accepts a proven WebView in external or in-app mode; in-app return now discovers live clickable native header controls, selects the rightmost close control from current rect geometry, taps its center, and proves the WebView is closed before re-asserting the RGI screen. Missing close control remains fail-closed.
  - Production business behavior changed: NO.
  - Focused validation: `test:full-screen-rgi-branch` job `aa50a5fc-cbe9-4f10-9320-4f14ae72a797` — PASS.
  - Mandatory gate: `test:bbl-automation-standard` job `bae19364-e991-439b-bdca-aade02779143` — PASS, exit 0.
  - Accepted runtime job: `06f24de9-2626-4347-af61-e307697d83ef`, run `20260926T125124984763Z-p17809` — PASS (1/1), `ETB_RUN_RESULT=PASS`, result trust `TRUSTED`.
  - Visual evidence: `Citizen ID card needs to be verified`, `Find a branch`, help code `RGI-012`, `Close app` confirmed on the accepted run.
  - Marker evidence: P0/P1 Profile markers present; P2 Profile markers absent; first recognized destination `RGI-012`.
  - Terminal evidence: Nexus Launcher foreground after `Close app`, proving BBL app closed.
  - Evidence index: COMPLETE, missing expected = 0, existing unindexed = 0.
  - CIS post-test cleanup: PASS / `ALREADY_CLEARED` / state ready / reusable.
  - Cleanup performed: NO.

- [x] B-Mobile TC008 high-risk 3A full-screen RGI acceptance is TRUSTED.
  - Job: `8caab66b-fa52-4e37-acd8-49b8ee617ddb`.
  - Run: `20260926T125749592097Z-p22905`.
  - Runtime: DEV / Build191 / `POST_MMP_1` / emulator-5556.
  - Result: PASS (1/1), `ETB_RUN_RESULT=PASS`, result trust `TRUSTED`.
  - Visual evidence: `Your profile information doesn’t meet our conditions for app sign up`, `Find a branch`, help code `RGI-014`, `Close app` confirmed.
  - Marker evidence: P0/P1 Profile markers present; P2 Profile markers absent; first recognized destination `RGI-014`; expected RGI-014 present.
  - Terminal evidence: Nexus Launcher foreground after `Close app`, proving BBL app closed.
  - Evidence index: COMPLETE, missing expected = 0, existing unindexed = 0.
  - CIS post-test cleanup: PASS / `ALREADY_CLEARED` / state ready / reusable.
  - Production business behavior changed: NO.
  - Cleanup performed: NO.

- [x] B-Mobile TC009 high-risk 3V full-screen RGI acceptance is TRUSTED.
  - Validation action receipt: `8e5d7a23-8b74-4d9c-91cd-71890f0f19eb`.
  - Run: `20260926T130442549114Z-p24890`.
  - Runtime: DEV / Build191 / `POST_MMP_1` / emulator-5556.
  - Result: PASS (1/1), `ETB_RUN_RESULT=PASS`, result trust `TRUSTED`.
  - Visual evidence: `Your profile information doesn’t meet our conditions for app sign up`, `Find a branch`, help code `RGI-014`, `Close app` confirmed.
  - Marker evidence: P0/P1 Profile markers present; P2 Profile markers absent; first recognized destination `RGI-014`; expected RGI-014 present.
  - Terminal evidence: Nexus Launcher foreground after `Close app`, proving BBL app closed.
  - CIS post-test cleanup: PASS / `ALREADY_CLEARED` / state ready / reusable.
  - Production business behavior changed: NO.
  - Cleanup performed: NO.

- [ ] B-Mobile TC010 high-risk 3U acceptance is DEFERRED after observed response mismatch.
  - Expected contract: `RGI-014` full-screen → `Find a branch` → return → `Close app`.
  - Initial job: `01cee92a-a295-477e-b21c-74468421f45f`, run `20260926T213928222575Z-p90893` — environment blocker `LANDING_OFFLINE_AFTER_ACTION`; visual evidence showed `No internet connection` before Profile/RGI.
  - Environment recheck: proxy job `d56e74d0-9b79-4733-976f-25614aa89130` PASS; CIS readiness job `6f44ab1f-afa5-4cb6-b36b-0313091aed4f` PASS.
  - Bounded retry job: `6a4ac22a-b86d-4c7c-bc52-5ea6090f1216`, run `20260926T214305142075Z-p26490`.
  - Retry result: FAIL with `EXPECTED_RGI_STAGE_MISMATCH expected=RGI-014 observed=AJI-001` after Profile Next.
  - Visual evidence: `Service is not available now`, `Please try again later`, help code `AJI-001`, `Close app`.
  - Marker evidence: P0/P1 Profile markers present; P2 Profile markers absent; first recognized destination `AJI-001`; expected RGI-014 absent.
  - CIS post-test cleanup: PASS / `ALREADY_CLEARED` / state ready / reusable.
  - Current decision: defer TC010; do not change expected RGI-014 and do not retry again unless explicitly resumed or service condition changes.
  - Disk guard on retry: WARN, free space ~8.47 GB; fail threshold remains 5 GB. Cleanup remains HOLD.
  - Production business behavior changed: NO.
  - Cleanup performed: NO.

- [ ] B-Mobile TC011 high-risk 3B acceptance is DEFERRED due the same observed AJI-001 response seen in TC010.
  - Expected contract: `RGI-014` full-screen → `Find a branch` → return → `Close app`.
  - Job: `d6f545d1-fe8d-48d1-a334-dfb725365f18`.
  - Run: `20260926T214941982962Z-p37811`.
  - Result: FAIL with `EXPECTED_RGI_STAGE_MISMATCH expected=RGI-014 observed=AJI-001` after Profile Next.
  - Visual evidence: `Service is not available now`, `Please try again later`, help code `AJI-001`, `Close app`.
  - Marker evidence: P0/P1 Profile markers present; P2 Profile markers absent; first recognized destination `AJI-001`; expected RGI-014 absent.
  - CIS post-test cleanup: PASS / `ALREADY_CLEARED` / state ready / reusable.
  - Cross-profile assessment: TC010 (3U) and TC011 (3B) independently reached AJI-001 instead of their expected RGI-014; treat as current app/backend service blocker rather than changing case expectations.
  - Hold: do not execute TC012/TC013 while this cross-profile AJI-001 condition persists.
  - Resume condition: service condition changes or owner explicitly requests a probe; then rerun one bounded high-risk/exception case before resuming remaining acceptance.
  - Disk guard remains WARN but above fail threshold; cleanup stays HOLD.
  - Production business behavior changed: NO.
  - Cleanup performed: NO.

## Block C — Maintainability

Status: GREEN with bounded legacy debt. Production business behavior changed: NO.

- [x] C1 Canonical immediate visibility assertions centralized.
  - Added `resources/keywords/appium_expectations.resource`.
  - `Element Should Be Visible Now` performs one visibility observation using non-deprecated `Wait Until Element Is Visible ... 0s`; it does not add a retry/wait budget.
  - Migrated canonical ETB/shared paths: Android permission handling, common onboarding, app-update prompt, Terms transition probes, canonical Landing, Profile fields/transition, Confirm PIN, Product Selection, post-PIN state and ETB regression reset/probes.
  - Canonical ETB/shared path no longer uses deprecated `Element Should Be Visible`; the remaining occurrence is in the legacy diagnostic/test-support Landing resource.

- [x] C1 synthetic contracts aligned with the canonical helper dependency.
  - Profile focus: job `c2cefa50-9887-4be0-9526-6181f14d883f` — PASS (3/3).
  - Landing transition/language: job `be8015f7-24e5-45fa-bb34-1ae8aba87820` — PASS (30 Python tests; 12/12 behavior + 12/12 dry-run scenarios; language scenarios PASS).
  - App update prompt: job `62b61167-dc10-4baf-bb5d-80d7b29b820b` — PASS (6/6).
  - Confirm PIN stale transition: job `aa545473-17be-440a-8c26-90054d7969ae` — PASS (1/1).

- [x] C1 focused ETB contracts remain green.
  - Profile contract: job `fa07ab76-9724-46a1-b229-9e12119e807e` — PASS (17/17).
  - Terms/consent: job `adff5f89-1e50-4be5-83c2-2ad5eb5ba972` — PASS (8/8).
  - Product Selection: job `9f83be40-8b71-4f5d-a8bb-a38aea5012b6` — PASS (4/4; embedded assertion scenarios PASS).
  - DOPA/profile boundary: job `b309322c-c567-4f54-98ba-b2c1fe7ff9b9` — PASS (2/2; 11 boundary scenarios PASS).
  - Appium launcher/runtime environment: job `4af61878-62c0-46de-8b08-9560e4261565` — PASS (9/9).

- [x] C1 mandatory regression gate is green.
  - Validation: `test:bbl-automation-standard`
  - Job: `289095fd-4b0f-4a86-a7c6-90b58fc7aeec`
  - Result: PASS / exit 0.

- [x] C2 Landing-resource roles are explicitly separated.
  - Canonical production shared onboarding: `resources/pages/common_onboarding/landing_screen_page.resource`.
  - Legacy diagnostic/test-support lane: `resources/pages/onboarding/landing_screen_page.resource`.
  - The legacy resource is intentionally retained because benchmark, health, investigation, preparation and regression support suites still reference it; deleting/merging it would create unnecessary cross-lane blast radius.
  - Added explicit documentation to the legacy resource pointing production callers to the canonical shared path.

- [x] C2 residual deprecated-enabled debt is bounded and intentionally retained.
  - Remaining `Element Should Be Enabled` usages: Terms Accept readiness and Profile Next readiness.
  - AppiumLibrary in the active environment has no direct `Wait Until Element Is Enabled` equivalent with proven identical semantics.
  - Decision: do not replace these two calls with custom element-object logic until a focused behavior-preserving contract is introduced.

- [x] C2 source hygiene audit found no TODO/FIXME markers in canonical resources during this wave.

## Block D — Documentation / Traceability

Status: GREEN for current ETB static scope. Production business behavior changed: NO.

- [x] D1 Full static traceability expanded from the historical pilot to TC-ETB-001..013.
  - Machine-readable SoT: `configs/etb_traceability_full.json` (`bbl-etb-traceability/v2`).
  - Human-readable SoT: `docs/standards/ETB_TRACEABILITY_MATRIX.md`.
  - Historical pilot retained unchanged as provenance/design-binding evidence: `configs/etb_traceability_pilot.json`.
  - Full registry maps requirement row, case contract, Robot testcase, production assertion source, expected terminal/error state and runtime-evidence binding where available.
  - Static scope: 13/13 mapped.
  - Runtime pass percentage: intentionally NOT published because Block B mobile acceptance is paused/incomplete.
  - Explicit exceptions preserved: TC003 requirement conflict; TC013 backend/test-data mule-branch mismatch.

- [x] D1 Traceability contract covers both historical pilot and full registry.
  - Validation: `test:etb-traceability-pilot`
  - Job: `f934c36b-4509-4e8d-8d7f-ff13f5cd8063`
  - Result: PASS (14/14).

- [x] D2 README and PROJECT_WIKI aligned with current runtime/security guidance.
  - Canonical Appium start is `pnpm appium`.
  - Default Appium privilege is bounded to `--allow-insecure=uiautomator2:adb_shell`; `--relaxed-security` is no longer documented as an active/default command.
  - Inspector/CORS remains explicit opt-in through `pnpm appium:inspector`.
  - Device serial examples are documented as examples; `DEVICE_UDID`, environment selection and target guard remain execution authority.
  - Full traceability matrix, machine-readable registry, acceptance snapshot and remediation checklist are linked from current docs.

- [x] D2 ETB standard baseline audit refreshed to current implemented state.
  - Result trust, conservative failure origin, evidence completeness and full traceability are documented as implemented rather than pending gaps.
  - Remaining real gaps: actual CI pipeline wiring, independent clean-machine fresh-install proof, paused mobile acceptance completion and NTB adoption.

- [x] D2 Documentation drift is regression-protected.
  - Validation: `test:etb-docs-contract`
  - Job: `6e414a1d-4e2c-46fd-a25d-fe28ff539a15`
  - Result: PASS (11/11).
  - Contract prevents reintroduction of obsolete pilot-only gap wording and relaxed-security startup guidance.

- [x] D3 Mandatory standards gate is green after Block D.
  - Validation: `test:bbl-automation-standard`
  - Job: `3da060cd-31ad-4091-a41c-fba4e41c6e9b`
  - Result: PASS / exit 0.

- [ ] D4 External/process documentation remains outside this Block D code/doc closure.
  - Actual CI pipeline wiring is not performed here.
  - Independent fresh-machine installation proof is not performed here.
  - NTB standards adoption remains a later wave.
  - Block B runtime/mobile acceptance remains paused by owner direction.

## Block E — Delivery Readiness / Repository Preparation

Status: GREEN / READY_FOR_PATH_SCOPED_COMMIT. Clean-checkout reproducibility is proven; broad/blanket commit remains prohibited because unrelated staged work still exists.

- [x] E1 Delivery security/readiness audit is green.
  - `maint:etb-delivery-readiness` job `bff9a3b9-c7a5-4a95-aad1-da0580965a36` — PASS.
  - Sensitive tracked/staged paths: 0.
  - Staged fingerprint: `3db7a2eff19efd26324c40cb8548a24aaf68811f701fb66e6fc55fbac892f144`.
  - Final worktree fingerprint: `737321ad092b2ee0b04c9e95c65d28f2dd0ba94b95159c2b3183b10a5d4a2a52`.
  - Branch: `feature/etb-regression-pack`; observed HEAD: `48c09a1cd975695c05da09b770c78cb502c38450`.
  - Final delivery-guard refresh job `83d8d03a-7b63-4493-80d3-ee40c7b97d19` — PASS; staged=57, modified=63, untracked=290, sensitive tracked/staged=0.
  - Artifact-security job `67d876aa-63b1-4c4d-996c-1d34372cb982` — PASS (5/5).
  - Delivery-readiness contract job `cb6da609-84d3-4fe7-9c67-0f3014a822bb` — PASS (5/5).

- [x] E2 Traceability/runtime receipts are clean-checkout safe.
  - Full traceability no longer requires committed `reports/run-etb/**` artifacts.
  - Runtime bindings retain run IDs + committed acceptance snapshot; raw/local evidence paths are explicitly `LOCAL_ONLY_NOT_REQUIRED_FOR_CLEAN_CHECKOUT`.
  - Validation: `test:etb-traceability-pilot`, job `14e3121b-a7f4-449b-a322-4ccf0154f3d5` — PASS (14/14).
  - `configs/mobile_delivery_manifest.json` now includes Block C/D files needed by the current clean candidate.

- [x] E3 Hygiene is green and non-destructive.
  - `test:bbl-hygiene` job `e23de144-276f-4b06-a564-19ec8a75fbc4` — PASS.
  - `maint:bbl-hygiene-status` job `b32c7b50-b25b-4c34-97c3-b8ad50b111e7` — PASS.
  - Cleanup mode: DRY_RUN; candidate count: 0; cleanup applied: NO.
  - APK inventory: 3 total, all protected active lanes (DEV mock / current DEV / current SIT).

- [x] E4 Mandatory working-tree automation gate remains green.
  - Validation: `test:bbl-automation-standard`
  - Job: `8835d648-4787-44bc-a62a-0de79d5462ea`
  - Result: PASS / exit 0.

- [x] E5 Clean-index reproducibility is proven.
  - Final `test:etb-reproducibility` job `47f8dd0f-3c8d-4d80-abb3-ec91887908c6` — PASS (7/7).
  - Final `maint:etb-reproducibility` job `fe874380-1218-42e7-bd18-f72d6173bc61` — PASS.
  - `MOBILE_LOCK=PASS`
  - `CANDIDATE_CLEAN_SNAPSHOT=PASS`
  - `CANDIDATE_DRY_RUN=PASS`
  - `CANDIDATE_SELECTED_COUNT=1`
  - `INDEX_TRANSFER_GAP_COUNT=0`
  - `F17_CLEAN_CHECKOUT_PROOF=PASS`
  - Clean-candidate dependency gap for the app-update locator was added to the delivery manifest.
  - Reproducibility guard handles synthetic repositories without a HEAD commit while preserving index-vs-worktree semantics.
  - Machine-readable receipt: `configs/etb_delivery_candidate.json`.

- [x] E6 Controlled index reconciliation is complete for the delivery manifest.
  - Original transfer gaps: 58 = 40 `INDEX_DIFFERS_FROM_WORKTREE` + 18 `MISSING_FROM_INDEX`.
  - Final transfer gaps: 0.
  - DOPA synthetic fixture was aligned with the production namespaced DOB keyword; production behavior was not changed.
  - DOPA validation job `880d7f25-210c-421e-8c89-8ffd2014b485` — PASS.
  - Final artifact-security job `d6607cdc-12b0-4f80-886a-3115e5488e63` — PASS (5/5).
  - Final delivery-readiness job `1bc275e8-ba3c-4cf5-82ae-81257282f54e` — PASS (5/5).
  - Final mandatory `test:bbl-automation-standard` job `4463d979-69af-4cce-8c6c-8f070f242425` — PASS / exit 0.
  - DO NOT use blanket `git add -A` or a broad `git commit`: pre-existing staged paths outside the delivery manifest remain in the repository.
  - Any commit for this delivery must be explicitly path-scoped to the approved delivery candidate.
  - PR / merge: NOT performed in Block E.

## Current live acceptance receipt — 2026-09-27

This section supersedes earlier temporary DEFER/HOLD runtime states below while preserving them as historical evidence.

- [ ] TC003 — latest bounded rerun reached Profile Next and observed `RAI-033`; DOPA was not reached. Treat as runtime/app-state blocker with root cause unproven. Do not change DOB logic or business expectation from this result.
  - Run: `20260927T031747603243Z-p15368`
  - Result: FAIL, `PROFILE_RESPONSE_UNEXPECTED_RAI_033`
  - Preflight: Build191 / POST_MMP_1 / emulator-5556 / CIS READY / target guard PASS / Appium READY.
- [ ] TC004 — independent rerun also reached Profile Next and observed `RAI-033`; DOPA was not reached. This cross-case match supports runtime/app-state classification rather than an automation interaction defect.
  - Run: `20260927T032347728621Z-p21564`
  - Result: FAIL, `PROFILE_RESPONSE_UNEXPECTED_RAI_033`
  - CIS clear before run: PASS.
- [x] TC005 — final verification completed last as requested and is TRUSTED.
  - Run: `20260927T042429089204Z-p89952`
  - Result: PASS (1/1), `ETB_RUN_RESULT=PASS`, result trust `TRUSTED`
  - Evidence: COMPLETE; missing expected = 0; existing unindexed = 0; CIS cleanup PASS.
- [ ] TC002 — owner resumed and manually cleared CIS before the latest isolated run; the testcase still observed `RAI-033` after Profile Next, so the earlier defer state is superseded by a current runtime/app-state blocker.
  - Run: `20260927T044036405305Z-p8528`
  - Result: FAIL, `PROFILE_RESPONSE_UNEXPECTED_RAI_033`
  - Marker evidence: P0/P1/P2 Profile markers present; first recognized destination = `RAI-033`; DOPA not reached.
  - Result trust: `DEGRADED`; blocker type `OBSERVED_RESPONSE`; failure origin remains `UNKNOWN`.
  - Preflight: Build191 / POST_MMP_1 / emulator-5556 / disk PASS / target guard PASS / Appium READY / CIS transport READY.
  - Decision: do not change the TC002 business expectation from this result; manual CIS clear alone did not remove the observed RAI-033 condition.
- [x] TC006 — previously TRUSTED; no rerun required.
- [x] TC007 — previously TRUSTED; no rerun required.
- [x] TC008 — previously TRUSTED; no rerun required.
- [x] TC009 — previously TRUSTED; no rerun required.
- [x] TC010 — service condition recovered; bounded reprobe is now TRUSTED PASS and supersedes the earlier AJI-001 defer state.
  - Run: `20260927T033120788982Z-p29583`
  - Result: PASS (1/1), result trust `TRUSTED`
  - Evidence: COMPLETE; missing expected = 0; existing unindexed = 0; CIS cleanup PASS.
- [x] TC011 — TRUSTED PASS after service recovery; supersedes the earlier AJI-001 defer state.
  - Run: `20260927T041035604187Z-p75478`
  - Result: PASS (1/1), result trust `TRUSTED`
  - Evidence: COMPLETE; missing expected = 0; existing unindexed = 0.
- [x] TC012 — TRUSTED PASS after service recovery.
  - Run: `20260927T041501698390Z-p80301`
  - Result: PASS (1/1), result trust `TRUSTED`
  - Evidence: COMPLETE; missing expected = 0; existing unindexed = 0.
- [ ] TC013 — backend/test-data branch mismatch remains open; do not change expected `RGI-016` or its locator.
  - Latest run: `20260927T050452876260Z-p34690`
  - Expected: `RGI-016` after Laser Code Next.
  - Observed: Profile exit reached DOPA, Laser Code was entered and Next submitted; the final failure hierarchy was on the normal OTP screen (`screenVerifyMobileNumberOTP_*`) with no `RGI-016`, AJI, RAI or GOD code present.
  - Result: FAIL, result trust `DEGRADED`; missing expected = 0; existing unindexed = 0; failure origin remains `UNKNOWN`.
  - Reproduction: same expected `RGI-016` miss occurred in the prior bounded run, so this is not a one-off locator/timing failure.
  - Classification: the configured TC013 profile is currently following the normal onboarding branch instead of the mule/suspicious-account branch. Clear CIS alone is insufficient.
  - Required next condition: backend/test-data owner must prepare the TC013 Citizen ID as mule/suspicious-account so Laser Code Next routes to `RGI-016`; then rerun unchanged automation.
  - Decision: do not patch the business expectation or locator to make the test pass.
- [x] CIS transport readiness = READY.
- [x] Final CIS harness independence: PASS, job `9e679cd4-4c08-4a10-8dad-2f028726c939`.
- [x] Final mandatory `test:bbl-automation-standard`: PASS / exit 0, job `6c72f00b-3f9c-485b-948c-8a67f5a9f170`.
- [x] `package.json` temporary single-case bridges removed; baseline hash restored to `c32389c95c3989ff0723c992df2d62fb2bfb6c16e0edb2537ba7d87b9f4379d9`.
- [ ] Cleanup remains HOLD until owner accepts this mobile-acceptance baseline and remaining deferred/blocker cases are dispositioned.

## Next before cleanup

- [ ] Mobile acceptance rerun: verify device, Build191, POST_MMP_1 target guard, CIS transport, network/proxy, Appium and evidence index before runtime.
- [ ] Run the agreed canonical TC005 smoke first; if the runtime setup/smoke is sound, proceed to TC002 and then independent selected cases according to the existing ETB procedure.
- [ ] Clear CIS ID before each testcase when required by the existing ETB procedure and require the clear/readiness step to pass before execution.
- [ ] Inspect runtime screenshots/evidence stage-by-stage; do not classify only from Robot status.
- [ ] Compare POST runtime evidence only against the local BBL Wiki at `/Users/RARW/BBL/local/obsidian-bbl`.
- [ ] Review runtime results and POST-MMP evidence before changing any business expectation.
- [ ] Cleanup remains HOLD until the test baseline and selected mobile acceptance are accepted.

## Guardrails

- Do not change ETB POST business requirements merely to make tests pass.
- Do not delete/archive project artifacts while Cleanup is HOLD.
- Do not reset or discard existing dirty/staged work as part of harness remediation.
- Every remediation item must record the validation command/job and terminal result before being checked off.
