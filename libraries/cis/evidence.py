"""CIS evidence persistence helpers.

Pure policy/state modules return data. This module owns the bounded filesystem
representation while preserving existing filenames and scoping semantics.
"""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from libraries.evidence_scope import resolve_scoped_output_dir


def write_lifecycle_result(
    output_dir: str,
    phase: str,
    result: dict[str, Any],
) -> dict[str, Any]:
    path = (
        Path(resolve_scoped_output_dir(output_dir))
        / f"cis_{phase.lower()}_result.json"
    )
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(
        json.dumps(result, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )
    return result


def write_profile_audit(
    output_dir: str,
    result: dict[str, Any],
    preparation: dict[str, Any],
    post_manifest: dict[str, Any],
) -> None:
    output = Path(output_dir)
    output.mkdir(parents=True, exist_ok=True)
    (output / "cis_profile_dependency_matrix.json").write_text(
        json.dumps(result, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )
    (output / "external_cis_preparation_manifest.json").write_text(
        json.dumps(preparation, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )
    (output / "external_cis_post_run_cleanup_manifest.json").write_text(
        json.dumps(post_manifest, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )


def write_readiness_result(
    output_dir: str,
    result: dict[str, Any],
) -> None:
    output = Path(output_dir)
    output.mkdir(parents=True, exist_ok=True)
    (output / "cis_readiness_result.json").write_text(
        json.dumps(result, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )
