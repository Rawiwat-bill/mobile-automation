# C2 — File Decisions Log

> Every untracked file from Sprint C1, its classification, and its destination.

---

## Investigation Tests (63 files → 13 promoted + 50 archived)

### Promoted to `tests/benchmark/` (1 file)

| File | Original Path | New Path | Rationale |
|------|---------------|----------|-----------|
| `next_tap_test.robot` | `tests/investigation/` | `tests/benchmark/` | Tap strategy comparison — reusable benchmark |

### Promoted to `tests/health/` (7 files)

| File | Original Path | New Path | Rationale |
|------|---------------|----------|-----------|
| `emulator_revival.robot` | `tests/investigation/` | `tests/health/` | Emulator recovery procedure — reusable |
| `emulator_runtime_verification.robot` | `tests/investigation/` | `tests/health/` | Device qualification — reusable |
| `real_device_baseline.robot` | `tests/investigation/` | `tests/health/` | Real device baseline — reusable |
| `real_device_appium_health.robot` | `tests/investigation/` | `tests/health/` | Appium readiness check — reusable |
| `real_device_locator_compatibility.robot` | `tests/investigation/` | `tests/health/` | Locator dryrun validation — reusable |
| `backend_gate.robot` | `tests/investigation/` | `tests/health/` | Backend availability check — reusable |
| `real_device_profile_resume.robot` | `tests/investigation/` | `tests/health/` | Device resume validation — reusable |

### Promoted to `tests/regression/` (3 files)

| File | Original Path | New Path | Rationale |
|------|---------------|----------|-----------|
| `final_virtual_scene_validation.robot` | `tests/investigation/` | `tests/regression/` | Validates camera setup — CI regression |
| `compare_authid_test.robot` | `tests/investigation/` | `tests/regression/` | AuthID comparison — M4 validation point |
| `onboarding_branch_decision.robot` | `tests/investigation/` | `tests/regression/` | NTB/ETB branching — regression validation |

### Promoted to `tests/preparation/` (2 files)

| File | Original Path | New Path | Rationale |
|------|---------------|----------|-----------|
| `virtual_scene_nav.robot` | `tests/investigation/` | `tests/preparation/` | Camera nav needed for OCR milestone |
| `navigate_to_camera_test.robot` | `tests/investigation/` | `tests/preparation/` | Camera navigation — OCR prep |

### Archived to `tests/_archive/investigation/` (50 files)

One-off debug scripts with findings already captured in `knowledge/`. Import paths may be stale (depth changed from 2 to 3). These files are tracked but not expected to run.

| File | Finding Captured In |
|------|---------------------|
| `profile_next_parity.robot` | `knowledge/profile/next_button.md` |
| `profile_next_parity2.robot` | `knowledge/profile/next_button.md` |
| `profile_parity_sprint.robot` | `knowledge/profile/next_button.md` |
| `profile_parity_attach.robot` | `knowledge/profile/next_button.md` |
| `manual_vs_auto_parity.robot` | `knowledge/playbooks/debugging-playbook.md` |
| `consent_scroll_bottom.robot` | Superseded by `scroll_keywords.resource` |
| `responsive_scroll_consent.robot` | Superseded by `Scroll Down Page Responsively` |
| `real_device_consent_accept_isolation.robot` | Finding captured |
| `virtual_scene_recheck.robot` | Superseded |
| `camera_capture_reverse.robot` | One-off |
| `cam_sleep_test.robot` | One-off |
| `diag_take_photo_test.robot` | Debug script |
| `frida_node_injection_test.robot` | Technique in `tools/frida/` |
| `frida_ocr_injection_resume.robot` | Technique documented |
| `early_frida_test.robot` | Technique documented |
| `listener_capture_test.robot` | Debug script |
| `authid_trace.robot` | Finding captured |
| `authid_trace_attach.robot` | Finding captured |
| `authid_capture.robot` | Finding captured |
| `full_response_test.robot` | Technique in `api_capture_keywords` |
| `forgerock_discovery.robot` | Finding captured |
| `line684_test.robot` | One-off |
| `rt_test.robot` | One-off |
| `real_device_demo.robot` | Superseded by `tests/demo/` |
| `real_device_onboarding_resume.robot` | One-off |
| `real_device_flow_migration.robot` | One-off |
| `promise_trace_test.robot` | Debug script |
| `promise_trace_full_test.robot` | Debug script |
| `take_photo_call_chain.robot` | Finding captured |
| `takephoto_hook_test.robot` | Finding captured |
| `init_takephoto_test.robot` | Finding captured |
| `init_event_test.robot` | Finding captured |
| `cnd_callback_capture.robot` | Finding captured |
| `native_flow_test.robot` | One-off |
| `lsf_test.robot` | One-off |
| `bridge_ocr_test.robot` | Technique documented |
| `bridge_next_contract_test.robot` | Technique documented |
| `ntb_lc_contract_test.robot` | Technique documented |
| `scenario_b_test.robot` | One-off |
| `mid_size_test.robot` | One-off |
| `approach_h_test.robot` | One-off |
| `image_trace_test.robot` | One-off |
| `eval_js_test.robot` | One-off |
| `eval_js_robust_test.robot` | One-off |
| `debug_panel_discovery.robot` | Finding captured |
| `debug_panel_deep.robot` | Finding captured |
| `diag_connect_test.robot` | Debug script |
| `exc_capture.robot` | Debug script |
| `nb_trace.robot` | Debug script |
| `real_device_consent_accept_isolation.robot` | Finding captured |
| `cam_sleep_test.robot` | One-off |

