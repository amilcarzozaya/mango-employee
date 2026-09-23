# MANGO Employee

**Portable specification, Skill system, safety layer, State/Memory plane, and multi-runtime CLI for supervised AI Employees.**

Created by **Amílcar Zozaya**, creator of **Método MANGO**.

> Diseña sistemas, no sólo prompts.

## New here? Start with this path

You do not need to understand agents, Skills, runtimes, or MANGO specifications before installing the project.

Read in this order:

1. [docs/START-HERE.md](docs/START-HERE.md)
2. [docs/PREREQUISITES.md](docs/PREREQUISITES.md)
3. [docs/INSTALLATION.md](docs/INSTALLATION.md)
4. [docs/CONCEPTS.md](docs/CONCEPTS.md)
5. [docs/FIRST-EMPLOYEE.md](docs/FIRST-EMPLOYEE.md)
6. [docs/SKILLS.md](docs/SKILLS.md)
7. [docs/COMMAND-REFERENCE.md](docs/COMMAND-REFERENCE.md)
8. [docs/TROUBLESHOOTING.md](docs/TROUBLESHOOTING.md)

The complete documentation index is [docs/README.md](docs/README.md).

## What MANGO Employee is

MANGO Employee treats an AI worker as an operational contract rather than one giant prompt.

The contract can define:

- identity, role, mission, and human owner;
- MANGO framing;
- context and sources;
- assigned Skills;
- tool permissions;
- autonomy limits;
- human Approval Gates;
- routines;
- governed Memory;
- persistent State;
- evaluation and learning;
- trace/audit;
- parent→child Skill handoffs.

The same bounded Runtime Package can be prepared for different model CLIs without rewriting the Employee.

## Método MANGO

Método MANGO is a framework created by Amílcar Zozaya for clearer instructions and AI systems:

- **M — Meta clara:** what result should be achieved?
- **A — Audiencia específica:** who consumes or is affected by the result?
- **N — Nivel de detalle:** how much depth, precision, frequency, and autonomy are appropriate?
- **G — Guía contextual:** which sources, rules, examples, constraints, and business context govern the work?
- **O — Opciones y formato:** what exact deliverable, structure, and output are required?

MANGO Employee extends that idea into:

**MANGO → Context → Sources → Memory → Skills → Tools → Autonomy → Gates → State → Evaluation → Learning → Governance**

## Minimum prerequisites

Required for MANGO itself:

- Python 3.10 or newer;
- pip;
- a terminal;
- Git if you clone/update with Git.

Third-party model CLIs are optional.

You can validate Employees and prepare Runtime Packages without any live model.

See [docs/PREREQUISITES.md](docs/PREREQUISITES.md).

## Install from zero

~~~bash
git clone https://github.com/amilcarzozaya/mango-employee.git
cd mango-employee

python3 -m venv .venv
source .venv/bin/activate

python -m pip install --upgrade pip
python -m pip install -e .

mango --version
~~~

Windows PowerShell:

~~~powershell
git clone https://github.com/amilcarzozaya/mango-employee.git
cd mango-employee

py -m venv .venv
.\.venv\Scripts\Activate.ps1

python -m pip install --upgrade pip
python -m pip install -e .

mango --version
~~~

Full installation details: [docs/INSTALLATION.md](docs/INSTALLATION.md).

## First successful run without a model

~~~bash
mango doctor
mango info reference-employees/mango-chief-of-staff
mango validate reference-employees/mango-chief-of-staff
mango test reference-employees/mango-chief-of-staff
mango security reference-employees/mango-chief-of-staff
~~~

Then prepare one task:

~~~bash
mango run reference-employees/mango-chief-of-staff \
  --skill pre-meeting-brief \
  --task "Prepare me for a fictional Acme meeting" \
  --runtime prepare \
  --package ./run-package.json \
  --prompt-out ./run-prompt.md
~~~

**prepare** is a built-in runtime mode. It builds the package/prompt and makes no model call.

## MANGO Meeting Intelligence

La Skill post-meeting-capture v2 transforma transcripciones y minutas en reportes
verificables con tareas, fechas, compromisos, decisiones, pendientes y hasta
tres puntos críticos. La extracción utiliza un modelo opcional, mientras que
las citas, fechas y exportaciones se validan en Python.

Ejemplo completamente offline con datos ficticios:

~~~bash
python -m pip install -e ".[meeting]"
mango meeting reference-employees/mango-chief-of-staff \
  --input examples/meeting-intelligence/transcript.md \
  --meeting-date 2026-09-23 \
  --extraction examples/meeting-intelligence/extraction.json \
  --formats json,md,docx,pdf --out-dir ./reportes
~~~

Con un modelo autenticado, omite --extraction y utiliza --runtime codex
u otro runtime compatible. El comando no envía mensajes ni crea tareas
externas, y no promueve automáticamente la memoria.

