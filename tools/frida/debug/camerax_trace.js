// Sprint 2.66 — CameraX Failure Owner Discovery: Frida Tracing Script
//
// This script was prepared for CameraX/Camera2 tracing but was NOT run
// because existing logcat evidence from Sprint 2.64 was sufficient.
//
// The script is retained here for reference and potential future use
// if a confirmatory dynamic trace is needed.

Java.perform(function () {
    console.log("[CX] === CameraX Failure Owner Tracer ===");

    var Thread = Java.use("java.lang.Thread");
    var frameCount = 0;

    // === Camera2 API Hooks ===

    // CameraManager.getCameraIdList
    try {
        var CameraManager = Java.use("android.hardware.camera2.CameraManager");
        CameraManager.getCameraIdList.implementation = function () {
            var result = this.getCameraIdList();
            console.log("[CX] CameraManager.getCameraIdList() → [" + result.join(", ") + "] thread=" + Thread.currentThread().getName());
            return result;
        };
        console.log("[CX] Hooked CameraManager.getCameraIdList");
    } catch (e) { console.log("[CX] getCameraIdList hook error: " + e); }

    // CameraManager.openCamera
    try {
        var CameraManager2 = Java.use("android.hardware.camera2.CameraManager");
        CameraManager2.openCamera.overload("java.lang.String", "android.hardware.camera2.CameraDevice$StateCallback", "android.os.Handler").implementation = function (id, cb, handler) {
            console.log("[CX] CameraManager.openCamera('" + id + "') thread=" + Thread.currentThread().getName());
            return this.openCamera(id, cb, handler);
        };
        console.log("[CX] Hooked CameraManager.openCamera");
    } catch (e) { console.log("[CX] openCamera hook error: " + e); }

    // === CameraX Hooks (if present) ===

    // CameraSelector.select
    try {
        var CameraSelector = Java.use("androidx.camera.core.CameraSelector");
        CameraSelector.select.overload("[Landroidx.camera.core.impl.CameraInternal;").implementation = function (cameras) {
            console.log("[CX] CameraSelector.select(" + cameras.length + " cameras) thread=" + Thread.currentThread().getName());
            try {
                return this.select(cameras);
            } catch (e) {
                console.log("[CX] CameraSelector.select THREW: " + e);
                throw e;
            }
        };
        console.log("[CX] Hooked CameraSelector.select");
    } catch (e) { console.log("[CX] CameraSelector hook error: " + e); }

    // CameraValidator.validateCameras
    try {
        var CameraValidator = Java.use("androidx.camera.core.impl.CameraValidator");
        var methods = CameraValidator.class.getDeclaredMethods();
        for (var i = 0; i < methods.length; i++) {
            if (methods[i].getName() === "validateCameras") {
                console.log("[CX] Found CameraValidator.validateCameras (params=" + methods[i].getParameterTypes().length + ")");
            }
        }
    } catch (e) { console.log("[CX] CameraValidator not found: " + e); }

    // === Throwable Hooks ===

    // IllegalArgumentException constructor (filter for camera messages)
    try {
        var IAE = Java.use("java.lang.IllegalArgumentException");
        IAE.$init.overload("java.lang.String").implementation = function (msg) {
            if (msg && (msg.indexOf("camera") >= 0 || msg.indexOf("Camera") >= 0)) {
                console.log("[CX] *** IllegalArgumentException: " + msg + " ***");
                console.log("[CX] Stack: " + Java.use("android.util.Log").getStackTraceString(Java.use("java.lang.Exception").$new()));
            }
            return this.$init(msg);
        };
        console.log("[CX] Hooked IllegalArgumentException");
    } catch (e) { console.log("[CX] IAE hook error: " + e); }

    // CameraIdListIncorrectException
    try {
        var CVException = Java.use("androidx.camera.core.impl.CameraValidator$CameraIdListIncorrectException");
        CVException.$init.overload("java.lang.String", "java.lang.Throwable").implementation = function (msg, cause) {
            console.log("[CX] *** CameraIdListIncorrectException: " + msg + " ***");
            return this.$init(msg, cause);
        };
        console.log("[CX] Hooked CameraIdListIncorrectException");
    } catch (e) { console.log("[CX] CVException hook error: " + e); }

    // === Camera2CameraImpl state transitions ===
    try {
        var C2CI = Java.use("androidx.camera.camera2.internal.Camera2CameraImpl");
        console.log("[CX] Camera2CameraImpl found");
    } catch (e) { console.log("[CX] Camera2CameraImpl not found: " + e); }

    console.log("[CX] All hooks installed. Waiting for camera activity...");
});
