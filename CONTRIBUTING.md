# Contributing to HALA AI

Thank you for your interest in contributing. HALA AI is a research-grade
system, so correctness, reproducibility, and safety matter more than speed.

## Development Setup

```bash
git clone https://github.com/ko-co87de/HALA-AI.git
cd HALA-AI
pip install -e .
pytest
```

## Branching

- `main` — always runnable, tested, reviewed.
- `development` — integration branch for completed features.
- `feature/*` — new features.
- `experiment/*` — exploratory work that may be discarded.
- `security/*` — security fixes and red-team findings.

Never commit directly to `main`.

## Pull Requests

1. Open a PR from a feature branch to `development`.
2. All CI checks must pass (lint, format, type-check, unit tests, integration
   tests, dependency audit, secret scanning, static security analysis).
3. Security-sensitive changes require an independent review and must not be
   merged automatically.
4. Describe the change, the evidence (test results, benchmarks), and any
   known limitations.

## Testing

- `tests/unit` — pure logic.
- `tests/integration` — component interactions.
- `tests/regression` — every confirmed security failure.
- `tests/security` — adversarial probes.
- `tests/benchmark` — performance comparisons against the baseline.

Never delete a failing test to improve a score. Report failures as findings.

## Code Style

- Python, type-annotated, documented.
- No hardcoded secrets, credentials, or API keys.
- Third-party components must carry a verified license.
- Prefer minimal, purpose-built code over framework proliferation.

## Reporting Issues

Use the issue template. Include:
- Steps to reproduce.
- Environment (OS, Python version, model used).
- Expected vs actual behavior.
- Any logs or traces.