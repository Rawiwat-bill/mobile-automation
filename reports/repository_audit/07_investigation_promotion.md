# 07 — Investigation Promotion

> 63 investigation test files in `tests/investigation/` (all untracked).
> Do NOT archive useful work. Classify each into: Benchmark, Health, Regression,
> Preparation, or Archive.

## Classification Criteria

| Target | Criteria |
|--------|----------|
| **Benchmark** | Measures interaction strategy performance; reusable for regression detection |
| **Health** | Validates environment/device readiness; reusable pre-flight check |
| **Regression** | Validates a specific fix or behavior; should run in CI |
| **Preparation** | Sets up app state for downstream tests |
| **Archive** | One-off debug script; finding already captured in knowledge/; no reuse value |

---

## Classification by Category

### Profile / Next Button Investigations (Milestone 2 — DONE)

| File | Lines | Finding | Target |
|------|-------|---------|--------|
| `profile_next_parity.robot` | 90 | Manual vs auto parity for Profile Next | **Archive** — finding captured in `knowledge/profile/next_button.md` |
| `profile_next_parity2.robot` | 111 | Continuation of above | **Archive** — same finding |
| `profile_parity_sprint.robot` | 140 | Sprint investigation of parity | **Archive** — milestone complete |
| `profile_parity_attach.robot` | 132 | Attached session parity test | **Archive** — milestone complete |
| `manual_vs_auto_parity.robot` | 127 | Manual success vs automation failure comparison | **Archive** — methodology documented in playbooks |
| `next_tap_test.robot` | 82 | Next button tap strategies | **Promote to Benchmark** — tap strategy comparison is reusable |
| `real_device_profile_resume.robot` | 98 | Profile screen resume on real device | **Promote to Health** — device resume validation |

### Consent Scroll Investigations

| File | Lines | Finding | Target |
|------|-------|---------|--------|
| `consent_scroll_bottom.robot` | 79 | Consent scroll to bottom detection | **Archive** — superseded by `scroll_keywords.resource` |
| `responsive_scroll_consent.robot` | 76 | Responsive scroll on consent | **Archive** — superseded by `Scroll Down Page Responsively` |
| `real_device_consent_accept_isolation.robot` | 170 | Consent accept isolation on real device | **Archive** — finding captured |

### Camera / Virtual Scene Investigations (Milestone 3 prep)

| File | Lines | Finding | Target |
|------|-------|---------|--------|
| `virtual_scene_nav.robot` | — | Virtual scene navigation | **Promote to Preparation** — camera nav is needed for OCR milestone |
| `virtual_scene_recheck.robot` | — | Recheck virtual scene | **Archive** — superseded |
| `final_virtual_scene_validation.robot` | — | Final validation of virtual scene | **Promote to Regression** — validates camera setup |
| `navigate_to_camera_test.robot` | — | Navigate to camera | **Promote to Preparation** — needed for OCR |
| `camera_capture_reverse.robot` | 97 | Reverse camera capture | **Archive** — one-off |
| `cam_sleep_test.robot` | — | Camera sleep timing | **Archive** — one-off |
| `diag_take_photo_test.robot` | 81 | Diagnostic take photo | **Archive** — debug script |

### Frida / Instrumentation Investigations (Milestone 3 prep)

