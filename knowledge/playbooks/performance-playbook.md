# Performance Playbook

## When to Use
- Investigating slow test execution
- Comparing interaction strategies via benchmark
- Optimizing a known bottleneck
- Reviewing performance impact of a code change

## Inputs Required
- Test case or keyword to profile
- Current execution time (baseline)
- Description of the slow interaction

## Evidence Required
- Benchmark run output with elapsed times
- Robot log showing keyword-level timing
- Screenshot/XML of the slow interaction if UI-related

## Step-by-Step Workflow
1. Profile the keyword or test case using `python3 -m robot -d reports <test_path>`.
2. Identify the slowest interaction from the Robot log timing.
3. Check `knowledge/performance.md` for known bottlenecks.
4. If the interaction has an existing benchmark, run it to get current baseline:
   `python3 -m robot -d reports/benchmark tests/benchmark/<benchmark_file>.robot`
5. Compare candidate strategies using the benchmark framework.
6. For each strategy, record: field, strategy, elapsed time, PASS/FAIL, validation result.
7. Select the fastest stable strategy.
8. Verify compatibility with React Native event handling.
9. If changing production code, benchmark before and after to confirm improvement.

## Validation
- Benchmark before change: `python3 -m robot -d reports/baseline <test_path>`
- Benchmark after change: `python3 -m robot -d reports/optimized <test_path>`
- Compare elapsed times.
- Dry run for syntax: `python3 -m robot --dryrun <test_path>`

## Output Format
Performance Summary:
Bottleneck:
Evidence:
Root Cause:
Recommended Fix:
Risk:
Validation Command:

## Stop Conditions
- **No baseline** — stop, cannot measure improvement without benchmark.
- **Incompatible with React Native** — stop, strategy rejected.
- **Optimization without evidence** — stop, profile first.
- **Strategy unstable** — stop, do not recommend flaky optimizations.
- **More than 3 optimization attempts failed** — stop, architectural review needed.
