#!/usr/bin/env python3
# Decisive test: drive to Profile (adb), set clipboard via Appium (no Find Element), paste into RN TextInput.
import subprocess, time, yaml
from appium import webdriver
from appium.options.android import UiAutomator2Options
UDID="48ZYD25C01422768"; DUMP="/data/local/tmp/hc.xml"
def sh(c,t=30): return subprocess.run(c,shell=True,capture_output=True,text=True,timeout=t).stdout
def dump():
    sh(f"adb -s {UDID} shell uiautomator dump {DUMP} >/dev/null 2>&1"); return sh(f"adb -s {UDID} shell cat {DUMP}")
def screen():
    x=dump()
    for m,t in [("RVCamera","ocr_camera"),("screenScanCardIntro_","scan"),("screenPDPA_","pdpa"),("Personal data consent","pdpa"),("screenProfile_","profile"),("screenLanding_","landing"),("WebView","consent"),("Terms and Conditions","consent")]:
        if m in x: return t
    return "unknown"
def center(attr,val):
    import re
    m=re.search(attr+r'="'+re.escape(val)+r'"[^>]*bounds="\[(\d+),(\d+)\]\[(\d+),(\d+)\]"',dump())
    return ((int(m.group(1))+int(m.group(3)))//2,(int(m.group(2))+int(m.group(4)))//2) if m else None
def tap(x,y): sh(f"adb -s {UDID} shell input tap {x} {y}"); time.sleep(0.6)
def swipe(a,b,c,d,dur): sh(f"adb -s {UDID} shell input swipe {a} {b} {c} {d} {dur}"); time.sleep(0.35)
def wait(t,tmo=30):
    for _ in range(tmo):
        if screen()==t: return True
        time.sleep(1)
    return False

data=yaml.safe_load(open("testdata/onboarding/ntb.local.yaml"))
CID=data["profile"]["citizen_id"]; MOB=data["profile"]["mobile_number"]
print("test values loaded (masked)")
# drive to Profile
sh(f"adb -s {UDID} shell am force-stop com.bangkokbank.blue.dev")
sh(f"adb -s {UDID} shell pm clear com.bangkokbank.blue.dev")
sh(f"adb -s {UDID} shell am start -n com.bangkokbank.blue.dev/com.bangkokbank.blue.MainActivity")
for _ in range(45):
    if center("resource-id","screenLanding_skipButton"): break
    time.sleep(1)
tap(*center("resource-id","screenLanding_skipButton"))
for _ in range(15):
    if center("resource-id","screenLanding_buttonReady"): break
    time.sleep(1)
tap(*center("resource-id","screenLanding_buttonReady"))
assert wait("consent",25), "consent not reached"
time.sleep(7)
for _ in range(25): swipe(360,1300,360,300,45)
tap(*center("content-desc","Accept"))
assert wait("profile",30), "profile not reached"
print("on Profile. cid bounds:", )
import re
m=re.search(r'resource-id="cid"[^>]*bounds="\[(\d+),(\d+)\]\[(\d+),(\d+)\]"',dump())
print("cid bounds raw:", m.group(0)[-40:] if m else None)
# set clipboard via Appium (no Find Element)
o=UiAutomator2Options(); o.platform_name="Android"; o.automation_name="UiAutomator2"; o.udid=UDID
o.device_name="MGA-LX3"; o.platform_version="10"; o.app_package="com.bangkokbank.blue.dev"
o.app_activity="com.bangkokbank.blue.MainActivity"; o.no_reset=True; o.auto_grant_permissions=True; o.new_command_timeout=30
drv=webdriver.Remote("http://127.0.0.1:4723",options=o)
drv.set_clipboard_text(CID); rb=drv.get_clipboard_text(); drv.quit()
print("clipboard readback:", (rb[:6]+"...") if rb else None)
time.sleep(1)
# ensure still on Profile after session
print("screen after appium session:", screen())
# paste into cid
c=center("resource-id","cid"); print("cid center:",c)
if c:
    tap(*c); time.sleep(0.8)
    sh(f"adb -s {UDID} shell input keyevent 279"); time.sleep(1)  # PASTE
    mm=re.search(r'resource-id="cid"[^>]*text="([^"]*)"',dump())
    val=mm.group(1) if mm else ""
    digits=re.sub(r"\D","",val)
    print("CID after paste:", (val[:4]+"...") if val else "(empty)", "digits_len:", len(digits), "MATCH" if len(digits)==13 else "NO_MATCH")
else:
    print("cid field not found after session")
