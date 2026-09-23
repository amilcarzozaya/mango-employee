# Command Reference — MANGO Employee CLI 0.13.0rc3

This guide explains the CLI without assuming you already know MANGO terminology.

## Placeholder notation

Examples use uppercase placeholders.

Replace them with real values:

- EMPLOYEE — path to an Employee directory or employee.json.
- RUN_ID — Run ID printed by mango start or mango chain.
- APPROVAL_ID — approval ID printed by request-approval.
- ACTION_ID — prepared action ID.
- TEAM_ID — Team ID returned by team create.
- HANDOFF_ID — Team handoff ID.
- MEM_ID — Memory ID printed by memory add.
- SKILL_ID — exact Skill ID assigned to the Employee.
- RUNTIME — prepare, codex, claude, gemini, hermes, or openclaw.

Example:

~~~text
EMPLOYEE = ./employees/my-employee
SKILL_ID = pre-meeting-brief
~~~

## Discover help from the CLI

~~~bash
mango --help
mango run --help
mango chain --help
mango memory --help
mango tools --help
mango release --help
~~~

## Global version

~~~bash
mango --version
~~~

## doctor — detect optional runtime CLIs

~~~bash
mango doctor
~~~

This checks whether codex, claude, gemini, hermes, and openclaw executables are found in PATH.

It does not test authentication or model access.

## init — create an Employee

~~~bash
mango init ./employees/my-employee
~~~

Interactive. See FIRST-EMPLOYEE.md.

## info — inspect an Employee

~~~bash
mango info EMPLOYEE
~~~

Shows identity, mission, owner, status, max autonomy, and assigned Skills.

## validate — validate Employee contract

~~~bash
mango validate EMPLOYEE
~~~

Exit code 0 means validation passed; 1 means failure.

## test — structural Golden Set test

~~~bash
mango test EMPLOYEE
~~~

Validates the Employee plus test harness structure.

## security — offline security audit

~~~bash
mango security EMPLOYEE
~~~

Run before live execution or autonomy expansion.

## evals — export behavioral eval prompts

~~~bash
mango evals EMPLOYEE --out ./mango-evals
~~~

Produces prompts that can be run with a model/runtime. This does not pretend to evaluate model behavior without execution.

# Single-Skill execution

## run — prepare or execute without persistent State Run

Prepare only:

~~~bash
mango run EMPLOYEE \
  --skill SKILL_ID \
  --task "Describe the task" \
  --runtime prepare
~~~

Write package/prompt:

~~~bash
mango run EMPLOYEE \
  --skill SKILL_ID \
  --task "Describe the task" \
  --runtime prepare \
  --package ./package.json \
  --prompt-out ./prompt.md
~~~

Live runtime:

~~~bash
mango run EMPLOYEE \
  --skill SKILL_ID \
  --task "Describe the task" \
  --runtime codex
~~~

Optional flags:

- --model MODEL
- --context RELATIVE_PATH, repeatable
- --package FILE
- --prompt-out FILE
- --output FILE
- --dry-run
- --verbose

Extra context must resolve inside the Employee directory.

## start — persistent single-Skill Run

~~~bash
mango start EMPLOYEE \
  --skill SKILL_ID \
  --task "Describe the task" \
  --runtime prepare
~~~

This prints RUN_ID.

Unlike plain mango run, mango start persists State and trace information.

# State / Control Plane

## status

List recent Runs:

~~~bash
mango status EMPLOYEE
~~~

Inspect one:

~~~bash
mango status EMPLOYEE RUN_ID
~~~

Filter list:

~~~bash
mango status EMPLOYEE --status blocked --limit 20
~~~

## checkpoint

~~~bash
mango checkpoint EMPLOYEE RUN_ID \
  --data '{"stage":"draft_ready"}' \
  --actor runtime
~~~

--data must be valid JSON.

## request-approval

~~~bash
mango request-approval EMPLOYEE RUN_ID \
  --category external_send \
  --action "Send client follow-up" \
  --reason "Client-facing communication"
~~~

The command prints APPROVAL_ID.

## approvals

~~~bash
mango approvals EMPLOYEE
mango approvals EMPLOYEE --run-id RUN_ID
~~~

## approve / reject

