# AIOS Query Engine

The AIOS Query Engine is a read-only shadow-mode repository knowledge query
service. It answers questions from existing mission state, lifecycle records,
runtime history, reports, artifacts, implementation, and patterns. It does not
own lifecycle, execute runtime, invoke Codex, or modify mission state.

## Usage

```text
python3 tools/aios_query.py query \
  --mission etb-runtime-baseline \
  --question "What is the current active blocker?"
```

```text
python3 tools/aios_query.py snapshot --mission etb-runtime-baseline
```

The Python API is available through `tools.aios_query`:

```python
from tools.aios_query import query, snapshot

answer = query("etb-runtime-baseline", "What is the current active blocker?")
context = snapshot("etb-runtime-baseline")
```

## Output contract

Every response is exactly one of two shapes.

Answer exists:

```json
{
  "repository_answer_exists": true,
  "confidence": "HIGH",
  "answer_source": ["..."],
  "existing_answer": "..."
}
```

Knowledge gap:

```json
{
  "repository_answer_exists": false,
  "knowledge_gap": "REQUIRES_RUNTIME",
  "missing_evidence_required": "..."
}
```

The engine never emits implementation, investigation, or runtime
recommendations. Hermes remains responsible for those decisions.

## Search order

1. Current mission state
2. Blocker lifecycle
3. Runtime timeline
4. Latest checkpoint
5. Handoff
6. Investigation reports
7. Robot artifacts
8. Repository implementation
9. Repository patterns

The engine stops after a sufficiently supported answer. Source hashes are used
to invalidate derived cache entries under `.runtime/aios/intelligence/`.

## Hermes pre-action integration

Hermes must call `tools.hermes_query_gate.query_before_action()` before any
new investigation, evidence collection, repository-wide search, or runtime
attempt. The boundary returns the exact Query Engine response and does not
approve, block, execute, or decide the requested action. Hermes remains the
lifecycle and decision owner.

```python
from tools.hermes_query_gate import query_before_action

answer = query_before_action(
    "etb-runtime-baseline",
    "What is the current active blocker?",
    "runtime_attempt",
)
```

If `repository_answer_exists` is true, Hermes uses the existing answer and does
not repeat the answered investigation. If false, Hermes reviews the explicit
knowledge gap and decides whether minimum evidence is necessary.

## Current mode

The Query Engine is mandatory for Hermes pre-action queries but remains
advisory and read-only. It is not wired into lifecycle execution, and ETB has
not been run as part of this integration change.
