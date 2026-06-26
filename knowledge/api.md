# API Knowledge

## Current State
The project tests mobile banking flows through the Appium-driven UI. There is no API-level testing layer at this stage.

## Observed Backend Behavior
- Dev backend returns `Service is not available now` (AJI-001) after Profile Next — this is an expected environment limitation, not a test failure
- Backend availability affects post-Profile flow steps (OCR, Face Verification, PIN Setup)
- Network and VPN stability affect session reliability

## Future Scope
API-level testing may be added to:
- Verify request/response payloads for onboarding steps
- Test backend error handling independently of UI
- Enable parallel UI + API validation

## Current Recommendation
Until API testing is implemented, UI-level observation is the only validation mechanism. Backend issues should be documented as environment failures, not automation defects.
