# MANGO Evals & Benchmark — From Zero

MANGO evaluation separates:

1. structural/offline contract tests;
2. exported behavioral prompts;
3. benchmark runs through prepare or live runtimes.

It does not claim a prepare-mode score is general model intelligence.

## Start with Employee tests

~~~bash
mango validate EMPLOYEE
mango test EMPLOYEE
~~~

## Export eval prompts

~~~bash
mango evals EMPLOYEE --out ./mango-evals
~~~

This converts the Employee Golden Set into prompts for external execution.

## Benchmark in prepare mode

~~~bash
mango benchmark run EMPLOYEE --runtime prepare
~~~

prepare is the reproducible offline baseline.

The command writes/returns benchmark result metadata according to the harness.

## Benchmark with a live runtime

Install/authenticate the runtime first.

Example:

~~~bash
mango benchmark run EMPLOYEE --runtime codex --limit 10
~~~

Live scores depend on model/runtime/provider behavior and should be compared with date/runtime/model context.

## Create a report

~~~bash
mango benchmark report EMPLOYEE RESULT_FILE --out ./benchmark-report.md
~~~

RESULT_FILE is the result path produced by a prior benchmark run.

## Compare results

~~~bash
mango benchmark compare EMPLOYEE result-a.json result-b.json
~~~

## Interpreting the historical baseline

docs/BENCHMARK-BASELINE-v0.10.md is a historical deterministic prepare-mode baseline.

Do not present it as a current frontier-model benchmark.

## Formal reference

See MANGO-EVALS-SPEC.md.
