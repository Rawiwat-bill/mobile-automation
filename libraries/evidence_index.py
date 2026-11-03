"""Deterministic, reference-only evidence index for ETB run artifacts."""

from __future__ import annotations

from datetime import datetime, timezone
import hashlib
import json
from pathlib import Path
import re
from typing import Any

_PROJECT_ROOT = Path(__file__).resolve().parents[1]
_CASE_ID = re.compile(r"^TC-ETB-\d{3}$")
_SAFE_PATH_PART = re.compile(r"^[A-Za-z0-9_.-]+$")
_SUPPORTED_DISCOVERY_SUFFIXES = {".json", ".png", ".xml", ".txt", ".html"}
_CLASSIFICATIONS = {"SHAREABLE_SANITIZED", "PRIVATE_LOCAL", "SENSITIVE", "RESTRICTED"}


def _utc_now() -> str:
    return datetime.now(timezone.utc).isoformat()


def _read_json(path: Path) -> dict[str, Any]:
    try:
        payload = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError, UnicodeDecodeError):
        return {}
    return payload if isinstance(payload, dict) else {}


def _safe_repo_ref(path: Path) -> tuple[str, str | None]:
    try:
        relative = path.resolve().relative_to(_PROJECT_ROOT.resolve())
    except (OSError, ValueError):
        return "EXTERNAL_PATH", None
    if all(_SAFE_PATH_PART.fullmatch(part) for part in relative.parts):
        return str(relative), None
    digest = hashlib.sha256(str(relative).encode("utf-8")).hexdigest()
    return "REDACTED_UNSAFE_PATH", digest


def _classification(payload: dict[str, Any], fallback: str) -> str:
    value = str(payload.get("artifact_classification") or "")
    return value if value in _CLASSIFICATIONS else fallback


def _artifact_ref(
    path: Path,
    *,
    classification: str,
    role: str,
    expected: bool = True,
) -> dict[str, Any]:
    ref, ref_hash = _safe_repo_ref(path)
    present = path.is_file()
    result: dict[str, Any] = {
        "role": role,
        "classification": classification,
        "presence": "PRESENT" if present else ("MISSING_EXPECTED" if expected else "MISSING_OPTIONAL"),
        "ref": ref,
    }
    if ref_hash is not None:
        result["ref_sha256"] = ref_hash
    return result


def _stage_name(path: Path, root: Path) -> str:
    try:
        relative = path.relative_to(root)
    except ValueError:
        relative = path
    raw = "_".join(relative.with_suffix("").parts)
    normalized = re.sub(r"[^A-Za-z0-9]+", "_", raw).strip("_").upper()
    return normalized or "UNSCOPED"


def _result_case_map(result: dict[str, Any]) -> dict[str, dict[str, Any]]:
    rows = result.get("cases")
    if not isinstance(rows, list):
        return {}
    mapped: dict[str, dict[str, Any]] = {}
    for item in rows:
        if not isinstance(item, dict):
            continue
        case_id = str(item.get("case_id") or "")
        if not _CASE_ID.fullmatch(case_id):
            continue
        mapped[case_id] = {
            "execution_status": item.get("execution_status"),
            "business_outcome": item.get("business_outcome"),
            "failure_origin": item.get("failure_origin"),
            "result_trust": item.get("result_trust"),
            "blocker": item.get("blocker"),
        }
    return mapped


def _case_ids(
    output: Path,
    run_id: str,
    manifest: dict[str, Any],
    result_cases: dict[str, dict[str, Any]],
) -> list[str]:
    discovered: list[str] = []

    selection = manifest.get("selection")
    if isinstance(selection, dict):
        selected = selection.get("case_ids")
        if isinstance(selected, list):
            for value in selected:
                candidate = str(value)
                if _CASE_ID.fullmatch(candidate) and candidate not in discovered:
                    discovered.append(candidate)

    for candidate in result_cases:
        if candidate not in discovered:
            discovered.append(candidate)

    evidence_root = output / "evidence" / run_id
    if evidence_root.is_dir():
        for path in sorted(evidence_root.iterdir()):
            if path.is_dir() and _CASE_ID.fullmatch(path.name) and path.name not in discovered:
                discovered.append(path.name)
    return discovered


