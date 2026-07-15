#!/usr/bin/env python3
# Emulator OCR tap + classify helper. Read-only UI dump + adb tap. No PII.
import subprocess, sys, re, json

SERIAL = sys.argv[1] if len(sys.argv) > 1 else "emulator-5554"
ACT = sys.argv[2] if len(sys.argv) > 2 else "tap"


def sh(*a):
    return subprocess.run(a, capture_output=True, text=True, timeout=30).stdout


def dump_ui():
    sh("adb", "-s", SERIAL, "shell", "uiautomator", "dump", "/sdcard/u.xml")
    return sh("adb", "-s", SERIAL, "exec-out", "cat", "/sdcard/u.xml")


def clickables(s):
    out = []
    for m in re.finditer(r'<node\b[^>]*?>', s):
        n = m.group(0)
        if 'clickable="true"' not in n:
            continue
        b = re.search(r'bounds="\[(\d+),(\d+)\]\[(\d+),(\d+)\]"', n)
        cd = re.search(r'content-desc="([^"]*)"', n)
        if not b:
            continue
        x1, y1, x2, y2 = map(int, b.groups())
        out.append(dict(cx=(x1+x2)//2, cy=(y1+y2)//2, cd=cd.group(1) if cd else "",
                        x1=x1, y1=y1, x2=x2, y2=y2))
    return out


def tap_takephoto():
    s = dump_ui()
    cl = clickables(s)
    # Take Photo = clickable, not DBG (cd=Open debug panel, x>900), not back (y<300), mid-lower screen
    cand = [c for c in cl
            if c["cd"] != "Open debug panel"
            and c["cy"] > 1300
            and c["cx"] < 850]
    if not cand:
        print(json.dumps({"ok": False, "reason": "no takephoto button found",
                          "clickables": cl}))
        return
    # pick the one closest to horizontal center, lowest (the big round button)
    tgt = sorted(cand, key=lambda c: (-c["cy"], abs(c["cx"]-540)))[0]
    subprocess.run(["adb", "-s", SERIAL, "shell", "input", "tap",
                    str(tgt["cx"]), str(tgt["cy"])], timeout=15)
    print(json.dumps({"ok": True, "x": tgt["cx"], "y": tgt["cy"],
                      "bounds": [tgt["x1"], tgt["y1"], tgt["x2"], tgt["y2"]],
                      "all": cl}))


def classify():
    s = dump_ui()
    texts = " ".join(re.findall(r'(?:text|content-desc)="([^"]+)"', s)).lower()
    cls = "UNKNOWN"
    if "god-016" in texts or "god016" in texts:
        cls = "GOD_016"
    elif "dopa" in texts or "information" in texts and "dopa" in texts:
        cls = "DOPA_INFORMATION"
    elif "rg1" in texts or "rgi" in texts or "055" in texts:
        cls = "RGI_055"
    elif "service is not available" in texts or "try again later" in texts:
        # generic service error — check help code
        m = re.search(r'(god-\d+)', " ".join(re.findall(r'(?:text|content-desc)="([^"]+)"', s)))
        cls = ("GOD_" + m.group(1).split("-")[1]) if m else "OTHER_OCR_ERROR"
    print(json.dumps({"classification": cls, "texts_snippet": texts[:300]}))


if ACT == "tap":
    tap_takephoto()
elif ACT == "classify":
    classify()
