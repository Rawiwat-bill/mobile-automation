#!/usr/bin/env python3
# Resume from the CURRENT Profile state (no pm clear / re-drive). adb-inputs CID+Mobile (focus + input text),
# then adb-drives DOB -> Next -> PDPA -> SignUp -> ScanCard -> OCR Camera -> Take Photo -> DOPA (STOP).
import subprocess, re, time, os, json, sys, yaml
sys.stdout.reconfigure(line_buffering=True)
UDID="48ZYD25C01422768"; DUMP="/data/local/tmp/hr.xml"
EVID="reports/investigation/huawei_hybrid_route/evidence"; os.makedirs(EVID,exist_ok=True)
MONTHS={"January":1,"February":2,"March":3,"April":4,"May":5,"June":6,"July":7,"August":8,"September":9,"October":10,"November":11,"December":12}
_PROF=yaml.safe_load(open("testdata/onboarding/ntb.local.yaml"))["profile"]
CID=re.sub(r"\D","",_PROF["citizen_id"]); MOB=re.sub(r"\D","",_PROF["mobile_number"])
_DOB=_PROF["date_of_birth"]; _DP=_DOB.split("-"); DAY,MON,YEAR=_DP[0],_DP[1],_DP[2]; MONNAME={v:k for k,v in MONTHS.items()}[int(MON)]   # from fixture (was hardcoded 1995)
LOG=[]
def log(s,step,status,d=""): LOG.append({"screen":s,"step":step,"status":status,"detail":d}); print(f"[{s}] {step}: {status} {d}")
def sh(c,t=30): return subprocess.run(c,shell=True,capture_output=True,text=True,timeout=t).stdout
def dump(): sh(f"adb -s {UDID} shell uiautomator dump {DUMP} >/dev/null 2>&1"); return sh(f"adb -s {UDID} shell cat {DUMP}")
def screen():
    x=dump()
    for m,t in [("RVCamera","ocr_camera"),("screenScanCardIntro_","scan"),("screenPDPA_","pdpa"),("Personal data consent","pdpa"),("screenProfile_","profile"),("screenSignUp_","signup"),("Let\u2019s start","signup"),("Let's start","signup"),("screenDopaInformation_","dopa")]:
        if m in x: return t
    return "unknown"
