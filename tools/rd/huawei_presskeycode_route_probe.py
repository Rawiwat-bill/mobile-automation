#!/usr/bin/env python3
# Huawei automated Profile text entry via Appium Press Keycode (Find-Element-free) — full route probe.
# adb for nav/focus/DOB/taps; Appium session ONLY for press_keycode (CID+Mobile). NO Find Element / Get Source / Get Element Rect.
import subprocess, re, time, os, json, yaml
from appium import webdriver
from appium.options.android import UiAutomator2Options
UDID="48ZYD25C01422768"; DUMP="/data/local/tmp/hp.xml"
EVID="reports/investigation/huawei_presskeycode_route/evidence"; os.makedirs(EVID,exist_ok=True)
import sys
sys.stdout.reconfigure(line_buffering=True)
KC={'0':7,'1':8,'2':9,'3':10,'4':11,'5':12,'6':13,'7':14,'8':15,'9':16}
MONTHS={"January":1,"February":2,"March":3,"April":4,"May":5,"June":6,"July":7,"August":8,"September":9,"October":10,"November":11,"December":12}
# Proven backend-accepted DOB per 4236bed run (testdata/onboarding/ntb.local.yaml says 1992 — flagged mismatch)
DAY,MON,YEAR="15","01","1995"; MONNAME="January"
LOG=[]
def log(s,step,status,detail=""): LOG.append({"screen":s,"step":step,"status":status,"detail":detail}); print(f"[{s}] {step}: {status} {detail}")
def sh(c,t=30): return subprocess.run(c,shell=True,capture_output=True,text=True,timeout=t).stdout
def dump():
    sh(f"adb -s {UDID} shell uiautomator dump {DUMP} >/dev/null 2>&1"); x=sh(f"adb -s {UDID} shell cat {DUMP}")
    print(f"   (dump nodes={x.count('<node>')})") if False else None
    return x
def nodes(): return dump().count("<node")
def screen():
    x=dump()
    for m,t in [("RVCamera","ocr_camera"),("screenScanCardIntro_","scan"),("screenPDPA_","pdpa"),("Personal data consent","pdpa"),("screenProfile_","profile"),("screenSignUp_","signup"),("Let\u2019s start","signup"),("Let's start","signup"),("WebView","consent"),("Terms and Conditions","consent"),("screenLanding_","landing")]:
        if m in x: return t
    return "unknown"
