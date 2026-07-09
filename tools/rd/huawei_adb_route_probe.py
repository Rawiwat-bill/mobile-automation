#!/usr/bin/env python3
# Huawei adb-only OCR-route probe (investigation only). ZERO Appium calls.
import subprocess, re, time, os, json, yaml

UDID = "48ZYD25C01422768"
EVID = "reports/investigation/huawei_adb_route/evidence"
DUMP = "/data/local/tmp/huawei_dump.xml"
os.makedirs(EVID, exist_ok=True)

def sh(cmd, timeout=30):
    return subprocess.run(cmd, shell=True, capture_output=True, text=True, timeout=timeout).stdout
def dump():
    sh(f"adb -s {UDID} shell uiautomator dump {DUMP} >/dev/null 2>&1")
    return sh(f"adb -s {UDID} shell cat {DUMP}")
def screen():
    x = dump()
    if "RVCamera" in x: return "ocr_camera"
    if "screenScanCardIntro_" in x: return "scan_card_intro"
    if "screenPDPA_" in x or "Personal data consent" in x: return "pdpa"
    if "screenProfile_" in x: return "profile"
    if "screenSignUp_" in x or "Let\u2019s start" in x or "Let's start" in x: return "signup"
    if "WebView" in x or "Terms and Conditions" in x: return "consent"
    if "screenLanding_" in x: return "landing"
    return "unknown"
