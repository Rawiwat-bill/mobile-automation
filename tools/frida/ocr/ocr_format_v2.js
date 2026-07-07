// Frida OCR Format & Persistence Test v2
// Uses Java.proxy for listener (avoids registerClass crash)
// Tries multiple IDToken2 formats

Java.perform(function () {
    console.log("[TEST] === OCR Format Test v2 ===");

    var TextInputCallback = Java.use("org.forgerock.android.auth.callback.TextInputCallback");
    var ChoiceCallback = Java.use("org.forgerock.android.auth.callback.ChoiceCallback");

    var MOCK_JSON = JSON.stringify({
        thaiFirstName: "สมใจ", thaiLastName: "ใจดี",
        englishTitle: "Miss", englishFirstName: "Somjai", englishLastName: "Jaidee",
        citizenId: "3872637115880", dateOfBirth: "15 Jan. 1992",
        dateOfIssue: "21 Aug. 2023", dateOfExpiry: "21 Aug. 2032",
        address: "888 หมู่ที่ 8 ต.ทดสอบ อ.ทดสอบ จ.กรุงเทพฯ"
    });

    var foundNode = false;

    Java.choose("org.forgerock.android.auth.Node", {
        onMatch: function (node) {
            if (foundNode) return;
            try {
                if (node.getStage() !== "OCR") return;
                foundNode = true;
                console.log("[TEST] *** OCR Node found ***");

                // Get context
                var context = Java.use("android.app.ActivityThread").currentApplication().getApplicationContext();

                // Get listener — try multiple approaches
                var listener = null;

                // Approach 1: Find existing
                Java.choose("org.forgerock.android.auth.NodeListener", {
                    onMatch: function (l) { if (!listener) { listener = l; console.log("[TEST] Found existing listener"); } },
                    onComplete: function () {}
                });

                // Approach 2: Try Java.proxy
                if (!listener) {
                    try {
                        var NodeListener = Java.use("org.forgerock.android.auth.NodeListener");
                        var proxyListener = Java.proxy(NodeListener.class, {
                            onCallbackReceived: function(n) {
                                console.log("[RESPONSE] *** onCallbackReceived! ***");
                                try { console.log("[RESPONSE] New stage: " + n.getStage()); } catch(e) {}
                            },
                            onException: function(e) {
                                console.log("[RESPONSE] *** onException: " + e + " ***");
                            }
                        });
                        listener = proxyListener;
                        console.log("[TEST] Created proxy listener");
                    } catch (e) {
                        console.log("[TEST] Proxy listener failed: " + e);
                    }
                }

                // Approach 3: Try with null listener
                if (!listener) {
                    console.log("[TEST] No listener — will try null");
                }

                // Fill callbacks with mock data
                var callbacks = node.getCallbacks();
                for (var i = 0; i < callbacks.size(); i++) {
                    var cb = callbacks.get(i);
                    var cls = cb.$className;
                    if (cls === "org.forgerock.android.auth.callback.TextInputCallback") {
                        Java.cast(cb, TextInputCallback).setValue(MOCK_JSON);
                        console.log("[TEST] Set TextInputCallback (format: JSON)");
                    }
                    if (cls === "org.forgerock.android.auth.callback.ChoiceCallback") {
                        Java.cast(cb, ChoiceCallback).setSelectedIndex(0);
                        console.log("[TEST] Set ChoiceCallback (proceed)");
                    }
                }

                // Verify by checking node JSON size
                var beforeSize = node.toJsonObject().toString().length;
                console.log("[TEST] Node JSON size after fill: " + beforeSize);

                // Call Node.next()
                console.log("[TEST] *** Calling Node.next() ***");
                try {
                    node.next(context, listener);
                    console.log("[TEST] *** Node.next() completed ***");
                } catch (e) {
                    console.log("[TEST] Node.next() error: " + e);
                    console.log("[TEST] Stack: " + (e.stack || "n/a"));
                }

                // Wait a bit for async response
                setTimeout(function() {
                    console.log("[TEST-COMPLETE] Done (after 5s wait)");
                }, 5000);

            } catch (e) {
                console.log("[TEST] Error: " + e);
            }
        },
        onComplete: function () {
            if (!foundNode) console.log("[TEST] No OCR Node found");
        }
    });
});
