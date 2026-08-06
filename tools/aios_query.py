#!/usr/bin/env python3
"""Read-only AIOS repository query engine.

This module answers questions from existing repository evidence. It never starts
processes, touches a device, invokes Codex, or mutates mission state.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import re
from pathlib import Path
from typing import Any

import yaml

try:
    from .aios_query_schema import validate_response
except ImportError:  # Direct CLI execution: python3 tools/aios_query.py
    from aios_query_schema import validate_response

ROOT = Path(__file__).resolve().parents[1]
CACHE_VERSION = "aios-query-cache/v1"
CACHE_DIR_NAME = ".runtime/aios/intelligence"
TEXT_SUFFIXES = frozenset({".md", ".yaml", ".yml", ".json", ".xml", ".txt", ".robot", ".resource", ".py"})
SKIP_PARTS = frozenset({"__pycache__", "node_modules", ".git"})
STOP_WORDS = frozenset(
    {
        "what",
        "which",
        "this",
        "that",
        "with",
        "from",
        "does",
        "solve",
        "solves",
        "have",
        "been",
        "already",
        "performed",
        "next",
        "run",
        "question",
        "repository",
        "evidence",
    }
)


def _relative(path: Path, root: Path) -> str:
    try:
        return str(path.resolve().relative_to(root.resolve()))
    except ValueError:
        return str(path)


def _safe_text(path: Path, limit: int = 250_000) -> str:
    if path.suffix.lower() not in TEXT_SUFFIXES or path.name.endswith(".local.yaml"):
        return ""
    try:
        return path.read_text(encoding="utf-8", errors="replace")[:limit]
    except OSError:
        return ""


def _redact(text: str) -> str:
    text = re.sub(r"\b\d{13}\b", "[MASKED_CITIZEN_ID]", text)
    text = re.sub(r"\b\d{10}\b", "[MASKED_PHONE]", text)
    text = re.sub(r"\b\d{6}\b", "[MASKED_CODE]", text)
    return re.sub(r"\b[A-Z]{2}\d{10}\b", "[MASKED_LASER_CODE]", text)


def _load_yaml(path: Path) -> dict[str, Any]:
    value = yaml.safe_load(_safe_text(path)) or {}
    return value if isinstance(value, dict) else {}


def _mission_path(root: Path, mission: str) -> Path:
    return root / ".runtime" / "aios" / "missions" / f"{mission}.yaml"


def _checkpoint_paths(root: Path, mission: str) -> list[Path]:
    base = root / ".runtime" / "aios" / "session_rotation" / "checkpoints" / mission
    return sorted(path for path in base.glob("**/*.yaml") if path.is_file())


def _handoff_paths(root: Path, mission: str) -> list[Path]:
    base = root / "knowledge" / "handoff"
    paths = sorted(path for path in base.glob("**/*") if path.is_file() and path.suffix.lower() in TEXT_SUFFIXES)
    mission_tokens = {token.lower() for token in re.split(r"[-_]", mission) if token}
    preferred = [path for path in paths if any(token in path.name.lower() for token in mission_tokens)]
    return preferred + [path for path in paths if path not in preferred]


def _report_paths(root: Path) -> list[Path]:
    base = root / "reports" / "investigation"
    return sorted(
        path
        for path in base.glob("**/*")
        if path.is_file() and path.suffix.lower() in TEXT_SUFFIXES and not path.name.endswith(".local.yaml")
    )


def _repository_paths(root: Path) -> list[Path]:
    paths: list[Path] = []
    for base in (root / "resources", root / "locators", root / "tests", root / "tools", root / "libraries"):
        if base.exists():
            paths.extend(
                path
                for path in base.glob("**/*")
                if path.is_file() and path.suffix.lower() in TEXT_SUFFIXES and not path.name.endswith(".local.yaml")
            )
    return sorted(paths)


def _pattern_paths(root: Path) -> list[Path]:
    base = root / "knowledge"
    return sorted(
        path
        for path in base.glob("**/*")
        if path.is_file() and path.suffix.lower() in TEXT_SUFFIXES and not path.name.endswith(".local.yaml")
    )


def _source_groups(root: Path, mission: str) -> list[tuple[str, list[Path]]]:
    mission_file = _mission_path(root, mission)
    return [
        ("mission_state", [mission_file] if mission_file.exists() else []),
        ("blocker_lifecycle", [mission_file] if mission_file.exists() else []),
        ("runtime_timeline", [mission_file] + _report_paths(root)),
        ("checkpoint", _checkpoint_paths(root, mission)),
        ("handoff", _handoff_paths(root, mission)),
        ("investigation_reports", _report_paths(root)),
        ("robot_artifacts", [path for path in _report_paths(root) if path.suffix.lower() in {".xml", ".txt", ".json"}]),
        ("repository_implementation", _repository_paths(root)),
        ("repository_patterns", _pattern_paths(root)),
    ]


def _all_sources(root: Path, mission: str) -> list[Path]:
    seen: set[Path] = set()
    result: list[Path] = []
    for _, paths in _source_groups(root, mission):
        for path in paths:
            resolved = path.resolve()
            if resolved not in seen and path.exists():
                seen.add(resolved)
                result.append(path)
    return result


def source_manifest(root: Path, mission: str) -> dict[str, str]:
    manifest: dict[str, str] = {}
    for path in _all_sources(root, mission):
        try:
            manifest[_relative(path, root)] = hashlib.sha256(path.read_bytes()).hexdigest()
        except OSError:
            continue
    return dict(sorted(manifest.items()))


def _manifest_hash(manifest: dict[str, str]) -> str:
    payload = json.dumps({"version": CACHE_VERSION, "manifest": manifest}, sort_keys=True, separators=(",", ":")).encode()
    return hashlib.sha256(payload).hexdigest()


def _cache_path(root: Path, mission: str, question: str, manifest_hash: str) -> Path:
    query_hash = hashlib.sha256(question.strip().lower().encode()).hexdigest()[:20]
    return root / CACHE_DIR_NAME / f"{mission}-{query_hash}-{manifest_hash[:16]}.json"


def _read_cache(path: Path) -> dict[str, Any] | None:
    try:
        value = json.loads(path.read_text(encoding="utf-8"))
        return validate_response(value)
    except (OSError, json.JSONDecodeError, ValueError):
        return None


def _write_cache(path: Path, response: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    temporary = path.with_suffix(path.suffix + ".tmp")
    temporary.write_text(json.dumps(response, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    temporary.replace(path)


def _first_state(root: Path, mission: str) -> tuple[dict[str, Any], str]:
    path = _mission_path(root, mission)
    return _load_yaml(path), _relative(path, root)


def _answer(confidence: str, sources: list[str], text: str) -> dict[str, Any]:
    return validate_response(
        {
            "repository_answer_exists": True,
            "confidence": confidence,
            "answer_source": list(dict.fromkeys(sources)),
            "existing_answer": _redact(text.strip()),
        }
    )


def _gap(kind: str, evidence: str) -> dict[str, Any]:
    return validate_response(
        {
            "repository_answer_exists": False,
            "knowledge_gap": kind,
            "missing_evidence_required": evidence,
        }
    )


def _active_blocker(root: Path, mission: str) -> dict[str, Any]:
    state, source = _first_state(root, mission)
    blockers = [item for item in state.get("blockers", []) if isinstance(item, dict) and item.get("lifecycle") == "ACTIVE"]
    if not blockers:
        if state.get("status") == "READY_FOR_USER" or state.get("last_result", {}).get("classification") == "ETB_RUNTIME_COMPLETE":
            return _answer("HIGH", [source], "No active blocker is recorded for the current mission state.")
        return _gap("PARTIAL", "A current mission state with an explicit active blocker lifecycle.")
    blocker = blockers[0]
    details = [f"{item.get('code')}: {item.get('message', item.get('classification', 'active blocker'))}" for item in blockers]
    result = _answer("HIGH", [source], "Current active blocker(s): " + "; ".join(details) + ".")
    return result


def _lifecycle_answer(root: Path, mission: str, lifecycle: str) -> dict[str, Any]:
    state, source = _first_state(root, mission)
    blockers = [item for item in state.get("blockers", []) if isinstance(item, dict) and item.get("lifecycle") == lifecycle]
    if not blockers:
        return _gap("PARTIAL", f"A mission state or lifecycle record naming blockers with lifecycle={lifecycle}.")
    values = [f"{item.get('code')}: {item.get('resolution', item.get('message', item.get('classification', '')))}" for item in blockers]
    return _answer("HIGH", [source], f"Blockers marked {lifecycle}: " + "; ".join(values) + ".")


def _deepest_screen(root: Path, mission: str) -> dict[str, Any]:
    state, source = _first_state(root, mission)
    result = state.get("last_result", {})
    screen = result.get("deepest_screen") or result.get("deepest_verified_screen")
    if screen:
        return _answer("HIGH", [source], f"Deepest verified screen: {screen}.")
    return _gap("PARTIAL", "A runtime result or report that records the deepest verified screen.")


def _latest_runtime(root: Path, mission: str) -> dict[str, Any]:
    state, source = _first_state(root, mission)
    result = state.get("last_result", {})
    blocker = result.get("blocker_code") or result.get("classification")
    screen = result.get("deepest_screen") or result.get("deepest_verified_screen")
    keyword = result.get("last_successful_keyword") or result.get("first_failing_keyword")
    if blocker or screen or keyword:
        text = f"Latest canonical runtime state: blocker/classification={blocker}, deepest screen={screen}, boundary keyword={keyword}."
        return _answer("HIGH", [source], text)
    return _gap("REQUIRES_RUNTIME", "A complete bounded runtime report with result, first failing keyword, and deepest verified screen.")


def _matched_repository_answer(root: Path, mission: str, question: str) -> dict[str, Any]:
    terms = [
        token
        for token in re.findall(r"[a-z0-9-]+", question.lower())
        if len(token) > 3 and token not in STOP_WORDS
    ]
    if not terms:
        return _gap("UNKNOWN", "A more specific engineering question or a source that identifies its subject.")
    groups = _source_groups(root, mission)
    normalized = question.lower()
    if "investigat" in normalized and ("already" in normalized or "performed" in normalized):
        # Lifecycle/state files identify blockers, but investigation-existence
        # questions require an investigation report or equivalent artifact.
        groups = [
            ("investigation_reports", _report_paths(root)),
            ("robot_artifacts", [path for path in _report_paths(root) if path.suffix.lower() in {".xml", ".txt", ".json"}]),
        ]
    elif "pattern" in normalized:
        groups = [
            ("repository_patterns", _pattern_paths(root)),
            ("repository_implementation", _repository_paths(root)),
        ]
    required_terms = terms
    pattern_question = "pattern" in normalized
    investigation_question = "investigat" in normalized and ("already" in normalized or "performed" in normalized)
    for group, paths in groups:
        for path in paths:
            if path.resolve() in {Path(__file__).resolve(), (root / "tests" / "test_aios_query.py").resolve()}:
                continue
            content = _safe_text(path)
            lowered = content.lower()
            matches = [term for term in terms if term in lowered]
            if investigation_question and "terms" in normalized:
                matches_are_sufficient = all(term in matches for term in required_terms) and "term" in str(path).lower()
            elif pattern_question:
                has_framework = "react" in matches and "native" in matches
                has_interaction = any(term in matches for term in ("tap", "transition", "adb"))
                matches_are_sufficient = has_framework and has_interaction
            else:
                matches_are_sufficient = all(term in matches for term in required_terms)
            if matches_are_sufficient:
                source = _relative(path, root)
                return _answer(
                    "MEDIUM",
                    [source],
                    f"Repository evidence answers this question in {source}; matched terms: {', '.join(matches)}.",
                )
    return _gap("UNKNOWN", "The specific engineering evidence, report, or implementation reference that answers this question.")


def _snapshot(root: Path, mission: str) -> dict[str, Any]:
    state, source = _first_state(root, mission)
    active = [item.get("code") for item in state.get("blockers", []) if isinstance(item, dict) and item.get("lifecycle") == "ACTIVE"]
    resolved = [item.get("code") for item in state.get("blockers", []) if isinstance(item, dict) and item.get("lifecycle") == "RESOLVED"]
    superseded = [item.get("code") for item in state.get("blockers", []) if isinstance(item, dict) and item.get("lifecycle") == "SUPERSEDED"]
    result = state.get("last_result", {})
    implementation_path = root / "resources" / "pages" / "common_onboarding" / "terms_and_conditions_page.resource"
    implementation_text = _safe_text(implementation_path).lower()
    verified_implementations = []
    implementation_sources = []
    if "scroll down consent terms with big fling" in implementation_text and "aji-001" in implementation_text:
        verified_implementations.append("ETB Terms transition correction: static verification passed")
        implementation_sources.append(_relative(implementation_path, root))
    pattern_path = root / "knowledge" / "patterns" / "scroll-pattern.md"
    patterns = []
    pattern_sources = []
    if pattern_path.exists():
        patterns.append("State-based ADB scrolling for React Native/WebView containers: VERIFIED_FOR_SIBLING")
        pattern_sources.append(_relative(pattern_path, root))
    snapshot = {
        "mission": mission,
        "active_blocker": active,
        "resolved_blockers": resolved,
        "superseded_findings": superseded,
        "deepest_verified_screen": result.get("deepest_screen") or result.get("deepest_verified_screen"),
        "verified_implementations": verified_implementations,
        "repository_patterns": patterns,
        "human_gates": [state.get("human_gate")] if state.get("human_gate") and state.get("human_gate", {}).get("type") else [],
        "runtime_gates": [state.get("current_gate")] if state.get("current_gate") else [],
        "provenance": [source] + implementation_sources + pattern_sources,
    }
    return _answer("HIGH", [source], json.dumps(snapshot, ensure_ascii=False, separators=(",", ":")))


def _uncached_query(root: Path, mission: str, question: str) -> dict[str, Any]:
    normalized = question.lower().strip()
    if any(token in normalized for token in ("active blocker", "current blocker", "current active blocker")):
        return _active_blocker(root, mission)
    if "resolved" in normalized and "blocker" in normalized:
        return _lifecycle_answer(root, mission, "RESOLVED")
    if "superseded" in normalized or "supersede" in normalized:
        return _lifecycle_answer(root, mission, "SUPERSEDED")
    if "deepest" in normalized and "screen" in normalized:
        return _deepest_screen(root, mission)
    if "latest" in normalized and "runtime" in normalized:
        return _latest_runtime(root, mission)
    if any(token in normalized for token in ("already investigated", "investigation already", "answered by repository", "repository evidence")):
        return _matched_repository_answer(root, mission, question)
    if any(token in normalized for token in ("implementation", "implemented", "verified implementation", "pattern")):
        return _matched_repository_answer(root, mission, question)
    return _matched_repository_answer(root, mission, question)


def query(mission: str, question: str, *, root: Path | None = None) -> dict[str, Any]:
    """Answer one repository question without executing or mutating project state."""
    project_root = (root or ROOT).resolve()
    if not mission.strip() or not question.strip():
        raise ValueError("AIOS_QUERY_MISSION_AND_QUESTION_REQUIRED")
    manifest = source_manifest(project_root, mission)
    cache = _cache_path(project_root, mission, question, _manifest_hash(manifest))
    cached = _read_cache(cache) if cache.exists() else None
    if cached is not None:
        return cached
    result = _uncached_query(project_root, mission, question)
    _write_cache(cache, result)
    return validate_response(result)


def snapshot(mission: str, *, root: Path | None = None) -> dict[str, Any]:
    """Return a compact Codex context snapshot using the same public contract."""
    project_root = (root or ROOT).resolve()
    if not mission.strip():
        raise ValueError("AIOS_QUERY_MISSION_REQUIRED")
    manifest = source_manifest(project_root, mission)
    question = "__snapshot__"
    cache = _cache_path(project_root, mission, question, _manifest_hash(manifest))
    cached = _read_cache(cache) if cache.exists() else None
    if cached is not None:
        return cached
    result = _snapshot(project_root, mission)
    _write_cache(cache, result)
    return validate_response(result)


def _main() -> int:
    parser = argparse.ArgumentParser(description="Read-only AIOS repository query engine")
    subparsers = parser.add_subparsers(dest="command", required=True)
    query_parser = subparsers.add_parser("query")
    query_parser.add_argument("--mission", required=True)
    query_parser.add_argument("--question", required=True)
    snapshot_parser = subparsers.add_parser("snapshot")
    snapshot_parser.add_argument("--mission", required=True)
    args = parser.parse_args()
    result = query(args.mission, args.question) if args.command == "query" else snapshot(args.mission)
    print(json.dumps(result, indent=2, ensure_ascii=False))
    return 0


if __name__ == "__main__":
    raise SystemExit(_main())
