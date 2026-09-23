# Security Policy

This file explains how to report security issues.

For the operating security model, read docs/SECURITY.md.

For first-time setup, read docs/START-HERE.md.

## Report privately

Prefer a GitHub Security Advisory for vulnerabilities.

Do not open a public issue containing:

- API keys;
- passwords/tokens;
- real client records;
- private Employee context;
- production database contents;
- confidential trace output.

## High-priority issue classes

Examples:

- credential exposure;
- permission escalation;
- path traversal;
- Gate/approval bypass;
- arbitrary command execution;
- cross-Employee data leakage;
- Tool authorization bypass;
- handoff/receipt lineage bypass;
- malicious context overriding policy;
- release/restore integrity bypass.

## Useful sanitized report details

Include when safe:

- MANGO version;
- OS/Python version;
- affected command;
- expected vs actual behavior;
- minimal fictional reproduction;
- whether a live runtime was involved;
- runtime name/version;
- relevant non-secret logs/trace IDs.

## Security boundary

MANGO is an application-level control system, not a replacement for OS/container/credential isolation.

See docs/SECURITY.md and THREAT-MODEL.md.
