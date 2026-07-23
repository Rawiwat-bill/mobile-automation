// Capture submitted JPEG via base64 signature search. Robust against key naming.
Java.perform(function () {
    console.log("[CAPTURE] Starting...");
    var Base64 = Java.use('android.util.Base64');
    var FileOutputStream = Java.use('java.io.FileOutputStream');
    var saved = false;

    var FRB = Java.use("com.bangkokbank.blue.ping.FRAuthBridge");
    FRB.next.overload("java.lang.String", "com.facebook.react.bridge.Promise")
        .implementation = function (json, promise) {
        var s = json.toString();
        if (!saved && s.length > 50000) {
            // Search for JPEG base64 signature
            var sig = s.indexOf('/9j/');
            console.log("[DEBUG] json len=" + s.length + " IDToken2 at=" +
                        s.indexOf('"IDToken2"') + " jpeg_sig at=" + sig);
            if (sig < 0) {
                // Try data URI prefix
                sig = s.indexOf('image/jpeg;base64,');
                if (sig >= 0) sig = s.indexOf(',', sig) + 1;
                console.log("[DEBUG] data_uri sig at=" + sig);
            }
            if (sig >= 0) {
                try {
                    // Walk back to opening quote
                    var start = s.lastIndexOf('"', sig) + 1;
                    var end = s.indexOf('"', sig + 10);
                    var b64 = s.substring(start, end);
                    console.log("[DEBUG] b64 len=" + b64.length + " start=" + start + " end=" + end);
                    if (b64.length > 1000) {
                        var bytes = Base64.decode(b64, 0);
                        var fos = FileOutputStream.$new('/data/data/com.bangkokbank.blue.dev/cache/stage5.jpg');
                        fos.write(bytes); fos.flush(); fos.close();
                        saved = true;
                        console.log("[STAGE5] Saved " + bytes.length + " bytes JPEG to cache/stage5.jpg");
                    }
                } catch (e) { console.log("[STAGE5] Error: " + e); }
            }
        }
        return this.next(json, promise);
    };
    console.log("[CAPTURE] Hooks installed.");
});
