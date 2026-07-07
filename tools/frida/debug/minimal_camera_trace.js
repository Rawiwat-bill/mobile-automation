// Minimal Frida Camera Trace — attach mode only
// No class enumeration (causes spawn crash)
// Only hooks Camera2 + File + Base64

Java.perform(function () {
    console.log("[TRACE] Camera trace attached");

    // 1. Camera2 CaptureCallback — frame delivery
    try {
        var CC = Java.use("android.hardware.camera2.CameraCaptureSession$CaptureCallback");
        CC.onCaptureCompleted.implementation = function (s, r, result) {
            console.log("[CAM2] onCaptureCompleted — FRAME DELIVERED");
            return this.onCaptureCompleted(s, r, result);
        };
        CC.onCaptureFailed.implementation = function (s, r, f) {
            console.log("[CAM2] onCaptureFailed");
        };
        console.log("[+] Camera2 hooked");
    } catch (e) { console.log("[-] Camera2: " + e); }

    // 2. File creation in app dirs
    try {
        var FOS = Java.use("java.io.FileOutputStream");
        FOS.$init.overload("java.io.String").implementation = function (p) {
            if (p && (p.indexOf("photo") >= 0 || p.indexOf("cache") >= 0 || p.indexOf("capture") >= 0 || p.indexOf(".jpg") >= 0)) {
                console.log("[FILE] FileOutputStream: " + p);
            }
            return this.$init(p);
        };
        console.log("[+] FileOutputStream hooked");
    } catch (e) {}

    // 3. Base64 encoding (OCR upload signal)
    try {
        var B64 = Java.use("android.util.Base64");
        B64.encodeToString.overload("[B", "int").implementation = function (data, flags) {
            if (data && data.length > 5000) {
                console.log("[B64] Encoding " + data.length + " bytes — possible image upload");
            }
            return this.encodeToString(data, flags);
        };
        console.log("[+] Base64 hooked");
    } catch (e) {}

    console.log("[TRACE] All hooks active");
});
