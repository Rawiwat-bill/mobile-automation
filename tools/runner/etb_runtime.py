"""Bounded helper CLI for the Bash ETB runner.

This module contains pure parsing/formatting helpers and explicit preflight
bridges previously embedded as inline Python heredocs in ./run.  Shell remains
responsible for orchestration and ordering; this module does not install APKs,
start Robot, or mutate test profiles.
"""

from __future__ import annotations

from datetime import datetime, timezone
import hashlib
import json
import os
from pathlib import Path
import re
import shutil
import sys
import xml.etree.ElementTree as ET

_PROJECT_ROOT = Path(__file__).resolve().parents[2]
if str(_PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(_PROJECT_ROOT))


def _suite_names(suite_path: str) -> list[str]:
    names: list[str] = []
    in_test_cases = False
    with open(suite_path, encoding="utf-8") as suite:
        for line in suite:
            stripped = line.strip()
            if stripped == "*** Test Cases ***":
                in_test_cases = True
                continue
            if in_test_cases and stripped.startswith("*** "):
                break
            if in_test_cases and line and not line[0].isspace() and stripped:
                names.append(stripped)
    return names


def resolve_selector(suite_path: str, requested: str) -> int:
    names = _suite_names(suite_path)
    matches = [name for name in names if name == requested or name.startswith(requested + " ")]
    if len(matches) == 1:
        print("MATCH\t" + matches[0])
    elif not matches:
        print("NOT_FOUND")
    else:
        print("AMBIGUOUS\t" + "\t".join(matches))
    return 0


def absolute_path(path: str) -> int:
    print(os.path.abspath(path))
    return 0


def selected_count(output_xml: str) -> int:
    root = ET.parse(output_xml).getroot()
    print(sum(1 for _ in root.iter("test")))
    return 0


def selected_case_ids(output_xml: str) -> int:
    root = ET.parse(output_xml).getroot()
    for test in root.iter("test"):
        match = re.match(r"^(TC-ETB-\d{3})(?:\s|$)", test.get("name", ""))
        if match:
            print(match.group(1))
    return 0


def generate_run_id() -> int:
    print(datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%S%fZ") + f"-p{os.getppid()}")
    return 0



def disk_guard(path: str, warn_gb: str, fail_gb: str) -> int:
    try:
        warn = float(warn_gb)
        fail = float(fail_gb)
    except ValueError:
        print("ETB_DISK_GUARD_INVALID_THRESHOLD", file=sys.stderr)
        return 2
    if warn < 0 or fail < 0 or warn < fail:
        print("ETB_DISK_GUARD_INVALID_THRESHOLD", file=sys.stderr)
        return 2

    try:
        free = shutil.disk_usage(path).free / (1024 ** 3)
    except OSError:
        print("ETB_DISK_GUARD_UNAVAILABLE", file=sys.stderr)
        return 3

    if free < fail:
        print(
            f"ETB_DISK_GUARD=FAIL free_gb={free:.2f} warn_gb={warn:.2f} fail_gb={fail:.2f}",
            file=sys.stderr,
        )
        return 3
    state = "WARN" if free < warn else "PASS"
    print(
        f"ETB_DISK_GUARD={state} free_gb={free:.2f} warn_gb={warn:.2f} fail_gb={fail:.2f}"
    )
    return 0


def resolved_adb_executable() -> int:
    from libraries.android_adb import resolve_adb_executable

    try:
        executable = resolve_adb_executable()
    except FileNotFoundError:
        print("ADB_EXECUTABLE_NOT_FOUND", file=sys.stderr)
        return 3
    print(executable)
    return 0


def target_guard(
    serial: str,
    execution_target: str,
    environment: str,
    package: str,
    activity: str,
    competing_package: str,
    product_release: str = "POST_MMP_1",
) -> int:
    from tools.real_device_preflight import validate_target_identity

    try:
        result = validate_target_identity(
            serial,
            execution_target,
            environment,
            package,
            activity,
            competing_package,
            product_release,
        )
    except ValueError as error:
        print(str(error), file=sys.stderr)
        return 3
    print(json.dumps(result, sort_keys=True))
    return 0


def target_build_identity(target_result_json: str) -> int:
    try:
        payload = json.loads(target_result_json)
    except json.JSONDecodeError:
        print("ETB_TARGET_BUILD_IDENTITY_INVALID_JSON", file=sys.stderr)
        return 3
    if not isinstance(payload, dict):
        print("ETB_TARGET_BUILD_IDENTITY_INVALID_PAYLOAD", file=sys.stderr)
        return 3
    if payload.get("target_identity") != "PASS" or payload.get("build_identified") is not True:
        print("ETB_TARGET_BUILD_IDENTITY_UNPROVEN", file=sys.stderr)
        return 3
    identity = _safe_manifest_value(str(payload.get("build_identity") or ""))
    if identity == "UNPROVEN":
        print("ETB_TARGET_BUILD_IDENTITY_UNSAFE", file=sys.stderr)
        return 3
    print(identity)
    return 0


def record_run_build_identity(manifest_path: str, build_identity: str) -> int:
    path = Path(manifest_path)
    try:
        payload = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError):
        print("ETB_RUN_MANIFEST_BUILD_IDENTITY_UNREADABLE", file=sys.stderr)
        return 3
    if not isinstance(payload, dict) or payload.get("schema") != "bbl-etb-run-manifest/v1":
        print("ETB_RUN_MANIFEST_BUILD_IDENTITY_INVALID_SCHEMA", file=sys.stderr)
        return 3
    runtime = payload.get("runtime")
    if not isinstance(runtime, dict):
        print("ETB_RUN_MANIFEST_BUILD_IDENTITY_RUNTIME_MISSING", file=sys.stderr)
        return 3
    identity = _safe_manifest_value(build_identity)
    if identity == "UNPROVEN":
        print("ETB_RUN_MANIFEST_BUILD_IDENTITY_UNSAFE", file=sys.stderr)
        return 3
    runtime["build_identity"] = identity
    _write_json_atomic(path, payload)
    print(f"ETB_RUN_BUILD_IDENTITY={identity}")
    return 0