def center(attr, val, xml=None):
    m = re.search(attr + r'="' + re.escape(val) + r'"[^>]*bounds="\[(\d+),(\d+)\]\[(\d+),(\d+)\]"', xml or dump())
    if not m: return None
    return ((int(m.group(1))+int(m.group(3)))//2, (int(m.group(2))+int(m.group(4)))//2)
def tap(x, y): sh(f"adb -s {UDID} shell input tap {x} {y}"); time.sleep(0.6)
def swipe(x1,y1,x2,y2,dur=400): sh(f"adb -s {UDID} shell input swipe {x1} {y1} {x2} {y2} {dur}"); time.sleep(0.4)
def keydigits(s):
    for c in s: sh(f"adb -s {UDID} shell input keyevent KEYCODE_{c}"); time.sleep(0.05)
def capture(lbl):
    sh(f"adb -s {UDID} exec-out screencap -p > {EVID}/{lbl}.png")
    with open(f"{EVID}/{lbl}.xml","w") as f: f.write(dump())

LOG=[]
def log(s,step,status,detail=""):
    LOG.append({"screen":s,"step":step,"status":status,"detail":detail}); print(f"[{s}] {step}: {status} {detail}",flush=True)
def wait_screen(target,timeout=25):
    for _ in range(timeout):
        if screen()==target: return True
        time.sleep(1)
    return False
def wait_marker(attr,val,timeout=40):
    for _ in range(timeout):
        if center(attr,val) is not None: return True
        time.sleep(1)
    return False

MONTHS={"January":1,"February":2,"March":3,"April":4,"May":5,"June":6,"July":7,"August":8,"September":9,"October":10,"November":11,"December":12}
def to_n(v,kind): return MONTHS[v] if kind=="month" else int(v)
def set_wheel(resid,target,kind):
    for _ in range(30):
        x=dump()
        m=re.search(r'resource-id="'+resid+r'"[^>]*content-desc="([^"]*)"[^>]*bounds="\[(\d+),(\d+)\]\[(\d+),(\d+)\]"',x)
        if not m: return "no-wheel"
        cur=m.group(1).split(",")[-1].strip()
        if cur==target: return "ok"
        x1,y1,x2,y2=int(m.group(2)),int(m.group(3)),int(m.group(4)),int(m.group(5)); cx=(x1+x2)//2; h=y2-y1
        try: cn=to_n(cur,kind); tn=to_n(target,kind)
        except: return "parse-fail:"+cur
        if abs(cn-tn)>2: top,bot=int(y1+h*0.30),int(y1+h*0.70)
        else: top,bot=int(y1+h*0.40),int(y1+h*0.60)
        if cn<tn: swipe(cx,bot,cx,top,400)
        else: swipe(cx,top,cx,bot,400)
    return "timeout"

def main():
    data=yaml.safe_load(open("testdata/onboarding/ntb.local.yaml"))
    CID=data["profile"]["citizen_id"]; DOB=data["profile"]["date_of_birth"]; MOB=data["profile"]["mobile_number"]
    p=DOB.split("-"); D_DAY,D_MON,D_YEAR=p[0],p[1],p[2]
    D_MON_NAME={v:k for k,v in MONTHS.items()}[int(D_MON)]
    sh(f"adb -s {UDID} shell am force-stop com.bangkokbank.blue.dev")
    sh(f"adb -s {UDID} shell pm clear com.bangkokbank.blue.dev")
    sh(f"adb -s {UDID} shell am start -n com.bangkokbank.blue.dev/com.bangkokbank.blue.MainActivity")
    if not wait_marker("resource-id","screenLanding_skipButton",45):
        log("landing","load","FAIL","skipButton never appeared (RN load)"); return finish()
    capture("01_landing")
    c=center("resource-id","screenLanding_skipButton")
    if c: tap(*c); log("landing","tap_skip","ok",str(c))
    else: log("landing","tap_skip","FAIL","skipButton not found"); return finish()
    if not wait_marker("resource-id","screenLanding_buttonReady",15):
        log("landing","ready_after_skip","FAIL","buttonReady not found"); return finish()
    c=center("resource-id","screenLanding_buttonReady"); tap(*c); log("landing","tap_ready","ok",str(c))
    if not wait_screen("consent",25): log("consent","wait","FAIL",screen()); return finish()
    capture("02_consent_before")
    time.sleep(7)  # let the freshly-loaded Consent WebView terms render before flinging
    for i in range(25):
        swipe(360,1300,360,300,45)
    c=center("content-desc","Accept")
    if c: tap(*c); log("consent","tap_accept","ok",str(c))
    else: log("consent","tap_accept","FAIL","Accept not found"); return finish()
    capture("02_consent_after")
    if not wait_screen("profile",30): log("profile","wait","FAIL",screen()); return finish()
    capture("03_profile_before")
    # citizen id
    c=center("resource-id","cid")
    if c:
        tap(*c); time.sleep(0.4); keydigits(CID); tap(360,200)
        after=re.search(r'resource-id="cid"[^>]*?text="([^"]*)"',dump())
        log("profile","citizen_keycodes","ok" if after and len(re.sub(r"\D","",after.group(1)))==13 else "CHECK",f"text={after.group(1) if after else None}")
    else: log("profile","citizen","FAIL","cid not found")
    # DOB
    c=center("resource-id","screenProfile_textInputDob-container")
    if c:
        tap(*c); time.sleep(1)
        ry=set_wheel("screenProfile_calendarDatePicker-yearScroll",D_YEAR,"number")
        rm=set_wheel("screenProfile_calendarDatePicker-monthScroll",D_MON_NAME,"month")
        rd=set_wheel("screenProfile_calendarDatePicker-dateScroll",D_DAY,"number")
        d=center("content-desc","Done")
        if d: tap(*d)
        log("profile","dob_picker",f"y={ry}/m={rm}/d={rd}",f"done={bool(d)}")
        time.sleep(1)
    else: log("profile","dob","FAIL","dob container not found")
    # mobile
    c=center("resource-id","screenProfile_textInputMobileNumber")
    if c:
        tap(*c); time.sleep(0.4); keydigits(MOB); tap(360,200)
        after=re.search(r'resource-id="screenProfile_textInputMobileNumber"[^>]*?text="([^"]*)"',dump())
        log("profile","mobile_keycodes","ok" if after and len(re.sub(r"\D","",after.group(1)))==10 else "CHECK",f"len={len(re.sub(r'\\D','',after.group(1))) if after else 0}")
    else: log("profile","mobile","FAIL","mobile not found")
    capture("03_profile_after_input")
    c=center("resource-id","screenProfile_buttonNext")
    if c: tap(*c); log("profile","tap_next","ok",str(c))
    else: log("profile","tap_next","FAIL","buttonNext not found"); return finish()
    if not wait_screen("pdpa",30): log("pdpa","wait","FAIL",screen()); return finish()
    capture("04_pdpa_before")
    for i in range(16): swipe(360,1300,360,300,45)
    c=center("content-desc","Accept")
    if c: tap(*c); log("pdpa","tap_accept","ok",str(c))
    else: log("pdpa","tap_accept","FAIL","Accept not found"); return finish()
    capture("04_pdpa_after")
    if not wait_screen("signup",30): log("signup","wait","FAIL",screen()); return finish()
    capture("05_signup")
    c=center("content-desc","Let\u2019s start") or center("content-desc","Let's start")
    if c: tap(*c); log("signup","tap_lets_start","ok",str(c))
    else: log("signup","tap_lets_start","FAIL","not found"); return finish()
    if not wait_screen("scan_card_intro",30): log("scan_card_intro","wait","FAIL",screen()); return finish()
    capture("06_scan_card_intro")
    c=center("resource-id","screenScanCardIntro_buttonReady")
    if c: tap(*c); log("scan_card_intro","tap_next","ok",str(c))
    else: log("scan_card_intro","tap_next","FAIL","not found"); return finish()
    if wait_screen("ocr_camera",30):
        capture("07_ocr_camera"); log("ocr_camera","reached","OK","adb-only route succeeded to OCR Camera")
    else: log("ocr_camera","wait","FAIL",screen())
    finish()

def finish():
    os.makedirs("reports/investigation/huawei_adb_route",exist_ok=True)
    open("reports/investigation/huawei_adb_route/route_status.json","w").write(json.dumps(LOG,indent=2))
    print("\n=== PER-SCREEN SUMMARY ===")
    for e in LOG: print(f"{e['screen']:16} {e['step']:24} {e['status']}")
    return None

if __name__=="__main__":
    main()
