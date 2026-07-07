# 05 — Health Check Review

## Health Check Inventory

### Resources

| File | Lines | Purpose | Status |
|------|-------|---------|--------|
| `health_check_keywords.resource` | 152 | Checkpoint tracking, blocker detection, JSON+MD report | Untracked |
| `dob_stability_keywords.resource` | 144 | DOB picker timing, retry tracking, stability JSON report | Untracked |
| `api_capture_keywords.resource` | 75 | ADB logcat capture, redaction via api_log_redactor.py | Untracked |

### Test

| File | Purpose | Status |
|------|---------|--------|
| `tests/android/onboarding/onboarding_health_check.robot` | E2E onboarding with health checkpoints + API capture | Untracked |

### Supporting Libraries

| File | Purpose | Status |
|------|---------|--------|
| `libraries/api_log_redactor.py` | Log redaction (PII masking) | Untracked |

---

## How It Works

1. `Start Health Check` initializes checkpoint list + timestamp.
2. `Mark Health Checkpoint <stage>` records elapsed time at each flow stage.
3. `Set Health Check Blocker <code> <reason> <evidence_path>` marks environment blockers.
4. `End Health Check <status>` writes JSON + Markdown report to `${OUTPUT_DIR}/health_check/`.
5. `Initialize DOB Stability Tracking` + `Generate DOB Stability Report` — separate DOB-focused tracking.
6. `Start API Capture` / `Stop API Capture` — logcat capture with PII redaction.

### Checkpoint Stages (from `onboarding_common.resource`)

```
APP_OPENED → LANDING_VISIBLE → LANDING_COMPLETED → CONSENT_VISIBLE →
CONSENT_ACCEPTED → PROFILE_VISIBLE → PROFILE_COMPLETED →
PDPA_CONSENT_VISIBLE → PDPA_CONSENT_ACCEPT_ATTEMPTED → SIGN_UP_VISIBLE →
SIGN_UP_STARTED → SCAN_CARD_INTRO_VISIBLE → SCAN_CARD_INTRO_COMPLETED →
ID_CARD_CAMERA_CAPTURE_VISIBLE → ID_CARD_PHOTO_CAPTURED
```

---

## Findings

### Strengths

| # | Finding |
|---|---------|
| 1 | Three-state status: PASS / FAIL / BLOCKED — correctly distinguishes automation failure from environment blocker |
| 2 | JSON + Markdown dual output — machine-readable + human-readable |
| 3 | API capture includes PII redaction — security-conscious |
| 4 | DOB stability tracking is isolated from health check — can run independently |
| 5 | `Mark Health Checkpoint` is a no-op when `HEALTH_CHECK_ACTIVE` is false — non-invasive to production flow |

### Issues

| # | Severity | Finding | Evidence | Recommendation |
|---|----------|---------|----------|----------------|
| 1 | High | `onboarding_common.resource:10` imports `health_check_keywords` | Shared flow coupled to health infrastructure | Acceptable (no-op when inactive) but document the coupling |
| 2 | Medium | DOB stability report path is `${OUTPUT_DIR}/stability/stability.json` | Separate from health check `${OUTPUT_DIR}/health_check/` | Consolidate or cross-reference in health report |
| 3 | Medium | `api_capture_keywords.resource:35` has `Sleep 1s` before terminating process | Violates "Avoid Sleep" performance baseline | Replace with `Wait For Process` or poll for file existence |
| 4 | Medium | `onboarding_health_check.robot:48` has `Sleep 3s` before evidence capture | Violates "Avoid Sleep" | Replace with `Wait Until Element Is Visible` on next-screen element |
| 5 | Low | Health check report filename uses timestamp but no run-id | `onboarding_health_check_${ts}.md` | Could collide if two runs start in same second; add `${SUITE_NAME}` or PID |
| 6 | Low | `dob_stability_keywords.resource` uses `Evaluate __import__('time').time()` pattern repeatedly | 12 occurrences | Extract to a `Now Timestamp` keyword |

---

## Classification

| Component | Classification | Track? | CI? |
|-----------|----------------|--------|-----|
| `health_check_keywords.resource` | **Health Check** — reusable | Yes | Manual trigger |
| `dob_stability_keywords.resource` | **Health Check** — reusable | Yes | With health check |
| `api_capture_keywords.resource` | **Health Check** — reusable | Yes | With health check |
| `api_log_redactor.py` | **Security utility** — reusable | Yes | Always |
| `onboarding_health_check.robot` | **Health Check** — reusable | Yes | Manual / nightly |

## Recommendation

Health check framework is production-quality. Track all files. The three-state
(PASS/FAIL/BLOCKED) model is exactly right for mobile automation where environment
blockers are common. C2 should:
1. Track all health check files in git.
2. Replace `Sleep` calls with condition-based waits.
3. Consolidate DOB stability + health check reporting paths.
4. Document the `onboarding_common` → `health_check_keywords` coupling as intentional.