def sit_cis_readiness(profile_path: str, report_dir: str, selected_ids: list[str]) -> int:
    from libraries.cis_preparation import verify_external_cis_readiness

    if selected_ids:
        results = [
            verify_external_cis_readiness(
                profile_path,
                str(Path(report_dir) / case_id),
                case_id,
            )
            for case_id in selected_ids
        ]
        statuses = {item["cis_readiness_status"] for item in results}
        capabilities = {item["read_only_cis_verification_capability"] for item in results}
        gates = {item["full_runtime_gate"] for item in results}
        all_ready = all(item["all_required_cis_ready"] == "YES" for item in results)
        result = {
            "cis_mode": "EXTERNAL_PREPARED",
            "read_only_cis_verification_capability": capabilities.pop() if len(capabilities) == 1 else "MIXED",
            "cis_readiness_status": statuses.pop() if len(statuses) == 1 else "MIXED",
            "gate_decision": "EXTERNAL_TEAM_CONFIRMATION_ACCEPTED"
            if gates == {"OPEN"} and all_ready
            else "SIT_CIS_EXTERNAL_CONFIRMATION_REQUIRED",
            "selected_testcase": selected_ids[0] if len(selected_ids) == 1 else "SELECTED_ETB_CASES",
            "selected_testcases": selected_ids,
            "all_required_cis_ready": "YES" if all_ready else "NO",
            "full_runtime_gate": "OPEN" if gates == {"OPEN"} and all_ready else "CLOSED",
        }
    else:
        result = verify_external_cis_readiness(profile_path, report_dir, None)

    print(
        json.dumps(
            {
                "cis_mode": result["cis_mode"],
                "read_only_cis_verification_capability": result["read_only_cis_verification_capability"],
                "cis_readiness_status": result["cis_readiness_status"],
                "gate_decision": result["gate_decision"],
                "selected_testcase": result["selected_testcase"],
                "selected_testcases": result.get("selected_testcases", []),
                "all_required_cis_ready": result["all_required_cis_ready"],
                "full_runtime_gate": result["full_runtime_gate"],
            },
            sort_keys=True,
        )
    )
    return 0


def cis_preflight(environment: str) -> int:
    from libraries.cis_preparation import probe_cis_transport, validate_mock_build_context

    if environment.upper() == "DEV_MOCK":
        validate_mock_build_context()
        result = {
            "cis_clear": "NOT_APPLICABLE",
            "cis_state_ready": "NOT_REQUIRED",
            "operation_count": 0,
        }
    else:
        result = {**probe_cis_transport(), "operation_count": 0}
    print(json.dumps(result, sort_keys=True))
    return 0



_SAFE_MANIFEST_VALUE = re.compile(r"^[A-Za-z0-9_./:+\-]{1,200}$")
_ENV_BLOCKER = re.compile(
    r"(?:BLOCKED_BY_ENVIRONMENT_[A-Z0-9_:-]*?(?:AJI-\d+|GOD-\d+)|\bAJI-\d+\b|\bGOD-\d+\b)"
)
_CASE_NAME = re.compile(r"^(TC-ETB-\d{3})(?:\s|$)")


def _utc_now() -> str:
    return datetime.now(timezone.utc).isoformat()


def _safe_manifest_value(value: str) -> str:
    candidate = str(value or "").strip()
    return candidate if _SAFE_MANIFEST_VALUE.fullmatch(candidate) else "UNPROVEN"


def _safe_int(value: str) -> int | None:
    try:
        parsed = int(value)
    except (TypeError, ValueError):
        return None
    return parsed if parsed >= 0 else None


