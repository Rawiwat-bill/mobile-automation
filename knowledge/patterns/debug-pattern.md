# Debug Pattern

## Problem
Test failures are approached with random fixes, changing multiple things at once, without understanding the root cause. This wastes time and introduces new bugs.

## Recommended Pattern
Apply systematic-debugging methodology:

1. **Phase 1 — Root Cause Investigation**
   - Read error messages carefully (don't skip).
   - Reproduce consistently.
   - Check recent changes (`git diff`, recent commits).
   - Gather evidence (screenshots, XML, logs).
   - Trace data flow to find where the bad value originates.

2. **Phase 2 — Pattern Analysis**
   - Find working examples in the same codebase.
   - Compare working vs broken to identify differences.
   - Understand dependencies.

3. **Phase 3 — Hypothesis and Testing**
   - Form a single hypothesis: "I think X is the root cause because Y."
   - Test minimally: change one variable at a time.
   - Verify before continuing.

4. **Phase 4 — Implementation**
   - Create a failing test case first.
   - Implement a single fix addressing the root cause.
   - Verify fix resolves the issue without breaking anything else.

## Anti-Pattern
- Changing multiple things at once and running tests.
- "Quick fix for now, investigate later."
- "Just try changing X and see if it works."
- Fixing symptoms instead of root cause.
- Adding more fixes after the first fix fails, instead of re-investigating.

## Example
```robot
# Step 1: Read error — "Element not found"
# Step 2: Check page source — element has different resource-id
# Step 3: Check recent commits — locator file was updated
# Step 4: Hypothesis — "The locator changed in the latest app build"
# Step 5: Test — Update to new resource-id, run test → PASS
```

## When Not to Use
- When the issue is purely a syntax error or typo that is immediately obvious.
- When following a well-known pattern with no ambiguity.