def center(a,v):
    m=re.search(a+r'="'+re.escape(v)+r'"[^>]*bounds="\[(\d+),(\d+)\]\[(\d+),(\d+)\]"',dump()); return ((int(m.group(1))+int(m.group(3)))//2,(int(m.group(2))+int(m.group(4)))//2) if m else None
def attr(a,v,n):
    m=re.search(a+r'="'+re.escape(v)+r'"[^>]*'+n+r'="([^"]*)"',dump()); return m.group(1) if m else None
def tap(x,y): sh(f"adb -s {UDID} shell input tap {x} {y}"); time.sleep(0.6)
def swipe(x1,y1,x2,y2,dur): sh(f"adb -s {UDID} shell input swipe {x1} {y1} {x2} {y2} {dur}"); time.sleep(0.35)
def wait(t,tmo=30):
    for _ in range(tmo):
        if screen()==t: return True
        time.sleep(1)
    return False
def capture(l):
    sh(f"adb -s {UDID} exec-out screencap -p > {EVID}/{l}.png"); open(f"{EVID}/{l}.xml","w").write(dump())
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

def main():
    d=yaml.safe_load(open("testdata/onboarding/ntb.local.yaml")); CID=d["profile"]["citizen_id"]; MOB=d["profile"]["mobile_number"]
    print(f"Using proven backend-accepted DOB {DAY}/{MON}/{YEAR} (testdata fixture = 1992 — flagged mismatch)")
    sh(f"adb -s {UDID} shell am force-stop com.bangkokbank.blue.dev"); sh(f"adb -s {UDID} shell pm clear com.bangkokbank.blue.dev")
    sh(f"adb -s {UDID} shell am start -n com.bangkokbank.blue.dev/com.bangkokbank.blue.MainActivity")
    for _ in range(45):
        if center("resource-id","screenLanding_skipButton"): break
        time.sleep(1)
    capture("01_landing"); tap(*center("resource-id","screenLanding_skipButton")); log("landing","tap_skip","ok")
    for _ in range(15):
        if center("resource-id","screenLanding_buttonReady"): break
        time.sleep(1)
    tap(*center("resource-id","screenLanding_buttonReady")); log("landing","tap_ready","ok")
    if not wait("consent",25): return finish("consent not reached")
    capture("02_consent_before"); time.sleep(7)
    for _ in range(25): swipe(360,1300,360,300,45)
    tap(*center("content-desc","Accept")); log("consent","tap_accept","ok"); capture("02_consent_after")
    if not wait("profile",30): return finish("profile not reached")
    capture("03_profile_before")
    # Pre-compute field centers from adb dump BEFORE opening the Appium session
    # (running adb uiautomator dump WHILE the session is alive opens a 2nd UiAutomation -> conflict -> instrumentation hangs).
    cid_c=center("resource-id","cid"); mob_c=center("resource-id","screenProfile_textInputMobileNumber")
    print("pre-computed centers: cid=",cid_c,"mobile=",mob_c)
    # Appium session (NO Find Element) — kept ALIVE ONLY for press_keycode; NO adb uiautomator dump during session.
    print("creating Appium session (NO Find Element, newCommandTimeout=600)...")
    o=UiAutomator2Options(); o.platform_name="Android"; o.automation_name="UiAutomator2"; o.udid=UDID; o.device_name="MGA_LX3"
    o.platform_version="10"; o.app_package="com.bangkokbank.blue.dev"; o.app_activity="com.bangkokbank.blue.MainActivity"
    o.no_reset=True; o.auto_grant_permissions=True; o.new_command_timeout=600
    drv=webdriver.Remote("http://127.0.0.1:4723",options=o); print("session OK")
    def pk_digits(val):
        for ch in re.sub(r"\D","",val): drv.press_keycode(KC[ch]); time.sleep(0.04)
    sh(f"adb -s {UDID} shell input tap {cid_c[0]} {cid_c[1]}"); time.sleep(0.5)  # raw adb focus (InputManager, no conflict)
    pk_digits(CID); sh(f"adb -s {UDID} shell input tap 360 200"); log("profile","cid_press_keycode","done")
    sh(f"adb -s {UDID} shell input tap {mob_c[0]} {mob_c[1]}"); time.sleep(0.5)
    pk_digits(MOB); sh(f"adb -s {UDID} shell input tap 360 200"); log("profile","mobile_press_keycode","done")
    drv.quit(); print("session closed immediately after keycodes")
    # DOB picker (adb)
    c=center("resource-id","screenProfile_textInputDob-container")
    tap(*c); time.sleep(1)
    ry=set_wheel("screenProfile_calendarDatePicker-yearScroll",YEAR,"number")
    rm=set_wheel("screenProfile_calendarDatePicker-monthScroll",MONNAME,"month")
    rd=set_wheel("screenProfile_calendarDatePicker-dateScroll",DAY,"number")
    dd=center("content-desc","Done");
    if dd: tap(*dd)
    log("profile","dob_picker",f"y={ry}/m={rm}/d={rd}"); time.sleep(1)
    capture("03_profile_after_fill")
    en=attr("resource-id","screenProfile_buttonNext","enabled"); log("profile","buttonNext_enabled",en)
    # Next: pure adb tap (session already closed to avoid UiAutomation conflict)
    c=center("resource-id","screenProfile_buttonNext")
    tap(*c); log("profile","tap_next_adb","sent",str(c))
    if not wait("pdpa",20): return finish("PDPA not reached after Next (screen="+screen()+")")
    capture("04_pdpa_before")
    for _ in range(16): swipe(360,1300,360,300,45)
    c=center("content-desc","Accept");
    if c: tap(*c); log("pdpa","tap_accept","ok"); capture("04_pdpa_after")
    else: return finish("pdpa Accept not found")
    if not wait("signup",30): return finish("signup not reached: "+screen())
    capture("05_signup")
    c=center("content-desc","Let\u2019s start") or center("content-desc","Let's start")
    if c: tap(*c); log("signup","tap_lets_start","ok")
    else: return finish("signup Let's start not found")
    if not wait("scan",30): return finish("scan not reached: "+screen())
    capture("06_scan_card_intro")
    c=center("resource-id","screenScanCardIntro_buttonReady")
    if c: tap(*c); log("scan","tap_next","ok")
    else: return finish("scan next not found")
    if wait("ocr_camera",30): capture("07_ocr_camera"); log("ocr_camera","reached","OK","Huawei automated route reached OCR Camera"); finish("ROUTE_COMPLETE: reached OCR Camera")
    else: finish("ocr_camera not reached: "+screen())

def finish(msg):
    open("reports/investigation/huawei_presskeycode_route/route_status.json","w").write(json.dumps(LOG,indent=2))
    print("\n>>> RESULT:",msg)
    for e in LOG: print(f"{e['screen']:16} {e['step']:22} {e['status']}")
if __name__=="__main__": main()