def _relative_repo_path(path: Path) -> str:
    try:
        return str(path.resolve().relative_to(_PROJECT_ROOT.resolve()))
    except ValueError:
        return "EXTERNAL_PATH"


def _write_json_atomic(path: Path, payload: dict[str, object]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    pending = path.with_suffix(path.suffix + ".pending")
    pending.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    pending.replace(path)


def _traceability_binding() -> dict[str, object]:
    path = _PROJECT_ROOT / "configs" / "etb_traceability_full.json"
    if not path.is_file():
        return {
            "traceability_path": "configs/etb_traceability_full.json",
            "traceability_sha256": None,
            "wiki_snapshot_status": "UNAVAILABLE",
            "immutable_wiki_snapshot_hash": None,
        }
    raw = path.read_bytes()
    try:
        payload = json.loads(raw.decode("utf-8"))
    except (UnicodeDecodeError, json.JSONDecodeError):
        payload = {}
    binding = payload.get("wiki_binding") if isinstance(payload, dict) else {}
    if not isinstance(binding, dict):
        binding = {}
    return {
        "traceability_path": "configs/etb_traceability_full.json",
        "traceability_sha256": hashlib.sha256(raw).hexdigest(),
        "wiki_snapshot_status": str(binding.get("snapshot_status") or "UNPROVEN"),
        "immutable_wiki_snapshot_hash": binding.get("immutable_snapshot_hash"),
    }


_BINDING_PATHS = (
    "tools/runner/etb_selection.sh", "tools/runner/etb_preflight.sh",
    "tools/runner/etb_runtime.py", "tools/appium_server.py",
    "tools/etb_network_preflight.py", "tools/etb_proxy_server.py",
    "resources/keywords/common_onboarding.resource",
    "resources/keywords/etb/etb_keywords.resource",
    "resources/keywords/etb/etb_regression_keywords.resource",
    "resources/pages/onboarding/profile_fields.resource",
    "resources/pages/onboarding/profile_dob.resource",
    "resources/pages/onboarding/profile_transition.resource",
    "libraries/etb_dob_candidate.py", "libraries/robot_output_sanitizer.py",
    "testdata/onboarding/etb_cases.yaml",
    "docs/source/testcases/etb/current/QA_TestCase_OPO_ETB Registration_Automation.xlsx",
)


def _execution_binding() -> dict[str, object]:
    """Capture configured invocation identity; not a claim that a step ran."""
    hashes = {}
    for rel in _BINDING_PATHS:
        path = _PROJECT_ROOT / rel
        hashes[rel] = hashlib.sha256(path.read_bytes()).hexdigest() if path.is_file() else None
    profile = Path(os.environ.get("ETB_CASE_PROFILES") or
                   _PROJECT_ROOT / "testdata/onboarding/etb_cases.local.yaml")
    strategy = os.environ.get("ETB_DOB_STRATEGY", "UNPROVEN")
    return {
        "schema": "bbl-etb-execution-binding/v1",
        "source_hashes": hashes,
        "profile_path": _relative_repo_path(profile),
        "profile_sha256": hashlib.sha256(profile.read_bytes()).hexdigest() if profile.is_file() else None,
        "dob_strategy": strategy if strategy in {"LEGACY", "STABLE_V1"} else "UNPROVEN",
        "strategy_evidence": "RUNNER_CONFIGURATION_NOT_LIVE_EXECUTION",
    }


def initialize_run_artifacts(args: list[str]) -> int:
    if len(args) < 15:
        print("ETB_INIT_RUN_ARGUMENTS_REQUIRED", file=sys.stderr)
        return 2
    (
        output_dir,
        output_base,
        run_id,
        environment,
        execution_target,
        selector_type,
        selector_value,
        branch,
        head,
        staged_count,
        modified_count,
        untracked_count,
        staged_fingerprint,
        worktree_fingerprint,
        build_identity,
        *context,
    ) = args

    product_release = "UNPROVEN"
    device_udid = "UNPROVEN"
    case_ids = list(context)
    if case_ids and not case_ids[0].startswith("TC-"):
        product_release = case_ids.pop(0)
    if case_ids and not case_ids[0].startswith("TC-"):
        device_udid = case_ids.pop(0)

    output = Path(output_dir)
    base = Path(output_base)
    output.mkdir(parents=True, exist_ok=True)
    counts = {
        "staged": _safe_int(staged_count),
        "modified": _safe_int(modified_count),
        "untracked": _safe_int(untracked_count),
    }
    known_counts = [value for value in counts.values() if value is not None]
    manifest = {
        "schema": "bbl-etb-run-manifest/v1",
        "artifact_classification": "SHAREABLE_SANITIZED",
        "run_id": _safe_manifest_value(run_id),
        "created_at": _utc_now(),
        "output_root": _relative_repo_path(output),
        "selection": {
            "type": _safe_manifest_value(selector_type or "all"),
            "value": _safe_manifest_value(selector_value) if selector_value else "",
            "case_ids": [_safe_manifest_value(case_id) for case_id in case_ids],
        },
        "runtime": {
            "environment": _safe_manifest_value(environment),
            "execution_target": _safe_manifest_value(execution_target),
            "build_identity": _safe_manifest_value(build_identity),
            "product_release": _safe_manifest_value(product_release),
            "device_udid": _safe_manifest_value(device_udid),
        },
        "code": {
            "branch": _safe_manifest_value(branch),
            "head": _safe_manifest_value(head),
            "dirty": bool(sum(known_counts)) if len(known_counts) == 3 else None,
            "counts": counts,
            "staged_fingerprint": _safe_manifest_value(staged_fingerprint),
            "worktree_fingerprint": _safe_manifest_value(worktree_fingerprint),
        },
        "knowledge_binding": _traceability_binding(),
        "execution_binding": _execution_binding(),
    }
    _write_json_atomic(output / "run_manifest.json", manifest)
    _write_json_atomic(
        base / "latest.json",
        {
            "schema": "bbl-etb-latest-run/v1",
            "artifact_classification": "SHAREABLE_SANITIZED",
            "run_id": manifest["run_id"],
            "output_root": manifest["output_root"],
            "updated_at": _utc_now(),
        },
    )
    print(f"ETB_RUN_MANIFEST={output / 'run_manifest.json'}")
    return 0


def _test_status(test: ET.Element) -> tuple[str, str]:
    status = next((child for child in test if child.tag == "status"), None)
    if status is None:
        return "UNKNOWN", ""
    return status.get("status", "UNKNOWN").upper(), "".join(status.itertext()).strip()


def _messages(test: ET.Element) -> list[str]:
    return [
        (message.text or "").strip()
        for message in test.iter("msg")
        if (message.text or "").strip()
    ]


def _terminal_failure_text(test: ET.Element, fallback: str = "") -> str:
    """Return the primary unhandled top-level failure, not recovered children."""
    failed_body: list[str] = []
    failed_teardown: list[str] = []
    for keyword in test:
        if keyword.tag != "kw":
            continue
        status = next((child for child in keyword if child.tag == "status"), None)
        if status is None or status.get("status", "").upper() != "FAIL":
            continue
        direct_messages = [
            (message.text or "").strip()
            for message in keyword.findall("msg")
            if (message.text or "").strip()
        ]
        text = "\n".join(
            part for part in ("".join(status.itertext()).strip(), *direct_messages) if part
        )
        if not text:
            continue
        target = failed_teardown if keyword.get("type", "").lower() == "teardown" else failed_body
        target.append(text)
    if failed_body:
        return failed_body[0]
    if failed_teardown:
        return failed_teardown[0]
    return fallback


def _environment_blocker(text: str) -> str | None:
    if "BLOCKED_BY_ENVIRONMENT_PROFILE_DATA_RAI_033" in text:
        return None
    if "BLOCKED_BY_ENVIRONMENT_" not in text:
        return None
    explicit = re.search(r"BLOCKED_BY_ENVIRONMENT_[A-Z0-9_:-]*?(AJI|GOD|RAI)[_-](\d+)", text)
    if explicit is not None:
        return f"{explicit.group(1)}-{explicit.group(2)}"
    generic = re.search(r"BLOCKED_BY_ENVIRONMENT_[A-Z0-9_:-]+", text)
    return generic.group(0) if generic is not None else None


def _application_blocker(text: str) -> str | None:
    match = re.search(r"\bTERMS_CONTENT_NOT_RENDERED_AFTER_\d+_RECOVERY_ATTEMPTS\b", text)
    if match is not None:
        return match.group(0)
    if "LANDING_FULL_SCREEN_GUB_AFTER_ACTION" in text:
        return "LANDING_FULL_SCREEN_GUB_AFTER_ACTION"
    return None


def _business_outcome(status: str, combined_text: str) -> tuple[str, dict[str, object]]:
    environment_blocker_code = _environment_blocker(combined_text)
    application_blocker_code = _application_blocker(combined_text)
    if status == "PASS":
        return "PASS", {"type": None, "code": None}
    if status == "SKIP":
        policy = "TC003_CONTROL_HOME_NOT_PROVEN" if "TC003_CONTROL_HOME_NOT_PROVEN" in combined_text else None
        return "SKIPPED", {"type": "EXECUTION_POLICY" if policy else None, "code": policy}
    if any(marker in combined_text for marker in (
        "PROFILE_RESPONSE_UNEXPECTED_RAI_033",
        "BLOCKED_BY_ENVIRONMENT_PROFILE_DATA_RAI_033",
        "ETB_COMMON_ONBOARDING_DID_NOT_REACH_DOPA: RAI-033 != NEXT",
    )):
        return "FAIL", {"type": "OBSERVED_RESPONSE", "code": "RAI-033"}
    if environment_blocker_code is not None:
        return "BLOCKED", {"type": "ENVIRONMENT", "code": environment_blocker_code}
    if application_blocker_code is not None:
        return "FAIL", {"type": "APPLICATION", "code": application_blocker_code}
    return "FAIL", {"type": None, "code": None}


def _failure_origin(
    outcome: str,
    combined_text: str,
    terminal_text: str | None = None,
) -> str | None:
    if outcome == "PASS":
        return None
    if outcome in {"NOT_RUN", "INTERRUPTED"}:
        return "EXECUTION"
    if outcome == "BLOCKED":
        return "ENVIRONMENT"
    if outcome == "SKIPPED":
        return "EXECUTION_POLICY"
    causal_text = terminal_text.strip() if terminal_text and terminal_text.strip() else combined_text
    if _application_blocker(causal_text) is not None:
        return "APPLICATION"

    automation_markers = (
        "AUTOMATION_EVIDENCE_CAPTURE_FAILED",
        "POST_CIS_CLEANUP_AUTOMATION_FAILED",
        "SESSION_CLOSE_FAILED",
        "REAL_DEVICE_ATTACH_RELAUNCHED_APPLICATION",
        "REAL_DEVICE_ATTACH_CURRENT_ACTIVITY_MISMATCH",
        "REAL_DEVICE_APPIUM_ATTACH_LANDING_NOT_ACCESSIBLE",
    )
    if any(marker in causal_text for marker in automation_markers):
        return "AUTOMATION"
    # Robot's BuiltIn Evaluate prefixes expression failures with this marker.
    # Keep the provenance requirement so application/backend TypeError text
    # remains UNKNOWN unless the Robot boundary proves the automation origin.
    if "Evaluating expression" in causal_text and "TypeError:" in causal_text:
        return "AUTOMATION"
    return "UNKNOWN"


def _cis_cleanup(output: Path, run_id: str, case_id: str) -> dict[str, object]:
    path = output / "evidence" / run_id / case_id / "cis_post_test_result.json"
    if not path.is_file():
        return {"status": "NOT_RECORDED", "artifact": None}
    try:
        payload = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError):
        return {"status": "UNREADABLE", "artifact": _relative_repo_path(path)}
    if not isinstance(payload, dict):
        return {"status": "UNREADABLE", "artifact": _relative_repo_path(path)}
    if payload.get("cis_clear") == "PASS":
        status = "PASS"
    elif payload.get("cis_clear") == "NOT_APPLICABLE":
        status = "NOT_APPLICABLE"
    elif payload.get("post_cis_cleanup_owner") == "EXTERNAL_TEAM":
        status = "EXTERNAL_OWNER"
    elif payload.get("cis_clear") in {"FAIL", "NO"}:
        status = "FAIL"
    else:
        status = "UNPROVEN"
    return {"status": status, "artifact": _relative_repo_path(path)}


