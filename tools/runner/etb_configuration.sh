# ETB runner runtime configuration.
# Sourced by etb_runner.sh; functions intentionally use Bash dynamic scope.

detect_etb_dry_run() {
    local arg
    for arg in "$@"; do
        if [[ "$arg" == "--dry-run" ]]; then
            dry_run=true
            break
        fi
    done
}

load_etb_runtime_configuration() {
    if [[ -r "$ROOT/local/env/etb.env" ]]; then
        local explicit_environment
        explicit_environment="$(export -p)"
        set -a
        # shellcheck disable=SC1091
        source "$ROOT/local/env/etb.env"
        set +a
        # export -p renders entries as "declare -x ...".  Evaluating those
        # inside a function creates locals, so caller overrides disappear
        # when the function returns.  Re-emit them as export assignments so
        # the original exported environment remains authoritative.
        explicit_environment="${explicit_environment//declare -x /export }"
        eval "$explicit_environment"
    fi

    if [[ -z "${PDPA_CA_BUNDLE:-}" && -r "$ROOT/local/certs/cis-ca-bundle.pem" ]]; then
        export PDPA_CA_BUNDLE="$ROOT/local/certs/cis-ca-bundle.pem"
    fi

    ETB_ENVIRONMENT="${ETB_ENVIRONMENT:-DEV}"
    ETB_PRODUCT_RELEASE="${ETB_PRODUCT_RELEASE:-POST_MMP_1}"
    case "$ETB_PRODUCT_RELEASE" in
        MMP_LOT2_V2|POST_MMP_1) ;;
        *)
            printf 'Unsupported ETB_PRODUCT_RELEASE: %s (expected MMP_LOT2_V2 or POST_MMP_1).\n' "$ETB_PRODUCT_RELEASE" >&2
            exit 2
            ;;
    esac
    ANDROID_EXECUTION_TARGET="${ANDROID_EXECUTION_TARGET:-REAL}"
    case "$ANDROID_EXECUTION_TARGET" in
        REAL|real)
            ANDROID_EXECUTION_TARGET="REAL"
            if [[ "$dry_run" != true && -z "${DEVICE_UDID:-}" ]]; then
                printf 'REAL_DEVICE_PREFLIGHT=FAIL DEVICE_UDID is required for REAL execution.\n' >&2
                exit 3
            fi
            ;;
        EMULATOR|emulator|DIAGNOSTIC_CONTROL)
            ANDROID_EXECUTION_TARGET="DIAGNOSTIC_CONTROL"
            ;;
        *)
            printf 'Unsupported ANDROID_EXECUTION_TARGET: %s (expected REAL or DIAGNOSTIC_CONTROL).\n' "$ANDROID_EXECUTION_TARGET" >&2
            exit 2
            ;;
    esac

    case "$ETB_ENVIRONMENT" in
        DEV|dev)
            ETB_TARGET_PACKAGE="com.bangkokbank.blue.dev"
            ETB_COMPETING_PACKAGE="com.bangkokbank.blue.sit"
            ETB_TARGET_ACTIVITY="com.bangkokbank.blue.MainActivity"
            case "$ETB_PRODUCT_RELEASE" in
                MMP_LOT2_V2) ETB_DEV_APK="$ROOT/apps/android/app-dev-mmp.apk" ;;
                POST_MMP_1) ETB_DEV_APK="$ROOT/apps/android/app-dev.apk" ;;
            esac
            ;;
        DEV_MOCK)
            if [[ "${CIS_READINESS_SOURCE:-}" != "MOCK_BUILD_NOT_REQUIRED" ]]; then
                printf 'DEV_MOCK requires CIS_READINESS_SOURCE=MOCK_BUILD_NOT_REQUIRED.\n' >&2
                exit 2
            fi
            ETB_TARGET_PACKAGE="com.bangkokbank.blue.dev"
            ETB_COMPETING_PACKAGE="com.bangkokbank.blue.sit"
            ETB_TARGET_ACTIVITY="com.bangkokbank.blue.MainActivity"
            ;;
        SIT|sit)
            export CIS_MODE="EXTERNAL_PREPARED"
            ETB_TARGET_PACKAGE="com.bangkokbank.blue.sit"
            ETB_COMPETING_PACKAGE="com.bangkokbank.blue.dev"
            ETB_TARGET_ACTIVITY="com.bangkokbank.blue.MainActivity"
            ETB_SIT_APK="$ROOT/apps/android/app-sit-mmplot2.apk"
            ;;
        *)
            printf 'Unsupported ETB environment: %s (expected DEV or SIT).\n' "$ETB_ENVIRONMENT" >&2
            exit 2
            ;;
    esac
}

