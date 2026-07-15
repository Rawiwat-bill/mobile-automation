# OCR Mock Thai ID Card Baseline

> Authoritative reference for generating emulator OCR mock Thai ID cards that reach
> `DOPA_INFORMATION`. Replaces the stale "Milestone 3 — not implemented" placeholder.
> Source evidence: `reports/investigation/layout_translate_minus20/` and
> `reports/investigation/layout_translate_x179_y164/`.

## Purpose

Let future mock ID cards be generated and used with the emulator OCR flow **without
repeating the layout investigation**. The layout (geometry + render pipeline) is settled;
future work changes only identity content.

## Proven Success Flow

```
OCR Camera (RVCamera)
  → Take Photo (adb tap, imagefile camera)
  → card detected
  → OCR extraction
  → extracted identity MATCHES the onboarding profile
  → DOPA_INFORMATION  (screenDopaInformation form — citizenIdNo / names / buttonNext)
```

Reached `DOPA_INFORMATION` in fresh runs at two positions (n=1 each).

## Source Template

`apps/android/mock/ntb_id_card.png` — 1536×1024 RGB, aspect 1.500, **no external padding**
(content fills the frame). This is the editable identity template.

## Final Geometry

| | value |
|---|---|
| Camera canvas | 1280×960 RGB |
| Card tile | 384×256 (aspect 1.500) |
| Background | solid white `RGB(255,255,255)` |
| Resize | Lanczos |
| Transformations | none — no rotation, perspective, blur, sharpen, color/gamma, shadow, markers, overlays, or auto-recentering |

## Preferred Position (latest, visually-aligned candidate)

| | value |
|---|---|
| X / Y | **179 / 164** |
| Bounds | [179,164][563,420] |
| Image | `apps/android/mock/derived/ntb_id_card_layout_x179_y164.png` |
| SHA256 | `69f0e88372b33ed91e5f3aaa2f64ccc3e2f9c07d79cdc1b9c0a4d73e6ea7af5a` |
| Result | DOPA_INFORMATION (fresh trial) |

## Protected Rollback Position

| | value |
|---|---|
| X / Y | **204 / 204** |
| Bounds | [204,204][588,460] |
| Image | `apps/android/mock/derived/ntb_id_card_layout_translate_minus20.png` |
| SHA256 | `1bf58b6b24b55c45a235374c8677e847742719f981797bad309260b9a99a8520` |
| Result | DOPA_INFORMATION (fresh trial) |

> The rollback baseline is **protected** — do not rename/regenerate/delete/overwrite it.

## Allowed Changes

For a **new mock identity**, change ONLY identity content:
citizen ID, Thai/English title + names, DOB, issue/expiry dates, address, portrait, barcode/printed reference.

The **geometry and render pipeline must stay consistent**: canvas size, card size
(384×256), card aspect (1.5), paste position, background (white), resize (Lanczos),
color mode (RGB), export (PNG).

## Forbidden Changes / Critical Correction

**Do NOT claim new mock cards are byte-identical to the baseline.** Changing identity
data (citizen ID, names, dates, portrait, barcode) **necessarily changes card pixels**.
SHA equality is expected ONLY for a position-only control experiment using the SAME card.

Forbidden: resizing the card away from 384×256, changing aspect, recentering, rotation,
perspective, blur/sharpen, color/gamma, shadows, debug markers/overlays, and altering
the OCR pipeline.

## New Mock Generation Procedure

1. Start from the Thai ID source/template (`apps/android/mock/ntb_id_card.png` or a copy).
2. Update only the required mock identity fields.
3. Confirm the card content is fully visible and readable.
4. Crop external padding (only if the editable source has margins — the current template has none).
5. Resize the card content to **384×256** (Lanczos).
6. Paste onto a **1280×960 RGB white** canvas at **X=179, Y=164**.
7. Save as deterministic PNG.
8. Keep a rollback image at X=204, Y=164 when needed.
9. Launch emulator with `-camera-back imagefile:<generated-image>`.
10. Run a fresh onboarding transaction (pm clear; do NOT reuse the prior ForgeRock session).
11. At OCR Camera: capture preview, tap Take Photo, poll every 2s (max 60s, no blind sleep >10s).
12. Expected successful terminal state: **DOPA_INFORMATION**.

> Use `tools/emulator/card_geometry_optimizer.py` — it performs steps 4–7 + prints geometry
> and SHA256 (see Emulator Launch Example).

## Emulator Launch Example

