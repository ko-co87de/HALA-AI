# HALA AI 100X — Deployment Guide

## Requirements

- Python 3.10+
- llama.cpp binary (`llama-cli` or `llama`) for local inference
- A GGUF model file (see below)
- 4 GB RAM minimum, 8 GB recommended

## Quick Start

### 1. Clone

```bash
git clone https://github.com/ko-co87de/HALA-AI.git
cd HALA-AI
```

### 2. Install

```bash
pip install -e .
```

### 3. Get a model

Download a GGUF model. The bundled default is Qwen2.5-Coder-1.5B:

```bash
mkdir -p models
# Download from HuggingFace
curl -L -o models/qwen2.5-coder-1.5b-q4_k_m.gguf \
  "https://huggingface.co/Qwen/Qwen2.5-Coder-1.5B-Instruct-GGUF/resolve/main/qwen2.5-coder-1.5b-instruct-q4_k_m.gguf"
```

### 4. Install llama.cpp (if not already)

```bash
# Termux/Android
pkg install git
git clone https://github.com/ggerganov/llama.cpp.git
cd llama.cpp && cmake -B build && cmake --build build
```

Or use a pre-built binary.

### 5. Run

```bash
hala run "What is the capital of France?"
hala reason "Explain quantum entanglement"
hala tools
hala test
```

## Configuration

HALA AI uses environment variables for configuration:

| Variable | Purpose | Default |
|----------|---------|---------|
| `HALA_MODEL` | Preferred model key | `hala-local-1.5b` |
| `HALA_DATA` | Data directory | `./` |
| `DASHSCOPE_API_KEY` | Qwen3 cloud API key | (none) |
| `DEEPSEEK_API_KEY` | DeepSeek cloud API key | (none) |

## Model Options

| Model | Size | Use Case |
|-------|------|----------|
| Qwen2.5-Coder-1.5B Q4_K_M | 1.1 GB | Local, offline, edge, testing |
| Qwen2.5-Coder-7B Q4_K_M | 4.5 GB | Local, better quality |
| Qwen3-235B-A22B | Cloud | Primary, best quality |
| DeepSeek-V3 | Cloud | Fallback, best coding |

## Android / Termux

Same steps as above. Termux has llama.cpp available via `pkg`:

```bash
pkg install llama.cpp
hala run "Hello"
```

## Cloud Deployment

Set API keys and use cloud models:

```bash
export DASHSCOPE_API_KEY="your-key"
hala run "Complex task" --model hala-primary
```

## Testing

```bash
# Unit + security + integration
pytest tests/test_unit.py tests/test_security.py tests/test_integration.py

# End-to-end (includes model inference)
pytest tests/test_e2e.py

# Generate evaluation report
python3 scripts/run_baseline.py
```

## Development

```bash
pip install -e ".[dev]"
pytest
ruff check .
mypy hala/
```

## Troubleshooting

**"No llama.cpp binary found"**
Install llama.cpp or set `LLAMA_CPP_BIN` to the binary path.

**"Model file not found"**
Ensure the model file exists in `models/` or set `HALA_DATA`.

**"Cloud API key missing"**
Set `DASHSCOPE_API_KEY` or `DEEPSEEK_API_KEY` in your environment.

**Slow inference**
Use a smaller model or Q4_K_M quantization. CPU inference is ~8 t/s on 7 cores.

## License

Code: Apache-2.0. Models carry their own licenses — verify before commercial use.