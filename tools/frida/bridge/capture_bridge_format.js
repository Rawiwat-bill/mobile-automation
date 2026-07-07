// Capture bridge.next() argument format during normal flow
Java.perform(function () {
    console.log("[FMT] === Bridge.next() Format Capture ===");

    var FRB = Java.use("com.bangkokbank.blue.ping.FRAuthBridge");

    // Hook ALL overloads of next()
    FRB.next.overloads.forEach(function (overload) {
        overload.implementation = function () {
            console.log("[FMT] bridge.next() called");
            console.log("[FMT] arg count: " + arguments.length);

            // Log the first argument (callback values string)
            if (arguments.length > 0 && arguments[0]) {
                var arg0 = arguments[0].toString();
                console.log("[FMT] arg0 type: " + typeof arg0);
                console.log("[FMT] arg0 length: " + arg0.length);
                // Log first 300 chars
                console.log("[FMT] arg0 value: " + arg0.substring(0, 300));
                if (arg0.length > 300) console.log("[FMT] ...(total " + arg0.length + " chars)");
            }

            // Log the second argument (promise)
            if (arguments.length > 1) {
                console.log("[FMT] arg1 type: " + (arguments[1] ? arguments[1].$className : "null"));
            }

            // Call original
            return overload.apply(this, arguments);
        };
    });
    console.log("[FMT] bridge.next() hooked — waiting for app flow...");
});
