// Sprint 2.39 — Capture real authId from HTTP response
// Compare with node.getAuthId()

Java.perform(function () {
    console.log("[CAP] === AuthId Capture ===");

    var capturedAuthId = null;

    // Hook ASC response — capture authId from each stage response
    try {
        var ASC1 = Java.use("org.forgerock.android.auth.AuthServiceClient$1");
        ASC1.onResponse.implementation = function (call, response) {
            try {
                var body = response.peekBody(2097152).string();
                if (body.indexOf('"authId"') >= 0) {
                    // Extract authId
                    var match = body.match(/"authId"\s*:\s*"([^"]+)"/);
                    if (match) {
                        capturedAuthId = match[1];
                        var stageMatch = body.match(/"stage"\s*:\s*"([^"]+)"/);
                        var stage = stageMatch ? stageMatch[1] : "?";
                        console.log("[CAP] Stage=" + stage + " authId length=" + capturedAuthId.length + " prefix=[MASKED]");
                    }
                }
            } catch (e) {}
            return this.onResponse(call, response);
        };
        console.log("[CAP] ASC1 hooked");
    } catch (e) {}

    try {
        var ASC2 = Java.use("org.forgerock.android.auth.AuthServiceClient$2");
        ASC2.onResponse.implementation = function (call, response) {
            try {
                var body = response.peekBody(2097152).string();
                if (body.indexOf('"authId"') >= 0) {
                    var match = body.match(/"authId"\s*:\s*"([^"]+)"/);
                    if (match) {
                        capturedAuthId = match[1];
                        var stageMatch = body.match(/"stage"\s*:\s*"([^"]+)"/);
                        var stage = stageMatch ? stageMatch[1] : "?";
                        console.log("[CAP2] Stage=" + stage + " authId length=" + capturedAuthId.length);
                    }
                }
            } catch (e) {}
            return this.onResponse(call, response);
        };
        console.log("[CAP] ASC2 hooked");
    } catch (e) {}

    // Poll: when OCR Node is found, compare authId sources
    var injected = false;
    var pollCount = 0;
    setInterval(function () {
        pollCount++;
        if (injected) return;

        Java.perform(function () {
            Java.choose("org.forgerock.android.auth.Node", {
                onMatch: function (node) {
                    if (injected) return;
                    try {
                        if (node.getStage() !== "OCR") return;
                        injected = true;

                        var nodeAuthId = node.getAuthId();
                        console.log("\n[COMPARE] === AUTHID COMPARISON ===");
                        console.log("[COMPARE] node.getAuthId() length: " + nodeAuthId.length);
                        console.log("[COMPARE] HTTP response authId length: " + (capturedAuthId ? capturedAuthId.length : "null"));

                        if (capturedAuthId) {
                            var same = nodeAuthId === capturedAuthId;
                            console.log("[COMPARE] Same value: " + same);

                            if (!same) {
                                console.log("[COMPARE] *** AUTHID MISMATCH! ***");
                                console.log("[COMPARE] Using HTTP authId for bridge.next()");

                                // Fill callbacks
                                var TIC = Java.use("org.forgerock.android.auth.callback.TextInputCallback");
                                var CC = Java.use("org.forgerock.android.auth.callback.ChoiceCallback");
                                var cbs = node.getCallbacks();
                                Java.cast(cbs.get(0), CC).setSelectedIndex(0);
                                Java.cast(cbs.get(1), TIC).setValue(B64_IMG);
                                console.log("[COMPARE] Callbacks filled");

                                // Build authId JSON with HTTP-captured authId
                                var authIdJson = JSON.stringify({authId: capturedAuthId});
                                console.log("[COMPARE] authIdJson length: " + authIdJson.length);

                                // Create mock Promise
                                var PromiseCls = Java.use("com.facebook.react.bridge.Promise");
                                var Proxy = Java.use("java.lang.reflect.Proxy");
                                var IH = Java.use("java.lang.reflect.InvocationHandler");
                                var PH = Java.registerClass({
                                    name: "com.frida.CMP" + Date.now(),
                                    implements: [IH],
                                    methods: { invoke: function(p, m, a) {
                                        console.log("[PROMISE] " + m.getName());
                                        if (m.getName() === "reject" && a) {
                                            for (var i = 0; i < a.length; i++) {
                                                if (a[i]) console.log("[PROMISE]   arg" + i + ": " + a[i].toString().substring(0, 150));
                                            }
                                        }
                                        if (m.getName() === "resolve") {
                                            console.log("[PROMISE] *** RESOLVED! ***");
                                        }
                                        return null;
                                    }}
                                });
                                var mockPromise = Proxy.newProxyInstance(
                                    PromiseCls.class.getClassLoader(),
                                    Java.array("java.lang.Class", [PromiseCls.class]),
                                    PH.$new()
                                );

                                // Call bridge.next with HTTP authId
                                Java.choose("com.bangkokbank.blue.ping.FRAuthBridge", {
                                    onMatch: function (bridge) {
                                        console.log("[COMPARE] *** CALLING bridge.next(HTTP_authId) ***");
                                        try {
                                            bridge.next(authIdJson, mockPromise);
                                            console.log("[COMPARE] bridge.next() returned");
                                        } catch (e) {
                                            console.log("[COMPARE] error: " + e);
                                        }
                                    },
                                    onComplete: function () { console.log("[COMPARE-COMPLETE]"); }
                                });
                            } else {
                                console.log("[COMPARE] Same authId — node.getAuthId() is correct");
                                console.log("[COMPARE] Issue is elsewhere");
                            }
                        }
                    } catch (e) { console.log("[COMPARE] error: " + e); }
                },
                onComplete: function () {}
            });
        });
        if (pollCount > 36) return;
    }, 5000);

    console.log("[CAP] Polling started");
});

var B64_IMG = "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";
