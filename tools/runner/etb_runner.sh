# ETB runner orchestration for ./run.
# Sourced by the root launcher after shared runtime variables and usage() are defined.
# Device/package preparation functions come from android_environment.sh.

# shellcheck source=tools/runner/etb_configuration.sh
source "$ROOT/tools/runner/etb_configuration.sh"
# shellcheck source=tools/runner/etb_selection.sh
source "$ROOT/tools/runner/etb_selection.sh"
# shellcheck source=tools/runner/etb_preflight.sh
source "$ROOT/tools/runner/etb_preflight.sh"
# shellcheck source=tools/runner/etb_execution.sh
source "$ROOT/tools/runner/etb_execution.sh"

run_etb() {
    local selector_type="all"
    local selector_value=""
    local canonical_case_id=""
    local dry_run=false
    local selected_count=""

    local -a robot_variable_args=()
    local -a selection_args=()
    local -a selected_case_ids=()
    local -a cis_selection_args=()

    shift

    # Syntax-only intent must be known before target validation.
    detect_etb_dry_run "$@"
    load_etb_runtime_configuration

    parse_etb_selection "$@"
    resolve_etb_selection
    resolve_etb_profile_path
    validate_etb_selection

    if [[ "$dry_run" == true ]]; then
        printf 'ETB dry-run selection: %s testcase(s)\n' "$selected_count"
        return 0
    fi

    finalize_etb_runtime_configuration
    run_etb_disk_preflight
    run_etb_target_preflight
    run_etb_network_preflight
    run_etb_appium_preflight
    run_etb_cis_preflight
    prepare_etb_android_environment
    execute_etb_robot
}
