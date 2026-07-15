// CameraX pipeline interceptor: capture FileOutputStream writes + bridge.next IDToken2.
Java.perform(function () {
    console.log("[PIPE] Starting...");
    var FOS = Java.use('java.io.FileOutputStream');
    var Base64 = Java.use('android.util.Base64');
    var saveCount = 0;
    var inHook = false;
    var stage5Saved = false;

    // Hook FileOutputStream.write(byte[]) — captures JPEG writes at all stages
    FOS.write.overload('[B').implementation = function (bytes) {
        if (!inHook && bytes.length > 5000 && saveCount < 8) {
            inHook = true;
            saveCount++;
            try {
                var path = '/data/data/com.bangkokbank.blue.dev/cache/pipeline_capture_' + saveCount + '.jpg';
                var fos = FOS.$new(path);
                fos.write(bytes); fos.flush(); fos.close();
                console.log("[FOS" + saveCount + "] " + bytes.length + " bytes → " + path);
            } catch (e) { console.log("[FOS] err: " + e); }
            inHook = false;
        }
        return this.write(bytes);
    };

    // Hook bridge.next — capture Stage5 (IDToken2 JPEG)
    try {
        var FRB = Java.use("com.bangkokbank.blue.ping.FRAuthBridge");
        FRB.next.overload("java.lang.String", "com.facebook.react.bridge.Promise")
            .implementation = function (json, promise) {
            var s = json.toString();
            if (!stage5Saved && s.length > 50000) {
                try {
                    var sig = s.indexOf('/9j/');
                    if (sig >= 0) {
                        var start = s.lastIndexOf('"', sig) + 1;
                        var end = s.indexOf('"', sig + 10);
                        var b64 = s.substring(start, end);
                        if (b64.length > 100) {
                            var bytes = Base64.decode(b64, 0);
                            var fos = FOS.$new('/data/data/com.bangkokbank.blue.dev/cache/stage5_final.jpg');
                            fos.write(bytes); fos.flush(); fos.close();
                            stage5Saved = true;
                            console.log("[STAGE5] " + bytes.length + " bytes saved");
                        }
                    }
                } catch (e) { console.log("[STAGE5] err: " + e); }
            }
            return this.next(json, promise);
        };
    } catch (e) { console.log("[STAGE5] hook err: " + e); }

    console.log("[PIPE] Hooks installed.");
});
