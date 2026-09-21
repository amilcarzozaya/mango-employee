# MANGO Evals & Benchmark

```bash
mango benchmark run EMPLOYEE --runtime prepare
mango benchmark run EMPLOYEE --runtime codex
mango benchmark report EMPLOYEE evals/results/bench_x.json
mango benchmark compare EMPLOYEE result-a.json result-b.json
```

The existing Golden Set is the benchmark corpus. Offline `prepare` mode is the reproducible baseline; live modes require the corresponding CLI and credentials.
