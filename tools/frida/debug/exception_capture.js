// Sprint 2.42 — GOD-017 Exception Root Cause Discovery
// Evidence only: no response mutation, no callback filling, no SDK behavior changes.

Java.perform(function () {
    var Thread = Java.use("java.lang.Thread");
    var Throwable = Java.use("java.lang.Throwable");
    var JSONObject = Java.use("org.json.JSONObject");
    var contextStack = [];
    var seen = {};

    function nowContext() {
        return contextStack.length ? contextStack[contextStack.length - 1] : null;
    }

    function safeString(v, max) {
        try {
            if (v === null || v === undefined) return "null";
            var s = v.toString();
            if (max && s.length > max) return s.substring(0, max) + "...(" + s.length + ")";
            return s;
        } catch (e) {
            return "<toString failed: " + e + ">";
        }
    }

    function stackLines(t) {
        var st;
        try {
            st = t && t.getStackTrace ? t.getStackTrace() : Thread.currentThread().getStackTrace();
        } catch (e) {
            st = Thread.currentThread().getStackTrace();
        }
        var lines = [];
        for (var i = 0; i < st.length; i++) lines.push(st[i].toString());
        return lines;
    }

    function jsonKeys(json) {
        var keys = [];
        try {
            var it = json.keys();
            while (it.hasNext()) keys.push(it.next().toString());
        } catch (e) {}
        return keys;
    }

    function callbackType(json) {
        try { return json.getString("type"); } catch (e) { return "NO_TYPE"; }
    }

    function shortCallback(json) {
        if (!json) return "none";
        var keys = jsonKeys(json);
        return "type=" + callbackType(json) + " keys=[" + keys.join(",") + "]";
    }

    function pushContext(label, json) {
        contextStack.push({
            label: label,
            callbackType: callbackType(json),
            keys: jsonKeys(json),
            lastJsonField: null,
            json: json
        });
    }

    function popContext() {
        contextStack.pop();
    }

    function maybeFieldFromMessage(msg) {
        if (!msg) return "?";
        var patterns = [
            /No value for ([A-Za-z0-9_.$-]+)/,
            /JSONObject\["([^"]+)"\]/,
            /field ['"]([^'"]+)['"]/i,
            /name ['"]([^'"]+)['"]/i
        ];
        for (var i = 0; i < patterns.length; i++) {
            var m = ("" + msg).match(patterns[i]);
            if (m) return m[1];
        }
        var ctx = nowContext();
        return ctx && ctx.lastJsonField ? ctx.lastJsonField : "?";
    }

    function shouldLog(className, msg) {
        var text = (className + " " + (msg || "")).toLowerCase();
        return text.indexOf("parsing response failed") >= 0 ||
            text.indexOf("parse") >= 0 ||
            text.indexOf("json") >= 0 ||
            text.indexOf("serialization") >= 0 ||
            text.indexOf("god-017") >= 0 ||
            nowContext() !== null;
    }

    function logThrowable(tag, className, message, throwable) {
        if (!shouldLog(className, message)) return;

        var lines = stackLines(throwable);
        var key = tag + "|" + className + "|" + message + "|" + lines.slice(0, 8).join("|");
        if (seen[key]) return;
        seen[key] = true;

        var ctx = nowContext();
        console.log("\n[GOD017] === " + tag + " ===");
        console.log("[GOD017] exception_class=" + className);
        console.log("[GOD017] message=" + safeString(message, 500));
        console.log("[GOD017] parser_context=" + (ctx ? ctx.label : "none"));
        console.log("[GOD017] offending_callback_type=" + (ctx ? ctx.callbackType : "?"));
        console.log("[GOD017] offending_json_field=" + maybeFieldFromMessage(message));
        console.log("[GOD017] callback_keys=" + (ctx ? ctx.keys.join(",") : "?"));
        console.log("[GOD017] full_stack_trace_begin");
        for (var i = 0; i < lines.length; i++) console.log("[GOD017]   " + lines[i]);
        console.log("[GOD017] full_stack_trace_end");
    }

    function hookThrowableConstructors(className) {
        try {
            var C = Java.use(className);
            C.$init.overloads.forEach(function (ov) {
                ov.implementation = function () {
                    var ret = ov.apply(this, arguments);
                    var msg = null;
                    try { msg = this.getMessage(); } catch (e) {}
                    logThrowable("exception_constructed", className, msg, this);
                    return ret;
                };
            });
            console.log("[GOD017] hooked_exception=" + className);
        } catch (e) {
            console.log("[GOD017] hook_failed=" + className + " error=" + e);
        }
    }

    [
        "java.lang.IllegalArgumentException",
        "com.google.gson.JsonParseException",
        "com.google.gson.JsonSyntaxException",
        "kotlinx.serialization.SerializationException",
        "java.lang.RuntimeException"
    ].forEach(hookThrowableConstructors);

    try {
        Throwable.printStackTrace.overloads.forEach(function (ov) {
            ov.implementation = function () {
                var msg = null;
                try { msg = this.getMessage(); } catch (e) {}
                logThrowable("printStackTrace", this.$className || "java.lang.Throwable", msg, this);
                return ov.apply(this, arguments);
            };
        });
        console.log("[GOD017] hooked Throwable.printStackTrace");
    } catch (e) {
        console.log("[GOD017] Throwable.printStackTrace hook failed: " + e);
    }

    function hookJsonGetter(name) {
        try {
            JSONObject[name].overloads.forEach(function (ov) {
                if (ov.argumentTypes.length !== 1 || ov.argumentTypes[0].className !== "java.lang.String") return;
                ov.implementation = function (field) {
                    var ctx = nowContext();
                    if (ctx) ctx.lastJsonField = safeString(field, 120);
                    try {
                        return ov.apply(this, arguments);
                    } catch (e) {
                        logThrowable("json_get_failed:" + name, e.$className || "java_exception", safeString(e, 500), e);
                        throw e;
                    }
                };
            });
        } catch (e) {}
    }

    ["get", "getString", "getJSONObject", "getJSONArray", "getInt", "getBoolean", "opt", "optString"].forEach(hookJsonGetter);
    console.log("[GOD017] hooked org.json.JSONObject getters");

    try {
        var NodeListener = Java.use("org.forgerock.android.auth.NodeListener");
        NodeListener.parseCallback.implementation = function (json) {
            pushContext("NodeListener.parseCallback", json);
            console.log("[GOD017] parseCallback_enter " + shortCallback(json));
            try {
                var result = this.parseCallback(json);
                console.log("[GOD017] parseCallback_exit type=" + callbackType(json) + " class=" + (result ? result.$className : "null"));
                return result;
            } catch (e) {
                logThrowable("parseCallback_throw", e.$className || "java_exception", safeString(e, 500), e);
                throw e;
            } finally {
                popContext();
            }
        };
        console.log("[GOD017] hooked NodeListener.parseCallback");
    } catch (e) {
        console.log("[GOD017] NodeListener.parseCallback hook failed: " + e);
    }

    try {
        var AbstractCallback = Java.use("org.forgerock.android.auth.callback.AbstractCallback");
        AbstractCallback.$init.overload("org.json.JSONObject").implementation = function (json) {
            pushContext("AbstractCallback.<init>", json);
            console.log("[GOD017] AbstractCallback_init_enter " + shortCallback(json));
            try {
                return this.$init(json);
            } catch (e) {
                logThrowable("AbstractCallback_init_throw", e.$className || "java_exception", safeString(e, 500), e);
                throw e;
            } finally {
                popContext();
            }
        };
        console.log("[GOD017] hooked AbstractCallback.<init>(JSONObject)");
    } catch (e) {
        console.log("[GOD017] AbstractCallback hook failed: " + e);
    }

    Java.enumerateLoadedClasses({
        onMatch: function (className) {
            if (className.indexOf("org.forgerock.android.auth.callback.") !== 0) return;
            try {
                var C = Java.use(className);
                if (!C.$init) return;
                C.$init.overloads.forEach(function (ov) {
                    if (ov.argumentTypes.length !== 1 || ov.argumentTypes[0].className !== "org.json.JSONObject") return;
                    ov.implementation = function (json) {
                        pushContext(className + ".<init>", json);
                        console.log("[GOD017] callback_ctor_enter class=" + className + " " + shortCallback(json));
                        try {
                            return ov.apply(this, arguments);
                        } catch (e) {
                            logThrowable("callback_ctor_throw", e.$className || "java_exception", safeString(e, 500), e);
                            throw e;
                        } finally {
                            popContext();
                        }
                    };
                    console.log("[GOD017] hooked_callback_ctor=" + className);
                });
            } catch (e) {}
        },
        onComplete: function () {
            console.log("[GOD017] callback constructor scan complete");
        }
    });

    function hookResponse(className) {
        try {
            var C = Java.use(className);
            C.onResponse.implementation = function (call, response) {
                try {
                    var body = response.peekBody(2097152).string();
                    if (body.indexOf("\"stage\"") >= 0) {
                        var stage = "?";
                        try {
                            var root = JSONObject.$new(body);
                            stage = root.optString("stage", "?");
                            console.log("[GOD017] http_response class=" + className + " code=" + response.code() + " stage=" + stage + " length=" + body.length);
                            if (root.has("callbacks")) {
                                var callbacks = root.getJSONArray("callbacks");
                                console.log("[GOD017] callback_count=" + callbacks.length());
                                for (var i = 0; i < callbacks.length(); i++) {
                                    var cb = callbacks.getJSONObject(i);
                                    console.log("[GOD017] callback[" + i + "] " + shortCallback(cb));
                                }
                            }
                        } catch (e) {
                            logThrowable("http_response_inspection_failed", e.$className || "java_exception", safeString(e, 500), e);
                        }
                    }
                } catch (e) {}
                return this.onResponse(call, response);
            };
            console.log("[GOD017] hooked_response=" + className + ".onResponse");
        } catch (e) {
            console.log("[GOD017] response_hook_failed=" + className + " error=" + e);
        }
    }

    hookResponse("org.forgerock.android.auth.AuthServiceClient$1");
    hookResponse("org.forgerock.android.auth.AuthServiceClient$2");

    try {
        var FRB = Java.use("com.bangkokbank.blue.ping.FRAuthBridge");
        if (FRB.handleError) {
            FRB.handleError.overloads.forEach(function (ov) {
                ov.implementation = function () {
                    console.log("\n[GOD017] === FRAuthBridge.handleError ===");
                    for (var i = 0; i < arguments.length; i++) {
                        var arg = arguments[i];
                        console.log("[GOD017] arg" + i + "=" + safeString(arg, 500));
                        try {
                            if (arg && arg.getStackTrace) logThrowable("handleError_arg" + i, arg.$className || "java_exception", arg.getMessage(), arg);
                        } catch (e) {}
                    }
                    return ov.apply(this, arguments);
                };
            });
            console.log("[GOD017] hooked FRAuthBridge.handleError");
        }
    } catch (e) {
        console.log("[GOD017] FRAuthBridge.handleError hook failed: " + e);
    }

    console.log("[GOD017] passive hooks installed");
});
