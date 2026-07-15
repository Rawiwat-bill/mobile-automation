# OCR Knowledge

## Status
Milestone 3 — **OCR layout investigation COMPLETE**. The mock ID card geometry now reaches
`DOPA_INFORMATION` (OCR Camera → detection → extraction → profile match → DOPA form) in fresh
emulator runs. Layout is no longer the blocker; remaining OCR work is pipeline-side
(recognition, preprocessing, validation, robustness).

➡️ **Authoritative mock-card baseline:** [`ocr_mock_id_card.md`](./ocr_mock_id_card.md)
(preferred geometry 384×256 @ (179,164); rollback @ (204,204); generator + procedure).

## Scope
NTB-only flow step after Profile handoff.

## Expected Flow
```
[Common Onboarding Complete]
↓
OCR Identity Verification
  │ Capture ID document image
  │ Extract text fields
  │ Verify extracted data
  ▼
[Face Verification or PIN Setup]
```

## Known Constraints
- Document capture requires camera permissions
- App may use native camera or WebView for capture
- OCR accuracy depends on image quality, lighting, document type
- Thai national ID card has specific format for citizen ID (13 digits)

## Placeholder
Retained for high-level milestone context. For the usable mock-card baseline (geometry,
generator, procedure, troubleshooting), see
[`ocr_mock_id_card.md`](./ocr_mock_id_card.md).
