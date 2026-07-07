// Sprint 2.43 — FRAuthBridge.next() Control Flow Analysis
// Hook every method called INSIDE bridge.next() to trace execution path
// Also hook Throwable constructors to capture original exception before wrapping

Java.perform(function () {
    console.log("[FLOW] === FRAuthBridge.next() Control Flow ===");

    var FRB = Java.use("com.bangkokbank.blue.ping.FRAuthBridge");
    var Node = Java.use("org.forgerock.android.auth.Node");

    // === Hook bridge.next() — trace entry + exit ===
    FRB.next.overloads.forEach(function (ov, idx) {
        ov.implementation = function () {
            console.log("\n[FLOW] === bridge.next() ENTRY (overload #" + idx + ") ===");
            console.log("[FLOW] arg0 (authId): type=" + typeof arguments[0] + " len=" + (arguments[0] ? arguments[0].toString().length : 0));

            // Dump ALL fields of this bridge instance
            try {
                var fields = FRB.class.getDeclaredFields();
                console.log("[FLOW] === Bridge state at entry ===");
                fields.forEach(function (f) {
                    try {
                        f.setAccessible(true);
                        var val = f.get(this);
                        var valStr = val === null ? "null" : val.toString().substring(0, 80);
                        console.log("[FLOW]   " + f.getName() + " (" + f.getType().getSimpleName() + ") = " + valStr);
                    } catch (e) {}
                }, this);
            } catch (e) {}

            try {
                var result = ov.apply(this, arguments);
                console.log("[FLOW] === bridge.next() EXIT — SUCCESS ===");
                return result;
            } catch (e) {
                console.log("[FLOW] === bridge.next() EXIT — THREW: " + e + " ===");
                throw e;
            }
        };
    });
    console.log("[FLOW] bridge.next() hooked");

    // === Hook ALL methods on FRAuthBridge to trace what next() calls internally ===
    var allMethods = FRB.class.getDeclaredMethods();
    var methodNames = new Set();
    allMethods.forEach(function (m) {
        var name = m.getName();
        // Skip access$ methods and already-hooked methods
        if (name.indexOf("access$") >= 0 || name === "next" || name === "getName") return;
        if (methodNames.has(name)) return;
        methodNames.add(name);

        try {
            FRB[name].overloads.forEach(function (ov) {
                var mName = name;
                ov.implementation = function () {
                    console.log("[CALL] " + mName + "(" + arguments.length + " args)");
                    // Log arg types
                    for (var i = 0; i < Math.min(arguments.length, 3); i++) {
                        if (arguments[i]) {
                            var s = arguments[i].toString();
                            if (s.length > 100) s = s.substring(0, 100) + "...";
                            console.log("[CALL]   arg" + i + ": " + s);
                        } else {
                            console.log("[CALL]   arg" + i + ": null");
                        }
                    }
                    try {
                        var r = ov.apply(this, arguments);
                        if (r !== undefined && r !== null) {
                            var rs = r.toString();
                            if (rs.length > 100) rs = rs.substring(0, 100) + "...";
                            console.log("[CALL] " + mName + " → " + rs);
                        } else {
                            console.log("[CALL] " + mName + " → void/null");
                        }
                        return r;
                    } catch (e) {
                        console.log("[CALL] " + mName + " → THREW: " + e);
                        throw e;
                    }
                };
            });
        } catch (e) {}
    });
    console.log("[FLOW] Hooked " + methodNames.size + " FRAuthBridge methods");

    // === Hook Throwable constructors — capture ORIGINAL exception ===
    var Throwable = Java.use("java.lang.Throwable");
    Throwable.$init.overload("java.lang.String").implementation = function (msg) {
        if (msg && (msg.indexOf("Pars") >= 0 || msg.indexOf("pars") >= 0 || msg.indexOf("GOD") >= 0)) {
            console.log("\n[THROW] *** Throwable(\"" + msg + "\") ***");
            console.log("[THROW] Class: " + this.$className);
            var stack = this.getStackTrace();
            console.log("[THROW] Stack (" + stack.length + "):");
            for (var i = 0; i < Math.min(stack.length, 20); i++) {
                console.log("[THROW]   " + stack[i].toString());
            }
            // Cause chain
            var cause = this.getCause();
            var depth = 0;
            while (cause && depth < 5) {
                depth++;
                console.log("[THROW] Caused by: " + cause.toString());
                var cs = cause.getStackTrace();
                for (var j = 0; j < Math.min(cs.length, 15); j++) {
                    console.log("[THROW]   " + cs[j].toString());
                }
                cause = cause.getCause();
            }
        }
        return this.$init(msg);
    };

    // Also hook Throwable(String, Throwable) — wraps a cause
    Throwable.$init.overload("java.lang.String", "java.lang.Throwable").implementation = function (msg, cause) {
        if (msg && (msg.indexOf("Pars") >= 0 || msg.indexOf("pars") >= 0)) {
            console.log("\n[THROW] *** Throwable(\"" + msg + "\", cause) ***");
            console.log("[THROW] Class: " + this.$className);
            console.log("[THROW] Cause: " + cause);
            if (cause) {
                var cs = cause.getStackTrace();
                console.log("[THROW] Cause stack (" + cs.length + "):");
                for (var j = 0; j < Math.min(cs.length, 20); j++) {
                    console.log("[THROW]   " + cs[j].toString());
                }
            }
        }
        return this.$init(msg, cause);
    };

    // Hook Throwable(Throwable) — wraps cause without message
    Throwable.$init.overload("java.lang.Throwable").implementation = function (cause) {
        if (cause) {
            var cmsg = cause.getMessage();
            if (cmsg && (cmsg.indexOf("Pars") >= 0 || cmsg.indexOf("pars") >= 0)) {
                console.log("\n[THROW] *** Throwable(cause: " + cause + ") ***");
                var cs = cause.getStackTrace();
                console.log("[THROW] Cause stack (" + cs.length + "):");
                for (var j = 0; j < Math.min(cs.length, 20); j++) {
                    console.log("[THROW]   " + cs[j].toString());
                }
            }
        }
        return this.$init(cause);
    };

    console.log("[THROW] Throwable constructors hooked");

    // === Hook IllegalArgumentException specifically ===
    var IAE = Java.use("java.lang.IllegalArgumentException");
    IAE.$init.overload("java.lang.String").implementation = function (msg) {
        console.log("\n[IAE] *** IllegalArgumentException(\"" + msg + "\") ***");
        var stack = Java.use("java.lang.Thread").currentThread().getStackTrace();
        console.log("[IAE] Thread stack (" + stack.length + "):");
        for (var i = 0; i < Math.min(stack.length, 25); i++) {
            console.log("[IAE]   " + stack[i].toString());
        }
        return this.$init(msg);
    };

    console.log("[FLOW] All hooks installed. Waiting for bridge.next()...");
});
