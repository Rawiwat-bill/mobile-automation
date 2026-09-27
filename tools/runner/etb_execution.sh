# ETB Robot execution boundary.
# Sourced by etb_runner.sh; functions intentionally use Bash dynamic scope.

execute_etb_robot() {
    local -a robot_cmd=("$PYTHON_BIN" -m robot --outputdir "$ETB_OUTPUT")
    if ((${#robot_variable_args[@]})); then
        robot_cmd+=("${robot_variable_args[@]}")
    fi
    if ((${#selection_args[@]})); then
        robot_cmd+=("${selection_args[@]}")
    fi
    robot_cmd+=("$ETB_SUITE")

    local robot_exit=0
    if "${robot_cmd[@]}"; then
        robot_exit=0
    else
        robot_exit=$?
    fi

    local result_exit=0
    if "$PYTHON_BIN" "$ROOT/tools/runner/etb_runtime.py" finalize-run "$ETB_OUTPUT" "$ETB_RUN_ID"; then
        result_exit=0
    else
        result_exit=$?
        printf 'ETB_RUN_RESULT=FAIL result summarizer exited %s for %s\n' "$result_exit" "$ETB_RUN_ID" >&2
    fi

    if ((robot_exit != 0)); then
        return "$robot_exit"
    fi
    if ((result_exit != 0)); then
        return 4
    fi
    return 0
}
