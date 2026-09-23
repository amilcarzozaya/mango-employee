# MANGO Employee CLI — 0.13.0rc1

This file is the short CLI entry point.

If you have never installed MANGO, read these first:

1. docs/START-HERE.md
2. docs/PREREQUISITES.md
3. docs/INSTALLATION.md
4. docs/CONCEPTS.md

The full command-by-command reference is:

**docs/COMMAND-REFERENCE.md**

## Install locally

From the repository root inside an activated Python virtual environment:

~~~bash
python -m pip install -e .
mango --version
~~~

## Understand the placeholders

Documentation examples use:

- EMPLOYEE — Employee directory or employee.json;
- SKILL_ID — Skill assigned to that Employee;
- RUN_ID — ID printed by mango start or mango chain;
- MEM_ID — ID printed by mango memory add;
- APPROVAL_ID — ID printed by request-approval;
- ACTION_ID — action ID;
- TEAM_ID / HANDOFF_ID — IDs printed by Team commands.

Do not type the literal word RUN_ID. Replace it with the ID the previous command printed.

## Discover built-in help

~~~bash
mango --help
mango run --help
mango chain --help
mango memory --help
mango tools --help
mango release --help
~~~

## Beginner verification

~~~bash
mango doctor
mango info reference-employees/mango-chief-of-staff
mango validate reference-employees/mango-chief-of-staff
mango test reference-employees/mango-chief-of-staff
mango security reference-employees/mango-chief-of-staff
~~~

## Prepare without a model

~~~bash
mango run reference-employees/mango-chief-of-staff \
  --skill pre-meeting-brief \
  --task "Prepare me for a fictional Acme meeting" \
  --runtime prepare \
  --package ./run-package.json \
  --prompt-out ./run-prompt.md
~~~

prepare is built into MANGO. It creates no live model call.

## Create an Employee

~~~bash
mango init ./employees/my-employee
mango info ./employees/my-employee
mango validate ./employees/my-employee
mango test ./employees/my-employee
mango security ./employees/my-employee
~~~

## Persistent single-Skill execution

~~~bash
mango start ./employees/my-employee \
  --skill SKILL_ID \
  --task "Describe the task" \
  --runtime prepare
~~~

The command prints RUN_ID.

~~~bash
mango status ./employees/my-employee RUN_ID
mango trace show ./employees/my-employee RUN_ID
~~~

## Parent→child Chain

Both Skills must already be assigned to the Employee.

~~~bash
mango chain ./employees/my-employee \
  --parent-skill category-search-system \
  --child-skill linkedin-search-visibility \
  --task "Select the next T1 and prepare the LinkedIn asset" \
  --runtime prepare
~~~

Use an executable runtime such as codex to run both steps automatically.

If a live chain blocks on handoff validation:

~~~bash
mango chain-status ./employees/my-employee RUN_ID
mango handoff ./employees/my-employee RUN_ID --file corrected-handoff.json
~~~

## Exit codes

General convention:

- 0 — success/pass/prepared;
- 1 — failure;
- 2 — command-specific blocked/approval-required condition where documented.

For automation, read the command output as well as the exit code.

## Full reference

See [docs/COMMAND-REFERENCE.md](docs/COMMAND-REFERENCE.md).

## Meeting Intelligence — transcripción a reporte

Una reunión produce un resumen, tareas/fechas, compromisos, decisiones,
pendientes y hasta tres asuntos críticos con citas verificadas.

Prueba sin modelo (con fixtures ficticios):

~~~bash
mango meeting reference-employees/mango-chief-of-staff \
  --input examples/meeting-intelligence/transcript.md \
  --meeting-date 2026-09-23 \
  --extraction examples/meeting-intelligence/extraction.json \
  --formats json,md --out-dir ./reportes
~~~

Word y PDF son opcionales: python -m pip install -e ".[meeting]".
Manual: docs/meeting-intelligence/USER-GUIDE.md.
