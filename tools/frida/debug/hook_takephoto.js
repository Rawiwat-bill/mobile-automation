// Sprint 2.62 — Hook CameraViewModule.takePhoto to inject fake photo
//
// PROBLEM:  Camera produces 0 FPS on emulator → takePhoto never resolves → bridge.next never called
// SOLUTION: Hook takePhoto and resolve the promise with a fake photo path.
//           JS reads the file → converts to base64 → fills OCR callbacks → calls bridge.next()
//           with a PROPER JS-CONNECTED PROMISE → server returns NTB_LC → JS NAVIGATES!

Java.perform(function () {
    console.log("[TPH] === TakePhoto Hook ===");

    var CVT;
    try {
        CVT = Java.use("com.mrousavy.camera.react.CameraViewModule");
    } catch (e) {
        console.log("[TPH] CameraViewModule not found: " + e);
        return;
    }

    // Hook takePhoto(int viewId, ReadableMap options, Promise promise)
    try {
        CVT.takePhoto.overload("int", "com.facebook.react.bridge.ReadableMap", "com.facebook.react.bridge.Promise")
            .implementation = function (viewId, options, promise) {
            console.log("[TPH] *** takePhoto CALLED! viewId=" + viewId + " ***");

            try {
                // Create fake photo result
                var WNM = Java.use("com.facebook.react.bridge.WritableNativeMap");
                var photo = WNM.$new();
                photo.putString("path", "file:///data/local/tmp/mock_card.jpg");
                photo.putInt("width", 720);
                photo.putInt("height", 480);
                photo.putBoolean("isRawPhoto", false);

                // Minimal metadata
                var meta = WNM.$new();
                meta.putInt("Orientation", 1);
                photo.putMap("metadata", meta);

                console.log("[TPH] Resolving promise with fake photo");
                promise.resolve(photo);
                console.log("[TPH] *** PROMISE RESOLVED ***");
            } catch (e) {
                console.log("[TPH] Error creating photo: " + e);
                // Try minimal resolution
                try {
                    var WNM2 = Java.use("com.facebook.react.bridge.WritableNativeMap");
                    var p2 = WNM2.$new();
                    p2.putString("path", "file:///data/local/tmp/mock_card.jpg");
                    promise.resolve(p2);
                    console.log("[TPH] Minimal resolve done");
                } catch (e2) {
                    console.log("[TPH] Minimal resolve failed: " + e2);
                    promise.resolve("file:///data/local/tmp/mock_card.jpg");
                }
            }
        };
        console.log("[TPH] takePhoto hooked successfully!");
    } catch (e) {
        console.log("[TPH] Hook error: " + e);
    }

    // Also hook bridge.next for tracking
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

    // HTTP tracking
    try {
        Java.use("org.forgerock.android.auth.AuthServiceClient$2").onResponse.implementation = function (c, r) {
            try { var b = r.peekBody(2097152).string(); var m = b.match(/"stage":"([^"]+)"/);
                  console.log("[HTTP] " + r.code() + " " + (m?m[1]:"?")); } catch(e){}
            return this.onResponse(c, r);
        };
    } catch(e) {}

    // Promise reject tracking
    try {
        var PI = Java.use("com.facebook.react.bridge.PromiseImpl");
        PI.reject.overloads.forEach(function(ov) {
            ov.implementation = function() {
                var a = [];
                for (var i = 0; i < arguments.length; i++) a.push(arguments[i] ? arguments[i].toString().substring(0,100) : "null");
                console.log("[REJECT] " + a.join(" | "));
                return ov.apply(this, arguments);
            };
        });
    } catch(e) {}

    console.log("[TPH] Hooks installed. Waiting for Take Photo...");
});