---

## Frida Scripts (68 files → organized by milestone)

### `tools/frida/ocr/` (13 scripts) — Milestone 3: NTB OCR

`ssl_bypass_ocr.js`, `ocr_format_persistence.js`, `ocr_format_v2.js`, `ocr_multi_format.js`, `ocr_callback_injector.js`, `ocr_v3_response_capture.js`, `ocr_image_base64.js`, `ocr_image_embedded.js`, `ocr_node_injector.js`, `load_script_ocr.js`, `camera_ocr_trace.js`, `eval_js_ocr.js`, `chain_ocr_to_ntblc.js`

### `tools/frida/bridge/` (13 scripts) — Milestone 3: OCR Bridge

`capture_bridge_format.js`, `bridge_small_160x100_q40.js`, `bridge_small_240x160_q50.js`, `bridge_small_360x240_q60.js`, `bridge_next_inject.js`, `bridge_next_contract_probe.js`, `two_step_bridge.js`, `scenario_b_bridge_only.js`, `flow_and_inject.js`, `fr_auth_bridge_684_probe.js`, `full_response_fix.js`, `ntb_lc_contract_submit_template.js`, `ntb_lc_parser_discovery.js`

### `tools/frida/face/` (8 scripts) — Milestone 4: Face Verification

`authid_compare.js`, `authid_session_trace.js`, `bridge_authid_inject.js`, `capture_all_authids.js`, `compare_authids.js`, `resolve_authid_inject.js`, `response_authid_bridge.js`, `response_authid_v2.js`

### `tools/frida/debug/` (33 scripts) — General Debugging/Tracing

`camerax_trace.js`, `minimal_camera_trace.js`, `find_camera_path.js`, `device_event_takephoto.js`, `diag_take_photo.js`, `hook_takephoto.js`, `take_photo_call_chain.js`, `init_and_takephoto.js`, `find_catalyst.js`, `enumerate_classes.js`, `control_flow_analysis.js`, `coroutine_trace.js`, `current_node_inject.js`, `exc_stack.js`, `exception_capture.js`, `forgerock_method_discovery.js`, `image_pipeline_trace.js`, `line684_deep_trace.js`, `listener_auto_inject.js`, `listener_auto_inject_v2.js`, `listener_auto_inject_v3.js`, `listener_capture_inject.js`, `mid_q30_test.js`, `mid_size_test.js`, `native_js_flow_trace.js`, `native_js_flow_v2.js`, `network_boundary_trace.js`, `parsecallback_failure.js`, `promise_resolve_capture.js`, `promise_state_check.js`, `promise_trace.js`, `real_listener_inject.js`, `runtime_deep_trace.js`

### `tools/frida/*.sh` (3 shell scripts) — Kept at root

`attach_frida.sh`, `attach_and_wait.sh`, `start_frida_bg.sh`

---

## Production Code Tracked (not previously tracked)

| Category | Files |
|----------|-------|
| Locators | `id_card_camera_capture_locators.resource`, `pdpa_consent_locators.resource`, `scan_card_intro_locators.resource`, `sign_up_locators.resource` |
| Page Resources | `id_card_camera_capture_page.resource`, `pdpa_consent_page.resource`, `scan_card_intro_page.resource`, `sign_up_page.resource` |
| Keywords | `api_capture_keywords.resource`, `dob_stability_keywords.resource`, `health_check_keywords.resource`, `scroll_keywords.resource` |
| Benchmark | `benchmark_base.resource`, `benchmark_strategies.resource`, `consent_scroll_strategies.resource`, `BenchmarkMetrics.py` |
| Libraries | `api_log_redactor.py` |
| Tests | `onboarding_health_check.robot` |
| Docs | `docs/architecture/`, `docs/knowledge/`, `docs/research/`, `docs/reviews/` |
| Config | `opencode.json`, `package.json`, `package-lock.json` |
| Knowledge | `knowledge/profile/dob_picker.md` |
| Tools | `tools/emulator/`, `tools/performance/`, `tools/ci/`, `tools/frida/` |
| Mock Data | `apps/android/mock/ntb_id_card.png` |
| Configs | `configs/env/dev.yaml`, `configs/devices/emulator.yaml`, `configs/devices/real_device.yaml` (empty but tracked as scaffold) |

---

## Files NOT Tracked (gitignored)

| Category | Reason |
|----------|--------|
| `.opencode/` | Local node_modules for opencode CLI |
| `apps/android/app.apk` | APK binary — gitignored |
| `*.local.yaml` | Local sensitive test data |
| `__pycache__/` | Python cache |
| `.DS_Store` | macOS metadata |
| `reports/` | Robot output and evidence |
| `log.html`, `output.xml`, `report.html` | Root robot outputs |
| `node_modules/` | Dependencies |
