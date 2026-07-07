// Frida OCR Callback Injector
// Sprint 2.30 — Temporary OCR unblock for emulator testing
//
// Injects mock OCR data into ForgeRock TextInputCallback (IDToken2)
// and selects "proceed" in ChoiceCallback (IDToken1)
//
// Based on callback structure from Sprint 2.21-2.23:
//   IDToken1 = ChoiceCallback ("proceed or go back?") → set to 0 (proceed)
//   IDToken2 = TextInputCallback ("ocrData") → set to mock card data
//
// PREREQUISITE: App must be at ID Card Camera Capture screen
// (ForgeRock SDK classes load lazily when OCR stage is reached)

Java.perform(function () {
    console.log("[OCR-INJECT] Starting OCR callback injector...");

    // Mock OCR data from testdata/onboarding/ntb.local.yaml
    // Format: JSON string (most likely format for TextInputCallback)
    var MOCK_OCR_DATA = JSON.stringify({
        thaiFirstName: "สมใจ",
        thaiLastName: "ใจดี",
        englishTitle: "Miss",
        englishFirstName: "Somjai",
        englishLastName: "Jaidee",
        citizenId: "3872637115880",
        dateOfBirth: "15 Jan. 1992",
        dateOfIssue: "21 Aug. 2023",
        dateOfExpiry: "21 Aug. 2032",
        address: "888 หมู่ที่ 8 ต.ทดสอบ อ.ทดสอบ จ.กรุงเทพฯ"
    });

    // ==========================================
    // Strategy 1: Hook ForgeRock SDK Callbacks
    // ==========================================

    // Try standard ForgeRock SDK class names
    var forgeRockClasses = [
        "org.forgerock.android.auth.TextInputCallback",
        "com.forgerock.android.auth.TextInputCallback",
        "org.forgerock.android.auth.callback.TextInputCallback",
    ];

    var hooked = false;

    for (var i = 0; i < forgeRockClasses.length && !hooked; i++) {
        try {
            var TIC = Java.use(forgeRockClasses[i]);
            console.log("[OCR-INJECT] Found TextInputCallback: " + forgeRockClasses[i]);

            // Hook setValue or setInputValue
            try {
                TIC.setValue.implementation = function (value) {
                    if (value === "" || value === null) {
                        console.log("[OCR-INJECT] Intercepted empty ocrData — injecting mock data");
                        console.log("[OCR-INJECT] Mock data: " + MOCK_OCR_DATA.substring(0, 80) + "...");
                        return this.setValue(MOCK_OCR_DATA);
                    }
                    console.log("[OCR-INJECT] TextInputCallback.setValue: " + value.substring(0, 80));
                    return this.setValue(value);
                };
                console.log("[+] TextInputCallback.setValue hooked");
                hooked = true;
            } catch (e) {
                console.log("[-] setValue not found: " + e);
            }
        } catch (e) {
            // Class not found, try next
        }
    }

    // ==========================================
    // Strategy 2: Hook ChoiceCallback (proceed)
    // ==========================================

    var choiceClasses = [
        "org.forgerock.android.auth.ChoiceCallback",
        "com.forgerock.android.auth.ChoiceCallback",
        "org.forgerock.android.auth.callback.ChoiceCallback",
    ];

    for (var i = 0; i < choiceClasses.length; i++) {
        try {
            var CC = Java.use(choiceClasses[i]);
            console.log("[OCR-INJECT] Found ChoiceCallback: " + choiceClasses[i]);
            try {
                CC.setSelectedIndex.implementation = function (index) {
                    console.log("[OCR-INJECT] ChoiceCallback: selecting proceed (0)");
                    return this.setSelectedIndex(0);
                };
                console.log("[+] ChoiceCallback.setSelectedIndex hooked");
            } catch (e) {}
            break;
        } catch (e) {}
    }

    // ==========================================
    // Strategy 3: Enumerate all loaded classes for OCR/ForgeRock
    // ==========================================
    if (!hooked) {
        console.log("[OCR-INJECT] Standard classes not found. Enumerating...");
        Java.enumerateLoadedClasses({
            onMatch: function (className) {
                var lower = className.toLowerCase();
                if (lower.indexOf("callback") >= 0 || lower.indexOf("forge") >= 0 ||
                    lower.indexOf("ocr") >= 0 || lower.indexOf("submit") >= 0 ||
                    lower.indexOf("ping") >= 0 || lower.indexOf("textinput") >= 0 ||
                    lower.indexOf("choice") >= 0 || lower.indexOf("idtoken") >= 0) {
                    console.log("[FOUND] " + className);
                    // List methods
                    try {
                        var cls = Java.use(className);
                        var methods = cls.class.getDeclaredMethods();
                        methods.forEach(function (m) {
                            console.log("  ." + m.getName());
                        });
                    } catch (e) {}
                }
            },
            onComplete: function () {
                console.log("[OCR-INJECT] Enumeration complete");
                console.log("[OCR-INJECT] If classes were found, update this script to hook them.");
            }
        });
    }

    // ==========================================
    // Strategy 4: Hook network layer to modify callback JSON
    // ==========================================

    // Hook String creation to catch "ocrData" being set to empty
    try {
        var JSONObject = Java.use("org.json.JSONObject");
        JSONObject.put.overload("java.lang.String", "java.lang.String").implementation = function (key, value) {
            if (key === "IDToken2" && (value === "" || value === null)) {
                console.log("[OCR-INJECT] Intercepted JSON put IDToken2=\"\" — injecting mock");
                return this.put(key, MOCK_OCR_DATA);
            }
            return this.put(key, value);
        };
        console.log("[+] JSONObject.put hooked for IDToken2 interception");
    } catch (e) {
        console.log("[-] JSONObject hook: " + e);
    }

    // ==========================================
    // Strategy 5: Hook Base64 for OCR upload detection
    // ==========================================
    try {
        var Base64 = Java.use("android.util.Base64");
        Base64.encodeToString.overload("[B", "int").implementation = function (data, flags) {
            if (data && data.length > 5000) {
                console.log("[OCR-INJECT] Base64 encoding " + data.length + " bytes — OCR upload detected");
            }
            return this.encodeToString(data, flags);
        };
        console.log("[+] Base64 hooked");
    } catch (e) {}

    console.log("[OCR-INJECT] All hooks installed. Waiting for OCR callback...");
    console.log("[OCR-INJECT] Tap 'Take Photo' to trigger the callback flow.");
});