Manual: [MANGO Meeting Intelligence](docs/meeting-intelligence/USER-GUIDE.md).
## Operational Workflows — two independent Skills, one control plane

**MANGO Employee v0.13 RC3** connects Meeting Intelligence and Quote Builder
to persistent Runs, formal Approval Cards, Observability, and release backup.
Neither Skill sends messages, issues CFDI or promotes Memory automatically.

A tracked meeting report using fictional data (no model call):

~~~bash
mango workflow meeting reference-employees/mango-chief-of-staff \
  --input examples/meeting-intelligence/transcript.md \
  --meeting-date 2026-09-23 \
  --extraction examples/meeting-intelligence/extraction.json \
  --formats json,md,docx,pdf
~~~

A tracked quotation with content-bound commercial approval:

~~~bash
mango quote profile init reference-employees/mango-chief-of-staff \
  --from-file examples/quote-builder/issuer-profile.json

mango workflow quote-draft reference-employees/mango-chief-of-staff \
  --profile demo --request examples/quote-builder/request.json \
  --formats json,md,docx,pdf
~~~

Copy RUN_ID and the APR_ID values from the response. Review the documents,
approve **each** pending category with
`mango approve EMPLOYEE APR_ID --actor "Reviewer"`, then issue:

~~~bash
mango workflow quote-issue EMPLOYEE RUN_ID --formats json,md,docx,pdf
mango trace audit EMPLOYEE RUN_ID
~~~

A workflow awaiting human approval returns status `waiting_approval`
and exit code 2. Both outputs default to private directories inside
the Employee. A direct `mango quote issue` cannot bypass commercial
Gates when they are configured.

Install optional Word/PDF support:

~~~bash
python -m pip install -e ".[meeting,quote]"
~~~

See the [from-zero Operational Workflows guide](docs/OPERATIONAL-WORKFLOWS.md),
[Meeting Intelligence guide](docs/meeting-intelligence/USER-GUIDE.md),
and [Quote Builder guide](docs/quote-builder/USER-GUIDE.md).

## Core terms in one minute

- **Employee** — who the AI worker is, what it may do, and who owns final authority.
- **Skill** — one repeatable job/procedure.
- **Runtime** — execution surface such as prepare, Codex, Claude Code, Gemini, Hermes, or OpenClaw.
- **Run** — persistent execution record.
- **Gate** — human approval boundary for high-impact actions.
- **Tool** — controlled action surface with explicit capabilities.
- **Memory** — governed durable knowledge with provenance/status.
- **Handoff** — typed transfer from one controlled actor/Skill to another.
- **Chain** — parent Skill → child Skill inside one persistent root Run.
- **Trace** — operational provenance, not hidden model reasoning.

See [docs/CONCEPTS.md](docs/CONCEPTS.md).

## Create your own Employee

~~~bash
mango init ./employees/my-employee

mango info ./employees/my-employee
mango validate ./employees/my-employee
mango test ./employees/my-employee
mango security ./employees/my-employee
~~~

mango init is interactive. Current presets are:

- chief-of-staff;
- sales-ops;
- client-ops;
- founder-ops.

Guide: [docs/FIRST-EMPLOYEE.md](docs/FIRST-EMPLOYEE.md).

## Skills: registry vs assignment

A Skill in skills/registry.json is **not automatically available** to every Employee.

The Employee must also explicitly assign it in employee.json.

Check assignments:

~~~bash
mango info ./employees/my-employee
~~~

Guide: [docs/SKILLS.md](docs/SKILLS.md).

## Optional live runtimes

Supported runtime names:

| Runtime name | External CLI | Default MANGO posture |
|---|---|---|
| prepare | none | no model call |
| codex | Codex CLI | ephemeral + read-only sandbox |
| claude | Claude Code | print mode + Bash/Edit/Write denied |
| gemini | Gemini CLI | stdin/headless invocation |
| hermes | Hermes Agent | query-file/stdin |
| openclaw | OpenClaw | isolated agent exec |

Install/authenticate the runtime separately, then:

~~~bash
mango doctor
~~~

mango doctor confirms binary discovery only. It does not prove authentication, quota, provider access, or billing.

Current setup instructions: [docs/RUNTIMES.md](docs/RUNTIMES.md).

## Single-Skill execution

Prepare only:

~~~bash
mango run ./employees/my-employee \
  --skill SKILL_ID \
  --task "Describe the task" \
  --runtime prepare
~~~

Live runtime:

~~~bash
mango run ./employees/my-employee \
  --skill SKILL_ID \
  --task "Describe the task" \
  --runtime codex
~~~

Use mango start instead of mango run when you need persistent State, Run ID, trace, approvals, checkpoints, retry, or history.

## Persistent Runs

