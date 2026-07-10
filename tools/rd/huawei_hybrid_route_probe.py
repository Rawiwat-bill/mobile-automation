#!/usr/bin/env python3
# Huawei full-adb route probe (investigation). adb-only, including CID+Mobile via focus + input text.
# Goal: Landing -> Consent -> Profile -> [adb CID+Mobile] -> DOB -> Next -> PDPA -> SignUp -> ScanCard -> OCR Camera.
import subprocess, re, time, os, json, sys, yaml

UDID="48ZYD25C01422768"
EVID="reports/investigation/huawei_hybrid_route/evidence"
DUMP="/data/local/tmp/hh.xml"; os.makedirs(EVID,exist_ok=True)

def sh(c,t=30): return subprocess.run(c,shell=True,capture_output=True,text=True,timeout=t).stdout
def dump():
    sh(f"adb -s {UDID} shell uiautomator dump {DUMP} >/dev/null 2>&1"); return sh(f"adb -s {UDID} shell cat {DUMP}")
def screen():
    x=dump()
    for m,t in [("RVCamera","ocr_camera"),("screenScanCardIntro_","scan_card_intro"),("screenPDPA_","pdpa"),("Personal data consent","pdpa"),("screenProfile_","profile"),("screenSignUp_","signup"),("Let\u2019s start","signup"),("Let's start","signup"),("WebView","consent"),("Terms and Conditions","consent"),("screenLanding_","landing")]:
        if m in x: return t
    return "unknown"
