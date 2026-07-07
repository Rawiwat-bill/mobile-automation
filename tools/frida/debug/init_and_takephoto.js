// Sprint 2.63 — Attach early, poll for CameraView with recursive setTimeout
// Emits topCameraInitialized when CameraView is found
// Hooks takePhoto to resolve with fake photo

Java.perform(function () {
    console.log("[TPH] === Early Attach + Recursive Poll ===");

    var B64 = "";
    try {
        var BR = Java.use("java.io.BufferedReader");
        var FR = Java.use("java.io.FileReader");
        var reader = BR.$new(FR.$new("/data/local/tmp/mock_card_b64.txt"));
        B64 = reader.readLine();
        reader.close();
        console.log("[TPH] Base64 loaded: " + B64.length);
    } catch (e) { console.log("[TPH] B64 error: " + e); }

    var eventEmitted = false;

    // Recursive search for CameraView
    function searchCameraView(delay, attempt) {
        if (eventEmitted || attempt > 100) return;
        setTimeout(function () {
            Java.perform(function () {
                Java.choose("com.mrousavy.camera.react.CameraView", {
                    onMatch: function (cameraView) {
                        if (eventEmitted) return;
                        eventEmitted = true;
                        console.log("[TPH] CameraView found! (attempt " + attempt + ")");

                        try {
                            var viewId = cameraView.getId();
                            console.log("[TPH] viewId=" + viewId);

                            var RCTEE = Java.use("com.facebook.react.uimanager.events.RCTEventEmitter");
                            var RC = Java.use("com.facebook.react.bridge.ReactContext");
                            var context = cameraView.getContext();
                            var rc = Java.cast(context, RC);
                            var emitter = rc.getJSModule(RCTEE.class);
                            var emitterCasted = Java.cast(emitter, RCTEE);
                            var WNM = Java.use("com.facebook.react.bridge.WritableNativeMap");

                            // Wait 3s after finding CameraView for camera session to stabilize
                            setTimeout(function () {
                                Java.perform(function () {
                                    try {
                                        emitterCasted.receiveEvent(viewId, "topCameraInitialized", WNM.$new());
                                        console.log("[TPH] *** topCameraInitialized EMITTED! ***");
                                        emitterCasted.receiveEvent(viewId, "topCameraStarted", WNM.$new());
                                        console.log("[TPH] *** topCameraStarted EMITTED! ***");
                                        emitterCasted.receiveEvent(viewId, "topCameraViewReady", WNM.$new());
                                        console.log("[TPH] *** topCameraViewReady EMITTED! ***");
                                    } catch (e) {
                                        console.log("[TPH] Event error: " + e);
                                    }
                                });
                            }, 3000);
                        } catch (e) {
                            console.log("[TPH] Setup error: " + e);
                        }
                    },
                    onComplete: function () {}
                });
            });
            if (!eventEmitted) searchCameraView(5000, attempt + 1);
        }, delay);
    }

    // Start polling after 10s (let app stabilize)
    searchCameraView(10000, 1);

    // === HOOK: takePhoto ===
    try {
        var CVT = Java.use("com.mrousavy.camera.react.CameraViewModule");
        CVT.takePhoto.overload("int", "com.facebook.react.bridge.ReadableMap", "com.facebook.react.bridge.Promise")
            .implementation = function (viewId, options, promise) {
            console.log("[TPH] *** takePhoto CALLED! viewId=" + viewId + " ***");
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
                console.log("[TPH] *** takePhoto RESOLVED! ***");
            } catch (e) {
                console.log("[TPH] takePhoto error: " + e);
            }
        };
        console.log("[TPH] takePhoto hooked");
    } catch (e) { console.log("[TPH] takePhoto hook error: " + e); }

    // === HOOK: bridge.next ===
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

    // === HOOK: HTTP ===
    try {
        Java.use("org.forgerock.android.auth.AuthServiceClient$2").onResponse.implementation = function (c, r) {
            try { var b = r.peekBody(2097152).string(); var m = b.match(/"stage":"([^"]+)"/);
                  console.log("[HTTP] " + r.code() + " " + (m?m[1]:"?")); } catch(e){}
            return this.onResponse(c, r);
        };
    } catch(e) {}

    console.log("[TPH] All hooks installed. Polling for CameraView...");
});
