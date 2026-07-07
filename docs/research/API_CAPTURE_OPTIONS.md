# API Capture Options Research

**Date:** 2026-06-26
**Author:** robotframework-agent / appium-agent
**Version:** 1.0
**Status:** Complete

## Objective

Determine the best mechanism for capturing API request/response data for Android mobile banking automation, without compromising security or requiring app modification.

---

## 1. Application Profile

| Attribute | Value |
|-----------|-------|
| Package | `com.bangkokbank.blue.dev` |
| Version | `1.13.0-debug-network-alpha-06-10-Unshield` |
| Min SDK | 29 (Android 10) |
| Target SDK | 36 (Android 16) |
| Debuggable | `false` |
| Cleartext | `false` (`usesCleartextTraffic="false"`) |
| Network Security Config | Not present (no `network_security_config.xml`) |
| Architecture | React Native 0.76+ New Architecture (Bridgeless) |
| Module Federation | `@callstack/repack` (RePack) |

---

## 2. Library Presence Scan

Searched all 6 DEX files in the APK for key networking/debug libraries:

| Library | Present | Details |
|---------|---------|---------|
| **OkHttp** | **Yes** | `okhttp3` classes found in `classes6.dex`. Bundled as React Native's default HTTP client. |
| **OkHttp Logging Interceptor** | **Yes** | `okhttp3/logging/HttpLoggingInterceptor$Level` found in `classes6.dex`. Class exists but **not enabled** at runtime. |
| **Retrofit** | **No** | No Retrofit classes found. React Native uses OkHttp directly, not Retrofit. |
| **Chucker** | **No** | No Chucker classes found. |
| **Flipper** | **No** | No Flipper classes found. |
| **Stetho** | **No** | No Stetho classes found. |
| **New Relic** | **Yes** | `newrelic` agent v7.6.15 present. Network error collection enabled (`response_body_limit=2048`). **Full payload logging is not enabled.** |
| **Firebase** | **Yes** | Firebase App, Analytics, Messaging present. |
| **Adobe Analytics** | **Yes** | `bbl_analytics`, `bbl_cdp-analytics` custom modules present. |

---

## 3. Logcat Runtime Analysis

The app was launched on emulator-5554 and logcat was captured at PID 29650 for 20+ seconds during landing screen display.

### Findings

| Data Point | Found in Logcat? | Evidence |
|------------|:----------------:|----------|
| HTTP request URL | No | No URL output in logcat. |
| HTTP response | No | No response output in logcat. |
| HTTP status code | No | No `200`, `201`, `400`, `401`, `500` in logcat. |
| JSON payload | No | No JSON payload found in logcat. |
| OkHttp logging | No | No `OkHttp` or `HttpLoggingInterceptor` log tags. |
| Network request/response | No | No network request/response log output. |
| New Relic network errors | Yes | NR agent logs configuration but **does not emit** request/response payloads. |

### Observed Logcat Tags

- `okbank.blue.dev` — App process logs (React Native init, GC, asset loading)
- `ReactNativeJS` — JavaScript console logs (no network output)
- `newrelic` — NR agent configuration (not payload data)
- `NRMA` — New Relic Mobile Agent status
- `FirebaseApp` — Firebase initialization
- `Unknown:BridgelessReact` — RN architecture lifecycle

**Conclusion:** The app emits **no HTTP request or response payloads to logcat**. The OkHttp Logging Interceptor is bundled but **not enabled** at runtime. New Relic captures network errors only (status codes, error messages) — not full payloads.

---

## 4. Why Payloads Are Not Available

Based on the investigation, here is the exact chain of reasons:

1. **React Native networking uses OkHttp** — React Native's `fetch()` and `XMLHttpRequest` polyfills use OkHttp on Android. This is why `okhttp3` is bundled.

2. **Logging interceptor not enabled** — The `HttpLoggingInterceptor` class is present in the APK (it ships with OkHttp), but the React Native layer does not add it to the OkHttp client. RN exposes no configuration point for this.

