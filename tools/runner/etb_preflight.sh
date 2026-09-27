# ETB target, CIS, and package/device preflight gates.
# Sourced by etb_runner.sh; functions intentionally use Bash dynamic scope.


run_etb_disk_preflight() {
    local disk_result
    if ! disk_result="$("$PYTHON_BIN" "$ROOT/tools/runner/etb_runtime.py" disk-guard "$ROOT" "${ETB_DISK_WARN_GB:-10}" "${ETB_DISK_FAIL_GB:-5}")"; then
        printf 'ETB_DISK_GATE=CLOSED; insufficient or unproven local disk capacity.\n' >&2
        exit 3
    fi
    printf '%s\n' "$disk_result"
}

run_etb_target_preflight() {
    local target_result
    if ! target_result="$("$PYTHON_BIN" "$ROOT/tools/runner/etb_runtime.py" target-guard "$DEVICE_UDID" "$ANDROID_EXECUTION_TARGET" "$ETB_ENVIRONMENT" "$APP_PACKAGE" "$APP_ACTIVITY" "$ETB_COMPETING_PACKAGE" "$ETB_PRODUCT_RELEASE")"; then
        printf 'TARGET_GUARD=FAIL; no backend or device preparation will start.\n' >&2
        exit 3
    fi
    printf 'TARGET_GUARD=PASS %s\n' "$target_result"

    local build_identity
    if ! build_identity="$("$PYTHON_BIN" "$ROOT/tools/runner/etb_runtime.py" target-build-identity "$target_result")"; then
        printf 'TARGET_GUARD_BUILD_IDENTITY=FAIL; runtime provenance will not continue.\n' >&2
        exit 3
    fi
    export ETB_BUILD_IDENTITY="$build_identity"
    if ! "$PYTHON_BIN" "$ROOT/tools/runner/etb_runtime.py" record-build-identity "$ETB_OUTPUT/run_manifest.json" "$ETB_BUILD_IDENTITY"; then
        printf 'TARGET_GUARD_BUILD_IDENTITY_PERSIST=FAIL; runtime provenance will not continue.\n' >&2
        exit 3
    fi

    if [[ "$ANDROID_EXECUTION_TARGET" == "REAL" ]]; then
        mkdir -p "$ETB_OUTPUT/device"
        if ! "$PYTHON_BIN" "$REAL_DEVICE_PREFLIGHT" \
            --serial "$DEVICE_UDID" \
            --report-dir "$ETB_OUTPUT/device" \
            --package "$ETB_TARGET_PACKAGE" \
            --activity "$ETB_TARGET_ACTIVITY"; then
            printf 'REAL_DEVICE_PREFLIGHT=FAIL; no backend or device preparation will start.\n' >&2
            exit 3
        fi
    fi
}

run_etb_network_preflight() {
    local network_result
    if ! network_result="$("$PYTHON_BIN" "$ROOT/tools/etb_network_preflight.py"         --serial "$DEVICE_UDID"         --environment "$ETB_ENVIRONMENT"         --execution-target "$ANDROID_EXECUTION_TARGET")"; then
        printf 'ETB_NETWORK_GATE=CLOSED; emulator proxy/network runtime is not ready.\n' >&2
        exit 3
    fi
    printf '%s\n' "$network_result"
}

run_etb_appium_preflight() {
    local appium_result
    if ! appium_result="$("$PYTHON_BIN" "$ROOT/tools/appium_server.py" --reconcile)"; then
        printf 'APPIUM_RUNTIME_GATE=CLOSED; managed Appium runtime is not ready.\n' >&2
        exit 3
    fi
    printf '%s\n' "$appium_result"
}

run_etb_cis_preflight() {
    local cis_result
    if [[ "$ETB_ENVIRONMENT" == "SIT" || "$ETB_ENVIRONMENT" == "sit" ]]; then
        local cis_report_dir="$ETB_OUTPUT/cis-preflight"
        mkdir -p "$cis_report_dir"
        if [[ "$selector_type" != "all" ]]; then
            cis_selection_args=("${selected_case_ids[@]}")
        fi
        if ! cis_result="$("$PYTHON_BIN" "$ROOT/tools/runner/etb_runtime.py" sit-cis-readiness "${ETB_CASE_PROFILES:-$ROOT/testdata/onboarding/etb_cases.local.yaml}" "$cis_report_dir" "${cis_selection_args[@]+"${cis_selection_args[@]}"}")"; then
            printf 'SIT CIS readiness audit could not execute under runner interpreter.\n' >&2
            exit 3
        fi
        printf 'SIT CIS external-preparation gate: %s\n' "$cis_result"
        if [[ "$cis_result" != *'"cis_readiness_status": "VERIFIED"'* && "$cis_result" != *'"cis_readiness_status": "EXTERNALLY_CONFIRMED"'* ]]; then
            printf 'FULL_RUNTIME_GATE=CLOSED; no SIT mobile runtime will start.\n' >&2
            exit 3
        fi
    elif ! cis_result="$("$PYTHON_BIN" "$ROOT/tools/runner/etb_runtime.py" cis-preflight "$ETB_ENVIRONMENT")"; then
        printf 'CIS preflight gate could not execute under runner interpreter.\n' >&2
        exit 3
    fi

    if [[ "$ETB_ENVIRONMENT" == "DEV_MOCK" ]]; then
        if [[ "$cis_result" != *'"cis_clear": "NOT_APPLICABLE"'* || "$cis_result" != *'"cis_state_ready": "NOT_REQUIRED"'* ]]; then
            printf 'Mock CIS readiness gate failed: %s\n' "$cis_result" >&2
            exit 3
        fi
    elif [[ "$ETB_ENVIRONMENT" != "SIT" && "$ETB_ENVIRONMENT" != "sit" ]]; then
        if [[ "$cis_result" != *'"ready": "YES"'* ]]; then
            printf 'CIS transport gate failed: %s\n' "$cis_result" >&2
            exit 3
        fi
    fi
    printf 'CIS preflight gate passed: %s\n' "$cis_result"
}

prepare_etb_android_environment() {
    if [[ "$ETB_ENVIRONMENT" == "DEV_MOCK" ]]; then
        prepare_dev_mock_environment
    elif [[ "$ETB_ENVIRONMENT" == "SIT" ]]; then
        prepare_sit_environment
    else
        prepare_dev_environment
    fi
}
