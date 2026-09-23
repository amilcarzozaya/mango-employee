# MANGO Employee Documentation

This directory is the documentation hub for MANGO Employee.

If you are new, do **not** start with the specification files. Start with the onboarding path below.

## Recommended reading order

1. [START-HERE.md](START-HERE.md) — what MANGO Employee is and the shortest path to a first successful run.
2. [PREREQUISITES.md](PREREQUISITES.md) — install and verify Python, Git, terminal access, and optional model runtimes.
3. [INSTALLATION.md](INSTALLATION.md) — clone the repository, create a virtual environment, install MANGO, and verify the CLI.
4. [CONCEPTS.md](CONCEPTS.md) — Employee, Skill, Runtime, Run, Gate, Tool, Memory, Handoff, and Chain in plain language.
5. [FIRST-EMPLOYEE.md](FIRST-EMPLOYEE.md) — create, inspect, validate, test, and run your first Employee.
6. [SKILLS.md](SKILLS.md) — understand the Skill registry, assignment, autonomy, and how to add Category Search skills.
7. [COMMAND-REFERENCE.md](COMMAND-REFERENCE.md) — practical command reference with examples.
8. [RUNTIMES.md](RUNTIMES.md) — install and authenticate Codex, Claude Code, Gemini CLI, Hermes Agent, or OpenClaw.
9. [TROUBLESHOOTING.md](TROUBLESHOOTING.md) — common setup and runtime problems.
10. [UPGRADE.md](UPGRADE.md) — backup, update, migrate, verify, and recover.

## Operational guides

- [STATE-CONTROL-PLANE.md](STATE-CONTROL-PLANE.md) — persistent Runs, checkpoints, retries, approvals.
- [MEMORY.md](MEMORY.md) — governed memory with provenance and human promotion.
- [TOOLS.md](TOOLS.md) — Tool Protocol, capabilities, authorization, and execution.
- [APPROVAL-EXECUTION.md](APPROVAL-EXECUTION.md) — prepared actions and human approval.
- [OBSERVABILITY.md](OBSERVABILITY.md) — traces, provenance, metrics, and audits.
- [TEAMS-HANDOFFS.md](TEAMS-HANDOFFS.md) — controlled multi-Employee delegation.
- [OPERATIONS-RUNBOOK.md](OPERATIONS-RUNBOOK.md) — maintenance, backup, restore, release readiness.
- [SECURITY.md](SECURITY.md) — security controls and limits.
- [ARCHITECTURE.md](ARCHITECTURE.md) — architecture overview.

## Meeting Intelligence

- [Meeting Intelligence — Manual desde cero](meeting-intelligence/USER-GUIDE.md): instala, ejecuta una reunión real o el ejemplo ficticio y exporta Word/PDF.
- [Meeting Intelligence — Especificación técnica](meeting-intelligence/TECHNICAL-SPEC.md): contratos, evidencia, fechas, seguridad y límites.

## Category Search System

- [category-search-system/USER-GUIDE.md](category-search-system/USER-GUIDE.md) — practical beginner workflow.
- [category-search-system/USER-MANUAL.md](category-search-system/USER-MANUAL.md) — complete operating manual.
- [category-search-system/HANDOFF-CONTRACT.md](category-search-system/HANDOFF-CONTRACT.md) — parent-to-child handoff contract.

## Advanced specifications

The root-level MANGO specification files are normative/technical references. They are not required reading for a first installation:

- MANGO-EMPLOYEE-SPEC.md
- MANGO-CHAIN-SPEC.md
- MANGO-STATE-SPEC.md
- MANGO-MEMORY-SPEC.md
- MANGO-TOOL-PROTOCOL.md
- MANGO-EXECUTION-SPEC.md
- MANGO-OBSERVABILITY-SPEC.md
- MANGO-TEAMS-SPEC.md
- MANGO-EVALS-SPEC.md
- MANGO-RELEASE-HARDENING-SPEC.md

## Version context

These docs target MANGO Employee CLI **0.13.0rc1** unless a page explicitly says otherwise.
