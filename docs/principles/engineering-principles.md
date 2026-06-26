# Engineering Principles — Enterprise Mobile QA Platform

## Principle 1: Evidence Before Code

No code change for a flaky mobile UI issue without screenshots, Appium XML, and comparison evidence. Manual success must be compared against automation failure before a fix is proposed.

## Principle 2: Smallest Safe Change

Every change must be minimal and scoped. No broad refactors without explicit approval. No "while I'm here" improvements. One experiment at a time.

## Principle 3: Reuse Before Create

Inspect existing keywords, locators, resources, and knowledge before writing new ones. Duplication is technical debt. Reuse is the default.

## Principle 4: Root Cause First

No fix is allowed for failures until systematic-debugging Phase 1 (root cause investigation) is complete. Symptom fixes are failures.

## Principle 5: Separation by Concern

Tests describe business flow. Page resources own screen interactions. Locator resources own element definitions. Shared resources own cross-screen flow. Libraries own reusable Python helpers. Knowledge owns solved problems.

## Principle 6: Security Is Not Optional

Real PII never enters the repository. Local sensitive data uses gitignored files. Logs, reports, and screenshots are masked. Security review gates every commit.

## Principle 7: Knowledge Over Skills

Internal project knowledge (`knowledge/`) is the primary truth source. External skills (`.agents/skits/`) are secondary reference. When they conflict, internal knowledge wins.

## Principle 8: Validate Before Commit

Robot code changes require dryrun. Locator changes require XML evidence. All changes require review-agent approval. Security-sensitive changes require security-review-agent approval.

## Principle 9: Idempotent Strategy

Every interaction strategy should produce the same result when run multiple times. Flaky strategies are replaced, not worked around.

## Principle 10: Platform Empathy

The app is React Native. Automation must adapt to RN's event handling model, not fight it. `adb shell` level interaction is a valid strategy when Appium gestures fail on RN components.