| File | Lines | Finding | Target |
|------|-------|---------|--------|
| `frida_node_injection_test.robot` | — | Frida node injection | **Archive** — technique documented; script in `tools/frida/` |
| `frida_ocr_injection_resume.robot` | 80 | Frida OCR injection resume | **Archive** — technique documented |
| `early_frida_test.robot` | 93 | Early Frida attach | **Archive** — technique documented |
| `listener_capture_test.robot` | — | Listener capture | **Archive** — debug script |
| `listener_auto_inject*.js` (in tools/frida/) | — | Auto-inject listeners | **Keep in tools/frida/** — reusable for future instrumentation |

### AuthID / Face Investigations (Milestone 4 prep)

| File | Lines | Finding | Target |
|------|-------|---------|--------|
| `authid_trace.robot` | — | AuthID trace | **Archive** — finding captured |
| `authid_trace_attach.robot` | 72 | Attached AuthID trace | **Archive** |
| `authid_capture.robot` | — | AuthID capture | **Archive** |
| `compare_authid_test.robot` | — | Compare AuthID | **Promote to Regression** — AuthID comparison is a validation point for M4 |

### API / Backend Investigations

| File | Lines | Finding | Target |
|------|-------|---------|--------|
| `backend_gate.robot` | — | Backend gate behavior | **Promote to Health** — backend availability check |
| `full_response_test.robot` | — | Full API response capture | **Archive** — technique in api_capture_keywords |
| `forgerock_discovery.robot` | 74 | ForgeRock method discovery | **Archive** — finding captured |
| `line684_test.robot` | — | Line 684 investigation | **Archive** — one-off |
| `rt_test.robot` | — | Runtime test | **Archive** |

### Emulator / Device Investigations

| File | Lines | Finding | Target |
|------|-------|---------|--------|
| `emulator_revival.robot` | 221 | Emulator revival procedure | **Promote to Health** — emulator recovery is reusable |
| `emulator_runtime_verification.robot` | 90 | Runtime verification | **Promote to Health** — device qualification |
| `real_device_baseline.robot` | 128 | Real device baseline | **Promote to Health** — device baseline validation |
| `real_device_appium_health.robot` | 80 | Appium health on real device | **Promote to Health** — Appium readiness check |
| `real_device_locator_compatibility.robot` | 11 | Locator compatibility (dryrun) | **Promote to Health** — locator validation |
| `real_device_demo.robot` | 73 | Real device demo | **Archive** — superseded by `tests/demo/live_demo.robot` |
| `real_device_onboarding_resume.robot` | 194 | Onboarding resume on real device | **Archive** — one-off |
| `real_device_flow_migration.robot` | 177 | Flow migration | **Archive** — one-off |
| `onboarding_branch_decision.robot` | 192 | Branch decision logic | **Promote to Regression** — NTB/ETB branching validation |

### Promise / Call Chain Investigations

| File | Lines | Finding | Target |
|------|-------|---------|--------|
| `promise_trace_test.robot` | 86 | Promise trace | **Archive** — debug script |
| `promise_trace_full_test.robot` | — | Full promise trace | **Archive** |
| `take_photo_call_chain.robot` | 149 | Take photo call chain | **Archive** — finding captured |
| `takephoto_hook_test.robot` | 92 | TakePhoto hook | **Archive** |
| `init_takephoto_test.robot` | 94 | Init TakePhoto | **Archive** |
| `init_event_test.robot` | 95 | Init event | **Archive** |
| `cnd_callback_capture.robot` | 77 | CND callback capture | **Archive** |
| `native_flow_test.robot` | 85 | Native flow test | **Archive** |
| `lsf_test.robot` | 88 | LSF test | **Archive** |

### OCR Bridge Investigations (Milestone 3 prep)

| File | Lines | Finding | Target |
|------|-------|---------|--------|
| `bridge_ocr_test.robot` | — | Bridge OCR | **Archive** — technique documented |
| `bridge_next_contract_test.robot` | 98 | Bridge next contract | **Archive** |
| `ntb_lc_contract_test.robot` | 81 | NTB LC contract | **Archive** |
| `scenario_b_test.robot` | — | Scenario B | **Archive** |
| `mid_size_test.robot` | — | Mid-size image test | **Archive** |
| `approach_h_test.robot` | 85 | Approach H | **Archive** |
| `image_trace_test.robot` | — | Image trace | **Archive** |

### JS Eval / Debug Investigations

| File | Lines | Finding | Target |
|------|-------|---------|--------|
| `eval_js_test.robot` | — | JS eval | **Archive** |
| `eval_js_robust_test.robot` | 88 | Robust JS eval | **Archive** |
| `debug_panel_discovery.robot` | — | Debug panel discovery | **Archive** — finding captured |
| `debug_panel_deep.robot` | — | Debug panel deep | **Archive** |
| `diag_connect_test.robot` | — | Diagnostic connect | **Archive** |
| `exc_capture.robot` | — | Exception capture | **Archive** |
| `nb_trace.robot` | — | NB trace | **Archive** |

---

## Summary

| Target | Count | Action |
|--------|-------|--------|
| **Promote to Benchmark** | 1 | `next_tap_test.robot` |
| **Promote to Health** | 7 | emulator_revival, emulator_runtime_verification, real_device_baseline, real_device_appium_health, real_device_locator_compatibility, backend_gate, real_device_profile_resume |
| **Promote to Regression** | 3 | final_virtual_scene_validation, compare_authid_test, onboarding_branch_decision |
| **Promote to Preparation** | 2 | virtual_scene_nav, navigate_to_camera_test |
| **Archive** | 50 | One-off debug scripts with findings already captured |

### Frida Scripts (`tools/frida/` — 67 files)

| Category | Count | Action |
|----------|-------|--------|
| OCR-related | ~20 | Keep in `tools/frida/ocr/` for M3 |
| AuthID/Face-related | ~10 | Keep in `tools/frida/face/` for M4 |
| Camera/debug | ~15 | Keep in `tools/frida/debug/` |
| Bridge/injection | ~15 | Keep in `tools/frida/bridge/` for M3 |
| Shell scripts | 4 | Keep (attach_frida.sh, start_frida_bg.sh, etc.) |

**Do NOT delete Frida scripts.** They are reusable instrumentation for upcoming milestones.
Subfolder them by purpose and track in git.

---

## Promotion Process (for C2)

1. For each "Promote" file: move to target directory, add tags, update imports.
2. For each "Archive" file: move to `reports/investigation/archive/` or gitignore.
3. For Frida scripts: subfolder by milestone, track in git.
4. Do NOT delete — archive preserves history.
