Java.perform(function () {
    console.log("[CAM] === Find Camera Submission Path ===");

    // Hook ALL PromiseImpl.resolve calls to see what happens at OCR stage
    var PromiseImpl = Java.use("com.facebook.react.bridge.PromiseImpl");
    var resolveCount = 0;
    PromiseImpl.resolve.implementation = function (value) {
        resolveCount++;
        if (value !== null) {
            var str = value.toString();
            if (str.length > 200) str = str.substring(0, 200) + "...(" + str.length + ")";
            console.log("[PROM#" + resolveCount + "] resolve: " + str);
        }
        return this.resolve(value);
    };

    // Hook ALL React Native bridge method invocations
    // Find all NativeModule subclasses
    Java.enumerateLoadedClasses({
        onMatch: function (className) {
            if (className.indexOf("bangkokbank") >= 0 && 
                className.indexOf("Module") >= 0 &&
                className.indexOf("$") < 0 &&
                className.indexOf("Bridge") < 0) {  // Skip FRAuthBridge (already known)
                console.log("[MOD] " + className);
                
                // List methods of this module
                try {
                    var cls = Java.use(className);
                    var methods = cls.class.getDeclaredMethods();
                    methods.forEach(function (m) {
                        var name = m.getName();
                        if (name.indexOf("access$") < 0 && name.indexOf("$") < 0 &&
                            name !== "getName" && name !== "equals" && name !== "hashCode" && name !== "toString") {
                            console.log("[MOD]   ." + name + " " + m.toGenericString().substring(0, 100));
                        }
                    });
                } catch (e) {}
            }
        },
        onComplete: function () {
            console.log("[CAM] Module enumeration done");
        }
    });

    // Hook FRAuthBridge methods that might be OCR-specific
    var FRB = Java.use("com.bangkokbank.blue.ping.FRAuthBridge");
    var frbMethods = FRB.class.getDeclaredMethods();
    console.log("\n[CAM] FRAuthBridge ALL methods:");
    frbMethods.forEach(function (m) {
        var name = m.getName();
        if (name.indexOf("access$") < 0 && name.indexOf("$r8") < 0 && name.indexOf("$lambda") < 0) {
            console.log("[FRB] " + name + " — " + m.toGenericString().substring(0, 120));
        }
    });

    console.log("[CAM] Done");
});