3. **App is not debuggable** — `android:debuggable="false"`. Even though the version name says "debug-network-alpha", the manifest flag is false. This prevents ADB from attaching a debugger and limits log verbosity.

4. **No Chucker/Flipper/Stetho** — These debug tools are not bundled. Their absence means no in-app network inspector exists.

5. **New Relic captures errors, not payloads** — NR agent is configured for error monitoring (`collect_network_errors=true`) with `response_body_limit=2048`, but logs no payload content to logcat.

6. **No proxy-friendly configuration** — No `network_security_config.xml`. `usesCleartextTraffic="false"`. This means a MITM proxy would need certificate installation and the app must trust user certificates — which stock Android does not allow for targetSdk >= 24 without network config.

---

## 5. Option Comparison

### 5.1 ADB Logcat

| Criterion | Evaluation |
|-----------|------------|
| **Setup effort** | Low. Already built into our framework (`api_capture_keywords.resource`). Zero config. |
| **Payload support** | **None.** App emits no HTTP logs. |
| **SSL pinning impact** | None. Passive capture. |
| **Automation friendly** | Yes. Runs in background via `Start Process`. |
| **Production suitable** | Yes. Passive, no side effects. Needs server-side payload output. |
| **Security** | Built-in redaction in `api_log_redactor.py` handles sensitive data. |
| **Verdict** | **Infrastructure ready, but no data to capture from this app build.** |

### 5.2 OkHttp Logging Interceptor

| Criterion | Evaluation |
|-----------|------------|
| **Setup effort** | **Requires app code change.** Add `HttpLoggingInterceptor` to OkHttp client in React Native native module. |
| **Payload support** | Full. Request/response headers + body at BODY level. |
| **SSL pinning impact** | None. Works within app's own SSL context. |
| **Automation friendly** | High. Output goes to logcat at specified level (BODY, HEADERS, BASIC, NONE). |
| **Production suitable** | **No.** BODY level logs sensitive data. Only for internal debug builds. |
| **Security** | Requires redaction layer (we have it) + never ship BODY level to production. |
| **Verdict** | **Best technical option if we can get a modified build. Requires developer team coordination.** |

### 5.3 Chucker

| Criterion | Evaluation |
|-----------|------------|
| **Setup effort** | Requires app change. Add Chucker dependency + interceptor. |
| **Payload support** | Full. In-app notification panel with request/response details. |
| **SSL pinning impact** | None. |
| **Automation friendly** | **Low.** UI-based — requires app interaction to view. Not logcat-friendly. |
| **Production suitable** | **No.** Not designed for production. Leaks data. |
| **Security** | Shows sensitive data in-app. Requires removal from release builds. |
| **Verdict** | **Not recommended for automation. Better suited for manual debugging.** |

### 5.4 Proxyman / Charles

| Criterion | Evaluation |
|-----------|------------|
| **Setup effort** | Medium-High. Requires: (1) Install CA cert on device, (2) Configure WiFi proxy, (3) Handle SSL pinning. |
| **Payload support** | Full. All HTTP/HTTPS traffic visible in GUI. |
| **SSL pinning impact** | **High.** If app has SSL pinning (likely in production), traffic will fail. "Unshield" version may allow it. |
| **Automation friendly** | **Low.** GUI tools. Charles has headless/CLI mode but fragile. |
| **Production suitable** | **No.** Proxy must be removed. Cert installed on device is a security risk. |
| **Security** | Proxyman/Charles decrypt TLS. Banking data exposed to third-party tool. |
| **Verdict** | **Not suitable for CI/CD automation. Useful for one-time manual investigation only.** |

### 5.5 mitmproxy

| Criterion | Evaluation |
|-----------|------------|
| **Setup effort** | Medium. Same cert proxy setup. Has CLI + Python scripting. |
| **Payload support** | Full. All HTTP/HTTPS traffic. |
| **SSL pinning impact** | **High.** Same SSL pinning issue as Proxyman/Charles. |
| **Automation friendly** | Medium. Has CLI mode, Python API for scripting. But cert setup is a one-time manual step. |
| **Production suitable** | **No.** Same security concerns. |
| **Security** | Same TLS decryption exposure. |
| **Verdict** | **Best proxy option for automation (Python API), but SSL pinning is a blocker.** |

