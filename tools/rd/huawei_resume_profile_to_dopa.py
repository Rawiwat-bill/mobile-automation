#!/usr/bin/env python3
# Resume from the CURRENT Profile state (no pm clear / re-drive). Polls for manual CID+Mobile entry,
# then adb-drives DOB -> Next -> PDPA -> SignUp -> ScanCard -> OCR Camera -> Take Photo -> DOPA (STOP).
import subprocess, re, time, os, json, sys, yaml
sys.stdout.reconfigure(line_buffering=True)
UDID="48ZYD25C01422768"; DUMP="/data/local/tmp/hr.xml"
EVID="reports/investigation/huawei_hybrid_route/evidence"; os.makedirs(EVID,exist_ok=True)
PAUSE_TIMEOUT=int(os.environ.get("PAUSE_TIMEOUT","600"))
MONTHS={"January":1,"February":2,"March":3,"April":4,"May":5,"June":6,"July":7,"August":8,"September":9,"October":10,"November":11,"December":12}
_DOB=yaml.safe_load(open("testdata/onboarding/ntb.local.yaml"))["profile"]["date_of_birth"]
_DP=_DOB.split("-"); DAY,MON,YEAR=_DP[0],_DP[1],_DP[2]; MONNAME={v:k for k,v in MONTHS.items()}[int(MON)]   # from fixture (was hardcoded 1995)
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
    m=re.search(a+r'="'+re.escape(v)+r'"[^>]*bounds="\[(\d+),(\d+)\]\[(\d+),(\d+)\]"',dump()); return ((int(m.group(1))+int(m.group(3)))//2,(int(m.group(2))+int(m.group(4)))//2) if m else None
def attr(a,v,n):
    # order-independent: uiautomator emits text BEFORE resource-id, so anchor on the
    # whole node opening tag then read the target attr anywhere inside it.
    m=re.search(r'<node[^>]*'+a+r'="'+re.escape(v)+r'"[^>]*>',dump())
    if not m: return None
    mm=re.search(n+r'="([^"]*)"',m.group(0)); return mm.group(1) if mm else None
def digits(resid):
    t=attr("resource-id",resid,"text") or ""; return len(re.sub(r"\D","",t))
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
def finish(msg):
    open("reports/investigation/huawei_hybrid_route/resume_status.json","w").write(json.dumps(LOG,indent=2))
    print("\n>>> RESULT:",msg); 
    for e in LOG: print(f"{e['screen']:16} {e['step']:22} {e['status']}")

def main():
    print("current screen:",screen())
    if screen()!="profile": return finish(f"not on Profile (screen={screen()}); aborting resume")
    # ensure cid focused + keyboard up
    sh(f"adb -s {UDID} shell input tap 347 416"); time.sleep(1)
    print(">>> MANUAL STEP: type FULL 13-digit Citizen ID, then tap Mobile, type FULL 10-digit Mobile. (RN clears PARTIAL values on focus change — complete each field before moving.)")
    t0=time.time(); resumed=False
    while time.time()-t0<PAUSE_TIMEOUT:
        if digits("cid")>=13 and digits("screenProfile_textInputMobileNumber")>=10: resumed=True; break
        time.sleep(3)
    if not resumed: return finish(f"manual entry not detected in {PAUSE_TIMEOUT}s (cid={digits('cid')},mobile={digits('screenProfile_textInputMobileNumber')})")
    log("profile","manual_entry","RESUMED",f"dur={round(time.time()-t0)}s")
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
