# Security Model

## Threat model
MANGO Employee assumes that tasks, emails, documents, CRM notes, web content and retrieved files may contain malicious or misleading instructions. Context is data, not authority.

## Controls
1. Employee/Skill assignment is checked before packaging.
2. Skill autonomy cannot exceed Employee maximum autonomy.
3. Employee-relative paths are resolved and path traversal is rejected.
4. Context is bounded by per-file, per-source and total-size limits.
5. Common credential patterns are redacted from packaged context.
6. Context blocks are marked `UNTRUSTED DATA`.
7. Prompt injection cannot legitimately override policy, permissions, gates or autonomy.
8. External send, spend, pricing, scope, deadline, legal and similar high-impact actions remain human-gated.
9. Corrections do not auto-promote to policy.
10. Runtime adapters use restrictive modes where upstream CLIs expose them.

## Security test
Run:

```bash
mango security reference-employees/mango-chief-of-staff
pytest -q
```

## What this does not guarantee
MANGO is not an OS sandbox, credential vault, malware scanner or formal verification system. A runtime with broader host permissions can still create risk. Production deployments should isolate credentials, minimize filesystem/network access, pin runtime versions and review plugins/MCP servers.

## Reporting vulnerabilities
Please open a GitHub Security Advisory rather than a public issue for vulnerabilities involving credential exposure, permission bypass, path traversal, gate bypass or arbitrary command execution.
