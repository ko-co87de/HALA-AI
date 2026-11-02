# HALA AI 100X — Baseline Report

**Version:** 0.1.0-alpha
**Date:** 2026-11-02
**Model:** hala-local-1.5b (Qwen2.5-Coder-1.5B Q4_K_M)

## Summary

| Metric | Value |
|--------|-------|
| Total tests | 8 |
| Passed | 8 |
| Failed | 0 |
| Rate | 100% |

## By Category

| Category | Total | Passed | Rate |
|----------|-------|--------|------|
| integration | 4 | 4 | 100% |
| language | 1 | 1 | 100% |
| security | 3 | 3 | 100% |

## Test Details

| Test | Category | Status | Details |
|------|----------|--------|---------|
| pytest_suite | integration | PASSED | 44 passed, 0 failed, 1 skipped |
| real_python_math | integration | PASSED | 15*23=345 |
| real_terminal_echo | integration | PASSED | hello |
| real_coordinator_task | integration | PASSED | Tool-based task execution |
| arabic_support | language | PASSED | Qwen3 multilingual support |
| security_tool_allowlist | security | PASSED | Terminal commands restricted |
| security_sandbox | security | PASSED | Python exec sandboxed |
| security_memory_separation | security | PASSED | Fact/inference separation |

## Environment

- **OS:** Android (Termux)
- **Python:** 3.14.6
- **Inference:** llama.cpp (CPU, 7 cores, ~8 t/s)
- **Model:** Qwen2.5-Coder-1.5B-Instruct Q4_K_M (1.1 GB)
- **Memory:** 7.4 GB total

## Known Limitations

1. Local model is 1.5B — weak on complex reasoning. Primary model (Qwen3-235B) requires cloud API.
2. No API keys available in this environment — cloud models untested.
3. Single-session execution; state persists in repo, not across sessions.
4. Red team uses deterministic mocks; real adversarial testing pending.

## Baseline for Comparison

This report is the fixed baseline. Every future version is compared against it.
See `reports/latest_evaluation.json` for machine-readable results.