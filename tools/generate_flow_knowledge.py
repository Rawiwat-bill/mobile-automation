#!/usr/bin/env python3
"""Generate AIOS flow knowledge from canonical Visio sequence diagrams.

The Visio files are read only by this generator.  The generator writes only
knowledge/flows/<flow>/flow.yaml, flow.md, and diagram.mmd.
"""

from __future__ import annotations

import argparse
import html
import re
import tempfile
from collections import Counter
from datetime import datetime, timezone
from pathlib import Path
from typing import Any
from zipfile import ZipFile
from xml.etree import ElementTree as ET

import yaml

ROOT = Path(__file__).resolve().parents[1]
SOURCE_ROOT = ROOT / "docs" / "source" / "sequence-diagrams"
OUTPUT_ROOT = ROOT / "knowledge" / "flows"
VISIO_NS = "http://schemas.microsoft.com/office/visio/2012/main"
NS = {"v": VISIO_NS}

FLOW_CONFIG = {
    "etb": {
        "flow_id": "ETB_NEW",
        "source": SOURCE_ROOT / "etb/current/Onboarding_Sequence Diagram.vsdx",
        "synchronization_date": "2026-08-05",
    },
    "ntb": {
        "flow_id": "NTB",
        "source": SOURCE_ROOT / "ntb/current/NTB_SequenceDiagram.vsdx",
    },
    "reactivate": {
        "flow_id": "REACTIVATE",
        "source": SOURCE_ROOT / "reactivate/current/Reactivation_Sequence Diagram (MVPX).vsdx",
    },
}

BRANCH_RE = re.compile(r"\b(if|else|otherwise|when|unless|retry|fail|failed|fallback|branch|option|valid|invalid)\b", re.I)
DECISION_RE = re.compile(r"\b(if|else|otherwise|when|unless|condition|pass|fail|failed|retry|valid|invalid|status|result|approve|approved|reject|rejected)\b", re.I)
SUCCESS_RE = re.compile(r"\b(success|successful|succeed|completed|complete|approved|accepted|created|normal|pass)\b", re.I)
CLEANUP_RE = re.compile(r"\b(cleanup|clean-up|rollback|compensat|terminate|logout|clear|delete|revoke|close|expire)\b", re.I)


def _clean_text(value: str) -> str:
    cleaned = " ".join(value.replace("\r", " ").replace("\n", " ").split()).strip()
    cleaned = re.sub(r"https?://\S+", "[MASKED_URL]", cleaned, flags=re.I)
    cleaned = re.sub(r"\b\d{13}\b", "[MASKED_CITIZEN_ID]", cleaned)
    cleaned = re.sub(r"\b\d{10}\b", "[MASKED_PHONE]", cleaned)
    cleaned = re.sub(r"\b\d{6}\b", "[MASKED_CODE]", cleaned)
    return cleaned


def _page_files(archive: ZipFile) -> list[str]:
    def page_number(name: str) -> int:
        return int(Path(name).stem.removeprefix("page"))

    return sorted(
        (
            name
            for name in archive.namelist()
            if re.fullmatch(r"visio/pages/page\d+\.xml", name)
        ),
        key=page_number,
    )


def _page_names(archive: ZipFile) -> list[str]:
    root = ET.fromstring(archive.read("visio/pages/pages.xml"))
    return [page.get("Name", f"Page {index}") for index, page in enumerate(root.findall(".//v:Page", NS), 1)]


def _shape_text(shape: ET.Element) -> str:
    return _clean_text(" ".join("".join(node.itertext()) for node in shape.findall("./v:Text", NS)))


def _cell_number(shape: ET.Element, name: str) -> float:
    value = next((cell.get("V") for cell in shape.findall("./v:Cell", NS) if cell.get("N") == name), "0")
    try:
        return float(value or 0)
    except ValueError:
        return 0.0


def _extract_shapes(page_root: ET.Element) -> list[dict[str, Any]]:
    shapes: list[dict[str, Any]] = []

    def visit(shape: ET.Element, parent_id: str | None) -> None:
        text = _shape_text(shape)
        if text:
            shapes.append(
                {
                    "id": shape.get("ID", ""),
                    "parent_id": parent_id,
                    "text": text,
                    "x": _cell_number(shape, "PinX"),
                    "y": _cell_number(shape, "PinY"),
                    "type": shape.get("Type", "Shape"),
                }
            )
        for child in shape.findall("./v:Shapes/v:Shape", NS):
            visit(child, shape.get("ID"))

    for shape in page_root.findall("./v:Shapes/v:Shape", NS):
        visit(shape, None)
    return shapes


