# Security Model — Setup and Operating Guide

If you are new, start with docs/START-HERE.md, then return here before live execution or increasing autonomy.

## Security objective

MANGO assumes tasks, emails, documents, CRM notes, web content, and retrieved files may contain malicious or misleading instructions.

**Context is data, not authority.**

## First security checklist

Before using a live runtime:

~~~bash
mango validate EMPLOYEE
mango test EMPLOYEE
mango security EMPLOYEE
mango doctor
~~~

Use prepare mode first.

## Main controls

1. Employee/Skill assignment is checked before packaging.
2. Skill autonomy cannot exceed Employee maximum autonomy.
3. Employee-relative paths reject traversal outside the project.
4. Context is bounded by file/source/total limits.
5. Common credential patterns are redacted from packaged context.
6. Context blocks are labeled UNTRUSTED DATA.
7. Context cannot legitimately override policy, permissions, Gates, or autonomy.
8. High-impact categories remain human-gated.
9. Corrections do not silently auto-promote to policy.
10. Runtime adapters use restrictive modes where upstream CLIs expose them.
11. Chain handoffs cannot expand authority.
12. Chain child must preserve receipt lineage.

## Credentials

Do not place real credentials in:

- employee.json;
- context markdown;
- test fixtures;
- public Git commits;
- Memory values.

Use the third-party runtime’s supported credential mechanism or a deployment secret manager.

MANGO includes pattern redaction, but redaction is defense-in-depth, not a secret-management strategy.

## Runtime boundary

MANGO is an application-level control layer.

It is not:

- an OS sandbox;
- a container boundary;
- a credential vault;
- a malware scanner;
- a formal verification system.

A third-party runtime with broad host permissions can still create risk.

## Tool boundary

The reference build locally executes only implemented adapters/capabilities.

External adapter declarations are not fake implementations.

Do not assume registering an email/CRM/finance Tool means MANGO can safely execute it.

## Human approval

Approval must be explicit.

Silence is never approval.

Do not manually edit State databases to convert pending/rejected decisions into approved state.

## Chain safety

mango chain does not grant the child extra permissions.

Trusted Runtime Handoff is trusted only for lineage/task narrowing. It cannot override:

- Employee policy;
- permissions;
- autonomy;
- Tools;
- Gates;
- human final authority.

## Run the repository security suite

For maintainers/developers:

~~~bash
python -m pip install pytest
pytest -q
~~~

For a specific Employee:

~~~bash
mango security EMPLOYEE
~~~

## Reporting vulnerabilities

Use a private GitHub Security Advisory for issues involving:

- credential exposure;
- permission bypass;
- path traversal;
- Gate bypass;
- arbitrary command execution;
- cross-Employee leakage;
- handoff/lineage bypass.

Do not post real credentials/client data in public issues.

Root policy: SECURITY.md.
Threat model: THREAT-MODEL.md.

## Meeting transcripts

Meeting Intelligence transcriptions may contain personal or confidential information.
A live runtime can transmit input to its configured model provider. Obtain appropriate
consent/authorization and restrict output-file and --prompt-out access.
The Meeting CLI does not automatically send reports or promote Memory candidates.

## Quotation data and approvals

Quote Builder stores seller profiles, customer names, pricing and issued
documents under each Employee's quotes/ directory. Protect this directory
and backups: never commit it to a public repository. The release backup
includes the folio SQLite ledger and profiles/drafts/issued JSON snapshots,
but not regenerated PDF/DOCX outputs.

An issued quote requires approved-by, which is a manual statement, **not
authenticated identity**. Do not use it as a replacement for enterprise
SSO, roles or a formal Approval Card workflow when such controls are needed.
A SHA256 draft digest detects accidental tampering but is not a signature.

## Formal Approval Cards para cotizaciones y reuniones (RC3)

La emisión comercial de un Employee que tenga Gates activos
pricing/scope/deadline/legal no puede utilizar sólo el argumento
--approved-by. Requiere tarjetas aprobadas vinculadas al Run y al SHA256
del borrador exacto. Cada tarjeta configurada debe estar aprobada.

Si el Employee activa sensitive_data y utiliza un runtime externo para
una transcripción, el workflow solicita aprobación vinculada al hash
del archivo y a runtime/modelo ANTES de enviarlo. Una fuente alterada
invalida esa aprobación. Las salidas rastreables se guardan dentro
del Employee. Los backups incluyen informes validados, pero no
transcripciones originales ni prompts completos por defecto.

El CLI registra decisiones de operadores pero no autentica su identidad.
Una empresa debe implementar SSO, roles, cifrado y políticas de conservación.

La comprobación `sensitive_data` se realiza tanto en el workflow como
en el propio servicio de Meeting Intelligence. El comando directo
no permite saltarse una aprobación formal antes de utilizar un modelo externo.