def center(a,v):
    m=re.search(r'<node[^>]*'+a+r'="'+re.escape(v)+r'"[^>]*>',dump())
    if not m: return None
    b=re.search(r'bounds="\[(\d+),(\d+)\]\[(\d+),(\d+)\]"',m.group(0))
    return ((int(b.group(1))+int(b.group(3)))//2,(int(b.group(2))+int(b.group(4)))//2) if b else None
def attr(a,v,n):
    # order-independent: uiautomator emits text BEFORE resource-id, so anchor on the
    # whole node opening tag then read the target attr anywhere inside it.
    m=re.search(r'<node[^>]*'+a+r'="'+re.escape(v)+r'"[^>]*>',dump())
    if not m: return None
    mm=re.search(n+r'="([^"]*)"',m.group(0)); return mm.group(1) if mm else None
def digits(resid):
    # digit count of REAL input only. RN reports the placeholder as `text` when the field is empty
    # (e.g. "Enter 13-digit Citizen ID number"); placeholder/hint text contains letters -> 0 real digits.
    t=attr("resource-id",resid,"text") or ""
    if re.search(r'[a-zA-Z]',t): return 0
    return len(re.sub(r"\D","",t))
def tap(x,y): sh(f"adb -s {UDID} shell input tap {x} {y}"); time.sleep(0.6)
def swipe(x1,y1,x2,y2,dur): sh(f"adb -s {UDID} shell input swipe {x1} {y1} {x2} {y2} {dur}"); time.sleep(0.35)
def capture(l): sh(f"adb -s {UDID} exec-out screencap -p > {EVID}/{l}.png"); open(f"{EVID}/{l}.xml","w").write(dump())
def wait(t,tmo=30):
    for _ in range(tmo):
        if screen()==t: return True
        time.sleep(1)
    return False
def set_wheel(resid,target,kind):
    for _ in range(30):
        x=dump(); m=re.search(r'resource-id="'+resid+r'"[^>]*content-desc="([^"]*)"[^>]*bounds="\[(\d+),(\d+)\]\[(\d+),(\d+)\]"',x)
        if not m: return "no-wheel"
        cur=m.group(1).split(",")[-1].strip()
        if cur==target: return "ok"
        x1,y1,x2,y2=int(m.group(2)),int(m.group(3)),int(m.group(4)),int(m.group(5)); cx=(x1+x2)//2; h=y2-y1
        cn=(MONTHS[cur] if kind=="month" else int(cur)); tn=(MONTHS[target] if kind=="month" else int(target))
        top,bot=(int(y1+h*0.30),int(y1+h*0.70)) if abs(cn-tn)>2 else (int(y1+h*0.40),int(y1+h*0.60))
        (swipe(cx,bot,cx,top,400) if cn<tn else swipe(cx,top,cx,bot,400))
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
def finish(msg):
    open("reports/investigation/huawei_hybrid_route/resume_status.json","w").write(json.dumps(LOG,indent=2))
    print("\n>>> RESULT:",msg); 
    for e in LOG: print(f"{e['screen']:16} {e['step']:22} {e['status']}")

def main():
    print("current screen:",screen())
    if screen()!="profile": return finish(f"not on Profile (screen={screen()}); aborting resume")
    print("\n>>> ADB PROFILE INPUT: CID focused and populated automatically; Mobile focused and populated automatically.",flush=True)
    if not adb_input_field("cid", CID, "cid", 13):
        return finish("CID adb-input failed (focus not confirmed within 10s or digits < 13)")
    if not adb_input_field("screenProfile_textInputMobileNumber", MOB, "mobile", 10):
        return finish("Mobile adb-input failed (focus not confirmed within 10s or digits < 10)")
    sh(f"adb -s {UDID} shell input keyevent KEYCODE_BACK"); time.sleep(1)  # dismiss keyboard
    # DOB
    c=center("resource-id","screenProfile_textInputDob-container")
    if not c: return finish("dob container not found")
    tap(*c); time.sleep(1)
    log("profile","dob",f"y={set_wheel('screenProfile_calendarDatePicker-yearScroll',YEAR,'number')} m={set_wheel('screenProfile_calendarDatePicker-monthScroll',MONNAME,'month')} d={set_wheel('screenProfile_calendarDatePicker-dateScroll',DAY,'number')}")
    d=center("content-desc","Done");
    if d: tap(*d)
    time.sleep(1); capture("03_profile_after_dob")
    if attr("resource-id","screenProfile_buttonNext","enabled")!="true": return finish("Next not enabled after DOB")
    c=center("resource-id","screenProfile_buttonNext"); tap(*c); log("profile","tap_next","ok")
    if not wait("pdpa",30): return finish("pdpa not reached: "+screen())
    capture("04_pdpa_before")
    for _ in range(16): swipe(360,1300,360,300,45)
    c=center("content-desc","Accept");
    if c: tap(*c); log("pdpa","tap_accept","ok"); capture("04_pdpa_after")
    else: return finish("pdpa Accept not found")
    if not wait("signup",30): return finish("signup not reached: "+screen())
    capture("05_signup"); c=center("content-desc","Let\u2019s start") or center("content-desc","Let's start")
    if c: tap(*c); log("signup","tap_lets_start","ok")
    else: return finish("signup not found")
    if not wait("scan",30): return finish("scan not reached: "+screen())
    capture("06_scan_card_intro"); c=center("resource-id","screenScanCardIntro_buttonReady")
    if c: tap(*c); log("scan","tap_next","ok")
    else: return finish("scan next not found")
    if not wait("ocr_camera",30): return finish("ocr_camera not reached: "+screen())
    capture("07_ocr_camera"); log("ocr_camera","reached","OK")
    if os.environ.get("STOP_AT_OCR_CAMERA")=="1":
        return finish("SMOKE STOP: reached OCR Camera (STOP_AT_OCR_CAMERA=1; OCR capture skipped)")
    print("\n>>> OCR RUNTIME: hold the ID card in front of the camera. Tapping Take Photo in 8s.",flush=True); time.sleep(8)
    for btn in ["permission_allow_button","permission_allow_foreground_only_button"]:
        pc=center("resource-id",btn)
        if pc: tap(*pc); break
    tp=center("content-desc","Take photo")
    if not tp: return finish("Take Photo not found at OCR Camera")
    tap(*tp); log("ocr_runtime","tap_take_photo","sent"); time.sleep(2)
    for btn in ["permission_allow_button","permission_allow_foreground_only_button"]:
        pc=center("resource-id",btn)
        if pc: tap(*pc); break
    result="NO_CAPTURE"; t0=time.time()
    while time.time()-t0<120:
        x=dump()
        if "screenDopaInformation_" in x: result="DOPA_INFORMATION"; break
        if "RGI-" in x: result="RGI_055"; break
        if "GOD-" in x or "not available" in x: result="OCR_ERROR"; break
        if "screenScanCardIntro_" in x: result="NO_CAPTURE"; break
        time.sleep(2)
    capture(f"08_ocr_result_{result}"); log("ocr_runtime","result",result,f"elapsed={round(time.time()-t0)}s")
    if result=="DOPA_INFORMATION":
        capture("08_dopa_information")
        elems=re.findall(r'(resource-id|content-desc|text)="([^"]{2,40})"',dump())
        log("dopa","reached","OK",f"markers={len(elems)};sample={[e[1] for e in elems[:10]]}")
        finish("ROUTE_COMPLETE: reached DOPA Information (STOP before DOPA Next)")
    else:
        finish(f"OCR result={result} — DOPA not reached")

if __name__=="__main__": main()