def _component_names(shapes: list[dict[str, Any]]) -> list[str]:
    counts = Counter(str(shape["text"]) for shape in shapes)
    names = {
        text
        for text, count in counts.items()
        if count >= 2
        and len(text) <= 80
        and not re.search(r"[.!?]", text)
        and not re.search(r"\b(if|else|request|response|input|output|user|then)\b", text, re.I)
    }
    return sorted(names, key=lambda item: (item.casefold(), item))


def _sequence_steps(shapes: list[dict[str, Any]], components: set[str]) -> list[dict[str, Any]]:
    selected = [shape for shape in shapes if str(shape["text"]) not in components and len(str(shape["text"])) >= 3]
    selected.sort(key=lambda shape: (-float(shape["y"]), float(shape["x"]), str(shape["id"])))
    steps: list[dict[str, Any]] = []
    seen: set[tuple[str, str]] = set()
    for shape in selected:
        key = (str(shape["text"]), str(shape["id"]))
        if key in seen:
            continue
        seen.add(key)
        steps.append(
            {
                "order": len(steps) + 1,
                "shape_id": str(shape["id"]),
                "text": str(shape["text"]),
                "x": round(float(shape["x"]), 6),
                "y": round(float(shape["y"]), 6),
            }
        )
    return steps


def _unique_matching(steps: list[dict[str, object]], pattern: re.Pattern[str]) -> list[str]:
    values: list[str] = []
    seen: set[str] = set()
    for step in steps:
        text = str(step["text"])
        if pattern.search(text) and text not in seen:
            values.append(text)
            seen.add(text)
    return values


def _source_timestamp(source: Path) -> tuple[str, str]:
    timestamp = datetime.fromtimestamp(source.stat().st_mtime, timezone.utc)
    return timestamp.date().isoformat(), timestamp.replace(microsecond=0).isoformat().replace("+00:00", "Z")


def _relative_source(source: Path) -> str:
    return source.resolve().relative_to(ROOT.resolve()).as_posix()


def extract_flow(flow: str) -> dict[str, Any]:
    if flow not in FLOW_CONFIG:
        raise ValueError(f"unknown flow: {flow}")
    config = FLOW_CONFIG[flow]
    source = Path(config["source"])
    if not source.is_file():
        raise FileNotFoundError(f"canonical Visio source missing: {source}")

    source_date, generation_timestamp = _source_timestamp(source)
    pages: list[dict[str, object]] = []
    all_components: set[str] = set()
    with ZipFile(source) as archive:
        names = _page_names(archive)
        for index, page_file in enumerate(_page_files(archive)):
            page_root = ET.fromstring(archive.read(page_file))
            shapes = _extract_shapes(page_root)
            components = _component_names(shapes)
            all_components.update(components)
            steps = _sequence_steps(shapes, set(components))
            pages.append(
                {
                    "page": index + 1,
                    "name": names[index] if index < len(names) else f"Page {index + 1}",
                    "source_file": page_file,
                    "expected_sequence": steps,
                    "optional_branches": _unique_matching(steps, BRANCH_RE),
                    "decision_points": _unique_matching(steps, DECISION_RE),
                    "success_markers": _unique_matching(steps, SUCCESS_RE),
                    "cleanup_contract": _unique_matching(steps, CLEANUP_RE),
                }
            )

    sync_date = str(config.get("synchronization_date", source_date))
    page_names = [str(page["name"]) for page in pages]
    flow_id = str(config["flow_id"])
    return {
        "flow_id": flow_id,
        "business_purpose": f"Canonical {flow_id} business sequence represented by the Visio pages: " + "; ".join(page_names),
        "expected_sequence": pages,
        "optional_branches": [branch for page in pages for branch in page["optional_branches"]],
        "decision_points": [decision for page in pages for decision in page["decision_points"]],
        "success_marker": [marker for page in pages for marker in page["success_markers"]],
        "cleanup_contract": [item for page in pages for item in page["cleanup_contract"]],
        "canonical_components_used": sorted(all_components, key=lambda item: (item.casefold(), item)),
        "synchronization_date": sync_date,
        "source_visio": _relative_source(source),
        "generation_timestamp": generation_timestamp,
    }


