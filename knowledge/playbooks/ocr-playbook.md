# OCR Playbook

## Status
Milestone 3 — **OCR layout proven** (mock card reaches `DOPA_INFORMATION`).
Authoritative baseline: [`../ocr_mock_id_card.md`](../ocr_mock_id_card.md).

## When to Use
- Generating a new mock Thai ID card for the emulator OCR flow.
- Validating an OCR layout change (position-only control experiments).
- Diagnosing RGI-055 / RGI-045 / DOPA on the emulator.

## Authoritative Reference
All geometry, the generation procedure, emulator launch, runtime validation, expected
results, the troubleshooting matrix, and known limitations live in
**`knowledge/ocr_mock_id_card.md`** (kept there to avoid duplication).

## Quick Rules
- Preferred geometry: **384×256 @ (179,164)** on 1280×960 white; rollback **(204,204)**.
- Change ONLY identity content for new mocks; keep geometry + pipeline identical.
- Do NOT claim byte-identity for new identity content (pixels necessarily change).
- Fresh flow only for certification (pm clear; never reuse a ForgeRock session).
- State-based polling: 2s interval, 60s max per result, no blind sleep >10s.
- Stop at the FIRST terminal state; a later GOD/SSL error never overwrites an RGI/DOPA result.
- Each proven position has **n=1** trial — do not claim "always passes."

## Stop Conditions
- `DOPA_INFORMATION` reached → success, stop.
- `RGI-055` / `RGI-045` → record, stop (do not auto-fix; see troubleshooting matrix).
- `GOD/COO/FSI` → capture minimum evidence, kill app, fresh happy flow, stop.
