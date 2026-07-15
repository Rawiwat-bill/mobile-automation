#!/usr/bin/env python3
"""Card-layout optimizer for the emulator OCR canvas.

Crops external padding from a source card image, resizes it (Lanczos) preserving
aspect ratio, fits it inside a target box on a 1280x960 canvas, validates bounds,
and emits diagnostics + optional preview overlay + metadata JSON.

PIL only. Never overwrites the source.

Usage:
  python3 tools/emulator/card_geometry_optimizer.py \
    --source <img> --canvas-width 1280 --canvas-height 960 \
    --x 124 --y 133 --width 1019 --height 643 \
    --background white --resample lanczos --output <out.png> \
    [--crop-padding auto|none] [--preview-output <png>] [--metadata-output <json>] \
    [--frame-left 45 --frame-top 105 --frame-right 1222 --frame-bottom 804]
"""
# ponytail: one file, stdlib + PIL, no classes, fail fast.
import argparse, hashlib, json, sys
from PIL import Image, ImageDraw

RESAMPLE = {"lanczos": Image.LANCZOS, "bicubic": Image.BICUBIC,
            "nearest": Image.NEAREST, "box": Image.BOX}


def detect_card_bbox(img, thresh=245):
    """Bounding box of non-background (non-near-white) pixels."""
    g = img.convert("L")
    import numpy as np  # ponytail: numpy already a project dep (used elsewhere)
    a = np.array(g)
    mask = a < thresh  # non-white
    if not mask.any():
        return None
    ys, xs = np.where(mask)
    return (int(xs.min()), int(ys.min()), int(xs.max()) + 1, int(ys.max()) + 1)


def fail(msg, code=2):
    print(f"ERROR: {msg}", file=sys.stderr)
    sys.exit(code)