~~~bash
mango start ./employees/my-employee \
  --skill SKILL_ID \
  --task "Describe the task" \
  --runtime prepare
~~~

The CLI prints RUN_ID.

Inspect:

~~~bash
mango status ./employees/my-employee RUN_ID
mango trace show ./employees/my-employee RUN_ID
~~~

See [docs/STATE-CONTROL-PLANE.md](docs/STATE-CONTROL-PLANE.md).

## MANGO Chain Runtime

MANGO CLI 0.12 RC2 supports governed parent→child Skill execution inside one persistent root Run.

Example:

~~~bash
mango chain ./employees/my-employee \
  --parent-skill category-search-system \
  --child-skill linkedin-search-visibility \
  --task "Select the next T1 and prepare the LinkedIn asset" \
  --runtime codex
~~~

Both Skills must be:

1. registered;
2. explicitly assigned to the Employee;
3. autonomy-compatible;
4. handoff-contract compatible.

If the parent produces an invalid handoff, the root Run becomes blocked instead of losing lineage.

Resume the same Run:

~~~bash
mango handoff ./employees/my-employee RUN_ID --file corrected-handoff.json
~~~

Inspect:

~~~bash
mango chain-status ./employees/my-employee RUN_ID
mango trace audit ./employees/my-employee RUN_ID
~~~

See [MANGO-CHAIN-SPEC.md](MANGO-CHAIN-SPEC.md) and [docs/category-search-system/USER-GUIDE.md](docs/category-search-system/USER-GUIDE.md).

## Security model

MANGO uses defense in depth:

- explicit Employee/Skill assignment;
- per-Skill autonomy bounded by Employee max;
- Employee-relative context path confinement;
- context size limits;
- secret-pattern redaction;
- context marked as untrusted data;
- human Gates for high-impact categories;
- corrections do not auto-promote to policy;
- restrictive runtime adapter modes where available;
- trace and provenance for persistent Runs.

Important: MANGO is an application-level control layer, not an OS sandbox, credential vault, malware scanner, or formal verification system.

Review [docs/SECURITY.md](docs/SECURITY.md), [SECURITY.md](SECURITY.md), and [THREAT-MODEL.md](THREAT-MODEL.md).

## Command families

Use [docs/COMMAND-REFERENCE.md](docs/COMMAND-REFERENCE.md) for syntax and examples.

Top-level areas include:

- init / info / validate / test / security / evals / doctor;
- run / start / status / history / checkpoint;
- chain / handoff / chain-status;
- approvals;
- memory;
- tools;
- action;
- trace;
- team;
- benchmark;
- release.

## Repository map

~~~text
mango_cli/                  CLI/runtime/state/memory/security implementation
schema/                     Employee JSON schema
skills/                     canonical machine-readable Skill library
.agents/skills/             portable agent Skill files
.claude/skills/             Claude-oriented Skill files
reference-employees/        canonical working Employee
docs/                       onboarding + operational documentation
cli-tests/                  CLI/runtime regression tests
security-tests/             security/hardening tests
.github/workflows/          CI
~~~

## Reference Employee

The canonical example is:

~~~text
reference-employees/mango-chief-of-staff/
~~~

It is intentionally bounded: it can read/analyze/draft but does not silently send, set price, accept scope, promise deadlines, modify legal terms, or move money.

See [REFERENCE-EMPLOYEE.md](REFERENCE-EMPLOYEE.md).

## State, Memory, Tools, and Observability

- State: [docs/STATE-CONTROL-PLANE.md](docs/STATE-CONTROL-PLANE.md)
- Memory: [docs/MEMORY.md](docs/MEMORY.md)
- Tools: [docs/TOOLS.md](docs/TOOLS.md)
- Approval/Execution: [docs/APPROVAL-EXECUTION.md](docs/APPROVAL-EXECUTION.md)
- Observability: [docs/OBSERVABILITY.md](docs/OBSERVABILITY.md)
- Teams/Handoffs: [docs/TEAMS-HANDOFFS.md](docs/TEAMS-HANDOFFS.md)
- Upgrade/Recovery: [docs/UPGRADE.md](docs/UPGRADE.md)
- Troubleshooting: [docs/TROUBLESHOOTING.md](docs/TROUBLESHOOTING.md)

## Release status

Current documentation target:

**MANGO Employee CLI 0.13.0rc3**

Release provenance is stored in RELEASE-MANIFEST.json and RC-CHECKLIST.md.

## Credits

**Método MANGO and MANGO Employee were created by Amílcar Zozaya.**

Concept, methodology, MANGO framework, AI Employee architecture, and product direction: **Amílcar Zozaya**.

## License

MIT. See LICENSE.

## Citation

If you use MANGO Employee in research, teaching, products, or derivative frameworks, please credit:

**Zozaya, Amílcar. “MANGO Employee Specification and Método MANGO.” 2026.**
