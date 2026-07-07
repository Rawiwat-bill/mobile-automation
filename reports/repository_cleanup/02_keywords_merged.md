# 02 — Keywords Merged

> Keywords merged this sprint.

---

**None.**

Zero keywords were merged. All duplicate candidates were classified as
BENCHMARK ISOLATION or INTENTIONAL DUPLICATE after side-by-side comparison
revealed different side effects, signatures, or retry behaviors.

Merging any of them would violate the sprint rule: "No runtime behavior change."

---

## Merge Attempt Log

No merge attempts were made. Classification was clear from the implementation
comparison — every duplicate has a legitimate reason to remain separate.

| Keyword | Why Not Merged |
|---------|----------------|
| Allow Android Permission If Visible | Benchmark version has `Record Appium Action` calls (measurement). Different locator robustness. |
| Landing Screen Should Be Visible | Production has 60s built-in retry; benchmark has none (caller controls). Different timing behavior. |
| Field Should Be Blurred / Profile Fields Should Be Blurred | Different signatures (generic vs page-specific). Merging requires Page Object change — out of scope. |
