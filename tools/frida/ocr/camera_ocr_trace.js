// Frida Comprehensive Camera + OCR Trace
// Observes ONLY — no modification of return values

Java.perform(function () {
    console.log("[TRACE] === Camera + OCR Trace Starting ===");

    // ==========================================
    // 1. Camera2 API — frame delivery tracking
    // ==========================================
    try {
        var CaptureCallback = Java.use("android.hardware.camera2.CameraCaptureSession$CaptureCallback");
        CaptureCallback.onCaptureCompleted.implementation = function (session, request, result) {
            console.log("[CAM2] onCaptureCompleted — frame delivered");
            return this.onCaptureCompleted(session, request, result);
        };
        CaptureCallback.onCaptureBufferLost.implementation = function (session, request, surface, frameNumber) {
            console.log("[CAM2] onCaptureBufferLost — frame dropped");
        };
        CaptureCallback.onCaptureFailed.implementation = function (session, request, failure) {
            console.log("[CAM2] onCaptureFailed — capture failed");
        };
        console.log("[+] Camera2 CaptureCallback hooked");
    } catch (e) { console.log("[-] Camera2 hook: " + e); }

    // CameraCaptureSession — session creation
    try {
        var CameraCaptureSession = Java.use("android.hardware.camera2.CameraCaptureSession");
        CameraCaptureSession.setRepeatingRequest.overloads.forEach(function (overload) {
            overload.implementation = function () {
                console.log("[CAM2] setRepeatingRequest — preview started");
                return overload.apply(this, arguments);
            };
        });
        console.log("[+] CameraCaptureSession.setRepeatingRequest hooked");
    } catch (e) { console.log("[-] setRepeatingRequest: " + e); }

    // ==========================================
    // 2. takePhoto / capture — trace all matching methods
    // ==========================================
    Java.enumerateLoadedClasses({
        onMatch: function (className) {
            var lower = className.toLowerCase();
            // Look for takePhoto, capture, crop, base64, submitOCR, pingSDK
            if (lower.indexOf("takephoto") >= 0 || lower.indexOf("ocrmodule") >= 0 ||
                lower.indexOf("pingsdk") >= 0 || lower.indexOf("cropimage") >= 0 ||
                lower.indexOf("convertfiletobase64") >= 0 || lower.indexOf("submitocr") >= 0) {
                console.log("[CLASS-FOUND] " + className);
                try {
                    var cls = Java.use(className);
                    var methods = cls.class.getDeclaredMethods();
                    methods.forEach(function (method) {
                        var mname = method.getName();
                        console.log("[METHOD] " + className + "." + mname);
                        try {
                            cls[mname].overloads.forEach(function (overload) {
                                overload.implementation = function () {
                                    console.log("[CALL] " + className + "." + mname + "()");
                                    if (arguments.length > 0) {
                                        for (var i = 0; i < Math.min(arguments.length, 3); i++) {
                                            var arg = arguments[i];
                                            if (arg !== null && typeof arg === 'object' && arg.toString) {
                                                console.log("  arg" + i + ": " + arg.toString().substring(0, 100));
                                            } else {
                                                console.log("  arg" + i + ": " + arg);
                                            }
                                        }
                                    }
                                    var result = overload.apply(this, arguments);
                                    console.log("  => result: " + (result ? result.toString().substring(0, 100) : "null/void"));
                                    return result;
                                };
                            });
                        } catch (hookErr) { /* skip unhookable */ }
                    });
                } catch (useErr) { /* skip */ }
            }
        },
        onComplete: function () { console.log("[*] Class scan complete"); }
    });

    // ==========================================
    // 3. File creation monitoring
    // ==========================================
    try {
        var File = Java.use("java.io.File");
        File.$init.overload("java.lang.String").implementation = function (path) {
            if (path && (path.indexOf("cache") >= 0 || path.indexOf("photo") >= 0 ||
                path.indexOf("capture") >= 0 || path.indexOf("ocr") >= 0 || path.indexOf(".jpg") >= 0 ||
                path.indexOf(".png") >= 0 || path.indexOf(".jpeg") >= 0)) {
                console.log("[FILE] Created: " + path);
            }
            return this.$init(path);
        };
        console.log("[+] File creation hooked");
    } catch (e) { console.log("[-] File hook: " + e); }

    // ==========================================
    // 4. ImageWriter / ImageReader — frame capture
    // ==========================================
    try {
        var ImageReader = Java.use("android.media.ImageReader");
        ImageReader.acquireLatestImage.implementation = function () {
            var img = this.acquireLatestImage();
            if (img !== null) {
                console.log("[IMG] ImageReader.acquireLatestImage — got frame");
            }
            return img;
        };
        console.log("[+] ImageReader hooked");
    } catch (e) { console.log("[-] ImageReader hook: " + e); }

    // ==========================================
    // 5. Base64 encoding (OCR upload detection)
    // ==========================================
    try {
        var Base64 = Java.use("android.util.Base64");
        Base64.encodeToString.overload("[B", "int").implementation = function (input, flags) {
            if (input && input.length > 1000) {
                console.log("[B64] Base64.encodeToString — encoding " + input.length + " bytes (possible image)");
            }
            return this.encodeToString(input, flags);
        };
        console.log("[+] Base64 hooked");
    } catch (e) { console.log("[-] Base64 hook: " + e); }

    // ==========================================
    // 6. FileWriter / FileOutputStream — image save
    // ==========================================
    try {
        var FileOutputStream = Java.use("java.io.FileOutputStream");
        FileOutputStream.$init.overload("java.lang.String").implementation = function (path) {
            if (path && (path.indexOf("photo") >= 0 || path.indexOf("capture") >= 0 ||
                path.indexOf("cache") >= 0 || path.indexOf("ocr") >= 0)) {
                console.log("[WRITE] FileOutputStream: " + path);
            }
            return this.$init(path);
        };
        console.log("[+] FileOutputStream hooked");
    } catch (e) { console.log("[-] FileOutputStream hook: " + e); }

    console.log("[TRACE] === All hooks installed. Monitoring active. ===");
});