def center(attr,val,xml=None):
    m=re.search(r'<node[^>]*'+attr+r'="'+re.escape(val)+r'"[^>]*>',xml or dump())
    if not m: return None
    b=re.search(r'bounds="\[(\d+),(\d+)\]\[(\d+),(\d+)\]"',m.group(0))
    return ((int(b.group(1))+int(b.group(3)))//2,(int(b.group(2))+int(b.group(4)))//2) if b else None
def attr(attr,val,name,xml=None):
    # order-independent: uiautomator emits text BEFORE resource-id, so anchor on the
    # whole node opening tag then read the target attr anywhere inside it.
    m=re.search(r'<node[^>]*'+attr+r'="'+re.escape(val)+r'"[^>]*>',xml or dump())
    if not m: return None
    mm=re.search(name+r'="([^"]*)"',m.group(0)); return mm.group(1) if mm else None
def tap(x,y): sh(f"adb -s {UDID} shell input tap {x} {y}"); time.sleep(0.6)
def swipe(a,b,c,d,dur): sh(f"adb -s {UDID} shell input swipe {a} {b} {c} {d} {dur}"); time.sleep(0.35)
def capture(l):
    sh(f"adb -s {UDID} exec-out screencap -p > {EVID}/{l}.png"); open(f"{EVID}/{l}.xml","w").write(dump())
def wait_screen(t,tmo=30):
    for _ in range(tmo):
        if screen()==t: return True
        time.sleep(1)
    return False
def digits(resid):
    # digit count of REAL input only. RN reports the placeholder as `text` when the field is empty
    # (e.g. "Enter 13-digit Citizen ID number"); placeholder/hint text contains letters -> 0 real digits.
    t=attr("resource-id",resid,"text") or ""
    if re.search(r'[a-zA-Z]',t): return 0
    return len(re.sub(r"\D","",t))
LOG=[]
def log(s,step,status,detail=""):
    LOG.append({"screen":s,"step":step,"status":status,"detail":detail}); print(f"[{s}] {step}: {status} {detail}",flush=True)

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
        except: return "parse-fail"
        top,bot=(int(y1+h*0.30),int(y1+h*0.70)) if abs(cn-tn)>2 else (int(y1+h*0.40),int(y1+h*0.60))
        swipe(cx,bot,cx,top,400) if cn<tn else swipe(cx,top,cx,bot,400)
    return "timeout"

def adb_input_field(resid, value, label, expect):
    # Certified adb text-entry: resolve center -> tap -> verify focus -> input text -> verify digits.
    # Order-independent node parsing (center()/attr() parse the full <node> first). Never logs raw value.
    c=center("resource-id",resid)
    if not c:
        log("profile",f"{label}_focus","FAIL","field not found"); capture(f"FAIL_{label}_node"); return False
    tap(*c)
    ok=False; t0=time.time()
    while time.time()-t0<10:
        if attr("resource-id",resid,"focused")=="true": ok=True; break
        time.sleep(0.5)
    log("profile",f"{label}_focus",str(ok).lower())
    if not ok:
        capture(f"FAIL_{label}_focus"); return False
    if digits(resid)>0:  # populated with a real prior value (placeholder/empty -> 0 -> skip)
        n=digits(resid)
        for _ in range(n+8):  # DEL covers digits + formatting separators; extra DELs are no-ops. (SELECT_ALL unreliable on RN/EMUI)
            sh(f"adb -s {UDID} shell input keyevent 67"); time.sleep(0.05)
        time.sleep(0.4)
        cleared=digits(resid)==0
        log("profile",f"{label}_cleared",str(cleared).lower())
        if not cleared:
            capture(f"FAIL_{label}_clear"); return False  # fail fast: clear did not empty the field
    sh(f"adb -s {UDID} shell input text {value}")
    n=0; t0=time.time()
    while time.time()-t0<15:
        n=digits(resid)
        if n==expect: break
        time.sleep(0.5)
    log("profile",f"{label}_digits",str(n))
    if n!=expect:
        capture(f"FAIL_{label}_digits"); return False  # exact-count verification (no lenient >=)
    return True

def main():
    prof=yaml.safe_load(open("testdata/onboarding/ntb.local.yaml"))["profile"]
    CID=re.sub(r"\D","",prof["citizen_id"]); MOB=re.sub(r"\D","",prof["mobile_number"])
    dob=prof["date_of_birth"]; p=dob.split("-"); DAY,MON,YEAR=p[0],p[1],p[2]; MONNAME={v:k for k,v in MONTHS.items()}[int(MON)]
    sh(f"adb -s {UDID} shell am force-stop com.bangkokbank.blue.dev")
    sh(f"adb -s {UDID} shell pm clear com.bangkokbank.blue.dev")
    sh(f"adb -s {UDID} shell am start -n com.bangkokbank.blue.dev/com.bangkokbank.blue.MainActivity")
    for _ in range(45):
        if center("resource-id","screenLanding_skipButton"): break
        time.sleep(1)
    capture("01_landing"); tap(*center("resource-id","screenLanding_skipButton")); log("landing","tap_skip","ok")
    for _ in range(15):
        if center("resource-id","screenLanding_buttonReady"): break
        time.sleep(1)
    tap(*center("resource-id","screenLanding_buttonReady")); log("landing","tap_ready","ok")
    if not wait_screen("consent",25): return finish("consent not reached: "+screen())
    capture("02_consent_before"); time.sleep(7)
    for _ in range(25): swipe(360,1300,360,300,45)
    tap(*center("content-desc","Accept")); log("consent","tap_accept","ok"); capture("02_consent_after")
    if not wait_screen("profile",30): return finish("profile not reached: "+screen())
    capture("03_profile_before")
    print("\n>>> ADB PROFILE INPUT: CID focused and populated automatically; Mobile focused and populated automatically.",flush=True)
    if not adb_input_field("cid", CID, "cid", 13):
        return finish("CID adb-input failed (focus not confirmed within 10s or digits < 13)")
    if not adb_input_field("screenProfile_textInputMobileNumber", MOB, "mobile", 10):
        return finish("Mobile adb-input failed (focus not confirmed within 10s or digits < 10)")
    capture("03_profile_after_adb_input")
    sh(f"adb -s {UDID} shell input keyevent KEYCODE_BACK"); time.sleep(1)  # dismiss keyboard
    # ---- DOB picker (adb) ----
    c=center("resource-id","screenProfile_textInputDob-container")
    if c:
        tap(*c); time.sleep(1)
        ry=set_wheel("screenProfile_calendarDatePicker-yearScroll",YEAR,"number")
        rm=set_wheel("screenProfile_calendarDatePicker-monthScroll",MONNAME,"month")
        rd=set_wheel("screenProfile_calendarDatePicker-dateScroll",DAY,"number")
        d=center("content-desc","Done")
        if d: tap(*d)
        log("profile","dob_picker",f"y={ry}/m={rm}/d={rd}",f"done={bool(d)}"); time.sleep(1)
    else: return finish("dob container not found")
    capture("03_profile_after_dob")
    # wait for Next enabled, then tap
    enabled=False
    for _ in range(20):
        if attr("resource-id","screenProfile_buttonNext","enabled")=="true": enabled=True; break
        time.sleep(1)
    c=center("resource-id","screenProfile_buttonNext")
    if c and enabled:
        tap(*c); log("profile","tap_next","ok",f"enabled={enabled}")
    else:
        return finish(f"profile Next not enabled (enabled={attr('resource-id','screenProfile_buttonNext','enabled')})")
    # ---- PDPA ----
    if not wait_screen("pdpa",30): return finish("pdpa not reached: "+screen())
    capture("04_pdpa_before")
    for _ in range(16): swipe(360,1300,360,300,45)
    c=center("content-desc","Accept")
    if c: tap(*c); log("pdpa","tap_accept","ok"); capture("04_pdpa_after")
    else: return finish("pdpa Accept not found")
    # ---- SignUp ----
    if not wait_screen("signup",30): return finish("signup not reached: "+screen())
    capture("05_signup")
    c=center("content-desc","Let\u2019s start") or center("content-desc","Let's start")
    if c: tap(*c); log("signup","tap_lets_start","ok")
    else: return finish("signup Let's start not found")
    # ---- ScanCardIntro ----
    if not wait_screen("scan_card_intro",30): return finish("scan not reached: "+screen())
    capture("06_scan_card_intro")
    c=center("resource-id","screenScanCardIntro_buttonReady")
    if c: tap(*c); log("scan_card_intro","tap_next","ok")
    else: return finish("scan next not found")
    # ---- OCR Camera ----
    if not wait_screen("ocr_camera",30):
        return finish("ocr_camera not reached: "+screen())
    capture("07_ocr_camera"); log("ocr_camera","reached","OK","Huawei hybrid route reached OCR Camera")
    if os.environ.get("STOP_AT_OCR_CAMERA")=="1":
        return finish("SMOKE STOP: reached OCR Camera (STOP_AT_OCR_CAMERA=1; OCR capture skipped)")
    # ---- OCR RUNTIME leg (adb-only) ----
    print("\n>>> OCR RUNTIME: tester, hold the ID card in front of the camera. Probe taps 'Take Photo' in 8s.",flush=True)
    time.sleep(8)
    # dismiss camera permission if present (before + after tapping capture)
    for btn in ["permission_allow_button","permission_allow_foreground_only_button"]:
        pc=center("resource-id",btn)
        if pc: tap(*pc); print("  dismissed permission "+btn,flush=True); break
    tp=center("content-desc","Take photo")
    if not tp:
        return finish("OCR Camera: 'Take photo' button not found")
    tap(*tp); log("ocr_runtime","tap_take_photo","sent",str(tp)); time.sleep(2)
    for btn in ["permission_allow_button","permission_allow_foreground_only_button"]:
        pc=center("resource-id",btn)
        if pc: tap(*pc); print("  dismissed permission (post-tap) "+btn,flush=True); break
    # classify OCR result: DOPA / RGI_055 / OCR_ERROR / NO_CAPTURE
    result="NO_CAPTURE"; t0=time.time()
    while time.time()-t0 < 120:
        x=dump()
        if "screenDopaInformation_" in x: result="DOPA_INFORMATION"; break
        if "RGI-" in x: result="RGI_055"; break
        if "GOD-" in x or "not available" in x: result="OCR_ERROR"; break
        if "screenScanCardIntro_" in x: result="NO_CAPTURE"; break
        time.sleep(2)
    capture(f"08_ocr_result_{result}"); log("ocr_runtime","result",result,f"elapsed={round(time.time()-t0)}s")
    if result=="DOPA_INFORMATION":
        capture("08_dopa_information")
        # visible elements summary on DOPA
        elems=re.findall(r'(resource-id|content-desc|text)="([^"]{2,40})"', dump())
        log("dopa_information","reached","OK",f"visible_markers={len(elems)}; sample={[e[1] for e in elems[:8]]}")
        finish("ROUTE_COMPLETE: reached DOPA Information (STOP before DOPA Next)")
    else:
        finish(f"OCR runtime result={result} — DOPA not reached (no card / OCR error / backend). Stopped at OCR Camera boundary.")

def finish(msg):
    open("reports/investigation/huawei_hybrid_route/route_status.json","w").write(json.dumps(LOG,indent=2))
    print("\n>>> RESULT:",msg,flush=True)
    print("=== PER-SCREEN SUMMARY ===")
    for e in LOG: print(f"{e['screen']:16} {e['step']:22} {e['status']}")
    return None

if __name__=="__main__": main()