def main():
    ap = argparse.ArgumentParser(description="Emulator OCR card-layout optimizer")
    ap.add_argument("--source", required=True)
    ap.add_argument("--canvas-width", type=int, default=1280)
    ap.add_argument("--canvas-height", type=int, default=960)
    ap.add_argument("--x", type=int, required=True, help="target box left")
    ap.add_argument("--y", type=int, required=True, help="target box top")
    ap.add_argument("--width", type=int, required=True, help="target box width")
    ap.add_argument("--height", type=int, required=True, help="target box height")
    ap.add_argument("--background", default="white")
    ap.add_argument("--resample", default="lanczos", choices=list(RESAMPLE))
    ap.add_argument("--output", required=True)
    ap.add_argument("--crop-padding", default="auto", choices=["auto", "none"])
    ap.add_argument("--safe-clearance-pct", type=float, default=None)
    ap.add_argument("--preview-output", default=None)
    ap.add_argument("--metadata-output", default=None)
    # OCR frame (canvas coords) for preview overlay; default = current known mapping
    ap.add_argument("--frame-left", type=int, default=45)
    ap.add_argument("--frame-top", type=int, default=105)
    ap.add_argument("--frame-right", type=int, default=1222)
    ap.add_argument("--frame-bottom", type=int, default=804)
    args = ap.parse_args()

    if args.output == args.source:
        fail("output path equals source path (refusing to overwrite source)")
    for k in ("width", "height", "canvas_width", "canvas_height"):
        if getattr(args, k) <= 0:
            fail(f"invalid {k}={getattr(args, k)}")

    src = Image.open(args.source).convert("RGB")
    src_w, src_h = src.size

    # 1-2. crop external padding
    if args.crop_padding == "auto":
        bbox = detect_card_bbox(src)
        if bbox is None:
            fail("could not detect card (image is all background)")
        card = src.crop(bbox)
        card_bounds = bbox
    else:
        card = src.copy()
        card_bounds = (0, 0, src_w, src_h)
    cw, ch = card.size
    card_aspect = cw / ch

    # optional safe-clearance: shrink target box around its center
    box_w, box_h = args.width, args.height
    bx, by = args.x, args.y
    if args.safe_clearance_pct:
        k = 1 - args.safe_clearance_pct / 100.0
        cx = bx + box_w / 2; cy = by + box_h / 2
        box_w, box_h = box_w * k, box_h * k
        bx, by = cx - box_w / 2, cy - box_h / 2

    # 3-4. fit inside target box preserving aspect (contain), center inside box
    box_aspect = box_w / box_h
    scale = min(box_w / cw, box_h / ch)
    rw, rh = round(cw * scale), round(ch * scale)
    if rw <= 0 or rh <= 0:
        fail("resized card degenerate")
    resized = card.resize((rw, rh), RESAMPLE[args.resample])

    # center inside the target box
    ox = bx + (box_w - rw) / 2
    oy = by + (box_h - rh) / 2
    px, py = int(round(ox)), int(round(oy))
    final = (px, py, px + rw, py + rh)

    # 6. validate bounds
    if px < 0 or py < 0 or final[2] > args.canvas_width or final[3] > args.canvas_height:
        fail(f"card exceeds canvas: final={final} canvas={args.canvas_width}x{args.canvas_height}")
    new_aspect = rw / rh
    if card_aspect > 0 and abs(new_aspect - card_aspect) / card_aspect > 0.01:
        fail(f"aspect changed >1%: src={card_aspect:.4f} out={new_aspect:.4f}")

    # 5. paste
    canvas = Image.new("RGB", (args.canvas_width, args.canvas_height), args.background)
    canvas.paste(resized, (px, py))
    canvas.save(args.output)

    sha = hashlib.sha256(open(args.output, "rb").read()).hexdigest()

    margin_l, margin_t = px, py
    margin_r = args.canvas_width - final[2]
    margin_b = args.canvas_height - final[3]
    occ_w = rw / args.canvas_width * 100
    occ_h = rh / args.canvas_height * 100

    meta = {
        "source": args.source, "source_dimensions": [src_w, src_h],
        "crop_padding": args.crop_padding,
        "detected_card_bounds_in_source": list(card_bounds),
        "detected_card_dimensions": [cw, ch], "detected_card_aspect": round(card_aspect, 4),
        "target_box": {"x": args.x, "y": args.y, "width": args.width, "height": args.height,
                       "aspect": round(args.width / args.height, 4)},
        "box_used_after_clearance": {"x": round(bx), "y": round(by),
                                     "width": round(box_w), "height": round(box_h)},
        "resample": args.resample, "preserve_aspect": True,
        "resized_card_dimensions": [rw, rh], "resized_aspect": round(new_aspect, 4),
        "aspect_change_pct": round(abs(new_aspect - card_aspect) / card_aspect * 100, 3),
        "paste_x": px, "paste_y": py, "final_bounds": list(final),
        "margins": {"left": margin_l, "top": margin_t, "right": margin_r, "bottom": margin_b},
        "occupancy_pct": {"width": round(occ_w, 2), "height": round(occ_h, 2)},
        "canvas": [args.canvas_width, args.canvas_height],
        "output": args.output, "sha256": sha, "background": args.background,
    }

    # 7. diagnostics
    print("source_dimensions:", src_w, "x", src_h)
    print("detected_card_bounds_in_source:", card_bounds)
    print("detected_card_dimensions:", cw, "x", ch, "aspect=%.4f" % card_aspect)
    print("target_box:", args.x, args.y, args.width, args.height, "aspect=%.4f" % box_aspect)
    print("resized_card_dimensions:", rw, "x", rh, "aspect=%.4f" % new_aspect)
    print("paste_x/y:", px, py)
    print("final_bounds:", final)
    print("margins L/T/R/B:", margin_l, margin_t, margin_r, margin_b)
    print("occupancy_pct w/h: %.2f / %.2f" % (occ_w, occ_h))
    print("aspect_change_pct: %.3f" % meta["aspect_change_pct"])
    print("sha256:", sha)

    if args.metadata_output:
        json.dump(meta, open(args.metadata_output, "w"), indent=2)

    # preview overlay: canvas + frame + target box + actual card
    if args.preview_output:
        pv = canvas.copy()
        d = ImageDraw.Draw(pv)
        d.rectangle((args.frame_left, args.frame_top, args.frame_right, args.frame_bottom),
                    outline=(255, 0, 0), width=4)           # OCR frame (red)
        d.rectangle((args.x, args.y, args.x + args.width, args.y + args.height),
                    outline=(0, 150, 255), width=4)          # target box (blue)
        d.rectangle(final, outline=(0, 200, 0), width=6)     # actual card (green)
        d.text((10, 10), "red=OCR frame  blue=safe-fit box  green=actual card", (255, 255, 0))
        pv.save(args.preview_output)
        print("preview:", args.preview_output)


if __name__ == "__main__":
    main()