~~~bash
mango approve EMPLOYEE APPROVAL_ID --actor Founder --note "Approved"
mango reject EMPLOYEE APPROVAL_ID --actor Founder --note "Change the wording"
~~~

## retry

~~~bash
mango retry EMPLOYEE RUN_ID
~~~

Use for failed/blocked Runs supported by State retry policy.

## cancel

~~~bash
mango cancel EMPLOYEE RUN_ID --actor Founder --reason "No longer needed"
~~~

## history

~~~bash
mango history EMPLOYEE --limit 50
~~~

# Chain Runtime

## chain — automatic parent→child execution

Preflight only:

~~~bash
mango chain EMPLOYEE \
  --parent-skill category-search-system \
  --child-skill linkedin-search-visibility \
  --task "Select the next T1 and prepare LinkedIn content" \
  --runtime prepare
~~~

Automatic live chain:

~~~bash
mango chain EMPLOYEE \
  --parent-skill category-search-system \
  --child-skill linkedin-search-visibility \
  --task "Select the next T1 and prepare LinkedIn content" \
  --runtime codex
~~~

Different runtime for child:

~~~bash
mango chain EMPLOYEE \
  --parent-skill category-search-system \
  --child-skill linkedin-search-visibility \
  --task "Prepare Q-017" \
  --runtime codex \
  --child-runtime claude
~~~

The live chain creates one root RUN_ID.

## chain-status

~~~bash
mango chain-status EMPLOYEE RUN_ID
~~~

Shows root Run plus ordered chain steps.

## handoff — resume a blocked chain

From a JSON file:

~~~bash
mango handoff EMPLOYEE RUN_ID --file corrected-handoff.json
~~~

Inline JSON is also supported:

~~~bash
mango handoff EMPLOYEE RUN_ID --json '{"handoff_version":"1.0", ...}'
~~~

For beginners, file mode is safer because JSON quoting differs by shell.

# Memory

## memory init

~~~bash
mango memory init EMPLOYEE
~~~

Creates/initializes memory/memory.db.

## memory add

~~~bash
mango memory add EMPLOYEE \
  --type decision \
  --subject acme.erp.phase1 \
  --value "ERP excluded from phase 1" \
  --scope client \
  --scope-id acme \
  --source-type meeting \
  --source-id meeting-2026-09-20 \
  --authority client \
  --confidence 1
~~~

Prints MEM_ID.

New memory is candidate.

Valid memory types currently include working, episodic, semantic, decision, procedural, correction, commitment, preference, rule, and operational_state.

Valid scopes include organization, employee, client, project, skill, and session.

## memory search

~~~bash
mango memory search EMPLOYEE "Acme ERP"
~~~

Optional:

~~~bash
mango memory search EMPLOYEE "Acme" --scope client --scope-id acme --limit 20
~~~

## memory verify

~~~bash
mango memory verify EMPLOYEE MEM_ID --actor Founder
~~~

## memory approve

Promotes:

~~~bash
mango memory approve EMPLOYEE MEM_ID --actor Founder
~~~

## memory reject

~~~bash
mango memory reject EMPLOYEE MEM_ID --actor Founder --detail "Incorrect"
~~~

## memory forget

~~~bash
mango memory forget EMPLOYEE MEM_ID --actor Founder
~~~

## memory supersede

~~~bash
mango memory supersede EMPLOYEE MEM_ID \
  --value "New durable value" \
  --actor Founder
~~~

## memory explain

~~~bash
mango memory explain EMPLOYEE MEM_ID
~~~

## memory audit

~~~bash
mango memory audit EMPLOYEE
~~~

## memory consolidate

~~~bash
mango memory consolidate EMPLOYEE
mango memory consolidate EMPLOYEE --out ./memory-summary.md
~~~

# Tool Protocol

Capabilities:

read, draft, write, send, delete, spend, admin.

## tools list

~~~bash
mango tools list EMPLOYEE
~~~

## tools audit

~~~bash
mango tools audit EMPLOYEE
~~~

## tools authorize

~~~bash
mango tools authorize EMPLOYEE TOOL_ID read
~~~

With a Gate:

~~~bash
mango tools authorize EMPLOYEE TOOL_ID send --gate external_send
~~~

## tools register

~~~bash
mango tools register EMPLOYEE workspace \
  --adapter filesystem \
  --capability read \
  --risk low \
  --root ./workspace