def _appium_cleanup(messages: list[str]) -> str:
    joined = "\n".join(messages)
    if "SESSION_CLOSE_FAILED" in joined:
        return "FAIL"
    match = re.search(r"APPIUM_SESSION_CLOSE=(PASS|NOT_REQUIRED)", joined)
    return match.group(1) if match else "UNPROVEN"


def _pdpa_cleanup(messages: list[str]) -> str:
    joined = "\n".join(messages)
    if "PDPA_CLEANUP_FAILED" in joined or "TC002_CLEANUP_FAILED" in joined:
        return "FAIL"
    if "CASE_SPECIFIC_PDPA_CLEANUP=PASS" in joined:
        return "PASS"
    if "CASE_SPECIFIC_PDPA_CLEANUP=ATTEMPTED" in joined:
        semantic = re.search(r"semantic_verifiable=([^\s]+)", joined)
        return "ATTEMPTED_VERIFIED" if semantic and semantic.group(1).lower() == "true" else "ATTEMPTED_UNVERIFIED"
    if "CASE_SPECIFIC_PDPA_CLEANUP=BEST_EFFORT_WARNING" in joined:
        return "BEST_EFFORT_WARNING"
    return "NOT_APPLICABLE"


def _evidence_capture_summary(output: Path, run_id: str, case_id: str) -> dict[str, object]:
    private_dir = output / "evidence" / run_id / case_id / "private_local"
    captures: list[dict[str, object]] = []
    if private_dir.is_dir():
        for path in sorted(private_dir.glob("*.json")):
            try:
                payload = json.loads(path.read_text(encoding="utf-8"))
            except (OSError, json.JSONDecodeError):
                continue
            if not isinstance(payload, dict) or payload.get("schema") != "etb-evidence/v2":
                continue
            captures.append(
                {
                    "artifact": _relative_repo_path(path),
                    "capture_status": payload.get("capture_status", "UNPROVEN"),
                }
            )
    if not captures:
        status = "NOT_REQUESTED"
    else:
        statuses = [str(item["capture_status"]) for item in captures]
        if all(value == "COMPLETE" for value in statuses):
            status = "COMPLETE"
        elif any(value == "COMPLETE" for value in statuses):
            status = "PARTIAL"
        else:
            status = "INCOMPLETE"
    return {"status": status, "captures": captures}


