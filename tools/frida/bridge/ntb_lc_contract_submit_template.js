// Sprint 2.46 — NTB_LC bridge.next contract submitter.
// Runtime-generated from ntb.local.yaml. Do not commit generated runtime file.

Java.perform(function () {
    var CONFIG = __NTB_LC_CONFIG__;
    var TAG = "[NTBLC]";

    function log(msg) { console.log(TAG + " " + msg); }

    function valueMask(v) {
        if (v === null || v === undefined || String(v).length === 0) return "empty";
        return "len=" + String(v).length;
    }

    function getOutput(cb, name) {
        if (!cb.output) return null;
        for (var i = 0; i < cb.output.length; i++) {
            if (cb.output[i] && cb.output[i].name === name) return cb.output[i].value;
        }
        return null;
    }

    function splitFieldMessage(value) {
        if (value === null || value === undefined) return null;
        var s = String(value);
        var idx = s.indexOf("|");
        if (idx < 0) return null;
        return { name: s.substring(0, idx), value: s.substring(idx + 1) };
    }

    function extractOutputValues(callbacks) {
        var out = {};
        for (var i = 0; i < callbacks.length; i++) {
            var cb = callbacks[i];
            if (!cb || cb.type !== "TextOutputCallback") continue;
            var pair = splitFieldMessage(getOutput(cb, "message"));
            if (pair && pair.name) out[pair.name] = pair.value;
        }
        return out;
    }

    function callbackSummary(callbacks) {
        var types = [];
        var inputs = [];
        var prompts = [];
        var outputs = [];
        for (var i = 0; i < callbacks.length; i++) {
            var cb = callbacks[i] || {};
            types.push(cb.type || "?");
            if (cb.input) {
                for (var j = 0; j < cb.input.length; j++) {
                    inputs.push(cb.input[j].name || "?");
                }
            }
            if (cb.type === "TextInputCallback") prompts.push(getOutput(cb, "prompt") || "?");
            if (cb.output) {
                for (var k = 0; k < cb.output.length; k++) {
                    outputs.push(cb.output[k].name || "?");
                }
            }
        }
        return {
            count: callbacks.length,
            types: types.join("|"),
            inputs: inputs.join("|"),
            prompts: prompts.join("|"),
            outputs: outputs.join("|")
        };
    }

    function buildPayloadFromResponse(responseJson) {
        var payload = JSON.parse(JSON.stringify(responseJson));
        payload.stage = payload.stage || "NTB_LC";
        var observed = extractOutputValues(payload.callbacks || []);
        var values = {
            titleNameTh: CONFIG.values.titleNameTh || observed.titleNameTh || "",
            titleNameEn: CONFIG.values.titleNameEn || observed.titleNameEn || "",
            firstNameTh: CONFIG.values.firstNameTh || observed.firstNameTh || "",
            lastNameTh: CONFIG.values.lastNameTh || observed.lastNameTh || "",
            firstNameEn: CONFIG.values.firstNameEn || observed.firstNameEn || "",
            lastNameEn: CONFIG.values.lastNameEn || observed.lastNameEn || "",
            DOB: CONFIG.values.DOB || observed.DOB || "",
            laserCode: CONFIG.values.laserCode || "",
            idExpiryDate: CONFIG.values.idExpiryDate || "",
            idIssuerDate: CONFIG.values.idIssuerDate || ""
        };

        var filled = [];
        for (var i = 0; i < payload.callbacks.length; i++) {
            var cb = payload.callbacks[i];
            if (!cb || cb.type !== "TextInputCallback") continue;
            var prompt = getOutput(cb, "prompt") || "";
            var val = values[prompt] || "";
            if (cb.input && cb.input.length > 0) {
                cb.input[0].value = val;
                filled.push((cb.input[0].name || "?") + ":" + prompt + ":" + valueMask(val));
            }
        }
        return { payload: payload, filled: filled };
    }

    function logThrowable(prefix, t) {
        try {
            log(prefix + "_class=" + t.$className);
            log(prefix + "_message=" + t.getMessage());
            var st = t.getStackTrace();
            for (var i = 0; i < Math.min(st.length, 10); i++) {
                log(prefix + "_stack=" + st[i].toString());
            }
        } catch (e) {
            log(prefix + "_log_failed=" + e);
        }
    }

    var TextInputCallback = Java.use("org.forgerock.android.auth.callback.TextInputCallback");
    var ChoiceCallback = Java.use("org.forgerock.android.auth.callback.ChoiceCallback");
    var PromiseCls = Java.use("com.facebook.react.bridge.Promise");
    var Proxy = Java.use("java.lang.reflect.Proxy");
    var IH = Java.use("java.lang.reflect.InvocationHandler");

    try {
        var FRB = Java.use("com.bangkokbank.blue.ping.FRAuthBridge");
        FRB.next.overload("java.lang.String", "com.facebook.react.bridge.Promise").implementation = function (response, promise) {
            try {
                var root = JSON.parse(String(response));
                var s = callbackSummary(root.callbacks || []);
                log("next_enter has_authId=" + !!root.authId + " has_callbacks=" + !!root.callbacks + " stage=" + (root.stage || "?") + " callback_count=" + s.count);
                log("next_types=" + s.types);
                log("next_input_names=" + s.inputs);
                log("next_prompts=" + s.prompts);
            } catch (e) {
                log("next_probe_error=" + e);
            }
            try {
                return this.next(response, promise);
            } catch (e) {
                logThrowable("next_throw", e);
                throw e;
            }
        };
        log("hooked FRAuthBridge.next");
    } catch (e) {
        log("FRAuthBridge.next hook failed: " + e);
    }

    ["java.lang.IllegalArgumentException", "java.lang.RuntimeException", "com.google.gson.JsonParseException", "com.google.gson.JsonSyntaxException"].forEach(function (name) {
        try {
            var C = Java.use(name);
            C.$init.overloads.forEach(function (ov) {
                ov.implementation = function () {
                    var ret = ov.apply(this, arguments);
                    try {
                        var msg = String(this.getMessage());
                        if (msg.indexOf("Parsing response failed") >= 0 || msg.indexOf("GOD-017") >= 0) logThrowable("constructed", this);
                    } catch (e) {}
                    return ret;
                };
            });
            log("hooked_exception=" + name);
        } catch (e) {
            log("hook_exception_failed=" + name + " " + e);
        }
    });

    var ntbResponse = null;
    var submitted = false;

    function submitContract() {
        if (submitted || !ntbResponse) return;
        submitted = true;

        var built = buildPayloadFromResponse(ntbResponse);
        var summary = callbackSummary(built.payload.callbacks || []);
        log("payload_shape has_authId=" + !!built.payload.authId + " has_callbacks=" + !!built.payload.callbacks + " stage=" + built.payload.stage + " callback_count=" + summary.count);
        log("payload_types=" + summary.types);
        log("payload_input_names=" + summary.inputs);
        for (var i = 0; i < built.filled.length; i++) log("filled=" + built.filled[i]);

        var body = JSON.stringify(built.payload);
        var mockPromise = Proxy.newProxyInstance(
            PromiseCls.class.getClassLoader(),
            Java.array("java.lang.Class", [PromiseCls.class]),
            Java.registerClass({
                name: "com.frida.NtbLcPromise" + Date.now(),
                implements: [IH],
                methods: { invoke: function (p, m, a) {
                    var name = m.getName();
                    log("promise_" + name);
                    if (name === "reject" && a) {
                        for (var i = 0; i < a.length; i++) {
                            if (a[i]) log("promise_reject_arg" + i + "=" + String(a[i]).substring(0, 160));
                        }
                    }
                    return null;
                }}
            }).$new()
        );

        Java.choose("com.bangkokbank.blue.ping.FRAuthBridge", {
            onMatch: function (bridge) {
                log("calling_bridge_next contract_length=" + body.length);
                try {
                    bridge.next(body, mockPromise);
                    log("bridge_next_returned");
                } catch (e) {
                    log("bridge_next_call_error=" + e);
                }
            },
            onComplete: function () { log("bridge_choose_complete"); }
        });
    }

    function captureResponse(body, source) {
        if (body.indexOf('"stage"') < 0) return;
        try {
            var parsed = JSON.parse(body);
            if (submitted && parsed.stage !== "NTB_LC") {
                var ps = callbackSummary(parsed.callbacks || []);
                log("post_response source=" + source + " stage=" + (parsed.stage || "?") + " callback_count=" + ps.count);
                log("post_types=" + ps.types);
                log("post_input_names=" + ps.inputs);
                log("post_output_names=" + ps.outputs);
                log("post_has_mobileNumberMasked=" + (body.indexOf("mobileNumberMasked") >= 0));
                log("post_has_otpResendsRemaining=" + (body.indexOf("otpResendsRemaining") >= 0));
                log("post_has_otpRetriesRemaining=" + (body.indexOf("otpRetriesRemaining") >= 0));
                return;
            }
            if (parsed.stage !== "NTB_LC") return;
            ntbResponse = parsed;
            var s = callbackSummary(parsed.callbacks || []);
            log("captured_source=" + source + " stage=NTB_LC has_authId=" + !!parsed.authId + " callback_count=" + s.count);
            log("captured_types=" + s.types);
            log("captured_input_names=" + s.inputs);
            log("captured_prompts=" + s.prompts);
            submitContract();
        } catch (e) {
            log("capture_parse_error=" + e);
        }
    }

    ["org.forgerock.android.auth.AuthServiceClient$2", "org.forgerock.android.auth.AuthServiceClient$1"].forEach(function (cls) {
        try {
            var C = Java.use(cls);
            C.onResponse.implementation = function (call, response) {
                try {
                    log("http_status=" + response.code());
                    captureResponse(String(response.peekBody(2097152).string()), cls);
                } catch (e) {
                    log("response_hook_error=" + cls + " " + e);
                }
                return this.onResponse(call, response);
            };
            log("hooked_response=" + cls);
        } catch (e) {
            log("response_hook_failed=" + cls + " " + e);
        }
    });

    var phase = 0;
    var polls = 0;
    var interval = setInterval(function () {
        polls++;
        if (submitted || polls > 48) {
            clearInterval(interval);
            if (!submitted) log("timeout_no_ntb_lc_submit");
            return;
        }

        Java.choose("org.forgerock.android.auth.Node", {
            onMatch: function (node) {
                if (phase !== 0) return;
                try {
                    if (String(node.getStage()) !== "OCR") return;
                    phase = 1;
                    log("ocr_node_found");
                    var callbacks = node.getCallbacks();
                    Java.cast(callbacks.get(0), ChoiceCallback).setSelectedIndex(0);
                    Java.cast(callbacks.get(1), TextInputCallback).setValue(CONFIG.ocrImageBase64);
                    log("ocr_callbacks_filled choice=IDToken1 image=IDToken2:" + valueMask(CONFIG.ocrImageBase64));

                    var context = Java.use("android.app.ActivityThread").currentApplication().getApplicationContext();
                    var NodeListener = Java.use("org.forgerock.android.auth.NodeListener");
                    var listener = Proxy.newProxyInstance(
                        NodeListener.class.getClassLoader(),
                        Java.array("java.lang.Class", [NodeListener.class]),
                        Java.registerClass({
                            name: "com.frida.NtbLcNodeListener" + Date.now(),
                            implements: [IH],
                            methods: { invoke: function (p, m, a) {
                                log("node_listener_" + m.getName());
                                return null;
                            }}
                        }).$new()
                    );
                    node.next(context, listener);
                    log("ocr_node_next_sent");
                } catch (e) {
                    log("ocr_submit_error=" + e);
                }
            },
            onComplete: function () {}
        });
    }, 5000);

    log("probe_started");
});
