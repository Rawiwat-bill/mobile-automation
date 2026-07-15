// Read-only OCR response capture. Logs the full backend JSON.
// Derived from eval_js_ocr.js — capture hooks only, zero modification.
Java.perform(function () {
    console.log("[CAPTURE] Read-only OCR response capture starting...");

    var PromiseImpl = Java.use("com.facebook.react.bridge.PromiseImpl");
    var captured = false;

    // === CAPTURE: Full OCR response JSON from RN promise resolve ===
    PromiseImpl.resolve.overload("java.lang.Object").implementation = function (value) {
        if (!captured && value !== null) {
            try {
                var str = value.toString();
                if (str.indexOf('"stage":"OCR"') >= 0 && str.length > 10000) {
                    captured = true;
                    console.log("[CAPTURE] OCR Response captured! len=" + str.length);
                    // Write full JSON to /sdcard (world-writable)
                    try {
                        var f = new File("/sdcard/ocr_response.json", "w");
                        f.write(str);
                        f.flush();
                        f.close();
                        console.log("[CAPTURE] Written to /sdcard/ocr_response.json");
                    } catch(fe) { console.log("[CAPTURE] File write error: " + fe); }
                    // Search for OCR data keywords and log surrounding context
                    var keywords = ["citizenId", "idNumber", "id_number", "thaiName", "thai_name",
                                    "firstName", "lastName", "dateOfBirth", "dob", "date_of_birth",
                                    "ocrData", "IDToken", "laserCode", "laser", "address",
                                    "dateOfIssue", "dateOfExpiry", "issueDate", "expiryDate",
                                    "RGI", "rgi", "helpCode", "help_code"];
                    for (var ki = 0; ki < keywords.length; ki++) {
                        var idx = str.indexOf(keywords[ki]);
                        while (idx >= 0 && idx < str.length) {
                            var start = Math.max(0, idx - 20);
                            var end = Math.min(str.length, idx + 200);
                            console.log("[OCR_FIELD] ..." + str.substring(start, end) + "...");
                            idx = str.indexOf(keywords[ki], idx + 1);
                            if (idx - start > 500) break; // ponytail: limit repeats per keyword
                        }
                    }
                }
            } catch (e) {
                console.log("[CAPTURE] Error: " + e);
            }
        }
        return this.resolve(value);
    };

    // === TRACK: bridge.next calls ===
    try {
        var FRB = Java.use("com.bangkokbank.blue.ping.FRAuthBridge");
        FRB.next.overload("java.lang.String", "com.facebook.react.bridge.Promise").implementation = function (json, promise) {
            var stage = "?";
            try { var sm = json.substring(0, 5000).match(/"stage"\s*:\s*"([^"]+)"/); if (sm) stage = sm[1]; } catch(e) {}
            console.log("[BRIDGE.NEXT] stage=" + stage + " len=" + json.length);
            return this.next(json, promise);
        };
    } catch(e) { console.log("[CAPTURE] bridge.next hook error: " + e); }

    // === TRACK: HTTP response codes ===
    try {
        Java.use("org.forgerock.android.auth.AuthServiceClient$2").onResponse.implementation = function (c, r) {
            try {
                var body = r.peekBody(2097152).string();
                var sm = body.match(/"stage"\s*:\s*"([^"]+)"/);
                console.log("[HTTP] code=" + r.code() + " stage=" + (sm ? sm[1] : "?") + " len=" + body.length);
            } catch (e) {}
            return this.onResponse(c, r);
        };
    } catch (e) {}

    // === TRACK: Promise rejects ===
    try {
        PromiseImpl.reject.overloads.forEach(function(ov) {
            ov.implementation = function() {
                var args = [];
                for (var i = 0; i < arguments.length; i++)
                    args.push(arguments[i] ? arguments[i].toString().substring(0,100) : "null");
                console.log("[REJECT] " + args.join(" | "));
                return ov.apply(this, arguments);
            };
        });
    } catch(e) {}

    console.log("[CAPTURE] Hooks installed. Waiting for OCR response...");
});
