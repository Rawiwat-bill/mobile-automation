// Sprint 2.63 — Real Promise Capture
// Trace ALL FRAuthBridge.next(responseJson, promise) calls.
// Log promise class/hash/thread/callbackID per stage.
// Track PromiseImpl lifecycle (create/resolve/reject).
// Prove whether Take Photo creates any new promise.

Java.perform(function () {
    console.log("[TRACE] === Promise Tracing Installed ===");

    var FRB = Java.use("com.bangkokbank.blue.ping.FRAuthBridge");
    var PromiseImpl = Java.use("com.facebook.react.bridge.PromiseImpl");
    var CallbackImpl = Java.use("com.facebook.react.bridge.CallbackImpl");
    var Thread = Java.use("java.lang.Thread");

    var nextCallCount = 0;
    var promiseRegistry = {};   // hash → { stage, thread, resolveCb, rejectCb, resolved, rejected }
    var callbackRegistry = {};  // callbackId → { type, createdAt, thread }

    // Helper: inspect a Callback object — defensive against non-standard objects
    function inspectCallback(cb) {
        if (!cb) return "null";
        try {
            var cls = cb.$className || "?";
            var hash = "?";
            try { hash = cb.hashCode(); } catch (e) {}
            var info = cls + " hash=" + hash;
            if (cls.indexOf("Callback") >= 0) {
                try {
                    var ci = Java.cast(cb, CallbackImpl);
                    try {
                        var cbId = ci.mCallbackID.value;
                        info += " callbackId=" + cbId;
                    } catch (e) {}
                } catch (e) {}
            }
            return info;
        } catch (e) {
            return "inspectError: " + e;
        }
    }

    // === HOOK 1: PromiseImpl constructor ===
    PromiseImpl.$init.overload(
        "com.facebook.react.bridge.Callback",
        "com.facebook.react.bridge.Callback"
    ).implementation = function (resolve, reject) {
        var original = PromiseImpl.$init.overload(
            "com.facebook.react.bridge.Callback",
            "com.facebook.react.bridge.Callback"
        );
        try {
            var hash = "?";
            try { hash = this.hashCode(); } catch (e) {}
            var thread = "?";
            try { thread = Thread.currentThread().getName(); } catch (e) {}
            var resolveInfo = inspectCallback(resolve);
            var rejectInfo = inspectCallback(reject);

            console.log("[PROMISE.NEW] hash=" + hash + " thread=" + thread);
            console.log("  resolve: " + resolveInfo);
            console.log("  reject: " + rejectInfo);

            promiseRegistry[hash] = {
                createdAt: Date.now(),
                thread: thread,
                resolveCb: resolveInfo,
                rejectCb: rejectInfo,
                resolved: false,
                rejected: false,
                stage: "?"
            };
        } catch (e) {
            console.log("[PROMISE.NEW] error: " + e);
        }
        return original.call(this, resolve, reject);
    };

    // === HOOK 2: FRAuthBridge.next(String, Promise) ===
    FRB.next.overload("java.lang.String", "com.facebook.react.bridge.Promise").implementation = function (json, promise) {
        var original = FRB.next.overload("java.lang.String", "com.facebook.react.bridge.Promise");
        nextCallCount++;
        var stage = "?";
        try { var m = json.substring(0, 10000).match(/"stage"\s*:\s*"([^"]+)"/); if (m) stage = m[1]; } catch (e) {}

        var thread = Thread.currentThread().getName();
        var promiseHash = promise.hashCode();
        var promiseClass = promise.$className;

        // Inspect promise internals
        var resolveInfo = "?";
        var rejectInfo = "?";
        try {
            var pi = Java.cast(promise, PromiseImpl);
            resolveInfo = inspectCallback(pi.mResolve.value);
            rejectInfo = inspectCallback(pi.mReject.value);
        } catch (e) {
            resolveInfo = "not PromiseImpl (" + e + ")";
        }

        // Link promise to stage
        if (promiseRegistry[promiseHash]) {
            promiseRegistry[promiseHash].stage = stage;
        }

        console.log("\n[BRIDGE.NEXT] #" + nextCallCount + " ──────────────────");
        console.log("  stage:       " + stage);
        console.log("  thread:      " + thread);
        console.log("  promiseCls:  " + promiseClass);
        console.log("  promiseHash: " + promiseHash);
        console.log("  resolve:     " + resolveInfo);
        console.log("  reject:      " + rejectInfo);
        console.log("  jsonLen:     " + json.length);

        return original.call(this, json, promise);
    };

    // === HOOK 3: PromiseImpl.resolve(Object) ===
    PromiseImpl.resolve.overload("java.lang.Object").implementation = function (value) {
        var original = PromiseImpl.resolve.overload("java.lang.Object");
        var hash = this.hashCode();
        var entry = promiseRegistry[hash];
        var valLen = 0;
        var valStage = "";

        if (value) {
            try {
                var s = value.toString();
                valLen = s.length;
                var m = s.substring(0, 500).match(/"stage"\s*:\s*"([^"]+)"/);
                if (m) valStage = m[1];
            } catch (e) {}
        }

        if (entry) {
            entry.resolved = true;
            console.log("[RESOLVE] hash=" + hash + " stage=" + entry.stage +
                        " valLen=" + valLen + (valStage ? " valStage=" + valStage : "") +
                        " elapsed=" + (Date.now() - entry.createdAt) + "ms");
        } else {
            console.log("[RESOLVE] hash=" + hash + " (untracked) valLen=" + valLen);
        }
        return original.call(this, value);
    };

    // === HOOK 4: PromiseImpl.reject ===
    try {
        PromiseImpl.reject.overloads.forEach(function (ov) {
            ov.implementation = function () {
                var hash = this.hashCode();
                var entry = promiseRegistry[hash];
                var args = [];
                for (var i = 0; i < arguments.length; i++)
                    args.push(arguments[i] ? arguments[i].toString().substring(0, 80) : "null");

                if (entry) {
                    entry.rejected = true;
                    console.log("[REJECT] hash=" + hash + " stage=" + entry.stage + " args=" + args.join(" | "));
                } else {
                    console.log("[REJECT] hash=" + hash + " (untracked) args=" + args.join(" | "));
                }
                return ov.call.apply(ov, [this].concat(Array.prototype.slice.call(arguments)));
            };
        });
    } catch (e) { console.log("[TRACE] reject hook error: " + e); }

    // === HOOK 5: CallbackImpl constructor ===
    try {
        CallbackImpl.$init.overload("com.facebook.react.bridge.queue.JSInstance", "int")
            .implementation = function (jsInstance, callbackId) {
                var original = CallbackImpl.$init.overload("com.facebook.react.bridge.queue.JSInstance", "int");
                var thread = Thread.currentThread().getName();
                var jsiClass = jsInstance ? jsInstance.$className : "null";
                console.log("[CALLBACK.NEW] id=" + callbackId + " thread=" + thread + " jsiClass=" + jsiClass);
                callbackRegistry[callbackId] = { thread: thread, jsiClass: jsiClass };
                return original.call(this, jsInstance, callbackId);
            };
    } catch (e) {
        // Try alternative constructor
        try {
            CallbackImpl.$init.overloads.forEach(function(ov) {
                ov.implementation = function() {
                    var thread = Thread.currentThread().getName();
                    console.log("[CALLBACK.NEW] thread=" + thread + " args=" + arguments.length);
                    return ov.call.apply(ov, [this].concat(Array.prototype.slice.call(arguments)));
                };
            });
        } catch(e2) {
            console.log("[TRACE] CallbackImpl hook error: " + e2);
        }
    }

    // === HOOK 6: HTTP tracking ===
    try {
        Java.use("org.forgerock.android.auth.AuthServiceClient$2").onResponse.implementation = function (c, r) {
            var original = Java.use("org.forgerock.android.auth.AuthServiceClient$2").onResponse;
            try {
                var code = r.code();
                var body = r.peekBody(2097152).string();
                var sm = body.match(/"stage"\s*:\s*"([^"]+)"/);
                console.log("[HTTP] " + code + " stage=" + (sm ? sm[1] : "?"));
            } catch (e) {}
            return original.call(this, c, r);
        };
    } catch (e) {}

    // === SUMMARY at 120s ===
    setTimeout(function () {
        Java.perform(function () {
            console.log("\n[TRACE] === 120s SUMMARY ===");
            console.log("[TRACE] bridge.next calls: " + nextCallCount);
            console.log("[TRACE] Promises created: " + Object.keys(promiseRegistry).length);
            var unresolved = 0;
            for (var h in promiseRegistry) {
                var e = promiseRegistry[h];
                if (!e.resolved && !e.rejected) {
                    unresolved++;
                    console.log("[TRACE] UNRESOLVED promise hash=" + h + " stage=" + e.stage + " thread=" + e.thread);
                    console.log("  resolve: " + e.resolveCb);
                    console.log("  reject: " + e.rejectCb);
                }
            }
            console.log("[TRACE] Unresolved: " + unresolved);
            console.log("[TRACE] Callbacks created: " + Object.keys(callbackRegistry).length);
        });
    }, 120000);

    console.log("[TRACE] Hooks ready. Flow through all stages to capture promise lifecycle.");
});