def _yaml_text(contract: dict[str, Any]) -> str:
    return yaml.safe_dump(contract, allow_unicode=True, sort_keys=False, width=120)


def _markdown(contract: dict[str, Any]) -> str:
    lines = [
        f"# {contract['flow_id']} Flow Knowledge",
        "",
        "This file is generated from the canonical Visio source. Do not edit manually.",
        "",
        f"- Source Visio: `{contract['source_visio']}`",
        f"- Synchronization date: `{contract['synchronization_date']}`",
        f"- Generation timestamp: `{contract['generation_timestamp']}`",
        "",
        "## Business Purpose",
        "",
        str(contract["business_purpose"]),
        "",
        "## Expected Sequence",
        "",
    ]
    for page in contract["expected_sequence"]:
        lines.extend([f"### Page {page['page']}: {page['name']}", ""])
        for step in page["expected_sequence"]:
            lines.append(f"{step['order']}. {step['text']}")
        lines.append("")
    for title, key in (
        ("Optional Branches", "optional_branches"),
        ("Decision Points", "decision_points"),
        ("Success Markers", "success_marker"),
        ("Cleanup Contract", "cleanup_contract"),
        ("Canonical Components Used", "canonical_components_used"),
    ):
        lines.extend([f"## {title}", ""])
        values = contract[key]
        if values:
            lines.extend(f"- {value}" for value in values)
        else:
            lines.append("- None explicitly identified in the source diagram.")
        lines.append("")
    return "\n".join(lines).rstrip() + "\n"


def _mermaid(contract: dict[str, Any]) -> str:
    lines = ["%% Generated from the canonical Visio source; do not edit manually.", "flowchart TD"]
    previous: str | None = None
    node_number = 0
    for page in contract["expected_sequence"]:
        page_id = f"page_{page['page']}"
        lines.append(f'    subgraph {page_id}["Page {page["page"]}: {_mermaid_label(str(page["name"]))}"]')
        for step in page["expected_sequence"]:
            node_number += 1
            node_id = f"n{node_number}"
            label = _mermaid_label(str(step["text"]))
            if str(step["text"]) in set(page["decision_points"]):
                lines.append(f'        {node_id}{{"{label}"}}')
            else:
                lines.append(f'        {node_id}["{label}"]')
            if previous is not None:
                lines.append(f"        {previous} --> {node_id}")
            previous = node_id
        lines.append("    end")
    if previous is None:
        lines.append('    empty["No sequence steps extracted"]')
    return "\n".join(lines) + "\n"


def _mermaid_label(value: str) -> str:
    return html.escape(value.replace('"', "'").replace("\n", " "), quote=False)[:240]


def _write_atomic(path: Path, content: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with tempfile.NamedTemporaryFile("w", encoding="utf-8", dir=path.parent, prefix=f".{path.name}.", delete=False) as handle:
        temporary = Path(handle.name)
        handle.write(content)
    temporary.replace(path)


def generate_flow(flow: str, output_root: Path = OUTPUT_ROOT) -> list[Path]:
    contract = extract_flow(flow)
    destination = output_root / flow
    outputs = {
        destination / "flow.yaml": _yaml_text(contract),
        destination / "flow.md": _markdown(contract),
        destination / "diagram.mmd": _mermaid(contract),
    }
    for path, content in outputs.items():
        _write_atomic(path, content)
    return list(outputs)


def generate(flows: list[str], output_root: Path = OUTPUT_ROOT) -> list[Path]:
    generated: list[Path] = []
    for flow in flows:
        generated.extend(generate_flow(flow, output_root))
    return generated


def main() -> int:
    parser = argparse.ArgumentParser(description="Generate deterministic AIOS flow knowledge from canonical Visio diagrams")
    parser.add_argument("--flow", choices=[*FLOW_CONFIG, "all"], default="all")
    parser.add_argument("--output-root", type=Path, default=OUTPUT_ROOT)
    args = parser.parse_args()
    flows = list(FLOW_CONFIG) if args.flow == "all" else [args.flow]
    for path in generate(flows, args.output_root):
        print(path)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