def _case_result_trust(
    outcome: str,
    blocker: dict[str, object],
    failure_origin: str | None,
    cleanup: dict[str, object],
    evidence: dict[str, object],
) -> str:
    evidence_status = str(evidence.get("status") or "NOT_REQUESTED")
    cis = cleanup.get("cis")
    cis_status = str(cis.get("status") if isinstance(cis, dict) else "UNPROVEN")
    pdpa_status = str(cleanup.get("pdpa") or "UNPROVEN")
    appium_status = str(cleanup.get("appium_session") or "UNPROVEN")

    if outcome == "PASS":
        cleanup_ok = (
            cis_status in {"PASS", "NOT_APPLICABLE", "EXTERNAL_OWNER"}
            and pdpa_status in {
                "PASS",
                "NOT_APPLICABLE",
                # TC002 declares PDPA cleanup BEST_EFFORT; preserve the
                # submitted/unverified or warning state without making it a
                # fabricated semantic reset.
                "ATTEMPTED_UNVERIFIED",
                "ATTEMPTED_VERIFIED",
                "BEST_EFFORT_WARNING",
            }
            and appium_status in {"PASS", "NOT_REQUIRED"}
        )
        if evidence_status != "COMPLETE" or not cleanup_ok:
            return "UNTRUSTED"
        return "TRUSTED"

    if outcome == "BLOCKED":
        cleanup_ok = (
            cis_status in {"PASS", "NOT_APPLICABLE", "EXTERNAL_OWNER"}
            and pdpa_status in {
                "PASS",
                "NOT_APPLICABLE",
                "ATTEMPTED_UNVERIFIED",
                "ATTEMPTED_VERIFIED",
                "BEST_EFFORT_WARNING",
            }
            and appium_status in {"PASS", "NOT_REQUIRED"}
        )
        if not blocker.get("code") or evidence_status != "COMPLETE" or not cleanup_ok:
            return "UNTRUSTED"
        return "TRUSTED"

    if outcome == "SKIPPED":
        policy_is_explicit = (
            blocker.get("type") == "EXECUTION_POLICY"
            and blocker.get("code") is not None
        )
        return "TRUSTED" if policy_is_explicit else "DEGRADED"

    if outcome in {"NOT_RUN", "INTERRUPTED"}:
        return "NOT_ASSESSABLE"

    if outcome == "FAIL":
        cleanup_ok = (
            cis_status in {"PASS", "NOT_APPLICABLE", "EXTERNAL_OWNER"}
            and pdpa_status in {
                "PASS",
                "NOT_APPLICABLE",
                "ATTEMPTED_VERIFIED",
                "ATTEMPTED_UNVERIFIED",
                "BEST_EFFORT_WARNING",
            }
            and appium_status in {"PASS", "NOT_REQUIRED"}
        )
        if evidence_status in {"PARTIAL", "INCOMPLETE", "NOT_REQUESTED"} or not cleanup_ok:
            return "UNTRUSTED"
        return "TRUSTED" if failure_origin not in {None, "UNKNOWN"} else "DEGRADED"

    return "NOT_ASSESSABLE"