finalize_etb_runtime_configuration() {
    if [[ -z "${ETB_RUN_ID:-}" ]]; then
        ETB_RUN_ID="$("$PYTHON_BIN" "$ROOT/tools/runner/etb_runtime.py" run-id)"
    fi
    export ETB_RUN_ID

    if [[ ! -r "${ETB_CASE_PROFILES:-$ROOT/testdata/onboarding/etb_cases.local.yaml}" ]]; then
        printf 'ETB runtime data is local-only and is not committed.\n' >&2
        printf 'Provide ETB_CASE_PROFILES pointing to an approved local YAML profile file.\n' >&2
        exit 3
    fi

    case "$ETB_ENVIRONMENT" in
        dev) ETB_ENVIRONMENT="DEV" ;;
        sit) ETB_ENVIRONMENT="SIT" ;;
    esac
    DEVICE_UDID="${DEVICE_UDID:-}"
    export ETB_ENVIRONMENT ETB_PRODUCT_RELEASE ANDROID_EXECUTION_TARGET DEVICE_UDID
    export APP_PACKAGE="$ETB_TARGET_PACKAGE" APP_ACTIVITY="$ETB_TARGET_ACTIVITY"
    robot_variable_args+=(--variable "ETB_ENVIRONMENT:${ETB_ENVIRONMENT}")
    robot_variable_args+=(--variable "ETB_PRODUCT_RELEASE:${ETB_PRODUCT_RELEASE}")
    robot_variable_args+=(--variable "ANDROID_EXECUTION_TARGET:${ANDROID_EXECUTION_TARGET}")
    robot_variable_args+=(--variable "DEVICE_UDID:${DEVICE_UDID}")
    robot_variable_args+=(--variable "APP_PACKAGE:${APP_PACKAGE}")
    robot_variable_args+=(--variable "APP_ACTIVITY:${APP_ACTIVITY}")
    initialize_etb_run_output
}


initialize_etb_run_output() {
    ETB_OUTPUT_BASE="${ETB_OUTPUT_BASE:-$ETB_OUTPUT}"
    ETB_OUTPUT="$ETB_OUTPUT_BASE/$ETB_RUN_ID"
    mkdir -p "$ETB_OUTPUT"

    local branch="UNPROVEN"
    local head="UNPROVEN"
    local staged_count="UNPROVEN"
    local modified_count="UNPROVEN"
    local untracked_count="UNPROVEN"
    local staged_fingerprint="UNPROVEN"
    local worktree_fingerprint="UNPROVEN"
    local guard_path="$ROOT/tools/etb_delivery_guard.py"
    if [[ -f "$guard_path" ]]; then
        local guard_output
        guard_output="$("$PYTHON_BIN" "$guard_path" 2>/dev/null || true)"
        local key value
        while IFS='=' read -r key value; do
            case "$key" in
                BRANCH) branch="$value" ;;
                HEAD) head="$value" ;;
                STAGED_COUNT) staged_count="$value" ;;
                MODIFIED_COUNT) modified_count="$value" ;;
                UNTRACKED_COUNT) untracked_count="$value" ;;
                STAGED_FINGERPRINT) staged_fingerprint="$value" ;;
                WORKTREE_FINGERPRINT) worktree_fingerprint="$value" ;;
            esac
        done <<< "$guard_output"
    fi

    "$PYTHON_BIN" "$ROOT/tools/runner/etb_runtime.py" init-run         "$ETB_OUTPUT"         "$ETB_OUTPUT_BASE"         "$ETB_RUN_ID"         "$ETB_ENVIRONMENT"         "$ANDROID_EXECUTION_TARGET"         "$selector_type"         "$selector_value"         "$branch"         "$head"         "$staged_count"         "$modified_count"         "$untracked_count"         "$staged_fingerprint"         "$worktree_fingerprint"         "${ETB_BUILD_IDENTITY:-UNPROVEN}"         "${ETB_PRODUCT_RELEASE:-UNPROVEN}"         "${DEVICE_UDID:-UNPROVEN}"         "${selected_case_ids[@]}"
    export ETB_OUTPUT ETB_OUTPUT_BASE
}
