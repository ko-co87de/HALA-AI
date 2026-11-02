# HALA AI 100X — Master Plan
Version: 1.0 | Date: 2026-11-01 | Status: Phase 1 (Alpha)

## 1. Vision

Build an open-weight, multi-capability, self-improving AI system that gets
measurably better through repeated experiments, evaluations, and adversarial
testing — not by claiming general intelligence.

## 2. Measurable Goals (100X)

| Metric | Baseline | Target | Measurement |
|--------|----------|--------|-------------|
| Task Success Rate | TBD | 100x baseline on matched tasks | `reports/latest_evaluation.json` |
| Cost per Successful Task | TBD | Reduce by 10-100x | Automated |
| Time per Successful Task | TBD | Reduce by 10-100x | Automated |
| Reasoning Accuracy | TBD | Improve via self-improvement cycles | Benchmarks |
| Coding Success | TBD | Improve via self-improvement cycles | SWE-style tests |
| Tool Reliability | TBD | Improve via regression tests | Automated |
| Memory Retrieval Accuracy | TBD | Improve via retrieval tests | Automated |
| Security Robustness | TBD | Reduce attack success | Red team reports |

No gaming of tests. Every version is compared against a fixed baseline.

## 3. Architecture Decisions

### 3.1 Single vs Multi-Agent
**Decision:** Hybrid. A central coordinator decomposes tasks and delegates to
specialized agents only when the task genuinely benefits. Evidence:
- Agentless achieves 32% on SWE-bench Lite at $0.70 — best open-source — by
  *not* letting the LLM decide actions (arXiv 2407.01489).
- Complex multi-step tasks still benefit from tool use and delegation.
- **Rule:** use the simplest mechanism that solves the task. Prefer
  deterministic code over LLM control flow.

### 3.2 Memory
**Decision:** Structured memory with fact/inference/source separation.
Evidence: HINDSIGHT (arXiv 2025) reaches 83.6% on LongMemEval with 20B model
using four retrieval channels (vector, BM25, graph, temporal) + fact-belief
separation. MemOS (SJTU/ZJU, 2025) treats memory as a schedulable resource.

### 3.3 Self-Improvement
**Decision:** Evolutionary loop with automated evaluators, inspired by
AlphaEvolve (DeepMind, 2025). Never auto-update weights in production. All
training happens in isolated branches; new versions are compared against the
old before promotion.

### 3.4 Model Strategy
**Decision:** Multi-model, provider-independent. Primary: Qwen3 / DeepSeek-V3
(open weights). Fallback: Mistral/Gemma. Local: Qwen2.5-Coder-1.5B GGUF for
offline/edge. See `docs/MODEL_SELECTION.md`.

### 3.5 Evaluation
**Decision:** Independent evaluation engine, never self-reported. Based on
Inspect AI (UK AISI) and SWE-bench. Fixed baseline. JSON + Markdown reports.

## 4. Phases

| Phase | Description | Status |
|-------|-------------|--------|
| 0 | GitHub verification, repo creation | DONE |
| 1 | Old repo audit | DONE (empty) |
| 2 | Multi-source research | DONE |
| 3 | Architecture & model selection | DONE |
| 4 | Project files & docs | IN PROGRESS |
| 5 | Runnable prototype | IN PROGRESS |
| 6 | Agent engine & tools | PENDING |
| 7 | Memory, research, planning | PENDING |
| 8 | Evaluation engine | PENDING |
| 9 | Red team | PENDING |
| 10 | Self-improvement engine | PENDING |
| 11 | Test execution & fixes | PENDING |
| 12 | Performance comparison | PENDING |
| 13 | HALA AI Alpha release | PENDING |

## 5. Key Risks

1. **No API keys available** — system must run locally-first with llama.cpp.
2. **Limited memory (7.4GB)** — small models only; no large-model training.
3. **Single session** — work persists in repo, not in memory.
4. **Research claims** — all sourced; nothing assumed.

## 6. Next Actions

See `NEXT_ACTIONS.md`.