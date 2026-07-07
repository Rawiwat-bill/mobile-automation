// Frida OCR Listener Capture + Injection
// Sprint 2.37
//
// Strategy:
// 1. At SPAWN time, hook Node.next() to capture the listener argument
// 2. Store the listener reference globally
// 3. When app reaches OCR stage, find the OCR Node
// 4. Fill callbacks with base64 image
// 5. Call node.next(context, capturedListener)

Java.perform(function () {
    console.log("[CAP] === Listener Capture + OCR Injection ===");

    var TextInputCallback = Java.use("org.forgerock.android.auth.callback.TextInputCallback");
    var ChoiceCallback = Java.use("org.forgerock.android.auth.callback.ChoiceCallback");
    var Node = Java.use("org.forgerock.android.auth.Node");

    // Global storage for captured listener
    var capturedListener = null;
    var capturedContext = null;
    var callCount = 0;

    // === HOOK: Capture listener from Node.next() calls ===
    Node.next.implementation = function (context, listener) {
        callCount++;
        var stage = "unknown";
        try { stage = this.getStage(); } catch (e) {}

        console.log("[CAP] Node.next() call #" + callCount + " — stage: " + stage);

        // Capture the FIRST listener we see (it's from the app's normal flow)
        if (capturedListener === null && listener !== null) {
            capturedListener = listener;
            console.log("[CAP] *** LISTENER CAPTURED from call #" + callCount + " (stage: " + stage + ") ***");
            console.log("[CAP] Listener class: " + listener.$className);
        }

        // Capture context
        if (capturedContext === null && context !== null) {
            capturedContext = context;
            console.log("[CAP] Context captured");
        }

        // If this is the OCR stage and the IDToken2 is empty, this is the app's
        // own (failing) call — let it pass through normally
        return this.next(context, listener);
    };
    console.log("[CAP] Node.next() hooked for listener capture");

    // === HOOK: Capture response for logging ===
    try {
        var ASC2 = Java.use("org.forgerock.android.auth.AuthServiceClient$2");
        ASC2.onResponse.implementation = function (call, response) {
            try {
                var code = response.code();
                var body = response.peekBody(1048576).string();
                console.log("[RESP] HTTP " + code + " (first 300): " + body.substring(0, 300));
                if (body.indexOf("stage") >= 0) {
                    var match = body.match(/"stage"\s*:\s*"([^"]+)"/);
                    if (match) console.log("[RESP] *** STAGE: " + match[1] + " ***");
                }
            } catch (e) {}
            return this.onResponse(call, response);
        };
        console.log("[CAP] Response hook installed");
    } catch (e) { console.log("[CAP] Response hook failed: " + e); }

    // === INJECTION: Triggered after a delay (when app reaches OCR stage) ===
    // The mock base64 is loaded from an embedded string (generated separately)
    // For now, we use a marker — the injection is triggered by a separate Frida call

    // Expose injection function
    rpc.exports = {
        inject: function (b64Image) {
            Java.perform(function () {
                console.log("\n[INJECT] === Starting OCR Injection ===");
                console.log("[INJECT] Base64 image: " + b64Image.length + " chars");

                var foundNode = false;
                Java.choose("org.forgerock.android.auth.Node", {
                    onMatch: function (node) {
                        if (foundNode) return;
                        try {
                            if (node.getStage() !== "OCR") return;
                            foundNode = true;
                            console.log("[INJECT] *** OCR Node found ***");

                            // Fill callbacks
                            var callbacks = node.getCallbacks();
                            Java.cast(callbacks.get(0), ChoiceCallback).setSelectedIndex(0);
                            Java.cast(callbacks.get(1), TextInputCallback).setValue(b64Image);
                            console.log("[INJECT] Callbacks filled (proceed + base64 image)");

                            // Use captured listener
                            var listener = capturedListener;
                            var context = capturedContext;

                            if (!context) {
                                context = Java.use("android.app.ActivityThread").currentApplication().getApplicationContext();
                            }

                            console.log("[INJECT] Listener: " + (listener ? listener.$className : "NULL"));
                            console.log("[INJECT] Context: " + (context ? "OK" : "NULL"));

                            if (context && listener) {
                                console.log("[INJECT] *** Calling Node.next() with REAL LISTENER ***");
                                try {
                                    node.next(context, listener);
                                    console.log("[INJECT] *** Node.next() completed ***");
                                } catch (e) {
                                    console.log("[INJECT] Node.next() error: " + e);
                                }
                            } else {
                                // Fallback: search for listener again
                                console.log("[INJECT] Searching for listener...");
                                Java.choose("org.forgerock.android.auth.NodeListener", {
                                    onMatch: function (l) {
                                        if (!listener) {
                                            listener = l;
                                            console.log("[INJECT] Found listener via search");
                                        }
                                    },
                                    onComplete: function () {
                                        if (listener && context) {
                                            console.log("[INJECT] *** Calling Node.next() with found listener ***");
                                            try {
                                                node.next(context, listener);
                                                console.log("[INJECT] *** Node.next() completed ***");
                                            } catch (e) {
                                                console.log("[INJECT] error: " + e);
                                            }
                                        } else {
                                            console.log("[INJECT] NO LISTENER — cannot submit");
                                        }
                                    }
                                });
                            }
                        } catch (e) {
                            console.log("[INJECT] Error: " + e);
                        }
                    },
                    onComplete: function () {
                        if (!foundNode) console.log("[INJECT] No OCR Node found");
                    }
                });
            });
        }
    };

    console.log("[CAP] === Setup complete. Waiting for app flow... ===");
    console.log("[CAP] Listener will be captured from first Node.next() call.");
    console.log("[CAP] Injection will be triggered via rpc.exports.inject().");
});