```
# Generate the preferred baseline from the template (reproduces the proven image, SHA 69f0e883…)
python3 tools/emulator/card_geometry_optimizer.py \
  --source apps/android/mock/ntb_id_card.png \
  --canvas-width 1280 --canvas-height 960 \
  --width 384 --height 256 --x 179 --y 164 \
  --crop-padding auto --background white --resample lanczos \
  --output apps/android/mock/derived/<mock-name>_ocr_baseline.png

# Rollback variant: change --x 204 --y 204

# Boot emulator with the generated imagefile
~/Library/Android/sdk/emulator/emulator -avd local_android_36 \
  -no-snapshot-load -no-boot-anim -gpu host \
  -camera-back imagefile:<absolute-path-to-generated-image> -grpc 8554
```

## Runtime Validation Procedure

1. Wait for `sys.boot_completed == 1`.
2. Fresh route: pm clear → Landing → Consent → Profile(CND) → PDPA → SignUp → ScanCardIntro → OCR Camera.
3. Confirm `RVCamera` present.
4. Capture `preview_before.png` + XML + activity.
5. Tap Take Photo (proven adb tap on the round button, ~540,2039 on the 1080×2400 screen).
6. Poll the result screen every 2s (max 60s). Stop at the **first** terminal state.

## Expected Results

| State | Meaning |
|---|---|
| `DOPA_INFORMATION` | Card detected → OCR extracted → data **matched** profile → DOPA form. **Success.** |
| `RGI-045` | Card accepted + OCR progressed, but data did not reach DOPA (e.g. mismatch). Intermediate. |
| `RGI-055` | Card NOT accepted as an ID card (detector rejection). |
| `GOD/COO/FSI` | Backend/service error — capture minimum evidence, kill app, restart happy flow. |

A later GOD/SSL/CDN error must **not** overwrite an earlier valid OCR result (stop at first terminal).

## Troubleshooting Matrix

| Result | Meaning | Check |
|---|---|---|
| **RGI-055** | card not accepted as an ID | card size, position, white margins, card clipping, source padding, actual tile dims (384×256), emulator imagefile path |
| **RGI-045** | accepted + OCR ran, did not reach DOPA | printed citizen ID, Thai/English names, DOB, OCR readability, **onboarding profile alignment**. Do NOT auto-call this a backend defect. |
| **DOPA_INFORMATION** | detected → extracted → matched → DOPA form | (success — no action) |
| **GOD/COO/FSI** | backend/service error | capture minimum evidence, kill app, fresh happy flow; do not root-cause in this workflow |

## Matching Requirements

Reaching `DOPA_INFORMATION` depends on **both**:
- **A.** OCR geometry/layout acceptance, AND
- **B.** OCR-extracted identity data matching the profile used earlier in onboarding.

Therefore the onboarding profile/testdata **must correspond** to the printed mock identity
fields (unless the environment intentionally mocks/bypasses a comparison). Do not assume any
field is always ignored. Known mocked/bypassed fields are recorded separately (e.g. laser ID
may be mocked/bypassed; OTP uses the configured mock value; address may be completed on a
later page) — do **not** modify those values here.

## Known Limitations

- **Trials:** each successful position has **n=1 observed fresh trial**. Deterministic success
  is **not** proven. The imagefile-camera on-device detector showed run-to-run non-determinism
  in prior sessions (identical geometry yielded RGI-045 / RGI-055 / DOPA across runs).
- **Preview render gate:** the preview only renders large/high-contrast imagefile content; tiny
  markers don't render. The canvas→screen preview transform is a ~2.2× non-deterministic zoom/crop
  (see `reports/investigation/ocr_frame_geometry_calib/`) — but this does not affect the
  ImageCapture still that the OCR pipeline reads.
- Do **not** state the layout "always passes." Correct wording: *"The geometry reached
  DOPA_INFORMATION in the observed fresh trial."*

## Evidence References

- Preferred (179,164): `reports/investigation/layout_translate_x179_y164/REPORT.md`
- Rollback (204,204): `reports/investigation/layout_translate_minus20/REPORT.md`
- Frozen baseline (224,224): `apps/android/mock/derived/ntb_id_card_layout_frozen_baseline.png`
- Geometry/mapping investigation: `reports/investigation/ocr_frame_geometry_calib/REPORT.md`
- Machine-readable baseline: `configs/ocr/mock_id_card_baseline.yaml`
- Generator: `tools/emulator/card_geometry_optimizer.py`

## Change History

| Date | Change |
|---|---|
| 2026-07-12 | Layout investigation complete; (204,204) and (179,164) both reached DOPA_INFORMATION (n=1 each). (224,224) frozen baseline. Authoritative baseline documented. |
