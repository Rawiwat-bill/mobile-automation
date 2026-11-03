# Android environment preparation functions for ./run.
# Sourced by the root runner; all variables are supplied by the runner runtime.

adb_target() {
    if [[ -z "${DEVICE_UDID:-}" ]]; then
        printf 'TARGET_GUARD_SERIAL_REQUIRED; no ADB command sent.\n' >&2
        return 3
    fi
    local adb_executable
    if ! adb_executable="$("$PYTHON_BIN" "$ROOT/tools/runner/etb_runtime.py" adb-executable 2>/dev/null)"; then
        printf 'ETB preflight failed: canonical ADB executable is unavailable.\n' >&2
        return 3
    fi
    "$adb_executable" -s "$DEVICE_UDID" "$@"
}

package_installed() {
    adb_target shell pm path "$1" 2>/dev/null | grep -q '^package:'
}

prepare_sit_environment() {
    printf 'ETB preflight: ETB_ENVIRONMENT=SIT TARGET_PACKAGE=%s COMPETING_PACKAGE=%s APP_ACTIVITY=%s\n' \
        "$ETB_TARGET_PACKAGE" "$ETB_COMPETING_PACKAGE" "$ETB_TARGET_ACTIVITY"
    if ! adb_target get-state 2>/dev/null | grep -qx 'device'; then
        printf 'ETB preflight failed: no healthy Android device.\n' >&2
        exit 3
    fi
    if package_installed "$ETB_COMPETING_PACKAGE"; then
        printf 'ETB preflight: COMPETING_INSTALLED=YES; removing explicit DEV package\n'
        adb_target uninstall "$ETB_COMPETING_PACKAGE" >/dev/null
    fi
    if package_installed "$ETB_COMPETING_PACKAGE"; then
        printf 'ENVIRONMENT_ISOLATION_FAILED: competing package remains installed.\n' >&2
        exit 3
    fi
    if package_installed "$ETB_TARGET_PACKAGE"; then
        printf 'ETB preflight: TARGET_INSTALLED=YES (preserving installed SIT package)\n'
    else
        if [[ ! -r "$ETB_SIT_APK" ]]; then
            printf 'ETB preflight failed: canonical SIT APK is missing.\n' >&2
            exit 3
        fi
        printf 'ETB preflight: TARGET_INSTALLED=NO; installing canonical SIT APK\n'
        adb_target install "$ETB_SIT_APK" >/dev/null
    fi
    if ! package_installed "$ETB_TARGET_PACKAGE"; then
        printf 'ETB preflight failed: SIT package is not installed.\n' >&2
        exit 3
    fi
    printf 'ETB preflight: TARGET_INSTALLED=YES\n'
    local resolved_activity
    resolved_activity="$(adb_target shell cmd package resolve-activity --brief -a android.intent.action.MAIN -c android.intent.category.LAUNCHER "$ETB_TARGET_PACKAGE" 2>/dev/null | tail -n 1 | tr -d '\r')"
    if [[ "$resolved_activity" != "$ETB_TARGET_PACKAGE/$ETB_TARGET_ACTIVITY" ]]; then
        printf 'ETB preflight failed: SIT activity is not resolvable as expected.\n' >&2
        exit 3
    fi
    printf 'ETB preflight: COMPETING_INSTALLED=NO ACTIVITY_RESOLVED_FROM_INSTALLED_TARGET=YES\n'
}

prepare_dev_environment() {
    printf 'ETB preflight: ETB_ENVIRONMENT=DEV TARGET_PACKAGE=%s COMPETING_PACKAGE=%s APP_ACTIVITY=%s\n' \
        "$ETB_TARGET_PACKAGE" "$ETB_COMPETING_PACKAGE" "$ETB_TARGET_ACTIVITY"
    if ! adb_target get-state 2>/dev/null | grep -qx 'device'; then
        printf 'ETB preflight failed: no healthy Android device.\n' >&2
        exit 3
    fi
    if package_installed "$ETB_COMPETING_PACKAGE"; then
        printf 'ETB preflight: COMPETING_INSTALLED=YES; removing explicit SIT package\n'
        adb_target uninstall "$ETB_COMPETING_PACKAGE" >/dev/null
    fi
    if package_installed "$ETB_COMPETING_PACKAGE"; then
        printf 'ENVIRONMENT_ISOLATION_FAILED: competing package remains installed.\n' >&2
        exit 3
    fi
    if package_installed "$ETB_TARGET_PACKAGE"; then
        printf 'ETB preflight: TARGET_INSTALLED=YES (preserving installed DEV package)\n'
    else
        if [[ ! -r "$ETB_DEV_APK" ]]; then
            printf 'ETB preflight failed: DEV APK is missing.\n' >&2
            exit 3
        fi
        printf 'ETB preflight: TARGET_INSTALLED=NO; installing available DEV APK\n'
        adb_target install "$ETB_DEV_APK" >/dev/null
    fi
    if ! package_installed "$ETB_TARGET_PACKAGE"; then
        printf 'ETB preflight failed: DEV package is not installed.\n' >&2
        exit 3
    fi
    local resolved_activity
    resolved_activity="$(adb_target shell cmd package resolve-activity --brief -a android.intent.action.MAIN -c android.intent.category.LAUNCHER "$ETB_TARGET_PACKAGE" 2>/dev/null | tail -n 1 | tr -d '\r')"
    if [[ "$resolved_activity" != "$ETB_TARGET_PACKAGE/$ETB_TARGET_ACTIVITY" ]]; then
        printf 'ETB preflight failed: DEV activity is not resolvable as expected.\n' >&2
        exit 3
    fi
    printf 'ETB preflight: COMPETING_INSTALLED=NO ACTIVITY_RESOLVED_FROM_INSTALLED_TARGET=YES\n'
}

prepare_dev_mock_environment() {
    printf 'ETB preflight: ETB_ENVIRONMENT=DEV_MOCK TARGET_PACKAGE=%s APP_ACTIVITY=%s\n' \
        "$ETB_TARGET_PACKAGE" "$ETB_TARGET_ACTIVITY"
    if ! adb_target get-state 2>/dev/null | grep -qx 'device'; then
        printf 'ETB preflight failed: no healthy Android device.\n' >&2
        exit 3
    fi
    if package_installed "$ETB_COMPETING_PACKAGE"; then
        printf 'MOCK_CIS_INVALID_CONTEXT: competing SIT package is installed.\n' >&2
        exit 3
    fi
    if ! package_installed "$ETB_TARGET_PACKAGE"; then
        printf 'MOCK_CIS_INVALID_CONTEXT: approved mock package is not installed.\n' >&2
        exit 3
    fi
    printf 'ETB preflight: installed approved mock target preserved; no APK install permitted\n'
}
