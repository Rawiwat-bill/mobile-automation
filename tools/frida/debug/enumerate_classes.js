// Frida Class Enumeration — find ForgeRock/Ping/OCR/Callback classes
// Run AFTER app reaches camera screen (classes load lazily)

Java.perform(function () {
    console.log("[ENUM] Starting class enumeration...");

    var keywords = [
        "forge", "forgerock", "frsdk", "callback", "textinput",
        "choicecallback", "submitocr", "ping", "ocr", "ocrdata",
        "idtoken", "authenticate", "auth", "takescan", "scanidcard",
        "cropimage", "convertfiletobase64", "base64", "visioncamera",
        "takephoto", "capturephoto", "idcard", "scancard",
        "pingidentity", "pingone", "daon", "verid", "onfido"
    ];

    var found = {};
    var count = 0;

    Java.enumerateLoadedClasses({
        onMatch: function (className) {
            var lower = className.toLowerCase();
            for (var i = 0; i < keywords.length; i++) {
                if (lower.indexOf(keywords[i]) >= 0) {
                    if (!found[className]) {
                        found[className] = true;
                        console.log("[FOUND] " + className);

                        // List methods of this class
                        try {
                            var cls = Java.use(className);
                            var methods = cls.class.getDeclaredMethods();
                            methods.forEach(function (m) {
                                console.log("  ." + m.getName() + " (" + m.toGenericString().substring(0, 120) + ")");
                            });
                        } catch (e) {
                            console.log("  (cannot introspect: " + e + ")");
                        }
                        count++;
                    }
                    break;
                }
            }
        },
        onComplete: function () {
            console.log("[ENUM] Complete. Found " + count + " matching classes.");

            // Also search for React Native modules
            console.log("\n[ENUM] Searching React Native modules...");
            try {
                var RN = Java.use("com.facebook.react.bridge.NativeModuleRegistry");
            } catch(e) {}

            // Search for any class with "Module" that might be OCR-related
            Java.enumerateLoadedClasses({
                onMatch: function (className) {
                    var lower = className.toLowerCase();
                    if (lower.indexOf("module") >= 0 &&
                        (lower.indexOf("ocr") >= 0 || lower.indexOf("scan") >= 0 ||
                         lower.indexOf("camera") >= 0 || lower.indexOf("capture") >= 0 ||
                         lower.indexOf("forge") >= 0 || lower.indexOf("auth") >= 0 ||
                         lower.indexOf("ping") >= 0 || lower.indexOf("id") >= 0)) {
                        console.log("[MODULE] " + className);
                    }
                },
                onComplete: function () {
                    console.log("[ENUM] Module search complete.");
                }
            });
        }
    });
});