def _execution_status(test: ET.Element, status_text: str) -> str:
    """Distinguish business execution from Robot records created after a fatal stop."""
    lowered = status_text.lower()
    # Setup status takes precedence even when its error contains a business code.
    if lowered.startswith("setup failed:"):
        return "SETUP_FAILED"
    keyword_count = sum(1 for _ in test.iter("kw"))
    if "execution terminated by signal" in lowered or "fatal error" in lowered:
        return "INTERRUPTED" if keyword_count else "UNEXECUTED"
    # A suite-level blocker may be recorded on the test status before Robot
    # emits child keywords. Preserve that explicit business/environment result.
    if "blocked_by_" in lowered or re.search(r"\b(?:RGI|GOD|AJI)-\d{3}\b", status_text):
        return "EXECUTED"
    if keyword_count == 0:
        return "UNEXECUTED"
    if lowered.startswith("setup failed:"):
        return "SETUP_FAILED"
    return "EXECUTED"


def _run_result_trust(cases: list[dict[str, object]]) -> str:
    if not cases:
        return "NOT_ASSESSABLE"
    trusts = [str(case.get("result_trust") or "NOT_ASSESSABLE") for case in cases]
    if any(value == "UNTRUSTED" for value in trusts):
        return "UNTRUSTED"
    if any(value == "DEGRADED" for value in trusts):
        return "DEGRADED"
    if all(value == "TRUSTED" for value in trusts):
        return "TRUSTED"
    return "NOT_ASSESSABLE"