def _timeline_checkpoints(
    private_dir: Path,
    indexed_files: set[Path],
    missing_expected: list[dict[str, Any]],
) -> list[dict[str, Any]]:
    timeline = private_dir / "timeline.json"
    if not timeline.is_file():
        return []
    indexed_files.add(timeline)
    try:
        events = json.loads(timeline.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError, UnicodeDecodeError):
        return []
    if not isinstance(events, list):
        return []

    checkpoints: list[dict[str, Any]] = []
    for index, event in enumerate(events, start=1):
        if not isinstance(event, dict):
            continue
        stage = re.sub(
            r"[^A-Za-z0-9_.-]+",
            "_",
            str(event.get("event") or event.get("recognized_state") or f"TIMELINE_{index}"),
        ).strip("._-") or f"TIMELINE_{index}"
        checkpoint: dict[str, Any] = {
            "stage": stage,
            "source": "VISUAL_TIMELINE",
            "recognized_state": str(event.get("recognized_state") or "UNPROVEN"),
            "artifacts": [
                _artifact_ref(
                    timeline,
                    classification="PRIVATE_LOCAL",
                    role="TIMELINE_METADATA",
                )
            ],
        }
        screenshot = event.get("screenshot")
        if isinstance(screenshot, str) and screenshot and _SAFE_PATH_PART.fullmatch(screenshot):
            screenshot_path = private_dir / screenshot
            screenshot_ref = _artifact_ref(
                screenshot_path,
                classification="PRIVATE_LOCAL",
                role="SCREENSHOT",
            )
            checkpoint["artifacts"].append(screenshot_ref)
            if screenshot_path.is_file():
                indexed_files.add(screenshot_path)
            else:
                missing_expected.append(
                    {"stage": stage, "role": "SCREENSHOT", "ref": screenshot_ref["ref"]}
                )
        checkpoints.append(checkpoint)
    return checkpoints


def _capture_checkpoints(
    private_dir: Path,
    indexed_files: set[Path],
    missing_expected: list[dict[str, Any]],
) -> list[dict[str, Any]]:
    checkpoints: list[dict[str, Any]] = []
    if not private_dir.is_dir():
        return checkpoints

    for metadata in sorted(private_dir.rglob("*.json")):
        if metadata.name == "timeline.json":
            continue
        payload = _read_json(metadata)
        if payload.get("schema") != "etb-evidence/v2":
            continue
        indexed_files.add(metadata)
        classification = _classification(payload, "PRIVATE_LOCAL")
        stage = _stage_name(metadata, private_dir)
        artifacts = [
            _artifact_ref(metadata, classification=classification, role="CAPTURE_METADATA")
        ]
        declared = payload.get("artifacts")
        declared = declared if isinstance(declared, dict) else {}
        candidates: list[tuple[str, Path]] = []
        if "screenshot" in declared:
            candidates.append(("SCREENSHOT", metadata.with_suffix(".png")))
        if "page_source" in declared:
            candidates.append(("PAGE_SOURCE", metadata.with_suffix(".xml")))
        if "foreground" in declared:
            candidates.append(
                ("FOREGROUND", metadata.with_name(metadata.stem + ".foreground.txt"))
            )
        for role, candidate in candidates:
            artifact = _artifact_ref(
                candidate,
                classification=classification,
                role=role,
            )
            artifacts.append(artifact)
            if candidate.is_file():
                indexed_files.add(candidate)
            elif str(declared.get(role.lower()) or "").upper() in {"PASS", "COMPLETE"}:
                missing_expected.append(
                    {"stage": stage, "role": role, "ref": artifact["ref"]}
                )
        checkpoints.append(
            {
                "stage": stage,
                "source": "ETB_EVIDENCE_V2",
                "capture_status": str(payload.get("capture_status") or "UNPROVEN"),
                "artifacts": artifacts,
            }
        )
    return checkpoints


def _generic_case_artifacts(
    case_dir: Path,
    private_dir: Path,
    indexed_files: set[Path],
) -> list[dict[str, Any]]:
    checkpoints: list[dict[str, Any]] = []
    if not case_dir.is_dir():
        return checkpoints

    for path in sorted(item for item in case_dir.rglob("*") if item.is_file()):
        if path in indexed_files or path.suffix.lower() not in _SUPPORTED_DISCOVERY_SUFFIXES:
            continue
        fallback = "PRIVATE_LOCAL" if private_dir in path.parents or path == private_dir else "SHAREABLE_SANITIZED"
        payload = _read_json(path) if path.suffix.lower() == ".json" else {}
        classification = _classification(payload, fallback)
        indexed_files.add(path)
        checkpoints.append(
            {
                "stage": _stage_name(path, case_dir),
                "source": "DISCOVERED_ARTIFACT",
                "artifacts": [
                    _artifact_ref(path, classification=classification, role="ARTIFACT")
                ],
            }
        )
    return checkpoints


