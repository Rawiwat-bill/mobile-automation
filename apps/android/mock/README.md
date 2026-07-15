# Android Mock Assets

## OCR Mock Thai ID Card

Editable identity template: `ntb_id_card.png` (1536×1024 RGB, aspect 1.5, no external padding).

The emulator OCR flow expects a **1280×960 white canvas** with the card resized to
**384×256** and pasted at **X=179, Y=164** (preferred) or **X=204, Y=204** (protected rollback).

### Generate the OCR baseline (one command)

```
python3 tools/emulator/card_geometry_optimizer.py \
  --source apps/android/mock/ntb_id_card.png \
  --canvas-width 1280 --canvas-height 960 \
  --width 384 --height 256 --x 179 --y 164 \
  --crop-padding auto --background white --resample lanczos \
  --output apps/android/mock/derived/<mock-name>_ocr_baseline.png
```

- Rollback variant: `--x 204 --y 204`.
- The generator crops padding, resizes (Lanczos, aspect-preserving), pastes, validates
  bounds, and prints geometry + SHA256. It never overwrites the source.
- Running the command above on `ntb_id_card.png` reproduces the proven DOPA-passing image
  (SHA `69f0e883…`).

### New mock identity

Change ONLY identity content (citizen ID, names, DOB, dates, portrait, barcode). Keep
geometry + render pipeline identical. A new identity **will have a different SHA** — that is
expected; pixel equality is only meaningful for position-only controls with the same card.

### Full reference

Geometry rationale, matching requirements, runtime validation, troubleshooting matrix, and
known limitations: **[`knowledge/ocr_mock_id_card.md`](../../knowledge/ocr_mock_id_card.md)**.

## `derived/`

Generated OCR mock images (gitignored-local investigation artifacts). Proven set:
- `ntb_id_card_layout_frozen_baseline.png` — frozen baseline (224,224).
- `ntb_id_card_layout_translate_minus20.png` — **protected rollback** (204,204), DOPA-passing.
- `ntb_id_card_layout_x179_y164.png` — **preferred** (179,164), DOPA-passing.

(Do not rename/regenerate/delete the protected rollback image.)