def _write_evidence_index(output: Path, run_id: str) -> bool:
    """Build the reference-only evidence index without leaking artifact content."""
    from libraries.evidence_index import build_evidence_index

    try:
        target = build_evidence_index(output, run_id)
    except Exception as error:
        print(
            f"ETB_EVIDENCE_INDEX=FAILED type={type(error).__name__}",
            file=sys.stderr,
        )
        return False
    print(f"ETB_EVIDENCE_INDEX={target}")
    return True


def finalize_run_artifacts(output_dir: str, run_id: str) -> int:
    output = Path(output_dir)
    manifest_path = output / "run_manifest.json"
    output_xml = output / "output.xml"
    manifest: dict[str, object] = {}
    if manifest_path.is_file():
        try:
            loaded = json.loads(manifest_path.read_text(encoding="utf-8"))
            if isinstance(loaded, dict):
                manifest = loaded
        except (OSError, json.JSONDecodeError):
            manifest = {}

    if not output_xml.is_file():
        _write_json_atomic(
            output / "run_result.json",
            {
                "schema": "bbl-etb-run-result/v1",
                "artifact_classification": "SHAREABLE_SANITIZED",
                "run_id": run_id,
                "run_status": "RESULT_UNAVAILABLE",
                "result_trust": "NOT_ASSESSABLE",
                "finalized_at": _utc_now(),
                "manifest": _relative_repo_path(manifest_path),
                "cases": [],
            },
        )
        _write_evidence_index(output, run_id)
        print("ETB_RUN_RESULT=RESULT_UNAVAILABLE", file=sys.stderr)
        return 4

    root = ET.parse(output_xml).getroot()
    cases: list[dict[str, object]] = []
    for test in root.iter("test"):
        name = test.get("name", "")
        match = _CASE_NAME.match(name)
        case_id = match.group(1) if match else "CASE_UNSCOPED"
        status, status_text = _test_status(test)
        messages = _messages(test)
        combined = "\n".join([status_text, *messages])
        execution_status = _execution_status(test, status_text)
        terminal_failure = _terminal_failure_text(test, status_text)
        if execution_status == "UNEXECUTED":
            outcome, blocker = "NOT_RUN", {"type": "EXECUTION", "code": "NOT_STARTED"}
        elif execution_status == "INTERRUPTED":
            outcome, blocker = "INTERRUPTED", {"type": "EXECUTION", "code": "INTERRUPTED"}
        elif execution_status == "SETUP_FAILED":
            outcome, blocker = "NOT_RUN", {"type": "SETUP", "code": "SETUP_FAILED"}
        else:
            outcome, blocker = _business_outcome(status, terminal_failure or status_text)
        failure_origin = _failure_origin(outcome, combined, terminal_failure)
        cleanup = {
            "cis": _cis_cleanup(output, run_id, case_id),
            "pdpa": _pdpa_cleanup(messages),
            "appium_session": _appium_cleanup(messages),
        }
        evidence = _evidence_capture_summary(output, run_id, case_id)
        result_trust = _case_result_trust(
            outcome,
            blocker,
            failure_origin,
            cleanup,
            evidence,
        )
        cases.append(
            {
                "case_id": case_id,
                "test_name": name,
                "robot_status": status,
                "execution_status": execution_status,
                "business_outcome": outcome,
                "failure_origin": failure_origin,
                "result_trust": result_trust,
                "blocker": blocker,
                "cleanup": cleanup,
                "evidence": evidence,
            }
        )

    outcomes = [str(case["business_outcome"]) for case in cases]
    if any(value == "FAIL" for value in outcomes):
        run_status = "FAIL"
    elif any(value == "BLOCKED" for value in outcomes):
        run_status = "BLOCKED"
    elif any(value == "INTERRUPTED" for value in outcomes):
        run_status = "INTERRUPTED"
    elif any(value == "NOT_RUN" for value in outcomes):
        run_status = "INCOMPLETE"
    elif cases and all(value == "SKIPPED" for value in outcomes):
        run_status = "SKIPPED"
    elif cases:
        run_status = "PASS"
    else:
        run_status = "RESULT_UNAVAILABLE"

    summary = {
        key: outcomes.count(key)
        for key in ("PASS", "FAIL", "BLOCKED", "SKIPPED", "NOT_RUN", "INTERRUPTED")
    }
    result = {
        "schema": "bbl-etb-run-result/v1",
        "artifact_classification": "SHAREABLE_SANITIZED",
        "run_id": run_id,
        "run_status": run_status,
        "result_trust": _run_result_trust(cases),
        "finalized_at": _utc_now(),
        "manifest": _relative_repo_path(manifest_path),
        "robot_output": _relative_repo_path(output_xml),
        "summary": summary,
        "cases": cases,
    }
    if manifest.get("run_id") not in {None, run_id}:
        result["manifest_consistency"] = "RUN_ID_MISMATCH"
    else:
        result["manifest_consistency"] = "PASS"
    start_binding = manifest.get("execution_binding")
    if isinstance(start_binding, dict) and start_binding.get("schema") == "bbl-etb-execution-binding/v1":
        end_binding = _execution_binding()
        unchanged = start_binding == end_binding
        result["source_consistency"] = "UNCHANGED" if unchanged else "CHANGED_DURING_RUN"
        if not unchanged:
            result["result_trust"] = "UNTRUSTED"
            for case in cases:
                case["source_consistency"] = "CHANGED_DURING_RUN"
                if case["execution_status"] == "EXECUTED":
                    case["result_trust"] = "UNTRUSTED"
    else:
        result["source_consistency"] = "UNPROVEN_LEGACY_MANIFEST"
    _write_json_atomic(output / "run_result.json", result)
    if not _write_evidence_index(output, run_id):
        return 5
    print(f"ETB_RUN_RESULT={run_status}")
    return 0



