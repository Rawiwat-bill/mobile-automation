// Sprint 2.64 — Take Photo Call Chain Discovery
// Observation only. No return values are modified.

Java.perform(function () {
    console.log("[CHAIN] === Take Photo Call Chain Trace Installed ===");

    var Thread = Java.use("java.lang.Thread");

    function safeString(v, maxLen) {
        if (v === null || v === undefined) return "null";
        try {
            var s = v.toString();
            return s.length > maxLen ? s.substring(0, maxLen) + "..." : s;
        } catch (e) {
            return "<toString-error>";
        }
    }

    function viewSummary(v) {
        if (!v) return "null";
        var parts = [];
        try { parts.push(v.$className || v.getClass().getName()); } catch (e) {}
        try { parts.push("hash=" + v.hashCode()); } catch (e) {}
        try { parts.push("id=" + v.getId()); } catch (e) {}
        try {
            var cd = v.getContentDescription();
            if (cd) parts.push("cd=" + safeString(cd, 80));
        } catch (e) {}
        try {
            var t = v.getText();
            if (t) parts.push("text=" + safeString(t, 80));
        } catch (e) {}
        return parts.join(" ");
    }

    function stackTop(limit) {
        try {
            var ex = Java.use("java.lang.Exception").$new();
            var frames = ex.getStackTrace();
            var out = [];
            var max = Math.min(frames.length, limit || 6);
            for (var i = 0; i < max; i++) out.push(frames[i].toString());
            return out.join("\n    ");
        } catch (e) {
            return "stack-error: " + e;
        }
    }

    function hookMethod(className, methodName, label, stackOnCall) {
        try {
            var cls = Java.use(className);
            if (!cls[methodName] || !cls[methodName].overloads) return false;

            cls[methodName].overloads.forEach(function (ov) {
                ov.implementation = function () {
                    var thread = Thread.currentThread().getName();
                    console.log("[" + label + "] " + className + "." + methodName + " thread=" + thread);
                    if (stackOnCall) {
                        console.log("    " + stackTop(8).replace(/\n/g, "\n    "));
                    }
                    if (label === "VIEW") {
                        console.log("    self=" + viewSummary(this));
                    }
                    if (label === "RN") {
                        for (var i = 0; i < arguments.length; i++) {
                            var arg = arguments[i];
                            var argCls = arg && arg.$className ? arg.$className : (arg === null ? "null" : typeof arg);
                            console.log("    arg" + i + "=" + safeString(argCls, 120) + " " + safeString(arg, 120));
                        }
                    }
                    if (label === "CAMERA") {
                        for (var j = 0; j < Math.min(arguments.length, 4); j++) {
                            console.log("    arg" + j + "=" + safeString(arguments[j], 120));
                        }
                    }
                    return ov.call.apply(ov, [this].concat(Array.prototype.slice.call(arguments)));
                };
            });
            console.log("[HOOKED] " + className + "." + methodName);
            return true;
        } catch (e) {
            return false;
        }
    }

    function hookIfLoaded(className, specs) {
        try {
            var cls = Java.use(className);
            var methods = cls.class.getDeclaredMethods();
            var methodNames = {};
            methods.forEach(function (m) {
                methodNames[m.getName()] = true;
            });
            specs.forEach(function (spec) {
                if (methodNames[spec.method]) {
                    hookMethod(className, spec.method, spec.label, spec.stack);
                }
            });
        } catch (e) {}
    }

    // UI tap chain
    hookMethod("android.view.View", "dispatchTouchEvent", "VIEW", true);
    hookMethod("android.view.View", "onTouchEvent", "VIEW", true);
    hookMethod("android.view.View", "performClick", "VIEW", true);
    hookMethod("android.view.View", "callOnClick", "VIEW", true);
    hookMethod("android.view.ViewGroup", "dispatchTouchEvent", "VIEW", true);

    // React Native touch / event path
    hookMethod("com.facebook.react.uimanager.TouchTargetHelper", "findTargetTagAndCoordinatesForTouch", "RN", true);
    hookMethod("com.facebook.react.uimanager.events.EventDispatcherImpl", "dispatchEvent", "RN", true);
    hookMethod("com.facebook.react.uimanager.events.TouchEventDispatcher", "dispatchEvent", "RN", true);
    hookMethod("com.facebook.react.uimanager.events.RCTEventEmitter", "receiveEvent", "RN", true);
    hookMethod("com.facebook.react.uimanager.JSPointerDispatcher", "handleMotionEvent", "RN", true);
    hookMethod("com.facebook.react.uimanager.JSTouchDispatcher", "handleTouchEvent", "RN", true);
    hookMethod("com.facebook.react.views.view.ReactViewGroup", "onTouchEvent", "RN", true);
    hookMethod("com.facebook.react.views.view.ReactViewGroup", "dispatchTouchEvent", "RN", true);

    // Camera / vision-camera path
    hookMethod("com.mrousavy.camera.react.CameraViewModule", "takePhoto", "CAMERA", true);
    hookMethod("com.mrousavy.camera.react.CameraDevicesManager", "getDevicesJson", "CAMERA", true);
    hookMethod("com.mrousavy.camera.react.CameraDevicesManager", "sendAvailableDevicesChangedEvent", "CAMERA", true);

    hookIfLoaded("com.mrousavy.camera.react.CameraView", [
        { method: "takePhoto", label: "CAMERA", stack: true },
        { method: "setIsActive", label: "CAMERA", stack: true },
        { method: "setDevice", label: "CAMERA", stack: true },
        { method: "setCameraPosition", label: "CAMERA", stack: true },
        { method: "onFrameProcessorEnabledChanged", label: "CAMERA", stack: true },
        { method: "onPreviewStarted", label: "CAMERA", stack: true },
        { method: "onCameraInitialized", label: "CAMERA", stack: true }
    ]);

    hookIfLoaded("com.mrousavy.camera.core.CameraSession", [
        { method: "start", label: "CAMERA", stack: true },
        { method: "stop", label: "CAMERA", stack: true },
        { method: "resume", label: "CAMERA", stack: true },
        { method: "pause", label: "CAMERA", stack: true },
        { method: "takePhoto", label: "CAMERA", stack: true },
        { method: "capturePhoto", label: "CAMERA", stack: true }
    ]);

    // Promise / bridge / network confirmation
    hookMethod("com.facebook.react.bridge.PromiseImpl", "$init", "PROMISE", true);
    hookMethod("com.facebook.react.bridge.PromiseImpl", "resolve", "PROMISE", true);
    hookMethod("com.facebook.react.bridge.PromiseImpl", "reject", "PROMISE", true);
    hookMethod("com.bangkokbank.blue.ping.FRAuthBridge", "next", "BRIDGE", true);

    try {
        Java.use("org.forgerock.android.auth.AuthServiceClient$2").onResponse.implementation = function (c, r) {
            try {
                var code = r.code();
                var body = r.peekBody(1024 * 1024).string();
                var stage = "?";
                var m = body.match(/"stage"\s*:\s*"([^"]+)"/);
                if (m) stage = m[1];
                console.log("[HTTP] code=" + code + " stage=" + stage + " thread=" + Thread.currentThread().getName());
            } catch (e) {
                console.log("[HTTP] error=" + e);
            }
            return this.onResponse(c, r);
        };
        console.log("[HOOKED] org.forgerock.android.auth.AuthServiceClient$2.onResponse");
    } catch (e) {}

    console.log("[CHAIN] Hooks ready.");
});
