// Sprint 2.40 — Capture authId lengths at each bridge.next() call
// Also: late-attach, fill callbacks, try Node.next with real listener

Java.perform(function () {
    console.log("[CAP] === AuthId Length Capture ===");

    var FRB = Java.use("com.bangkokbank.blue.ping.FRAuthBridge");
    var callCount = 0;
    var lastAuthIdJson = null;

    FRB.next.overloads.forEach(function (overload) {
        overload.implementation = function () {
            callCount++;
            var authIdArg = arguments[0] ? arguments[0].toString() : "null";
            console.log("[CAP] bridge.next() #" + callCount + " — authId length: " + authIdArg.length);
            // Store the last authId (from the call BEFORE OCR)
            if (authIdArg.length > 10) {
                lastAuthIdJson = authIdArg;
            }
            return overload.apply(this, arguments);
        };
    });
    console.log("[CAP] bridge.next() hooked");

    // After flow completes, show the last authId
    // This will be the authId used for the OCR stage submission
    rpc = {
        getLastAuthId: function () {
            return lastAuthIdJson;
        }
    };
});