def validate_case_set(manifest_path: str, selected_ids: list[str]) -> int:
    path = Path(manifest_path)
    try:
        payload = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as error:
        print(f"ETB_CASE_SET_MANIFEST_UNREADABLE={type(error).__name__}", file=sys.stderr)
        return 3
    if not isinstance(payload, dict) or payload.get("schema") != "bbl-etb-case-set/v1":
        print("ETB_CASE_SET_MANIFEST_INVALID_SCHEMA", file=sys.stderr)
        return 3
    expected = payload.get("canonical_case_ids")
    if not isinstance(expected, list) or not expected or not all(isinstance(item, str) for item in expected):
        print("ETB_CASE_SET_MANIFEST_INVALID_CASE_IDS", file=sys.stderr)
        return 3

    duplicate_expected = sorted({item for item in expected if expected.count(item) > 1})
    duplicate_selected = sorted({item for item in selected_ids if selected_ids.count(item) > 1})
    missing = [item for item in expected if item not in selected_ids]
    extra = [item for item in selected_ids if item not in expected]
    order_match = selected_ids == expected

    if duplicate_expected or duplicate_selected or missing or extra or not order_match:
        print(
            "ETB_CASE_SET_MISMATCH "
            + json.dumps(
                {
                    "duplicate_expected": duplicate_expected,
                    "duplicate_selected": duplicate_selected,
                    "missing": missing,
                    "extra": extra,
                    "order_match": order_match,
                },
                sort_keys=True,
            ),
            file=sys.stderr,
        )
        return 3

    print(
        "ETB_CASE_SET=PASS "
        + json.dumps(
            {
                "count": len(expected),
                "first": expected[0],
                "last": expected[-1],
            },
            sort_keys=True,
        )
    )
    return 0


def main(argv: list[str]) -> int:
    if not argv:
        print("ETB_RUNTIME_COMMAND_REQUIRED", file=sys.stderr)
        return 2

    command, *args = argv
    if command == "resolve-selector" and len(args) == 2:
        return resolve_selector(args[0], args[1])
    if command == "absolute-path" and len(args) == 1:
        return absolute_path(args[0])
    if command == "selected-count" and len(args) == 1:
        return selected_count(args[0])
    if command == "selected-case-ids" and len(args) == 1:
        return selected_case_ids(args[0])
    if command == "run-id" and not args:
        return generate_run_id()
    if command == "adb-executable" and not args:
        return resolved_adb_executable()
    if command == "disk-guard" and len(args) == 3:
        return disk_guard(args[0], args[1], args[2])
    if command == "target-guard" and len(args) in {6, 7}:
        return target_guard(*args)
    if command == "target-build-identity" and len(args) == 1:
        return target_build_identity(args[0])
    if command == "record-build-identity" and len(args) == 2:
        return record_run_build_identity(args[0], args[1])
    if command == "sit-cis-readiness" and len(args) >= 2:
        return sit_cis_readiness(args[0], args[1], args[2:])
    if command == "cis-preflight" and len(args) == 1:
        return cis_preflight(args[0])
    if command == "init-run":
        return initialize_run_artifacts(args)
    if command == "finalize-run" and len(args) == 2:
        return finalize_run_artifacts(args[0], args[1])
    if command == "validate-case-set" and len(args) >= 1:
        return validate_case_set(args[0], args[1:])

    print(f"ETB_RUNTIME_INVALID_ARGUMENTS command={command}", file=sys.stderr)
    return 2


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
