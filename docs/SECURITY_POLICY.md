# HALA AI 100X — Security Policy

## Purpose

HALA AI executes code, accesses tools, and processes untrusted data. This
document defines the security requirements and operational rules.

## Threat Model

Based on OWASP Top 10 for Agentic Applications (2025):

| ID | Threat | Mitigation |
|----|--------|------------|
| ASI01 | Agent Goal Hijack | Input validation, untrusted data isolation |
| ASI02 | Tool Misuse | Least privilege, action confirmation |
| ASI03 | Identity & Privilege Abuse | Scoped credentials, no hardcoded secrets |
| ASI04 | Supply Chain | Verified dependencies, license checks |
| ASI05 | Unexpected Code Execution | Sandboxed execution |
| ASI06 | Memory Poisoning | Fact/inference/source separation |
| ASI07 | Insecure Inter-Agent Comms | Authenticated channels |
| ASI08 | Cascading Failures | Isolation, circuit breakers |
| ASI09 | Human-Agent Trust | Explicit confidence, citations |
| ASI10 | Rogue Agents | Independent monitoring, rollback |

## Design Rules

1. **Untrusted data isolation.** All external content (web pages, files,
   tool outputs, user inputs) is explicitly marked as untrusted and separated
   from system instructions. Never concatenate untrusted data into prompts
   without delimiters.

2. **Least privilege.** Agents receive only the tools they need for the
   current task. No blanket access.

3. **Tool allowlist.** Terminal commands are restricted to a safe allowlist.
   Blocked: sudo, curl, wget, rm -rf /, network tools, shell interpreters.

4. **Sandboxing.** Python execution uses a restricted namespace without
   os.system, subprocess, or filesystem access.

5. **Deterministic validation.** Tool outputs are validated by code, not
   trusted. Model outputs are never treated as facts without verification.

6. **Memory separation.** Facts, inferences, experiences, and sources are
   stored separately with confidence tiers. Inferences are never promoted to
   facts without verification.

7. **No secrets.** Credentials use environment variables only. Never stored
   in the repository.

8. **Human approval.** Destructive, financial, or externally visible actions
   require explicit confirmation.

9. **Independent red team.** Security findings are not modified or deleted
   without independent review.

## Operational Rules

- Run in an isolated environment (container, VM, or sandbox).
- Never execute untrusted code with real privileges.
- Keep the system updated; run `scripts/audit_deps.sh` regularly.
- Review red team reports before deploying any change.
- Report vulnerabilities privately to maintainers.

## Testing

Security tests live in `tests/test_security.py`. Every confirmed failure
becomes a permanent regression test. Never delete a failing test to improve
a benchmark score.

## Incident Response

1. Isolate the affected environment.
2. Preserve logs and reports.
3. Assess scope and impact.
4. Apply fix and regression test.
5. Document in `docs/SECURITY_INCIDENTS.md`.
6. Notify affected parties if required.