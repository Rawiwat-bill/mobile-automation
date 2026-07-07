// Sprint 2.64 — Camera Device + Event + takePhoto Hook (COMBINED)
//
// ROOT CAUSE: JS doesn't call takePhoto() because CameraDevicesManager.getDevicesJson()
//             returns empty array (no camera device on emulator).
// FIX: 1. Hook getDevicesJson() → return fake camera device
//      2. Call sendAvailableDevicesChangedEvent() → JS re-fetches devices
//      3. Emit topCameraInitialized → JS sets cameraReady=true
//      4. Hook takePhoto → resolve with fake photo
//      5. JS calls bridge.next() → server returns NTB_LC → JS NAVIGATES!

Java.perform(function () {
    console.log("[DEV] === Camera Device + Event + takePhoto ===");

    var B64 = "";
    try {
        var BR = Java.use("java.io.BufferedReader");
        var FR = Java.use("java.io.FileReader");
        var reader = BR.$new(FR.$new("/data/local/tmp/mock_card_b64.txt"));
        B64 = reader.readLine();
        reader.close();
    } catch (e) {}

    // === HOOK 1: CameraDevicesManager.getDevicesJson() → return fake device ===
    try {
        var CDM = Java.use("com.mrousavy.camera.react.CameraDevicesManager");

        CDM.getDevicesJson.implementation = function () {
            console.log("[DEV] *** getDevicesJson() called! Returning fake device ***");
            var Arguments = Java.use("com.facebook.react.bridge.Arguments");
            var arr = Arguments.createArray();
            var device = Arguments.createMap();
            device.putString("id", "0");
            device.putString("name", "Emulator Camera");
            device.putString("sensors", "back");
            device.putDouble("minZoom", 1.0);
            device.putDouble("maxZoom", 1.0);
            device.putDouble("neutralZoom", 1.0);
            device.putBoolean("isMultiCam", false);
            device.putBoolean("supportsRawCapture", false);
            device.putBoolean("supportsLowLightBoost", false);
            device.putBoolean("supportsFocus", true);
            device.putBoolean("hasTorch", false);
            device.putArray("formats", Arguments.createArray());
            arr.pushMap(device);
            console.log("[DEV] Fake device array created");
            return arr;
        };

        console.log("[DEV] CameraDevicesManager.getDevicesJson hooked");
    } catch (e) { console.log("[DEV] CDM hook error: " + e); }

    // === HOOK 2: Emit topCameraInitialized when CameraView is found (delayed search) ===
    var eventEmitted = false;
    // Wait 5s for Frida to stabilize, then search for CameraView
    setTimeout(function () {
        Java.perform(function () {
            Java.choose("com.mrousavy.camera.react.CameraView", {
        onMatch: function (cameraView) {
            if (eventEmitted) return;
            eventEmitted = true;
            console.log("[DEV] CameraView found!");

            try {
                var viewId = cameraView.getId();
                console.log("[DEV] viewId=" + viewId);
                var RCTEE = Java.use("com.facebook.react.uimanager.events.RCTEventEmitter");
                var RC = Java.use("com.facebook.react.bridge.ReactContext");
                var context = cameraView.getContext();
                var rc = Java.cast(context, RC);
                var emitter = rc.getJSModule(RCTEE.class);
                var emitterCasted = Java.cast(emitter, RCTEE);
                var WNM = Java.use("com.facebook.react.bridge.WritableNativeMap");

                emitterCasted.receiveEvent(viewId, "topCameraInitialized", WNM.$new());
                console.log("[DEV] *** topCameraInitialized EMITTED! ***");
                emitterCasted.receiveEvent(viewId, "topCameraStarted", WNM.$new());
                console.log("[DEV] *** topCameraStarted EMITTED! ***");
                emitterCasted.receiveEvent(viewId, "topCameraViewReady", WNM.$new());
                console.log("[DEV] *** topCameraViewReady EMITTED! ***");

                // Trigger device change event
                Java.choose("com.mrousavy.camera.react.CameraDevicesManager", {
                    onMatch: function(cdm) {
                        try { cdm.sendAvailableDevicesChangedEvent(); console.log("[DEV] *** Device change event sent! ***"); } catch(e) { console.log("[DEV] device event err: " + e); }
                    },
                    onComplete: function() {}
                });
            } catch (e) { console.log("[DEV] Event error: " + e); }
        },
            onComplete: function () {
                if (!eventEmitted) console.log("[DEV] CameraView NOT found (delayed)");
            }
        });
        });
    }, 5000);

    // === HOOK 3: takePhoto → resolve with fake photo ===
    try {
        var CVT = Java.use("com.mrousavy.camera.react.CameraViewModule");
        CVT.takePhoto.overload("int", "com.facebook.react.bridge.ReadableMap", "com.facebook.react.bridge.Promise")
            .implementation = function (viewId, options, promise) {
            console.log("[DEV] *** takePhoto CALLED! viewId=" + viewId + " ***");
            try {
                var WNM = Java.use("com.facebook.react.bridge.WritableNativeMap");
                var photo = WNM.$new();
                photo.putString("path", "file:///data/local/tmp/mock_card.jpg");
                photo.putInt("width", 720);
                photo.putInt("height", 480);
                photo.putBoolean("isRawPhoto", false);
                var meta = WNM.$new();
                meta.putInt("Orientation", 1);
                photo.putMap("metadata", meta);
                promise.resolve(photo);
                console.log("[DEV] *** takePhoto RESOLVED with fake photo! ***");
            } catch (e) { console.log("[DEV] takePhoto error: " + e); }
        };
        console.log("[DEV] takePhoto hooked");
    } catch (e) { console.log("[DEV] takePhoto hook error: " + e); }

    // === HOOK 4: bridge.next tracking ===
    try {
        var FRB = Java.use("com.bangkokbank.blue.ping.FRAuthBridge");
        var nc = 0;
        FRB.next.overload("java.lang.String", "com.facebook.react.bridge.Promise").implementation = function (j, p) {
            nc++;
            var s = "?"; try { var m = j.substring(0,5000).match(/"stage":"([^"]+)"/); if(m) s=m[1]; } catch(e){}
            console.log("[BN] #" + nc + " stage=" + s + " len=" + j.length);
            return this.next(j, p);
        };
    } catch(e) {}

    // === HOOK 5: HTTP tracking ===
    try {
        Java.use("org.forgerock.android.auth.AuthServiceClient$2").onResponse.implementation = function (c, r) {
            try { var b = r.peekBody(2097152).string(); var m = b.match(/"stage":"([^"]+)"/);
                  console.log("[HTTP] " + r.code() + " " + (m?m[1]:"?")); } catch(e){}
            return this.onResponse(c, r);
        };
    } catch(e) {}

    console.log("[DEV] All hooks installed");
});
