Java.perform(function () {
    console.log("[CMP] === Compare AuthId: Resolve vs next() ===");

    var FRB = Java.use("com.bangkokbank.blue.ping.FRAuthBridge");
    var PromiseImpl = Java.use("com.facebook.react.bridge.PromiseImpl");
    var resolveCount = 0;
    var nextCount = 0;

    // Hook PromiseImpl.resolve — capture what JS receives
    PromiseImpl.resolve.implementation = function (value) {
        resolveCount++;
        if (value !== null) {
            var str = value.toString();
            if (str.indexOf("authId") >= 0) {
                // Extract authId length
                var match = str.match(/"authId":"([^"]+)"/);
                if (match) {
                    console.log("[CMP] resolve #" + resolveCount + ": authId=" + match[1].length + " chars, total payload=" + str.length + " chars");
                }
            }
        }
        return this.resolve(value);
    };

    // Hook bridge.next() — capture what JS passes back
    FRB.next.overloads.forEach(function (ov) {
        ov.implementation = function () {
            nextCount++;
            var arg0 = arguments[0] ? arguments[0].toString() : "null";
            var match = arg0.match(/"authId":"([^"]+)"/);
            if (match) {
                console.log("[CMP] next() #" + nextCount + ": authId=" + match[1].length + " chars, total arg=" + arg0.length + " chars");
            } else {
                console.log("[CMP] next() #" + nextCount + ": arg len=" + arg0.length + " (no authId match)");
                console.log("[CMP]   first 200: " + arg0.substring(0, 200));
            }
            return ov.apply(this, arguments);
        };
    });

    console.log("[CMP] Hooks installed — waiting for normal flow...");
});
