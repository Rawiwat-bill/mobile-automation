"""Pure CIS profile-dependency and external-readiness policy helpers."""

from __future__ import annotations

from typing import Any

SIT_MODE = "EXTERNAL_PREPARED"
STATEFUL_CASE_NUMBERS = frozenset({1, 2, 3, 4})
READINESS_VERIFIED = "VERIFIED"
READINESS_EXTERNALLY_CONFIRMED = "EXTERNALLY_CONFIRMED"
READINESS_NOT_READY = "NOT_READY"
READINESS_UNKNOWN = "UNKNOWN"


def readiness_status(source: str | None, ready: str | None) -> str:
    """Normalize external readiness metadata without reading process state."""
    if source == "EXTERNAL_TEAM_CONFIRMATION":
        if ready == "EXTERNALLY_CONFIRMED":
            return READINESS_EXTERNALLY_CONFIRMED
        return READINESS_NOT_READY
    return READINESS_UNKNOWN


def case_number(tc_id: str) -> int | None:
    try:
        return int(tc_id.rsplit("-", 1)[1])
    except (IndexError, ValueError):
        return None


def dependency_class(tc_id: str, case: dict[str, Any]) -> tuple[str, str]:
    """Classify CIS dependency from testcase contract, not profile reuse."""
    if case_number(tc_id) in STATEFUL_CASE_NUMBERS:
        return "STATEFUL_PROFILE_REQUIRED", "YES"
    terminal_state = str(case.get("terminal_state", "")).lower()
    if terminal_state in {"popup closed", "app closed"}:
        return "NEGATIVE_FLOW_REUSABLE_PROFILE", "NO"
    return "NEGATIVE_FLOW_REUSABLE_PROFILE", "UNKNOWN"


