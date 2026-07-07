// Frida SSL Pinning Bypass for Android
// Hooks common SSL pinning implementations

Java.perform(function () {
    console.log("[*] SSL Pinning Bypass starting...");

    // 1. TrustManager bypass - accept all certificates
    var X509TrustManager = Java.use("javax.net.ssl.X509TrustManager");
    var SSLContext = Java.use("javax.net.ssl.SSLContext");

    var TrustManager = Java.registerClass({
        name: "com.frida.TrustManager",
        implements: [X509TrustManager],
        methods: {
            checkClientTrusted: function (chain, authType) { },
            checkServerTrusted: function (chain, authType) { },
            getAcceptedIssuers: function () { return []; }
        }
    });

    var TrustManagers = [TrustManager.$new()];
    var sslContextInstance = SSLContext.getInstance("TLS");
    sslContextInstance.init(null, TrustManagers, null);
    SSLContext.setDefault(sslContextInstance);
    console.log("[+] TrustManager bypassed");

    // 2. OkHttp3 CertificatePinner bypass
    try {
        var CertificatePinner = Java.use("okhttp3.CertificatePinner");
        CertificatePinner.check.overload("java.lang.String", "java.util.List").implementation = function (a, b) {
            console.log("[+] OkHttp3 CertificatePinner.check bypassed: " + a);
        };
        console.log("[+] OkHttp3 CertificatePinner bypassed");
    } catch (e) {
        console.log("[-] OkHttp3 CertificatePinner not found: " + e);
    }

    // 3. OkHttp3 hostname verifier bypass
    try {
        var HostnameVerifier = Java.registerClass({
            name: "com.frida.HostnameVerifier",
            implements: [Java.use("javax.net.ssl.HostnameVerifier")],
            methods: {
                verify: function (hostname, session) { return true; }
            }
        });
        console.log("[+] HostnameVerifier bypass registered");
    } catch (e) {}

    // 4. Hook all OkHttp3 requests for logging
    try {
        var OkHttpClient = Java.use("okhttp3.OkHttpClient");
        var Builder = Java.use("okhttp3.Request$Builder");

        // Log every request URL
        var Response = Java.use("okhttp3.Response");
        Response.body.implementation = function () {
            var request = this.request();
            var url = request.url().toString();
            var method = request.method();
            var code = this.code();
            console.log("[NET] " + method + " " + url.substring(0, 100) + " -> " + code);

            // Log OCR/ForgeRock/auth related responses
            if (url.indexOf("auth") >= 0 || url.indexOf("ocr") >= 0 ||
                url.indexOf("forge") >= 0 || url.indexOf("json") >= 0 ||
                url.indexOf("authenticate") >= 0 || url.indexOf("callback") >= 0) {
                console.log("[OCR/AUTH] *** Found auth/OCR endpoint: " + url);
                try {
                    var peekBody = this.peekBody(1048576);
                    var contentType = peekBody.contentType();
                    var bodyString = peekBody.string();
                    if (bodyString.indexOf("ocrData") >= 0 || bodyString.indexOf("IDToken") >= 0) {
                        console.log("[OCR/AUTH] *** OCR response body:");
                        console.log(bodyString.substring(0, 500));
                    }
                } catch (e) {}
            }
            return this.body();
        };
        console.log("[+] OkHttp3 response logging hooked");
    } catch (e) {
        console.log("[-] OkHttp3 logging hook failed: " + e);
    }

    console.log("[*] SSL Pinning Bypass complete. All hooks active.");
});
