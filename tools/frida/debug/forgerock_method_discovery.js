// ForgeRock SDK Class & Method Discovery
// Attaches to NCBD-DEV, enumerates all ForgeRock classes and their methods
// Searches for submission-related method names

Java.perform(function () {
    console.log("[DISCOVERY] === ForgeRock SDK Method Discovery ===");

    var submitKeywords = [
        "next", "submit", "proceed", "continue", "login", "authenticate",
        "send", "resume", "callback", "finalize", "advance", "invoke",
        "request", "response", "process", "handle", "execute", "start"
    ];

    var forgeRockClasses = [];
    var candidateMethods = [];

    // ==========================================
    // 1. Enumerate ALL ForgeRock-related classes
    // ==========================================
    Java.enumerateLoadedClasses({
        onMatch: function (className) {
            if (className.indexOf("org.forgerock") >= 0 ||
                className.indexOf("com.forgerock") >= 0 ||
                className.indexOf("ForgeRock") >= 0 ||
                className.indexOf("frsdk") >= 0) {
                forgeRockClasses.push(className);
            }
        },
        onComplete: function () {
            console.log("[DISCOVERY] Found " + forgeRockClasses.length + " ForgeRock classes");

            // ==========================================
            // 2. Enumerate methods for each class
            // ==========================================
            forgeRockClasses.forEach(function (className) {
                try {
                    var cls = Java.use(className);
                    var methods = cls.class.getDeclaredMethods();

                    var methodNames = [];
                    methods.forEach(function (method) {
                        var mname = method.getName();
                        var msig = method.toGenericString();
                        methodNames.push(mname);

                        // Check if method name matches submission keywords
                        var lowerName = mname.toLowerCase();
                        for (var i = 0; i < submitKeywords.length; i++) {
                            if (lowerName.indexOf(submitKeywords[i]) >= 0) {
                                candidateMethods.push({
                                    className: className,
                                    methodName: mname,
                                    signature: msig.substring(0, 200),
                                    keyword: submitKeywords[i]
                                });
                                break;
                            }
                        }
                    });

                    // Log class with its methods
                    if (methodNames.length > 0) {
                        console.log("[CLASS] " + className + " (" + methodNames.length + " methods)");
                        methodNames.forEach(function (mn) {
                            console.log("  ." + mn);
                        });
                    }
                } catch (e) {
                    console.log("[CLASS-ERR] " + className + ": " + e);
                }
            });

            // ==========================================
            // 3. Print candidate submission methods
            // ==========================================
            console.log("\n[DISCOVERY] === CANDIDATE SUBMISSION METHODS ===");
            console.log("[DISCOVERY] Found " + candidateMethods.length + " candidates:\n");

            candidateMethods.forEach(function (c, idx) {
                console.log("[CANDIDATE " + (idx + 1) + "] keyword='" + c.keyword + "'");
                console.log("  Class: " + c.className);
                console.log("  Method: " + c.methodName);
                console.log("  Signature: " + c.signature);
                console.log("");
            });

            // ==========================================
            // 4. Hook ALL candidate methods for logging
            // ==========================================
            console.log("[DISCOVERY] === INSTALLING LOGGING HOOKS ===");

            candidateMethods.forEach(function (c) {
                try {
                    var cls = Java.use(c.className);
                    var overloads = cls[c.methodName].overloads;
                    if (overloads && overloads.length > 0) {
                        overloads.forEach(function (overload) {
                            overload.implementation = function () {
                                console.log("[CALL] " + c.className + "." + c.methodName + "()");
                                // Log arguments
                                for (var i = 0; i < arguments.length; i++) {
                                    var arg = arguments[i];
                                    var argStr = "null";
                                    if (arg !== null && arg !== undefined) {
                                        try { argStr = arg.toString().substring(0, 150); } catch(e) {}
                                    }
                                    console.log("  arg" + i + ": " + argStr);
                                }
                                var result = overload.apply(this, arguments);
                                if (result !== undefined) {
                                    try {
                                        console.log("  => " + result.toString().substring(0, 150));
                                    } catch(e) {
                                        console.log("  => (void)");
                                    }
                                }
                                return result;
                            };
                        });
                        console.log("[HOOKED] " + c.className + "." + c.methodName);
                    }
                } catch (e) {
                    console.log("[HOOK-FAIL] " + c.className + "." + c.methodName + ": " + e);
                }
            });

            console.log("\n[DISCOVERY] === ALL HOOKS INSTALLED ===");
            console.log("[DISCOVERY] Tap 'Take Photo' or interact to trigger methods.");
            console.log("[DISCOVERY] Monitor this log for [CALL] entries.");
        }
    });
});
