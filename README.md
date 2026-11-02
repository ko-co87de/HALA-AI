# HALA AI 100X

**Open-weight, multi-capability, self-improving AI system.**

HALA AI 100X is an open-source AI system designed to improve through repeated
experiments, evaluations, and adversarial testing. It is not a single chatbot
wrapper; it is a research-grade platform for building, evaluating, and evolving
autonomous AI agents.

> **Status:** Phase 1 (Alpha) — architecture documented, research completed,
> prototype runnable, automated tests passing.

## Features

- **Central Reasoning Engine** — task understanding, planning, tool selection,
  delegation, and result verification.
- **Specialized Agents** — researcher, programmer, scientist, mathematician,
  analyst, reviewer, security (all pluggable).
- **Memory System** — conversation memory, task memory, project memory,
  episodic experience memory, error/fix log, and a searchable knowledge base.
  Facts, inferences, and external sources are explicitly separated.
- **Research Agent** — independent scientific researcher that can search the
  web, read papers, analyze repositories, and produce cited reports.
- **Red Team** — independent adversarial system that probes for prompt
  injection, memory poisoning, tool abuse, data leakage, and more. Every
  discovered failure becomes a permanent regression test.
- **Self-Improvement Engine** — research → idea generation → multiple
  candidates → implementation → red team → independent evaluation → benchmark
  → comparison → accept/reject → next cycle.
- **Evaluation Engine** — unit, integration, regression, security, benchmark,
  and end-to-end tests with JSON/Markdown reports and a fixed baseline.
- **Multi-model routing** — pluggable model registry with adapters for local
  (llama.cpp) and cloud providers. No single-model dependency.

## Architecture

See [`docs/ARCHITECTURE.md`](docs/ARCHITECTURE.md).

```
HALA-AI/
├── core/            # coordinator, reasoning, planning, orchestration
├── agents/          # specialized expert agents
├── models/          # registry, adapters, inference, routing
├── memory/          # short-term, long-term, episodic, knowledge
├── tools/           # filesystem, python, terminal, github, browser, integrations
├── research/        # independent scientific researcher
├── training/        # datasets, finetuning, evaluation
├── redteam/         # attacks, regression tests, reports
├── evaluation/      # benchmarks, metrics, reports
├── security/        # policies, input validation, sandboxing
├── interface/       # CLI, API, web
├── deployment/      # android, local, cloud
├── tests/           # unit, integration, regression, security, e2e
└── .github/workflows
```

## Quick Start

```bash
git clone https://github.com/ko-co87de/HALA-AI.git
cd HALA-AI
pip install -e .

# Run locally with the bundled model
hala run "What is the capital of France?" --local

# Run a programming task
hala run "Create a function that checks if a number is prime" --local
```

See [`docs/DEPLOYMENT_GUIDE.md`](docs/DEPLOYMENT_GUIDE.md) for detailed setup.

## Model Strategy

| Role | Model | Purpose |
|------|-------|---------|
| Primary | Qwen3 / DeepSeek-V3 (open weights) | General reasoning, coding, Arabic |
| Fallback | Mistral / Gemma | Alternative provider |
| Local | Qwen2.5-Coder-1.5B (GGUF Q4_K_M) | Offline, low-resource, edge |

All models are **open weights**. The system is designed to be independent of
any single provider or model.

## License

Code owned by this project: **Apache-2.0**. See `LICENSE`.

Third-party components and models carry their own licenses. Always verify
before commercial use. See [`docs/MODEL_SELECTION.md`](docs/MODEL_SELECTION.md).

## Safety

HALA AI is a research system. It executes code and accesses tools. Always run
in an isolated environment. See [`docs/SECURITY_POLICY.md`](docs/SECURITY_POLICY.md).

## Citation

If you use HALA AI in research, please cite this repository.