# Troubleshooting — From Installation to Chain Runtime

Start by identifying which layer failed:

1. Python/package installation;
2. MANGO Employee validation;
3. Skill assignment/autonomy;
4. third-party Runtime;
5. State/Gate/approval;
6. Tool adapter;
7. Memory;
8. Chain/handoff;
9. release/upgrade.

## mango: command not found

Check whether your virtual environment is active.

~~~bash
python -m pip show mango-employee-cli
python -m mango_cli --version
~~~

If python -m mango_cli works, reactivate the environment or reinstall:

~~~bash
python -m pip install -e .
~~~

## Python version is too old

Verify:

~~~bash
python --version
~~~

MANGO requires Python >=3.10.

Install a newer Python, recreate the virtual environment, then reinstall.

## PowerShell blocks .venv activation

You can use Command Prompt:

~~~cmd
.venv\Scripts\activate.bat
~~~

Or follow your organization’s PowerShell execution-policy requirements.

Do not weaken enterprise security policy just to activate a virtual environment.

## Git pull fails because you changed files

Check:

~~~bash
git status
~~~

Do not discard work blindly.

Options:

- commit your changes;
- create a branch;
- stash them;
- manually reconcile them.

See UPGRADE.md.

## mango validate fails

Read every ERROR line.

Common causes:

- invalid JSON;
- missing required Employee fields;
- incomplete Skill object;
- Skill autonomy above Employee max;
- Gate/tool inconsistency.

Validate after each edit:

~~~bash
mango validate EMPLOYEE
~~~

## Skill not declared/found

The Skill ID is wrong, unregistered, or unassigned.

Check assigned Skills:

~~~bash
mango info EMPLOYEE
~~~

Then inspect skills/registry.json.

## Skill exists in registry but is not assigned to this employee

This is intentional security behavior.

Add an explicit Skill assignment to employee.json and validate again.

See SKILLS.md.

## Skill autonomy exceeds employee maximum

Do not immediately raise max autonomy.

First decide whether the Employee should run that Skill.

If yes, update the Employee deliberately, then:

~~~bash
mango validate EMPLOYEE
mango security EMPLOYEE
~~~

## Context path escapes employee directory

--context only accepts Employee-relative paths that remain inside the Employee project.

Move/copy the intended context into the Employee directory or declare an appropriate bounded source. Do not use ../ to bypass the boundary.

## Runtime CLI not found in PATH

~~~bash
mango doctor
~~~

Install the desired runtime, open a new terminal if PATH changed, activate your environment, then run doctor again.

## Runtime is FOUND but live execution fails

mango doctor checks binary discovery only.

Verify the third-party runtime directly:

~~~bash
codex --version
claude --version
gemini --version
hermes --help
openclaw --version
~~~

Then complete that runtime’s authentication/setup.

See RUNTIMES.md.

## Runtime authentication or quota error

This is normally upstream of MANGO.

Test the runtime outside MANGO with a simple prompt according to its official docs.

Do not put API keys in Employee context files.

## prepare works but live runtime fails

This usually proves the MANGO contract/package is buildable and narrows the issue to:

- runtime installation;
- authentication;
- provider/model access;
- runtime CLI compatibility;
- network;
- account quota.

Save the prepare package/prompt and compare.

## A Run is blocked

Inspect:

~~~bash
mango status EMPLOYEE RUN_ID
mango trace explain EMPLOYEE RUN_ID
~~~

Blocked may be intentional.

Examples:

- waiting for corrected handoff;
- missing/critical context;
- policy decision;
- supported retry path.

## A Chain is blocked

Inspect:

~~~bash
mango chain-status EMPLOYEE RUN_ID
mango trace audit EMPLOYEE RUN_ID
~~~

Chain can block if the parent fails to emit a valid typed handoff.

The parent output is preserved under:

~~~text
state/chains/RUN_ID/01-parent-output.txt
~~~

Correct the handoff JSON, then:

