// Sprint 2.44: passive FRAuthBridge.next contract capture.
// Logs shape only. No authId, tokens, cookies, PII, or callback values.

Java.perform(function () {
    var JSONObject = Java.use("org.json.JSONObject");
    var JSONArray = Java.use("org.json.JSONArray");
    var FRB = Java.use("com.bangkokbank.blue.ping.FRAuthBridge");
    var callNo = 0;

    function names(itemArray) {
        var out = [];
        for (var i = 0; i < itemArray.length(); i++) {
            try {
                var item = itemArray.getJSONObject(i);
                out.push(item.optString("name", "?"));
            } catch (e) {
                out.push("?");
            }
        }
        return out.join("|");
    }

    FRB.next.overload("java.lang.String", "com.facebook.react.bridge.Promise").implementation = function (response, promise) {
        callNo += 1;
        try {
            var root = JSONObject.$new(response);
            var hasCallbacks = root.has("callbacks");
            console.log("[CONTRACT] call=" + callNo);
            console.log("[CONTRACT] has_authId=" + root.has("authId"));
            console.log("[CONTRACT] has_callbacks=" + hasCallbacks);
            console.log("[CONTRACT] stage=" + (root.has("stage") ? root.optString("stage", "?") : "?"));
            if (hasCallbacks) {
                var callbacks = Java.cast(root.get("callbacks"), JSONArray);
                var types = [];
                console.log("[CONTRACT] callback_count=" + callbacks.length());
                for (var i = 0; i < callbacks.length(); i++) {
                    var cb = callbacks.getJSONObject(i);
                    var type = cb.optString("type", "?");
                    types.push(type);
                    if (cb.has("input")) {
                        console.log("[CONTRACT] callback[" + i + "] type=" + type + " input_names=" + names(cb.getJSONArray("input")));
                    } else {
                        console.log("[CONTRACT] callback[" + i + "] type=" + type + " input_names=");
                    }
                    if (cb.has("output")) {
                        console.log("[CONTRACT] callback[" + i + "] type=" + type + " output_names=" + names(cb.getJSONArray("output")));
                    } else {
                        console.log("[CONTRACT] callback[" + i + "] type=" + type + " output_names=");
                    }
                }
                console.log("[CONTRACT] callback_types=" + types.join("|"));
            } else {
                console.log("[CONTRACT] callback_count=0");
                console.log("[CONTRACT] callback_types=");
            }
        } catch (e) {
            console.log("[CONTRACT] probe_error=" + e);
        }
        return this.next(response, promise);
    };

    console.log("[CONTRACT] probe_installed");
});
