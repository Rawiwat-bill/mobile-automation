# Benchmark Knowledge

## Benchmark Framework

Location: `tests/benchmark/profile_field_benchmark.robot`
Strategy definitions: `resources/benchmark/benchmark_strategies.resource`

## Approach

Each benchmark iteration:
1. Opens app → Landing → Consent → Profile
2. Applies one strategy to the field under test
3. Fills remaining fields with production baseline
4. Validates field value
5. Taps Profile Next, confirms navigation
6. Closes app
7. Records elapsed time and PASS/FAIL result

Clean app restart for each strategy.

## Strategies by Field

### Citizen ID (5 strategies)
- Input Text
- Input Value
- Press Keycodes (current production)
- Adb Shell
- Execute Script

### DOB (4 strategies)
- Picker Calculated (current production — uses date picker)
- Input Text
- Adb Shell
- Input Value

### Mobile Number (5 strategies)
- Input Text
- Input Value
- Press Keycodes (current production)
- Adb Shell
- Execute Script

## Classification

- **PASS:** Strategy completed, field validated, navigation confirmed
- **FAIL_STRATEGY:** Strategy executed but field validation or navigation failed
- **BLOCKED_ENV:** Failed before strategy execution (navigation, permission, device)

## Ranking

Valid (PASS) strategies only. Ranked fastest to slowest per field.

## Internal Project Truth

Benchmark results are the authoritative data source for strategy selection. External skill suggestions about interaction patterns are secondary to measured results from the project's own benchmark suite. Do not change production strategy without benchmark evidence.