### 5.6 Backend Logs

| Criterion | Evaluation |
|-----------|------------|
| **Setup effort** | Medium. Requires backend team to provide log access or API to query requests. |
| **Payload support** | Full. Server has complete request/response data. |
| **SSL pinning impact** | None. |
| **Automation friendly** | High. API-based access. Can correlate by session or timestamp. |
| **Production suitable** | **Yes.** No device impact. |
| **Security** | Backend logs must already redact PII. Verify compliance. |
| **Verdict** | **Best option if accessible. No device-side setup. But requires cross-team coordination.** |

---

## 6. Recommendation

### Short-term (Sprint 2.x): ADB Logcat

Continue with the current `api_capture_keywords.resource` / `api_log_redactor.py` approach. Even though the current app build emits no API payloads, the infrastructure is:

- Production-safe (passive, no device modification)
- Security-safe (redaction built in)
- Ready for when/if server-side logging improves or the dev team enables OkHttp logging on a test build

**Limitation:** No API payloads will be captured from the current `1.13.0-debug-network-alpha` build. Logcat will only show app lifecycle and New Relic error config.

### Medium-term: Request Developer Team for a Logging Build

The highest-value single action is to ask the mobile development team to:

1. Enable `HttpLoggingInterceptor` at `BODY` level in a **dedicated test build** (not release).
2. Log output at Android `Log.DEBUG` or `Log.VERBOSE` level so it appears in `adb logcat`.
3. Provide a build where `android:debuggable="true"` or at minimum enable log output from the React Native networking layer.

This requires **no architectural change** — the interceptor class is already bundled. It's a configuration change only.

### Long-term: Dual Approach

| Source | Purpose | When |
|--------|---------|------|
| **Backend logs** | Ground truth for assertions | Production + Staging |
| **Logcat (OkHttp)** | Client-side timing evidence | Test builds |
| **ADB logcat (passive)** | Fallback for all builds | Always running |

Backend logs should be the long-term source for **assertions** (status codes, response structure), while logcat-based capture serves as **debugging evidence** for timing and client-side behavior.

---

## 7. Action Items

1. **Contact mobile dev team**: Request a debug build with:
   - `HttpLoggingInterceptor` at `BODY` level
   - `android:debuggable="true"` OR explicit `Log.d` output for network calls
   - Tag prefix like `OkHttp` or `BBL-NETWORK` for easy filtering

2. **Verify proxy feasibility**: Test the "Unshield" build with mitmproxy to confirm SSL pinning is truly disabled. If yes, mitmproxy becomes viable for this build.

3. **Explore React Native Network Inspector**: React Native's built-in network inspector (DevSupportManager present) may expose requests via its internal event system. Investigate whether we can hook into it via ADB.

4. **Document in knowledge/**: Add findings about the app's networking architecture to `knowledge/appium.md`.

---

## 8. Appendix: Investigation Commands

```bash
# APK library scan
unzip -l apps/android/app.apk | grep -iE "okhttp|retrofit|chucker|flipper|stetho"

# DEX class scan for logging interceptor
python3 -c "
import zipfile
zf = zipfile.ZipFile('apps/android/app.apk')
data = zf.read('classes6.dex')
if b'HttpLoggingInterceptor' in data:
    print('PRESENT')
zf.close()
"

# Manifest checks
apkanalyzer manifest debuggable apps/android/app.apk
apkanalyzer manifest print apps/android/app.apk | grep -iE 'debuggable|network_security'

# Logcat capture (app PID)
adb logcat -b main -v brief --pid=$(adb shell pidof -s com.bangkokbank.blue.dev)

# Live HTTP search
adb logcat -b main --pid=$(adb shell pidof -s com.bangkokbank.blue.dev) | grep -iE 'http|okhttp|request|response|api|url'
```
