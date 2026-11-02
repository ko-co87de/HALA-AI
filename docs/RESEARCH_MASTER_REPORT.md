# HALA AI 100X — Research Master Report
Date: 2026-11-01 | Sources: GitHub, arXiv, Reddit, technical reports

## Executive Summary

This report synthesizes findings from GitHub projects, scientific papers,
Reddit discussions, and technical reports to inform the HALA AI architecture.
Every claim is sourced. Key findings:

1. **Simple beats complex for code tasks.** Agentless (arXiv 2407.01489)
   achieves 32% on SWE-bench Lite at $0.70 — best open-source — by *not*
   letting the LLM decide actions. Use deterministic code wherever possible.
2. **Structured memory wins.** HINDSIGHT (arXiv 2025) reaches 83.6% on
   LongMemEval using four retrieval channels and fact-belief separation.
3. **Evolutionary self-improvement works.** AlphaEvolve (DeepMind, 2025)
   discovered a 56-year-open matrix multiplication improvement using LLMs +
   automated evaluators + evolutionary search.
4. **Qwen3 is the strongest open-weight model** on aggregate benchmarks
   (MMLU 88.4%, GPQA 62.8%, HumanEval 88.2%) with Apache-2.0 license.
5. **Red teaming is essential.** OWASP Top 10 for Agentic Apps (2025) lists
   10 categories of attacks that all apply to HALA.

## Key Projects Evaluated

| Project | License | Verdict | Use |
|---------|---------|---------|-----|
| SWE-agent | MIT | Useful | ACI design, tool interfaces |
| OpenHands | MIT | Useful | Event-driven agent loop, SDK design |
| DSPy | MIT | Useful | Signature-based module design |
| Reflexion | MIT | Useful | Verbal self-reflection, episodic memory |
| Agentless | MIT | **Highly useful** | Proves simple beats complex |
| Inspect AI | Apache-2.0 | **Highly useful** | Evaluation framework |
| AlphaEvolve | Proprietary | Concept only | Evolutionary loop design |
| HINDSIGHT | MIT | **Highly useful** | Memory architecture |
| MemOS | MIT | Concept | Memory as schedulable resource |

## Key Papers

- SWE-agent (arXiv 2405.15793) — ACI design, 12.5% SWE-bench.
- Agentless (arXiv 2407.01489) — 32% SWE-bench Lite, $0.70.
- Reflexion (NeurIPS 2023) — 91% HumanEval via verbal reinforcement.
- DSPy (Stanford HAI 2024) — declarative LM pipelines, optimizers.
- OpenHands V1 (arXiv 2511.03690) — production agent SDK.
- AlphaEvolve (arXiv 2506.13131) — evolutionary coding agent.
- HINDSIGHT (arXiv 2025) — structured agent memory.
- Qwen3 Technical Report (arXiv 2505.09388) — model benchmarks.
- DeepSeek-V3 Technical Report (arXiv 2412.19437) — model benchmarks.

## Reddit Findings

- r/LocalLLaMA: Q4_K_M is the sweet spot for quality/speed on commodity
  hardware. llama.cpp beats Ollama by ~18% on raw speed.
- Memory systems converge on extract-store-retrieve. Nobody has solved
  selective access or global consistency.
- Common failure modes: context fragmentation, relevance drift, loops of
  doom, premature termination.

## Technical Reports

- Qwen3 (Alibaba, 2025-04): Best open-weight model on aggregate. Apache-2.0.
- DeepSeek-V3 (DeepSeek, 2024-12): Best on SWE-bench (42%) among Chinese
  models. Custom license.
- AlphaEvolve (DeepMind, 2025-05): Evolutionary coding agent.
- OWASP Top 10 for Agentic Apps (2025-12): 10 attack categories.

## Recommendations

1. Use deterministic code first; add LLM steps only where needed.
2. Implement structured memory with fact/inference/source separation.
3. Build an evolutionary self-improvement loop with automated evaluators.
4. Use Qwen3 as primary open-weight model; DeepSeek-V3 as fallback.
5. Run llama.cpp locally for offline/edge; cloud as optional.
6. Red team every change; every failure becomes a regression test.
7. Never auto-update weights in production.

See `docs/MODEL_SELECTION.md` for model comparison details.