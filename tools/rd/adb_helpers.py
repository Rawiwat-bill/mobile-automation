import subprocess, re, sys, time

def sh(cmd, timeout=30):
    r = subprocess.run(cmd, shell=True, capture_output=True, text=True, timeout=timeout)
    return r.stdout

def _dump(udid):
    sh(f"adb -s {udid} shell uiautomator dump /data/local/tmp/rd_dump.xml >/dev/null 2>&1")
    return sh(f"adb -s {udid} shell cat /data/local/tmp/rd_dump.xml")

def screen(udid):
    x = _dump(udid)
    if "RVCamera" in x: return "ocr_camera"
    if "screenScanCardIntro_" in x: return "scan_card_intro"
    if "screenPDPA_" in x: return "pdpa"
    if "screenProfile_" in x: return "profile"
    if "screenDopaInformation_" in x: return "dopa"
    if "WebView" in x or "Terms and Conditions" in x: return "consent"
    if "screenLanding_" in x: return "landing"
    if "Let\u2019s start" in x or "Let's start" in x: return "signup"
    return "unknown"

def has(udid, marker):
    return "1" if marker in _dump(udid) else "0"

def _node_center(xml, attr, val):
    m = re.search(attr + r'="' + re.escape(val) + r'"[^>]*bounds="\[(\d+),(\d+)\]\[(\d+),(\d+)\]"', xml)
    if not m: return None
    return ((int(m.group(1)) + int(m.group(3))) // 2, (int(m.group(2)) + int(m.group(4))) // 2)

def tap_desc(udid, desc):
    c = _node_center(_dump(udid), "content-desc", desc)
    if not c: return "0"
    sh(f"adb -s {udid} shell input tap {c[0]} {c[1]}")
    return "1"

def tap_resid(udid, resid):
    c = _node_center(_dump(udid), "resource-id", resid)
    if not c: return "0"
    sh(f"adb -s {udid} shell input tap {c[0]} {c[1]}")
    return "1"

def capture(udid, png, xml_path, activity):
    sh(f"adb -s {udid} exec-out screencap -p > {png}")
    with open(xml_path, "w") as f: f.write(_dump(udid))
    with open(activity, "w") as f: f.write(sh(f"adb -s {udid} shell dumpsys window"))

def consent_pass(udid, max_swipe=20):
    for _ in range(max_swipe):
        sh(f"adb -s {udid} shell input swipe 360 1300 360 300 300")
        time.sleep(0.25)
        if "I have read and understood" in _dump(udid):
            break
    time.sleep(0.5)
    ok = tap_desc(udid, "Accept")
    time.sleep(3)
    return f"accept_tapped={ok} profile_reached={'1' if screen(udid)=='profile' else '0'}"

if __name__ == "__main__":
    cmd, udid = sys.argv[1], sys.argv[2]; rest = sys.argv[3:]
    if cmd == "screen": print(screen(udid))
    elif cmd == "has": print(has(udid, rest[0]))
    elif cmd == "tap_desc": print(tap_desc(udid, rest[0]))
    elif cmd == "tap_resid": print(tap_resid(udid, rest[0]))
    elif cmd == "consent_pass": print(consent_pass(udid))
    elif cmd == "capture": capture(udid, rest[0], rest[1], rest[2]); print("1")
