// Sprint 2.60 Diagnostic — Check if Take Photo triggers bridge.next()
// Also captures module name and OCR Response for later use

Java.perform(function () {
    console.log("[DIAG] === Diagnostic Start ===");

    var FRB = Java.use("com.bangkokbank.blue.ping.FRAuthBridge");
    var Node = Java.use("org.forgerock.android.auth.Node");

    // === Get module name ===
    try {
        Java.choose("com.bangkokbank.blue.ping.FRAuthBridge", {
            onMatch: function (b) {
                try {
                    var name = b.getName();
                    console.log("[DIAG] RN Module name: " + name);
                } catch(e) { console.log("[DIAG] getName error: " + e); }
            },
            onComplete: function() {}
        });
    } catch(e) {}

    // === HOOK: bridge.next — log ALL calls ===
    var nextCallCount = 0;
    try {
        FRB.next.overload("java.lang.String", "com.facebook.react.bridge.Promise").implementation = function (json, promise) {
            nextCallCount++;
            var stage = "?";
            try {
                var sm = json.substring(0, 5000).match(/"stage"\s*:\s*"([^"]+)"/);
                if (sm) stage = sm[1];
            } catch(e) {}
            console.log("[BRIDGE.NEXT] #" + nextCallCount + " stage=" + stage + " jsonLen=" + json.length);
            return this.next(json, promise);
        };
        console.log("[DIAG] bridge.next() hooked");
    } catch(e) { console.log("[DIAG] bridge.next hook error: " + e); }

    // === HOOK: Node.next — log ALL calls ===
    var nodeNextCount = 0;
    try {
        Node.next.overload("android.content.Context", "org.forgerock.android.auth.NodeListener").implementation = function (ctx, listener) {
            nodeNextCount++;
            var stage = "?";
            try { stage = this.getStage(); } catch(e) {}
            console.log("[NODE.NEXT] #" + nodeNextCount + " stage=" + stage);
            return this.next(ctx, listener);
        };
        console.log("[DIAG] Node.next() hooked");
    } catch(e) { console.log("[DIAG] Node.next hook error: " + e); }

    // === HOOK: PromiseImpl.resolve — track stages ===
    try {
        var PI = Java.use("com.facebook.react.bridge.PromiseImpl");
        PI.resolve.overload("java.lang.Object").implementation = function(value) {
            if (value !== null) {
                try {
                    var str = value.toString();
                    if (str.indexOf('"stage"') >= 0) {
                        var sm = str.match(/"stage":"([^"]+)"/);
                        console.log("[RESOLVE] stage=" + (sm ? sm[1] : "?") + " len=" + str.length);
                    }
                } catch(e) {}
            }
            return this.resolve(value);
        };
    } catch(e) {}

    // === HOOK: ASC2 — HTTP tracking ===
    try {
        Java.use("org.forgerock.android.auth.AuthServiceClient$2").onResponse.implementation = function (c, r) {
            try {
                var body = r.peekBody(2097152).string();
                var sm = body.match(/"stage"\s*:\s*"([^"]+)"/);
                console.log("[HTTP] " + r.code() + " stage=" + (sm ? sm[1] : "?"));
            } catch (e) {}
            return this.onResponse(c, r);
        };
    } catch (e) {}

    // === Summary after 60s ===
    setTimeout(function() {
        console.log("\n[DIAG] === 60s SUMMARY ===");
        console.log("[DIAG] bridge.next calls: " + nextCallCount);
        console.log("[DIAG] Node.next calls: " + nodeNextCount);
    }, 60000);

    console.log("[DIAG] Hooks installed");
});