~~~

Registering an external adapter does not implement that external system automatically.

## tools invoke

Prepare only:

~~~bash
mango tools invoke EMPLOYEE workspace read --args '{"path":"notes.md"}'
~~~

Execute implemented local adapter:

~~~bash
mango tools invoke EMPLOYEE workspace read --args '{"path":"notes.md"}' --execute
~~~

If a Gate is required, execution returns approval_required instead of bypassing the Gate.

# Approval & Execution Engine

## action prepare

~~~bash
mango action prepare EMPLOYEE RUN_ID TOOL_ID write \
  --args '{"path":"draft.md","content":"Hello"}'
~~~

Prints ACTION_ID/details.

## action list

~~~bash
mango action list EMPLOYEE
mango action list EMPLOYEE --run-id RUN_ID
~~~

## action approve

~~~bash
mango action approve EMPLOYEE ACTION_ID --actor Founder
~~~

Approve and execute when supported:

~~~bash
mango action approve EMPLOYEE ACTION_ID --actor Founder --execute
~~~

## action reject

~~~bash
mango action reject EMPLOYEE ACTION_ID --actor Founder --note "Not yet"
~~~

## action execute

~~~bash
mango action execute EMPLOYEE ACTION_ID
~~~

Authorization/Gate rules still apply.

# Observability

## trace show

~~~bash
mango trace show EMPLOYEE RUN_ID
~~~

## trace explain

~~~bash
mango trace explain EMPLOYEE RUN_ID
mango trace explain EMPLOYEE RUN_ID --out ./explanation.md
~~~

## trace audit

~~~bash
mango trace audit EMPLOYEE RUN_ID
~~~

# Teams & Handoffs

Teams are for delegation between Employees, separate from Skill chain.

## team create

~~~bash
mango team create EMPLOYEE \
  --name "Revenue Team" \
  --owner founder \
  --purpose "Coordinate revenue workflows"
~~~

Prints TEAM_ID.

## team add-member

~~~bash
mango team add-member EMPLOYEE TEAM_ID employee-a \
  --role researcher \
  --authority member \
  --can-delegate
~~~

## team status

~~~bash
mango team status EMPLOYEE TEAM_ID
~~~

## team delegate

~~~bash
mango team delegate EMPLOYEE TEAM_ID employee-a employee-b \
  --skill research-brief \
  --task "Research account" \
  --deliverable "One-page brief" \
  --acceptance "Sources are cited"
~~~

Prints HANDOFF_ID.

## team accept

~~~bash
mango team accept EMPLOYEE HANDOFF_ID --actor employee-b
~~~

## team return

~~~bash
mango team return EMPLOYEE HANDOFF_ID --actor employee-b --reason "Missing context"
~~~

## team complete

~~~bash
mango team complete EMPLOYEE HANDOFF_ID --actor employee-b --result "Brief completed"
~~~

# Benchmark / Evals

## benchmark run

~~~bash
mango benchmark run EMPLOYEE --runtime prepare
~~~

Live:

~~~bash
mango benchmark run EMPLOYEE --runtime codex --limit 10
~~~

## benchmark report

~~~bash
mango benchmark report EMPLOYEE RESULT_FILE --out ./benchmark-report.md
~~~

## benchmark compare

~~~bash
mango benchmark compare EMPLOYEE result-a.json result-b.json
~~~

# Release / maintenance

## release migrate

~~~bash
mango release migrate EMPLOYEE
~~~

## release audit

~~~bash
mango release audit EMPLOYEE
~~~

## release readiness

~~~bash
mango release readiness EMPLOYEE
~~~

## release backup

~~~bash
mango release backup EMPLOYEE --out ./backups
~~~

Prints a backup directory.

## release verify-backup

~~~bash
mango release verify-backup EMPLOYEE BACKUP_DIRECTORY
~~~

## release restore

Restore refuses overwrite by default.

~~~bash
mango release restore EMPLOYEE BACKUP_DIRECTORY --force
~~~

Use --force only when you deliberately intend to overwrite operational stores with the verified backup.

## release manifest

Maintainer/release command:

~~~bash
mango release manifest EMPLOYEE --out ./release-manifest.json
~~~

