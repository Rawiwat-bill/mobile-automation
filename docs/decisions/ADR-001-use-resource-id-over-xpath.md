# ADR-001: Use Resource-ID Over XPath for Android Locators

## Status
Accepted

## Context
Appium mobile automation supports multiple locator strategies: resource-id, accessibility_id, class name, XPath, etc. The project needed a consistent locator strategy that balances stability, readability, and performance across different Android versions and devices.

## Decision
Use screen-specific `resource-id` as the primary locator strategy for Android elements.

Priority order:
1. Screen-specific `resource-id` (e.g., `com.bank.app:id/profile_citizen_id_input`)
2. `accessibility_id` / `content-desc`
3. Stable text (only when language-independent)
4. Relative XPath (last resort)

## Consequences
**Positive:**
- resource-id is stable across app versions when maintained by developers
- Screen-specific prefixes prevent element ambiguity
- Faster than XPath queries in Appium
- Works across screen sizes and resolutions

**Negative:**
- Requires developer cooperation to add/maintain resource-ids
- Generic resource-ids (e.g., `base-btn`) require fallback strategies
- Not all elements have screen-specific resource-ids

## Evidence
See `knowledge/locator.md` for documented locator findings and rejected patterns.

## Compliance
- Locator agent enforces this priority
- Review agent rejects XPath when a stable resource-id exists
- Screenshot + XML evidence required for all new locators