def _case_index(
    output: Path,
    run_id: str,
    case_id: str,
    status: dict[str, Any],
) -> dict[str, Any]:
    case_dir = output / "evidence" / run_id / case_id
    private_dir = case_dir / "private_local"
    indexed_files: set[Path] = set()
    missing_expected: list[dict[str, Any]] = []

    checkpoints = _timeline_checkpoints(private_dir, indexed_files, missing_expected)
    checkpoints.extend(_capture_checkpoints(private_dir, indexed_files, missing_expected))
    checkpoints.extend(_generic_case_artifacts(case_dir, private_dir, indexed_files))
    checkpoints.sort(key=lambda item: (str(item.get("stage") or ""), str(item.get("source") or "")))

    existing = sorted(item for item in case_dir.rglob("*") if item.is_file()) if case_dir.is_dir() else []
    unindexed: list[dict[str, Any]] = []
    for path in existing:
        if path in indexed_files:
            continue
        ref, ref_hash = _safe_repo_ref(path)
        row: dict[str, Any] = {"ref": ref, "reason": "UNSUPPORTED_OR_UNMAPPED_ARTIFACT"}
        if ref_hash is not None:
            row["ref_sha256"] = ref_hash
        unindexed.append(row)

    evidence_ref, evidence_hash = _safe_repo_ref(case_dir)
    discovery: dict[str, Any] = {
        "case_evidence_root": evidence_ref,
        "case_evidence_root_presence": "PRESENT" if case_dir.is_dir() else "MISSING",
        "private_root_presence": "PRESENT" if private_dir.is_dir() else "MISSING",
        "existing_file_count": len(existing),
        "indexed_existing_file_count": sum(1 for path in existing if path in indexed_files),
        "existing_unindexed": unindexed,
        "missing_expected": missing_expected,
    }
    if evidence_hash is not None:
        discovery["case_evidence_root_sha256"] = evidence_hash

    return {
        "case_id": case_id,
        "status": status or {
            "execution_status": "UNPROVEN",
            "business_outcome": "UNPROVEN",
            "failure_origin": None,
            "result_trust": "UNPROVEN",
            "blocker": {"type": None, "code": None},
        },
        "checkpoints": checkpoints,
        "discovery": discovery,
    }


def build_evidence_index(output_dir: str | Path, run_id: str) -> Path:
    """Build one sanitized index without copying underlying evidence content."""
    output = Path(output_dir)
    manifest_path = output / "run_manifest.json"
    result_path = output / "run_result.json"
    manifest = _read_json(manifest_path)
    result = _read_json(result_path)
    result_cases = _result_case_map(result)

    robot_artifacts = [
        _artifact_ref(output / "output.xml", classification="PRIVATE_LOCAL", role="ROBOT_OUTPUT"),
        _artifact_ref(output / "log.html", classification="PRIVATE_LOCAL", role="ROBOT_LOG"),
        _artifact_ref(output / "report.html", classification="PRIVATE_LOCAL", role="ROBOT_REPORT"),
    ]
    run_refs = [
        _artifact_ref(
            manifest_path,
            classification=_classification(manifest, "SHAREABLE_SANITIZED"),
            role="RUN_MANIFEST",
        ),
        _artifact_ref(
            result_path,
            classification=_classification(result, "SHAREABLE_SANITIZED"),
            role="RUN_RESULT",
        ),
    ]
    global_missing = [
        {"role": item["role"], "ref": item["ref"]}
        for item in [*run_refs, *robot_artifacts]
        if item["presence"] == "MISSING_EXPECTED"
    ]

    cases = [
        _case_index(output, run_id, case_id, result_cases.get(case_id, {}))
        for case_id in _case_ids(output, run_id, manifest, result_cases)
    ]

    payload = {
        "schema": "bbl-etb-evidence-index/v1",
        "artifact_classification": "SHAREABLE_SANITIZED",
        "run_id": run_id,
        "generated_at": _utc_now(),
        "run_status": str(result.get("run_status") or "RESULT_UNAVAILABLE"),
        "result_trust": str(result.get("result_trust") or "NOT_ASSESSABLE"),
        "run_artifacts": run_refs,
        "robot_artifacts": robot_artifacts,
        "cases": cases,
        "discovery": {
            "missing_expected": global_missing,
            "case_count": len(cases),
            "existing_unindexed_count": sum(
                len(case["discovery"]["existing_unindexed"]) for case in cases
            ),
            "missing_expected_count": len(global_missing)
            + sum(len(case["discovery"]["missing_expected"]) for case in cases),
        },
    }

    target = output / "evidence_index.json"
    pending = target.with_suffix(".json.pending")
    pending.write_text(
        json.dumps(payload, indent=2, sort_keys=True, ensure_ascii=True) + "\n",
        encoding="utf-8",
    )
    pending.replace(target)
    return target
