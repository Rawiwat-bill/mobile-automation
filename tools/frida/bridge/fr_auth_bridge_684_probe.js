// Sprint 2.43: passive FRAuthBridge.next argument/catch probe.
// No response mutation, no OCR payload mutation.

Java.perform(function () {
    function s(v) {
        try { return v === null || v === undefined ? "null" : v.toString(); }
        catch (e) { return "<toString failed>"; }
    }

    function logThrowable(prefix, t) {
        try {
            console.log("[FR684] " + prefix + "_class=" + t.$className);
            console.log("[FR684] " + prefix + "_message=" + s(t.getMessage()));
            var cause = t.getCause ? t.getCause() : null;
            console.log("[FR684] " + prefix + "_cause=" + (cause ? (cause.$className + ": " + s(cause.getMessage())) : "null"));
            var st = t.getStackTrace();
            for (var i = 0; i < Math.min(st.length, 12); i++) {
                console.log("[FR684] " + prefix + "_stack " + st[i].toString());
            }
        } catch (e) {
            console.log("[FR684] " + prefix + "_log_failed=" + e);
        }
    }

    var JSONObject = Java.use("org.json.JSONObject");
    var JSONArray = Java.use("org.json.JSONArray");
    var FRB = Java.use("com.bangkokbank.blue.ping.FRAuthBridge");

    FRB.next.overload("java.lang.String", "com.facebook.react.bridge.Promise").implementation = function (response, promise) {
        console.log("[FR684] next_enter response_length=" + response.length);
        try {
            var root = JSONObject.$new(response);
            console.log("[FR684] keys=" + s(root.keys()));
            console.log("[FR684] has_authId=" + root.has("authId"));
            console.log("[FR684] has_callbacks=" + root.has("callbacks"));
            if (root.has("stage")) console.log("[FR684] stage=" + root.optString("stage", "?"));
            if (root.has("callbacks")) {
                var callbacks = Java.cast(root.get("callbacks"), JSONArray);
                console.log("[FR684] callback_count=" + callbacks.length());
                for (var i = 0; i < Math.min(callbacks.length(), 8); i++) {
                    var cb = callbacks.getJSONObject(i);
                    console.log("[FR684] callback[" + i + "].type=" + cb.optString("type", "?") + " has_input=" + cb.has("input"));
                }
            }
        } catch (e) {
            console.log("[FR684] response_json_probe_error=" + e);
        }
        try {
            return this.next(response, promise);
        } catch (e) {
            logThrowable("next_throw", e);
            throw e;
        }
    };

    ["java.lang.IllegalArgumentException", "java.lang.RuntimeException", "com.google.gson.JsonParseException", "com.google.gson.JsonSyntaxException"].forEach(function (name) {
        try {
            var C = Java.use(name);
            C.$init.overloads.forEach(function (ov) {
                ov.implementation = function () {
                    var ret = ov.apply(this, arguments);
                    var msg = null;
                    try { msg = this.getMessage(); } catch (e) {}
                    if (s(msg).indexOf("Parsing response failed") >= 0) logThrowable("constructed", this);
                    return ret;
                };
            });
            console.log("[FR684] hooked=" + name);
        } catch (e) {
            console.log("[FR684] hook_failed=" + name + " " + e);
        }
    });

    console.log("[FR684] probe_installed");
});