~~~bash
mango handoff EMPLOYEE RUN_ID --file corrected-handoff.json
~~~

This resumes the same root Run.

## Child receipt missing or query_id mismatch

A completed child must return a handoff receipt preserving lineage.

If not, the chain fails rather than silently accepting a different query.

Inspect:

~~~text
state/chains/RUN_ID/
~~~

and trace audit.

## Chain says child Skill is not assigned

Both parent and child must be explicitly assigned to the Employee.

See SKILLS.md.

## Approval is pending

List:

~~~bash
mango approvals EMPLOYEE
~~~

Then approve or reject explicitly.

Silence does not count as approval.

## Tool invoke returns approval_required

This is expected when:

- the Tool/capability is authorized;
- but the configured Gate requires human approval;
- and --execute was requested.

Use the Approval/Action flow instead of bypassing the Gate.

## External Tool does nothing

Registering an adapter named email/calendar/CRM does not implement the external integration by itself.

The reference build intentionally does not fake external side effects.

Only supported local adapters actually execute.

## Memory I added is not appearing in prompts

New memories are candidate by default.

Normal Runtime Packages retrieve bounded relevant **verified/promoted** memory.

Check:

~~~bash
mango memory explain EMPLOYEE MEM_ID
mango memory audit EMPLOYEE
mango memory search EMPLOYEE "topic"
~~~

Verify/promote only when authority/provenance is appropriate.

## memory approve fails or policy seems strict

MANGO enforces “Data cannot become Authority.”

Unknown/external/agent-originated data cannot silently become promoted authority without human approval/provenance rules.

Do not work around this by lying about authority.

## Trace audit reports orphan spans or chain problems

Inspect:

~~~bash
mango trace show EMPLOYEE RUN_ID
mango chain-status EMPLOYEE RUN_ID
~~~

For a completed two-Skill chain, audit expects two completed chain steps and parent/child handoff provenance.

## Release version mismatch

If mango release manifest reports a version mismatch, the hardening release version and pyproject.toml do not match.

For repository maintainers, align release metadata intentionally. Do not edit the generated manifest to hide the mismatch.

## Backup verification fails

Do not restore it.

Create or locate a backup whose checksums pass:

~~~bash
mango release verify-backup EMPLOYEE BACKUP_DIRECTORY
~~~

## Restore refuses overwrite

This is a safety feature.

Use --force only after you:

1. chose the correct backup;
2. verified checksums;
3. intentionally want to overwrite the operational stores.

## Still stuck

Collect:

- mango --version;
- python --version;
- mango doctor;
- mango validate EMPLOYEE;
- mango security EMPLOYEE;
- exact command;
- exact error;
- OS;
- runtime name/version if live execution is involved.

Do not include secrets, API keys, client records, or confidential files in a public GitHub issue.

## Meeting Intelligence

Si mango meeting rechaza una cita, revisa que source_excerpt sea una
subcadena literal de la transcripción. No desactives la verificación.
Si falta un responsable o una fecha, puede ser correcto: revisa
review_required. Para DOCX/PDF instala python -m pip install -e ".[meeting]".
El comando rechaza PDFs sin texto y no hace OCR ni transcripción de audio.
Consulta meeting-intelligence/USER-GUIDE.md.

## Quote Builder

Si no aparece commercial-quotation en mango info EMPLOYEE, asígnala
explícitamente y ejecuta mango validate/mango security.
Si falta Word/PDF, instala python -m pip install -e ".[quote]".
Si un impuesto no está configurado o vigente, consulta el perfil y confirma
el tratamiento con tu asesor. Nunca fuerces la tasa desde una descripción.
Si el borrador falla el control SHA256, restaura la versión original o
genera un borrador nuevo. Si ya existe un archivo de salida utiliza un
directorio nuevo; no lo sobrescribas. Folios ya asignados se reutilizan
en reintentos de issue del mismo borrador/atestado.
Consulta [Quote Builder](quote-builder/USER-GUIDE.md).