def build_profile_audit(
    cases: dict[str, Any],
    contract_cases: dict[str, Any],
    selected_case_id: str | None = None,
) -> tuple[dict[str, Any], dict[str, Any], dict[str, Any]]:
    """Build sanitized profile dependency/audit records with no file I/O."""
    ordered = sorted(
        ((str(case.get("tc_id", "")), key, case) for key, case in cases.items()),
        key=lambda item: item[0],
    )
    if selected_case_id is not None:
        ordered = [item for item in ordered if item[0] == selected_case_id]
        if not ordered:
            raise ValueError(
                f"Selected ETB testcase is not present in CIS case data: {selected_case_id}"
            )

    groups: dict[str, str] = {}
    aliases: dict[str, list[str]] = {}
    case_metadata: dict[str, dict[str, str]] = {}

    for tc_id, case_key, case in ordered:
        identity = case.get("profile", {}).get("citizen_id")
        if not isinstance(identity, str) or not identity:
            raise ValueError(f"Missing local CIS identity for {tc_id or 'case'}")
        group = groups.setdefault(identity, f"PROFILE_GROUP_{len(groups) + 1:02d}")
        aliases.setdefault(group, []).append(tc_id)
        policy_case = contract_cases.get(case_key, case)
        dep_class, persistent_mutation = dependency_class(tc_id, policy_case)
        case_metadata[tc_id] = {
            "cis_dependency": dep_class,
            "persistent_mutation": persistent_mutation,
        }

    matrix = {
        tc_id: groups[case["profile"]["citizen_id"]]
        for tc_id, _, case in ordered
    }
    shared = {
        group: testcases
        for group, testcases in aliases.items()
        if len(testcases) > 1
    }
    stateful_groups = sorted(
        {
            matrix[tc_id]
            for tc_id, metadata in case_metadata.items()
            if metadata["cis_dependency"] == "STATEFUL_PROFILE_REQUIRED"
        }
    )
    negative_groups = sorted(
        {
            matrix[tc_id]
            for tc_id, metadata in case_metadata.items()
            if metadata["cis_dependency"] == "NEGATIVE_FLOW_REUSABLE_PROFILE"
        }
    )
    shared_profile_safe = {
        group: (
            "YES"
            if all(
                case_metadata[tc_id]["persistent_mutation"] == "NO"
                for tc_id in testcases
            )
            else "NO"
        )
        for group, testcases in shared.items()
    }
    one_pass_compatible = all(
        value == "YES" for value in shared_profile_safe.values()
    )

    result = {
        "total_cases": len(matrix),
        "unique_profile_groups": len(aliases),
        "shared_profile_groups": len(shared),
        "testcase_to_profile_group": matrix,
        "shared_groups": shared,
        "case_dependencies": {
            tc_id: {"profile_group": matrix[tc_id], **metadata}
            for tc_id, metadata in case_metadata.items()
        },
        "shared_profile_safe_for_reuse": shared_profile_safe,
        "stateful_profile_groups": stateful_groups,
        "negative_reusable_profile_groups": negative_groups,
        "one_pass_external_preparation_compatible": (
            "YES" if one_pass_compatible else "NO"
        ),
        "external_preparation_required": "YES",
        "external_cis_profile_count": len(stateful_groups),
        "tc002_readiness": {
            "cis_preparation": "EXTERNAL_TEAM_REQUIRED",
            "pdpa_preparation": "APPROVED_SHARED_ADAPTER_READY",
            "tc002_runtime": "READY_AFTER_EXTERNAL_CIS_CONFIRMATION",
        },
        "pdpa_preparation_policy": {
            "owner": "AUTOMATION",
            "environment_scope": "DEV_AND_SIT",
            "adapter_status": "APPROVED_SHARED_ADAPTER_READY",
        },
    }

    preparation = {
        "external_cis_preparation_required": "YES",
        "profiles": [
            {
                "testcase_id": tc_id,
                "profile_group": group,
                "required_action": (
                    "CLEAR_CIS"
                    if case_metadata[tc_id]["cis_dependency"]
                    == "STATEFUL_PROFILE_REQUIRED"
                    else "REUSE_NEGATIVE_FLOW_PROFILE"
                ),
                "cis_dependency": case_metadata[tc_id]["cis_dependency"],
                "persistent_mutation": case_metadata[tc_id]["persistent_mutation"],
            }
            for tc_id, group in matrix.items()
        ],
        "shared_profile_warning": shared,
        "shared_profile_safe_for_reuse": shared_profile_safe,
        "cleanup_owner": "EXTERNAL_TEAM",
    }

    post_manifest = {
        "post_run_external_cis_cleanup_required": "YES",
        "profiles": [
            {"testcase_id": tc_id, "profile_group": group}
            for tc_id, group in matrix.items()
            if case_metadata[tc_id]["cis_dependency"]
            == "STATEFUL_PROFILE_REQUIRED"
        ],
        "cleanup_owner": "EXTERNAL_TEAM",
    }

    return result, preparation, post_manifest


def build_external_readiness(
    matrix: dict[str, Any],
    status: str,
    selected_case_id: str | None,
) -> dict[str, Any]:
    """Build the external readiness gate decision with no environment or file I/O."""
    required_groups = matrix["stateful_profile_groups"]
    runtime_allowed = status in {
        READINESS_VERIFIED,
        READINESS_EXTERNALLY_CONFIRMED,
    }
    return {
        "cis_mode": SIT_MODE,
        "cis_readiness_status": status,
        "read_only_cis_verification_capability": (
            "EXTERNAL_TEAM_CONFIRMATION"
            if status == READINESS_EXTERNALLY_CONFIRMED
            else "NOT_CONFIGURED"
        ),
        "gate_decision": (
            "EXTERNAL_TEAM_CONFIRMATION_ACCEPTED"
            if runtime_allowed
            else "SIT_CIS_EXTERNAL_CONFIRMATION_REQUIRED"
        ),
        "selected_testcase": selected_case_id or "ALL_ETB_CASES",
        "profiles": [
            {"profile_group": group, "cis_ready": status}
            for group in required_groups
        ],
        "negative_reusable_profile_groups": matrix[
            "negative_reusable_profile_groups"
        ],
        "all_required_cis_ready": (
            "YES" if runtime_allowed else ("NO" if required_groups else "YES")
        ),
        "full_runtime_gate": "OPEN" if runtime_allowed else "CLOSED",
    }
