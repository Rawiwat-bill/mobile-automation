// Quick diagnostic: find CatalystInstance and evaluateJavaScript method
Java.perform(function () {
    console.log("[FIND] Searching for CatalystInstance...");

    // Method 1: Try ReactContext.getCatalystInstance()
    Java.choose("com.facebook.react.bridge.ReactContext", {
        onMatch: function (ctx) {
            console.log("[FIND] ReactContext found: " + ctx.$className);

            // List all methods
            try {
                var methods = ctx.getClass().getMethods();
                for (var i = 0; i < methods.length; i++) {
                    var mn = methods[i].getName();
                    if (mn.indexOf("Catalyst") >= 0 || mn.indexOf("catalyst") >= 0 ||
                        mn.indexOf("evaluate") >= 0 || mn.indexOf("Eval") >= 0 ||
                        mn.indexOf("JS") >= 0 || mn.indexOf("js") >= 0 ||
                        mn.indexOf("Script") >= 0 || mn.indexOf("script") >= 0 ||
                        mn.indexOf("Hermes") >= 0 || mn.indexOf("hermes") >= 0 ||
                        mn.indexOf("Runtime") >= 0 || mn.indexOf("runtime") >= 0) {
                        var params = methods[i].getParameterTypes();
                        var pStr = [];
                        for (var j = 0; j < params.length; j++) pStr.push(params[j].getName());
                        console.log("[FIND]   Method: " + mn + "(" + pStr.join(", ") + ")");
                    }
                }
            } catch (e) {
                console.log("[FIND] Method listing error: " + e);
            }

            // Try getCatalystInstance via reflection
            try {
                var m = ctx.getClass().getMethod("getCatalystInstance");
                var catalyst = m.invoke(ctx);
                if (catalyst) {
                    console.log("[FIND] Got CatalystInstance via reflection: " + catalyst.$className);
                    // List its methods
                    var cms = catalyst.getClass().getMethods();
                    for (var i = 0; i < cms.length; i++) {
                        var mn = cms[i].getName();
                        if (mn.indexOf("eval") >= 0 || mn.indexOf("Eval") >= 0 ||
                            mn.indexOf("script") >= 0 || mn.indexOf("Script") >= 0 ||
                            mn.indexOf("JS") >= 0 || mn.indexOf("runJS") >= 0) {
                            var params = cms[i].getParameterTypes();
                            var pStr = [];
                            for (var j = 0; j < params.length; j++) pStr.push(params[j].getName());
                            console.log("[FIND]   Catalyst method: " + mn + "(" + pStr.join(", ") + ")");
                        }
                    }
                } else {
                    console.log("[FIND] getCatalystInstance returned null");
                }
            } catch (e) {
                console.log("[FIND] getCatalystInstance error: " + e);
            }
        },
        onComplete: function () {}
    });

    // Method 2: Search for CatalystInstanceImpl directly
    Java.choose("com.facebook.react.bridge.CatalystInstanceImpl", {
        onMatch: function (impl) {
            console.log("[FIND] CatalystInstanceImpl found directly!");
            var ms = impl.getClass().getMethods();
            for (var i = 0; i < ms.length; i++) {
                var mn = ms[i].getName();
                if (mn.indexOf("eval") >= 0 || mn.indexOf("Eval") >= 0) {
                    console.log("[FIND]   Impl method: " + mn);
                }
            }
        },
        onComplete: function () {}
    });

    // Method 3: Search for Hermes runtime
    Java.choose("com.facebook.hermes.reactexecutor.HermesExecutor", {
        onMatch: function (h) {
            console.log("[FIND] HermesExecutor found!");
            var ms = h.getClass().getMethods();
            for (var i = 0; i < ms.length; i++) {
                var mn = ms[i].getName();
                if (mn.indexOf("eval") >= 0 || mn.indexOf("Eval") >= 0 || mn.indexOf("run") >= 0) {
                    console.log("[FIND]   Hermes method: " + mn);
                }
            }
        },
        onComplete: function () {}
    });

    // Method 4: Search for HermesExecutorImpl
    try {
        Java.choose("com.facebook.hermes.reactexecutor.HermesExecutorImpl", {
            onMatch: function (h) {
                console.log("[FIND] HermesExecutorImpl found!");
            },
            onComplete: function () {}
        });
    } catch(e) {}

    console.log("[FIND] Search complete");
});
