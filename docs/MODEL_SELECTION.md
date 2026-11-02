# Model Selection

Date: 2026-11-01

## Distinction: Open Weights vs Open Source

**Open Weights:** Model parameters are publicly downloadable. The training
data, code, and pipeline are often NOT public. You can run and fine-tune the
model, but cannot reproduce or audit the training.

**Open Source:** Full reproducibility — code, data, training pipeline, and
weights are all public and auditable.

HALA AI uses **open-weight** models. We prefer Apache-2.0 or MIT licenses for
maximum permissiveness, but evaluate each model independently.

## Evaluation Criteria

| Criterion | Weight | Why |
|-----------|--------|-----|
| Reasoning | High | Core capability |
| Math | High | STEM tasks |
| Coding | High | Programming tasks |
| Tool use | High | Agent capability |
| Arabic | Medium | Project requirement |
| Context length | Medium | Long tasks |
| Memory usage | High | Local deployment |
| Inference speed | High | Local deployment |
| Fine-tuning ease | Medium | Customization |
| License | High | Legal safety |

## Candidate Models

### Qwen3-235B-A22B (Alibaba)
- **License:** Apache-2.0 ✓
- **Architecture:** MoE, 235B total / 22B active
- **MMLU:** 88.4% | **GPQA:** 62.8% | **HumanEval:** 88.2% | **MATH:** 81.3%
- **SWE-bench:** 38.4%
- **Context:** 33k tokens
- **Arabic:** Strong (multilingual training)
- **Verdict:** **PRIMARY** — best aggregate, Apache-2.0, strong Arabic.

### DeepSeek-V3 (DeepSeek)
- **License:** Custom (permissive but not standard) ⚠
- **Architecture:** MoE, 671B total / 37B active
- **MMLU:** 87.1% | **GPQA:** 59.1% | **HumanEval:** 82.6% | **MATH:** 61.6%
- **SWE-bench:** 42.0% (best among Chinese models)
- **Context:** 128k tokens
- **Verdict:** **FALLBACK** — best coding, but custom license.

### Mistral Large / Mistral Small
- **License:** Apache-2.0 (some variants)
- **Verdict:** Secondary fallback.

### Gemma 3 (Google)
- **License:** Gemma terms (permissive but restrictive clauses)
- **Verdict:** Local small model option.

### Qwen2.5-Coder-1.5B (GGUF Q4_K_M)
- **License:** Apache-2.0 ✓
- **Size:** 1.1 GB
- **Speed:** ~8 t/s on CPU (7 cores, 7.4GB RAM)
- **Context:** 32k
- **Verdict:** **LOCAL** — offline, edge, Termux, testing.

## Final Selection

| Role | Model | License | Why |
|------|-------|---------|-----|
| Primary | Qwen3-235B-A22B | Apache-2.0 | Best aggregate, Apache-2.0, Arabic |
| Fallback | DeepSeek-V3 | Custom | Best coding, long context |
| Local | Qwen2.5-Coder-1.5B Q4_K_M | Apache-2.0 | Offline, edge, 1.1GB |
| Local Small | Gemma 3 4B / Qwen2.5-7B | Various | If 1.5B too weak |

## Provider Independence

HALA AI supports multiple providers via adapters:
- llama.cpp (local, default)
- OpenAI-compatible APIs
- Hugging Face inference
- Custom endpoints

No single provider dependency. Failover is automatic.