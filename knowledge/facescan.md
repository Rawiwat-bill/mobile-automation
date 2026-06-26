# Face Verification Knowledge

## Status
Milestone 4 — Not yet implemented.

## Scope
NTB-only flow step after OCR.

## Expected Flow
```
[OCR Complete]
↓
Face Verification
  │ Capture face image
  │ Match against ID document
  │ Verification result
  ▼
[PIN Setup]
```

## Known Constraints
- Camera permission required
- Face verification may use native SDK or WebView
- Lighting, angle, and face positioning affect success rate
- May require liveness detection (blink, smile, head turn)

## Placeholder
This knowledge file will be updated when face verification implementation begins. Until then, no face verification automation code exists.
