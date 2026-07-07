// Sprint 2.67 — Image Processing Pipeline Trace
// Hook ML Kit, CameraX ImageAnalysis, BitmapFactory, Bitmap
// Find ANY image processing that fires on the camera screen

Java.perform(function () {
    console.log("[IMG] === Image Pipeline Trace ===");
    var Thread = Java.use("java.lang.Thread");

    // === ML Kit InputImage ===
    var mlKitHooks = [
        "com.google.mlkit.vision.common.InputImage"
    ];
    mlKitHooks.forEach(function (cls) {
        try {
            var C = Java.use(cls);
            var methods = C.class.getDeclaredMethods();
            methods.forEach(function (m) {
                var name = m.getName();
                if (name.indexOf("from") >= 0 || name.indexOf("create") >= 0) {
                    try {
                        var paramTypes = [];
                        m.getParameterTypes().forEach(function (p) { paramTypes.push(p.getName()); });
                        console.log("[IMG] Found: " + cls + "." + name + "(" + paramTypes.join(", ") + ")");
                    } catch(e) {}
                }
            });
            // Hook all static factory methods
            try {
                C.fromBitmap.overloads.forEach(function (ov) {
                    ov.implementation = function () {
                        console.log("[IMG] *** InputImage.fromBitmap called! thread=" + Thread.currentThread().getName() + " ***");
                        return ov.apply(this, arguments);
                    };
                });
                console.log("[IMG] Hooked InputImage.fromBitmap");
            } catch(e) {}
            try {
                C.fromByteArray.overloads.forEach(function (ov) {
                    ov.implementation = function () {
                        console.log("[IMG] *** InputImage.fromByteArray called! len=" + (arguments[0] ? arguments[0].length : "?") + " ***");
                        return ov.apply(this, arguments);
                    };
                });
                console.log("[IMG] Hooked InputImage.fromByteArray");
            } catch(e) {}
            try {
                C.fromMediaImage.overloads.forEach(function (ov) {
                    ov.implementation = function () {
                        console.log("[IMG] *** InputImage.fromMediaImage called! ***");
                        return ov.apply(this, arguments);
                    };
                });
                console.log("[IMG] Hooked InputImage.fromMediaImage");
            } catch(e) {}
        } catch (e) { console.log("[IMG] " + cls + " not found"); }
    });

    // === CameraX ImageAnalysis ===
    try {
        var IA = Java.use("androidx.camera.core.ImageAnalysis");
        console.log("[IMG] ImageAnalysis found");
        // Hook setAnalyzer
        try {
            IA.setAnalyzer.overloads.forEach(function (ov) {
                ov.implementation = function () {
                    console.log("[IMG] *** ImageAnalysis.setAnalyzer called! ***");
                    return ov.apply(this, arguments);
                };
            });
            console.log("[IMG] Hooked ImageAnalysis.setAnalyzer");
        } catch(e) {}
    } catch (e) {}

    // Hook ImageAnalysis.Analyzer.analyze if it exists
    try {
        var Analyzer = Java.use("androidx.camera.core.ImageAnalysis$Analyzer");
        console.log("[IMG] ImageAnalysis.Analyzer interface found");
    } catch(e) {}

    // === CameraX ImageCapture ===
    try {
        var IC = Java.use("androidx.camera.core.ImageCapture");
        console.log("[IMG] ImageCapture found");
        // Hook takePicture
        try {
            IC.takePicture.overloads.forEach(function (ov) {
                ov.implementation = function () {
                    console.log("[IMG] *** ImageCapture.takePicture called! thread=" + Thread.currentThread().getName() + " ***");
                    return ov.apply(this, arguments);
                };
            });
            console.log("[IMG] Hooked ImageCapture.takePicture (" + IC.takePicture.overloads.length + " overloads)");
        } catch(e) { console.log("[IMG] takePicture hook error: " + e); }
    } catch(e) { console.log("[IMG] ImageCapture not found"); }

    // === BitmapFactory (LIMITED — only decodeFile, skip the rest to avoid noise) ===
    try {
        var BF = Java.use("android.graphics.BitmapFactory");
        BF.decodeFile.overloads.forEach(function (ov) {
            ov.implementation = function () {
                console.log("[IMG] BitmapFactory.decodeFile(" + (arguments[0] || "?") + ") thread=" + Thread.currentThread().getName());
                return ov.apply(this, arguments);
            };
        });
        console.log("[IMG] Hooked BitmapFactory.decodeFile (only)");
    } catch(e) {}

    // === CameraViewModule.takePhoto ===
    try {
        var CVT = Java.use("com.mrousavy.camera.react.CameraViewModule");
        CVT.takePhoto.overload("int", "com.facebook.react.bridge.ReadableMap", "com.facebook.react.bridge.Promise")
            .implementation = function (viewId, options, promise) {
            console.log("[IMG] *** CameraViewModule.takePhoto CALLED! viewId=" + viewId + " ***");
            return this.takePhoto(viewId, options, promise);
        };
        console.log("[IMG] Hooked CameraViewModule.takePhoto");
    } catch(e) {}

    // === FRAuthBridge.next ===
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

    // === HTTP ===
    try {
        Java.use("org.forgerock.android.auth.AuthServiceClient$2").onResponse.implementation = function (c, r) {
            try { var b = r.peekBody(2097152).string(); var m = b.match(/"stage":"([^"]+)"/);
                  console.log("[HTTP] " + r.code() + " " + (m?m[1]:"?")); } catch(e){}
            return this.onResponse(c, r);
        };
    } catch(e) {}

    // === vision-camera FrameProcessor ===
    try {
        var FP = Java.use("com.mrousavy.camera.frameprocessors.FrameProcessor");
        console.log("[IMG] FrameProcessor class found");
        var methods = FP.class.getDeclaredMethods();
        methods.forEach(function(m) {
            if (m.getName().indexOf("call") >= 0 || m.getName().indexOf("process") >= 0) {
                console.log("[IMG]   FrameProcessor." + m.getName());
            }
        });
    } catch(e) {}

    // === CameraView onFrame ===
    try {
        var CV = Java.use("com.mrousavy.camera.react.CameraView");
        CV.onFrame.implementation = function (frame) {
            console.log("[IMG] *** CameraView.onFrame called! ***");
            return this.onFrame(frame);
        };
        console.log("[IMG] Hooked CameraView.onFrame");
    } catch(e) {}

    console.log("[IMG] All hooks installed. Navigate to camera and tap Take Photo.");
});
