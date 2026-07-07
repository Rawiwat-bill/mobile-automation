// Frida OCR Image Base64 Injection
// Sprint 2.36 — Submits base64 JPEG of mock card as IDToken2

Java.perform(function () {
    console.log("[IMG] === OCR Image Base64 Injection ===");

    var TextInputCallback = Java.use("org.forgerock.android.auth.callback.TextInputCallback");
    var ChoiceCallback = Java.use("org.forgerock.android.auth.callback.ChoiceCallback");
    var File = Java.use("java.io.File");
    var FileInputStream = Java.use("java.io.FileInputStream");
    var String = Java.use("java.lang.String");

    // Read base64 from file on device
    var b64Data = "";
    try {
        var file = File.$new("/data/data/com.bangkokbank.blue.dev/mock_card_b64.txt");
        var fis = FileInputStream.$new(file);
        var bytes = Java.array("byte", new Array(file.length()).fill(0));
        fis.read(bytes);
        fis.close();
        b64Data = String.$new(bytes).toString();
        console.log("[IMG] Base64 loaded: " + b64Data.length + " chars");
        console.log("[IMG] Prefix: " + b64Data.substring(0, 40));
        console.log("[IMG] Suffix: ..." + b64Data.substring(b64Data.length - 30));
    } catch (e) {
        console.log("[IMG] File read error: " + e);
        return;
    }

    // Hook response handler
    try {
        var ASC2 = Java.use("org.forgerock.android.auth.AuthServiceClient$2");
        ASC2.onResponse.implementation = function (call, response) {
            try {
                var code = response.code();
                var body = response.peekBody(1048576).string();
                console.log("[RESP] HTTP " + code);
                console.log("[RESP] Body (first 500): " + body.substring(0, 500));

                // Check for stage
                if (body.indexOf("stage") >= 0) {
                    var match = body.match(/"stage"\s*:\s*"([^"]+)"/);
                    if (match) console.log("[RESP] *** STAGE: " + match[1] + " ***");
                }
                if (body.indexOf("error") >= 0 || body.indexOf("401") >= 0) {
                    console.log("[RESP] *** Error/401 detected ***");
                }
            } catch (e) {
                console.log("[RESP] Read error: " + e);
            }
            return this.onResponse(call, response);
        };
        console.log("[IMG] Response hook installed");
    } catch (e) { console.log("[IMG] Hook failed: " + e); }

    // Also hook ASC$1
    try {
        var ASC1 = Java.use("org.forgerock.android.auth.AuthServiceClient$1");
        ASC1.onResponse.implementation = function (call, response) {
            try {
                var code = response.code();
                var body = response.peekBody(1048576).string();
                console.log("[RESP1] HTTP " + code + ": " + body.substring(0, 300));
            } catch (e) {}
            return this.onResponse(call, response);
        };
    } catch (e) {}

    // Find OCR Node and inject
    var foundNode = false;
    Java.choose("org.forgerock.android.auth.Node", {
        onMatch: function (node) {
            if (foundNode) return;
            try {
                if (node.getStage() !== "OCR") return;
                foundNode = true;
                console.log("[IMG] *** OCR Node found ***");

                // Get context + listener
                var context = Java.use("android.app.ActivityThread").currentApplication().getApplicationContext();
                var listener = null;
                Java.choose("org.forgerock.android.auth.NodeListener", {
                    onMatch: function (l) { if (!listener) { listener = l; console.log("[IMG] Found listener"); } },
                    onComplete: function () {}
                });

                // Inspect callbacks
                var callbacks = node.getCallbacks();
                console.log("[IMG] Callbacks: " + callbacks.size());
                for (var i = 0; i < callbacks.size(); i++) {
                    console.log("[IMG] [" + i + "] " + callbacks.get(i).$className);
                }

                // Fill ChoiceCallback → proceed
                var cc = Java.cast(callbacks.get(0), ChoiceCallback);
                cc.setSelectedIndex(0);
                console.log("[IMG] ChoiceCallback → proceed");

                // Fill TextInputCallback → base64 image
                var tic = Java.cast(callbacks.get(1), TextInputCallback);
                tic.setValue(b64Data);
                console.log("[IMG] TextInputCallback → base64 image (" + b64Data.length + " chars)");

                // Verify Node JSON size changed
                var jsonSize = node.toJsonObject().toString().length;
                console.log("[IMG] Node JSON size: " + jsonSize + " (should be ~573k + 119k = ~692k)");

                // Submit
                console.log("[IMG] *** Calling Node.next() ***");
                try {
                    node.next(context, listener);
                    console.log("[IMG] *** Node.next() completed ***");
                    console.log("[IMG] Waiting for server response...");
                } catch (e) {
                    console.log("[IMG] Node.next() error: " + e);
                }

            } catch (e) {
                console.log("[IMG] Error: " + e);
            }
        },
        onComplete: function () {
            if (!foundNode) console.log("[IMG] No OCR Node found");
            console.log("[IMG-COMPLETE] Done");
        }
    });
});
