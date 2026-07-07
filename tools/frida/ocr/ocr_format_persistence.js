// Frida OCR Node Injection — Format & Persistence Test
// Sprint 2.35
//
// 1. Dumps node.toJsonObject() BEFORE injection
// 2. Fills callbacks
// 3. Dumps node.toJsonObject() AFTER injection
// 4. Calls Node.next()
// 5. If callbacks didn't persist, uses setCallback() to replace

Java.perform(function () {
    console.log("[TEST] === OCR Format & Persistence Test ===");

    var TextInputCallback = Java.use("org.forgerock.android.auth.callback.TextInputCallback");
    var ChoiceCallback = Java.use("org.forgerock.android.auth.callback.ChoiceCallback");
    var JSONObject = Java.use("org.json.JSONObject");

    var MOCK_JSON_A = JSON.stringify({
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
                var stage = node.getStage();
                if (stage !== "OCR") return;
                foundNode = true;
                console.log("[TEST] *** OCR Node found ***");

                // === STEP 1: Dump node JSON BEFORE ===
                console.log("\n[BEFORE] === Node JSON before injection ===");
                try {
                    var beforeJson = node.toJsonObject();
                    var beforeStr = beforeJson.toString();
                    console.log("[BEFORE] " + beforeStr.substring(0, 500));
                    if (beforeStr.length > 500) console.log("[BEFORE] ...(truncated, total " + beforeStr.length + " chars)");
                } catch (e) {
                    console.log("[BEFORE] toJsonObject error: " + e);
                }

                // === STEP 2: Inspect callbacks individually ===
                var callbacks = node.getCallbacks();
                var count = callbacks.size();
                console.log("\n[INSPECT] Callback count: " + count);

                for (var i = 0; i < count; i++) {
                    var cb = callbacks.get(i);
                    var cls = cb.$className;
                    console.log("[INSPECT] [" + i + "] " + cls);

                    // Dump callback's internal JSON
                    try {
                        var cbJson = cb.getContent();
                        var cbStr = cbJson ? cbJson.toString() : "null";
                        console.log("[INSPECT] [" + i + "] content: " + cbStr.substring(0, 300));
                    } catch (e) {
                        // Try toJsonObject or toString
                        try {
                            console.log("[INSPECT] [" + i + "] toString: " + cb.toString().substring(0, 300));
                        } catch (e2) {
                            console.log("[INSPECT] [" + i + "] (cannot dump)");
                        }
                    }
                }

                // === STEP 3: Fill callbacks ===
                console.log("\n[FILL] Setting callback values...");
                for (var i = 0; i < count; i++) {
                    var cb = callbacks.get(i);
                    var cls = cb.$className;

                    if (cls === "org.forgerock.android.auth.callback.TextInputCallback") {
                        var tic = Java.cast(cb, TextInputCallback);
                        tic.setValue(MOCK_JSON_A);
                        console.log("[FILL] TextInputCallback.setValue called (len=" + MOCK_JSON_A.length + ")");
                    }

                    if (cls === "org.forgerock.android.auth.callback.ChoiceCallback") {
                        var cc = Java.cast(cb, ChoiceCallback);
                        cc.setSelectedIndex(0);
                        console.log("[FILL] ChoiceCallback.setSelectedIndex(0) called");
                    }
                }

                // === STEP 4: Dump node JSON AFTER ===
                console.log("\n[AFTER] === Node JSON after injection ===");
                try {
                    var afterJson = node.toJsonObject();
                    var afterStr = afterJson.toString();
                    console.log("[AFTER] " + afterStr.substring(0, 500));
                    if (afterStr.length > 500) console.log("[AFTER] ...(truncated, total " + afterStr.length + " chars)");
                } catch (e) {
                    console.log("[AFTER] toJsonObject error: " + e);
                }

                // === STEP 5: Re-inspect callbacks AFTER ===
                console.log("\n[VERIFY] === Callback values after fill ===");
                for (var i = 0; i < count; i++) {
                    var cb = callbacks.get(i);
                    var cls = cb.$className;

                    if (cls === "org.forgerock.android.auth.callback.TextInputCallback") {
                        try {
                            var content = cb.getContent();
                            console.log("[VERIFY] TextInput content: " + (content ? content.toString().substring(0, 200) : "null"));
                        } catch (e) {
                            console.log("[VERIFY] TextInput content error: " + e);
                        }
                        // Also try getting defaultText to see if value differs
                        try {
                            var tic = Java.cast(cb, TextInputCallback);
                            var dt = tic.getDefaultText();
                            console.log("[VERIFY] TextInput defaultText: " + dt);
                        } catch(e) {}
                    }

                    if (cls === "org.forgerock.android.auth.callback.ChoiceCallback") {
                        try {
                            var cc = Java.cast(cb, ChoiceCallback);
                            var idx = cc.getDefaultChoice();
                            console.log("[VERIFY] ChoiceCallback defaultChoice: " + idx);
                        } catch(e) {
                            console.log("[VERIFY] ChoiceCallback error: " + e);
                        }
                    }
                }

                // === STEP 6: Call Node.next() ===
                console.log("\n[NEXT] === Calling Node.next() ===");
                var context = Java.use("android.app.ActivityThread").currentApplication().getApplicationContext();

                var listener = null;
                Java.choose("org.forgerock.android.auth.NodeListener", {
                    onMatch: function (l) {
                        if (listener === null) listener = l;
                    },
                    onComplete: function () {}
                });

                if (context && listener) {
                    console.log("[NEXT] Context + listener ready. Calling next()...");
                    try {
                        node.next(context, listener);
                        console.log("[NEXT] *** Node.next() completed ***");
                    } catch (e) {
                        console.log("[NEXT] Node.next() error: " + e);
                    }
                } else {
                    console.log("[NEXT] Missing context or listener");
                }

            } catch (e) {
                console.log("[TEST] Error: " + e);
                console.log("[TEST] Stack: " + (e.stack || "n/a"));
            }
        },
        onComplete: function () {
            if (!foundNode) console.log("[TEST] No OCR Node found");
            console.log("[TEST-COMPLETE] Done");
        }
    });
});
