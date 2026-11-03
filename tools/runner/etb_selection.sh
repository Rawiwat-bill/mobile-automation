# ETB testcase/tag selection and syntax-only preflight.
# Sourced by etb_runner.sh; functions intentionally use Bash dynamic scope.

parse_etb_selection() {
    local arg
    while (($#)); do
        arg="$1"
        case "$arg" in
            --dry-run)
                dry_run=true
                ;;
            --smoke)
                if [[ "$selector_type" != "all" ]]; then
                    printf 'ETB selection options are mutually exclusive.\n' >&2
                    exit 2
                fi
                selector_type="tag"
                selector_value="smoke"
                ;;
            --tag)
                if [[ "$selector_type" != "all" || $# -lt 2 || -z "$2" || "$2" == -* ]]; then
                    printf 'Expected exactly one tag after --tag; selection options are mutually exclusive.\n' >&2
                    exit 2
                fi
                selector_type="tag"
                selector_value="$2"
                shift
                ;;
            TC-ETB-[0-9][0-9][0-9]|TC-ETB-[0-9][0-9][0-9]\ *)
                if [[ "$selector_type" != "all" ]]; then
                    printf 'ETB selection options are mutually exclusive.\n' >&2
                    exit 2
                fi
                selector_type="test"
                selector_value="$arg"
                canonical_case_id="${arg%% *}"
                ;;
            TC-ETB-*|*)
                printf 'Invalid ETB testcase or option: %s\n' "$arg" >&2
                usage >&2
                exit 2
                ;;
        esac
        shift
    done
}

resolve_etb_selection() {
    case "$selector_type" in
        test)
            local resolution
            local resolved_test_name
            resolution="$("$PYTHON_BIN" "$ROOT/tools/runner/etb_runtime.py" resolve-selector "$ETB_SUITE" "$selector_value")"
            case "$resolution" in
                MATCH$'\t'*)
                    resolved_test_name="${resolution#*$'\t'}"
                    selection_args+=(--test "$resolved_test_name")
                    ;;
                AMBIGUOUS$'\t'*)
                    printf 'ETB testcase selector ambiguous: %s\n' "$selector_value" >&2
                    exit 2
                    ;;
                *)
                    printf 'ETB testcase not found in canonical suite: %s\n' "$selector_value" >&2
                    exit 2
                    ;;
            esac
            if [[ "$canonical_case_id" == "TC-ETB-004" ]]; then
                robot_variable_args+=(--variable "ETB_ISOLATED_VALIDATION:TC-ETB-004")
            fi
            ;;
        tag)
            selection_args+=(--include "$selector_value")
            ;;
    esac
}

resolve_etb_profile_path() {
    local resolved_case_profiles
    resolved_case_profiles="$("$PYTHON_BIN" "$ROOT/tools/runner/etb_runtime.py" absolute-path "${ETB_CASE_PROFILES:-$ROOT/testdata/onboarding/etb_cases.local.yaml}")"
    export ETB_CASE_PROFILES="$resolved_case_profiles"
    robot_variable_args+=(--variable "ETB_CASE_PROFILES:${resolved_case_profiles}")

    local dob_strategy="${ETB_DOB_STRATEGY:-STABLE_V1}"
    case "$dob_strategy" in
        LEGACY|STABLE_V1)
            export ETB_DOB_STRATEGY="$dob_strategy"
            robot_variable_args+=(--variable "ETB_DOB_STRATEGY:${dob_strategy}")
            ;;
        *)
            printf 'Unsupported ETB_DOB_STRATEGY: %s\n' "$dob_strategy" >&2
            exit 2
            ;;
    esac
}

validate_etb_selection() {
    local preflight_dir
    preflight_dir="$(mktemp -d "${TMPDIR:-/tmp}/etb-run-preflight.XXXXXX")"

    if ((${#selection_args[@]})); then
        if ! "$PYTHON_BIN" -m robot --dryrun --console none --outputdir "$preflight_dir" "${robot_variable_args[@]}" "${selection_args[@]}" "$ETB_SUITE" >/dev/null 2>&1; then
            rm -rf "$preflight_dir"
            if [[ "$selector_type" == "test" ]]; then
                printf 'ETB testcase selector resolution failed: %s\n' "$selector_value" >&2
            else
                printf 'ETB tag selected no testcases in canonical suite: %s\n' "$selector_value" >&2
            fi
            exit 2
        fi
    else
        if ! "$PYTHON_BIN" -m robot --dryrun --console none --outputdir "$preflight_dir" "${robot_variable_args[@]}" "$ETB_SUITE" >/dev/null 2>&1; then
            rm -rf "$preflight_dir"
            printf 'Canonical ETB suite dry-run failed: %s\n' "$ETB_SUITE" >&2
            exit 2
        fi
    fi

    selected_count="$("$PYTHON_BIN" "$ROOT/tools/runner/etb_runtime.py" selected-count "$preflight_dir/output.xml")"
    if [[ "$selector_type" == "test" && "$selected_count" != "1" ]]; then
        rm -rf "$preflight_dir"
        printf 'ETB testcase selector resolved %s tests: %s\n' "$selected_count" "$selector_value" >&2
        exit 2
    fi
    if [[ "$selector_type" == "tag" && "$selected_count" == "0" ]]; then
        rm -rf "$preflight_dir"
        printf 'ETB tag selected no testcases in canonical suite: %s\n' "$selector_value" >&2
        exit 2
    fi

    selected_case_ids=()
    local selected_case_id
    while IFS= read -r selected_case_id; do
        [[ -n "$selected_case_id" ]] && selected_case_ids+=("$selected_case_id")
    done < <("$PYTHON_BIN" "$ROOT/tools/runner/etb_runtime.py" selected-case-ids "$preflight_dir/output.xml")
    rm -rf "$preflight_dir"

    if [[ "${#selected_case_ids[@]}" -ne "$selected_count" ]]; then
        printf 'ETB selector produced %s testcases but %s canonical case IDs.\n' "$selected_count" "${#selected_case_ids[@]}" >&2
        exit 2
    fi

    if [[ "$selector_type" == "all" ]]; then
        if ! "$PYTHON_BIN" "$ROOT/tools/runner/etb_runtime.py" validate-case-set             "$ROOT/configs/etb_case_set.json"             "${selected_case_ids[@]}"; then
            printf 'Canonical ETB case-set validation failed.\n' >&2
            exit 2
        fi
    fi

}
