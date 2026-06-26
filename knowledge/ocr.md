# OCR Knowledge

## Status
Milestone 3 — Not yet implemented.

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
This knowledge file will be updated when OCR implementation begins. Until then, no OCR-specific automation code exists.