The repository’s committed RELEASE-MANIFEST.json is release provenance, not a per-Employee runtime file.

# Exit-code guidance

Common conventions:

- 0 — success/pass/prepared;
- 1 — failure;
- 2 — special blocked/approval-required condition in commands that explicitly use it, including Chain blocked or gated Tool execution.

Always read the command output; do not rely on the number alone when automating.

## Related guides

- FIRST-EMPLOYEE.md
- SKILLS.md
- RUNTIMES.md
- STATE-CONTROL-PLANE.md
- MEMORY.md
- TOOLS.md
- OBSERVABILITY.md
- UPGRADE.md

# Meeting Intelligence — transcripción/minuta a reporte

mango meeting recibe un Employee que tenga asignada la Skill post-meeting-capture v2.
No envía correos ni modifica calendarios/CRM/Memory.

Prueba offline completa:

~~~bash
mango meeting reference-employees/mango-chief-of-staff \
  --input examples/meeting-intelligence/transcript.md \
  --meeting-date 2026-09-23 \
  --extraction examples/meeting-intelligence/extraction.json \
  --formats json,md,docx,pdf \
  --out-dir ./reportes
~~~

Para Word y PDF instala: python -m pip install -e ".[meeting]".

Con modelo live, omite --extraction e indica --runtime codex (u otro
runtime instalado/autenticado). Para sólo preparar el prompt sin modelo,
indica --runtime prepare y opcionalmente --prompt-out archivo-privado.md.

Opciones: --input, --meeting-date, --timezone, --title, --runtime, --model,
--extraction, --formats, --out-dir, --prompt-out. Los formatos predeterminados
son json,md. El reporte requiere revisión humana. Más información:
meeting-intelligence/USER-GUIDE.md.

# Quote Builder — cálculo puro y perfiles

~~~bash
mango quote profile init EMPLOYEE --from-file issuer.json
mango quote profile list EMPLOYEE
mango quote calculate EMPLOYEE --profile mi_empresa --request solicitud.json
~~~

Estos comandos son independientes del modelo. Los datos de los ejemplos
son ficticios; las tasas fiscales las configura el emisor y requieren
revisión profesional.

# Operational Workflows — ambas Skills dentro del control plane

El comando `mango workflow` reutiliza State, Approval Cards, Gates y
Observability. Una operación devuelve RUN_ID; los comandos `mango status`,
`mango approvals` y `mango trace` pueden consultar ese mismo Run.

## Reunión trazable sin llamadas de IA

~~~bash
mango workflow meeting EMPLOYEE \
  --input examples/meeting-intelligence/transcript.md \
  --meeting-date 2026-09-23 \
  --extraction examples/meeting-intelligence/extraction.json \
  --formats json,md,docx,pdf
~~~

Con `--runtime prepare` sin `--extraction`, sólo se prepara un paquete,
no un reporte. Con un runtime live y Gate `sensitive_data` configurado:

~~~bash
mango workflow meeting EMPLOYEE --input transcripcion.md \
  --meeting-date 2026-09-23 --runtime codex
mango approvals EMPLOYEE --run-id RUN_ID
mango approve EMPLOYEE APPROVAL_ID --actor "Responsable de privacidad"
mango workflow meeting-resume EMPLOYEE RUN_ID
~~~

El segundo paso verifica SHA256 de transcripción y runtime/modelo antes
de enviarla. Los reportes quedan dentro del Employee.

## Cotización rastreable y aprobación formal

~~~bash
mango workflow quote-draft EMPLOYEE \
  --profile mi_empresa --request solicitud.json \
  --formats json,md,docx,pdf
mango approvals EMPLOYEE --run-id RUN_ID
mango approve EMPLOYEE APPROVAL_ID --actor "Responsable comercial"
mango workflow quote-issue EMPLOYEE RUN_ID --formats json,md,docx,pdf
mango trace audit EMPLOYEE RUN_ID
~~~

Repite `mango approve` para CADA tarjeta pendiente. Si la solicitud
incluye Gates pricing/scope/deadline/legal, la emisión directa
`mango quote issue` rechaza `--approved-by` sin un Run aprobado.
No se crea CFDI ni se envía correo. El código de salida 2 significa
`waiting_approval`.

Manual completo: [Operational Workflows](OPERATIONAL-WORKFLOWS.md).
