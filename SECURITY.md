# Security Policy

## Supported Versions

Only the latest `main` / tagged release receives security fixes.

## Reporting a Vulnerability

**Do not open a public issue.** Email the maintainers with:
- Description of the vulnerability.
- Reproduction steps.
- Impact assessment.
- Proposed fix (optional).

We will acknowledge within 5 business days.

## Scope

This policy covers the HALA AI codebase and its official tools. It does not
cover:
- Third-party models or providers.
- User misconfiguration.
- Environments the user controls outside this repository.

## Security Design Principles

1. **Least privilege.** Agents receive only the tools they need.
2. **Sandboxing.** Code execution happens in isolated sandboxes, never on the
   host with real privileges.
3. **Untrusted data isolation.** External content (web pages, files, tool
   outputs) is explicitly marked as untrusted and separated from instructions.
4. **Human approval for high-risk actions.** Destructive, financial, or
   externally visible actions require confirmation.
5. **Deterministic validation.** Tool outputs and model outputs are validated
   by code, not trusted.
6. **No secrets in the repository.** Secrets use environment variables or a
   secret manager. GitHub Actions secret scanning is enabled.
7. **Independent red team.** Security findings are not modified or deleted
   without independent review.

## Prohibited

- Committing credentials, API keys, or private data.
- Executing untrusted code in privileged environments.
- Disabling security tests to improve benchmark scores.

See [`docs/SECURITY_POLICY.md`](docs/SECURITY_POLICY.md) for the full policy.