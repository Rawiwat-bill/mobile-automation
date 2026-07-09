#!/usr/bin/env python3
# Test: can Appium Press Keycode (instrumentation inject, NO Find Element) populate RN TextInput on Huawei?
# Focus via adb tap, type via Appium press_keycode. Then adb DOB, check Profile Next enabled.
import subprocess, re, time, yaml
from appium import webdriver
from appium.options.android import UiAutomator2Options
UDID="48ZYD25C01422768"; DUMP="/data/local/tmp/hk.xml"
def sh(c,t=30): return subprocess.run(c,shell=True,capture_output=True,text=True,timeout=t).stdout
def dump():
    sh(f"adb -s {UDID} shell uiautomator dump {DUMP} >/dev/null 2>&1"); return sh(f"adb -s {UDID} shell cat {DUMP}")
def screen():
    x=dump()
    for m,t in [("RVCamera","ocr"),("screenScanCardIntro_","scan"),("screenPDPA_","pdpa"),("Personal data consent","pdpa"),("screenProfile_","profile"),("WebView","consent"),("Terms and Conditions","consent"),("screenLanding_","landing")]:
        if m in x: return t
    return "unknown"
def center(a,v):
    m=re.search(a+r'="'+re.escape(v)+r'"[^>]*bounds="\[(\d+),(\d+)\]\[(\d+),(\d+)\]"',dump()); return ((int(m.group(1))+int(m.group(3)))//2,(int(m.group(2))+int(m.group(4)))//2) if m else None
def attr(a,v,n):
    m=re.search(a+r'="'+re.escape(v)+r'"[^>]*'+n+r'="([^"]*)"',dump()); return m.group(1) if m else None
def tap(x,y): sh(f"adb -s {UDID} shell input tap {x} {y}"); time.sleep(0.6)
def swipe(x1,y1,x2,y2,dur):
    sh(f"adb -s {UDID} shell input swipe {x1} {y1} {x2} {y2} {dur}"); time.sleep(0.35)
def wait(t,tmo=30):
    for _ in range(tmo):
        if screen()==t: return True
        time.sleep(1)
    return False
KC={'0':7,'1':8,'2':9,'3':10,'4':11,'5':12,'6':13,'7':14,'8':15,'9':16}
d=yaml.safe_load(open("testdata/onboarding/ntb.local.yaml"))
CID=d["profile"]["citizen_id"]; MOB=d["profile"]["mobile_number"]; DOB=d["profile"]["date_of_birth"]
p=DOB.split("-"); DAY,MON,YEAR=p[0],p[1],p[2]; MONNAME={v:k for k,v in {"January":1,"February":2,"March":3,"April":4,"May":5,"June":6,"July":7,"August":8,"September":9,"October":10,"November":11,"December":12}.items()}[int(MON)]
# drive to Profile
sh(f"adb -s {UDID} shell am force-stop com.bangkokbank.blue.dev"); sh(f"adb -s {UDID} shell pm clear com.bangkokbank.blue.dev")
sh(f"adb -s {UDID} shell am start -n com.bangkokbank.blue.dev/com.bangkokbank.blue.MainActivity")
for _ in range(45):
    if center("resource-id","screenLanding_skipButton"): break
    time.sleep(1)
tap(*center("resource-id","screenLanding_skipButton"))
for _ in range(15):
    if center("resource-id","screenLanding_buttonReady"): break
    time.sleep(1)
tap(*center("resource-id","screenLanding_buttonReady"))
assert wait("consent",25); time.sleep(7)
for _ in range(25): swipe(360,1300,360,300,45)
tap(*center("content-desc","Accept"))
assert wait("profile",30)
print("on Profile. Creating Appium session (NO Find Element)...")
o=UiAutomator2Options(); o.platform_name="Android"; o.automation_name="UiAutomator2"; o.udid=UDID; o.device_name="MGA_LX3"
o.platform_version="10"; o.app_package="com.bangkokbank.blue.dev"; o.app_activity="com.bangkokbank.blue.MainActivity"
o.no_reset=True; o.auto_grant_permissions=True; o.new_command_timeout=30
drv=webdriver.Remote("http://127.0.0.1:4723",options=o); print("session OK")
def type_digits(val):
    for ch in re.sub(r"\D","",val): drv.press_keycode(KC[ch]); time.sleep(0.04)
# CID via adb-focus + Appium press_keycode
c=center("resource-id","cid"); tap(*c); time.sleep(0.5); type_digits(CID); print("CID keycodes sent")
tap(360,200); time.sleep(0.4)  # blur
# Mobile
c=center("resource-id","screenProfile_textInputMobileNumber"); tap(*c); time.sleep(0.5); type_digits(MOB); print("Mobile keycodes sent")
tap(360,200); time.sleep(0.4)
drv.quit(); print("session closed"); time.sleep(1)
print("dump nodes after session:", dump().count("<node"))
# DOB picker (adb)
c=center("resource-id","screenProfile_textInputDob-container")
def set_wheel(resid,target,kind):
    M={"January":1,"February":2,"March":3,"April":4,"May":5,"June":6,"July":7,"August":8,"September":9,"October":10,"November":11,"December":12}
    for _ in range(30):
        x=dump(); m=re.search(r'resource-id="'+resid+r'"[^>]*content-desc="([^"]*)"[^>]*bounds="\[(\d+),(\d+)\]\[(\d+),(\d+)\]"',x)
        if not m: return "no-wheel"
        cur=m.group(1).split(",")[-1].strip()
        if cur==target: return "ok"
        x1,y1,x2,y2=int(m.group(2)),int(m.group(3)),int(m.group(4)),int(m.group(5)); cx=(x1+x2)//2; h=y2-y1
        cn=(M[cur] if kind=="month" else int(cur)); tn=(M[target] if kind=="month" else int(target))
        top,bot=(int(y1+h*0.30),int(y1+h*0.70)) if abs(cn-tn)>2 else (int(y1+h*0.40),int(y1+h*0.60))
        (swipe(cx,bot,cx,top,400) if cn<tn else swipe(cx,top,cx,bot,400))
    return "timeout"
tap(*c); time.sleep(1)
print("DOB:", set_wheel("screenProfile_calendarDatePicker-yearScroll",YEAR,"number"), set_wheel("screenProfile_calendarDatePicker-monthScroll",MONNAME,"month"), set_wheel("screenProfile_calendarDatePicker-dateScroll",DAY,"number"))
d=center("content-desc","Done");
if d: tap(*d)
time.sleep(1)
en=attr("resource-id","screenProfile_buttonNext","enabled")
print("=== RESULT: screenProfile_buttonNext enabled =", en)
