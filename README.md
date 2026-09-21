# MANGO Employee

**Portable specification, Skill system, safety layer and runtime for supervised AI Employees.**

Created by **Amílcar Zozaya**, creator of **Método MANGO**.

MANGO Employee is an open implementation of a simple idea: an AI Employee should not be a giant prompt. It should be a portable, auditable and versionable operational contract describing **what it is trying to achieve, who it serves, what context it may use, which Skills it can perform, what tools it may access, how much autonomy it has, and where a human must remain in control**.

> Diseña sistemas, no sólo prompts.

## Método MANGO

Método MANGO is a framework created by **Amílcar Zozaya** for designing clearer instructions and AI systems:

- **M — Meta clara:** What result should be achieved?
- **A — Audiencia específica:** Who will consume, receive or be affected by the result?
- **N — Nivel de detalle:** What depth, frequency, precision and autonomy are appropriate?
- **G — Guía contextual:** Which sources, rules, examples, constraints and business context govern the work?
- **O — Opciones y formato:** What exact deliverable, structure and output format is required?

MANGO Employee extends that framework from prompting into an operating architecture:

**MANGO → Context → Sources → Memory → Skills → Tools → Autonomy → Gates → Routines → Evaluation → Learning → Governance**

## Why this exists

Most AI agents mix instructions, context, memory, permissions and execution into one opaque layer. MANGO Employee separates them. The canonical Employee Specification can be version-controlled and the same runtime package can be prepared for different agent CLIs without rewriting the employee.

Current adapters:

| Runtime | Adapter | Safety posture |
|---|---|---|
| OpenAI Codex CLI | `--runtime codex` | ephemeral + read-only sandbox |
| Claude Code | `--runtime claude` | print mode + Bash/Edit/Write denied by adapter |
| Google Gemini CLI | `--runtime gemini` | stdin/headless execution |
| Hermes Agent | `--runtime hermes` | one-shot query from stdin |
| OpenClaw | `--runtime openclaw` | isolated `agent exec` |

Runtime availability depends on the corresponding CLI being installed and authenticated on the host. MANGO itself does not bundle those third-party runtimes.

## Quick start

```bash
python -m pip install -e .

mango --version
mango doctor
mango validate reference-employees/mango-chief-of-staff
mango test reference-employees/mango-chief-of-staff
mango security reference-employees/mango-chief-of-staff
```

Prepare a task without calling a model:

```bash
mango run reference-employees/mango-chief-of-staff \
  --skill pre-meeting-brief \
  --task "Prepárame para la reunión con Acme" \
  --runtime prepare \
  --package run-package.json \
  --prompt-out run-prompt.md
```

Execute the same Employee + Skill through another runtime:

```bash
mango run reference-employees/mango-chief-of-staff --skill pre-meeting-brief --task "Prepárame para Acme" --runtime codex
mango run reference-employees/mango-chief-of-staff --skill pre-meeting-brief --task "Prepárame para Acme" --runtime claude
mango run reference-employees/mango-chief-of-staff --skill pre-meeting-brief --task "Prepárame para Acme" --runtime gemini
mango run reference-employees/mango-chief-of-staff --skill pre-meeting-brief --task "Prepárame para Acme" --runtime hermes
mango run reference-employees/mango-chief-of-staff --skill pre-meeting-brief --task "Prepárame para Acme" --runtime openclaw
```

## Build your own Employee

```bash
mango init ./employees/my-employee
mango validate ./employees/my-employee
mango test ./employees/my-employee
mango security ./employees/my-employee
```

Presets include `chief-of-staff`, `sales-ops`, `client-ops`, and `founder-ops`.

## Security model

MANGO uses defense in depth rather than trusting model behavior alone. Context is explicitly labeled **untrusted data**. Employee autonomy is bounded per Skill. High-impact actions use human Approval Gates. Context paths are confined to the Employee directory. Common secret patterns are redacted before context packaging. Runtime adapters default toward restricted/headless execution where the upstream CLI supports it.

The included offline security suite tests path traversal, Skill assignment, autonomy limits, prompt-injection boundaries, secret redaction, Approval Gate policy, learning-loop policy and adapter safety flags.

**Important:** this project is an application-level control layer, not a security sandbox or formal proof. The host runtime, OS permissions, credentials, plugins/MCP servers and model behavior remain part of the security boundary. Review each upstream runtime before granting write, network, send, spend or production permissions.

## Repository map

```text
mango_cli/                  CLI, runtime, initializer, validator, security audit
schema/                     MANGO Employee JSON schema
skills/                     machine-readable official Skill library + registry
.agents/skills/             agent-oriented Skill files
.claude/skills/             Claude-oriented Skill files
reference-employees/        canonical MANGO Chief of Staff implementation
cli-tests/                  CLI/runtime tests
security-tests/             adversarial and boundary tests
docs/                       architecture, runtime compatibility and security docs
.github/workflows/          CI validation
```

## Commands

- `mango init` — scaffold a MANGO Employee.
- `mango info` — inspect an Employee.
- `mango validate` — validate the operational contract.
- `mango test` — validate the Golden Set structure.
- `mango evals` — export behavioral eval prompts.
- `mango security` — run offline security controls.
- `mango doctor` — detect installed runtime CLIs.
- `mango run` — prepare or execute Employee + Skill + Task.

## MANGO Teams & Handoffs

v0.11 adds controlled multi-Employee collaboration with roles, delegation, scoped memory, Handoff Contracts and linked Runs. See `MANGO-TEAMS-SPEC.md`.

## MANGO v0.12 Release Candidate

v0.12 freezes feature growth and hardens migrations, integrity checks, backup/restore, release provenance and clean installation before v1.0.

**Migrations ∩ Integrity ∩ Security ∩ Tests ∩ Clean Install ∩ Recovery = RC Ready**

See `MANGO-RELEASE-HARDENING-SPEC.md`, `THREAT-MODEL.md`, `docs/RELEASE-CANDIDATE.md` and `docs/OPERATIONS-RUNBOOK.md`.

## MANGO Teams & Handoffs

v0.11 adds controlled multi-Employee collaboration through explicit Team roles and Handoff Contracts.

## MANGO Evals & Benchmark

v0.10 converts the Golden Set into a reproducible operational benchmark. It measures contract behavior rather than general model intelligence.

Commands: `mango benchmark run`, `report`, and `compare`.

See `MANGO-EVALS-SPEC.md` and `docs/EVALS-BENCHMARK.md`.

## MANGO Observability & Audit

v0.9 makes MANGO Employees inspectable.

**What did this Employee do, what information did it use, what did a human approve, and what happened?**

Every persistent Run now produces trace spans, provenance edges, human-decision records and operational metrics. `mango trace explain` generates a human-readable explanation without exposing hidden chain-of-thought.

See `MANGO-OBSERVABILITY-SPEC.md` and `docs/OBSERVABILITY.md`.

## MANGO Approval & Execution Engine

v0.8 closes the controlled action loop:

**THINK → PREPARE → AUTHORIZE → ASK → APPROVE → RE-AUTHORIZE → ACT → RECORD**

Every prepared action receives an ID and SHA-256 binding over the exact Run, Tool, Capability and arguments. A human approval authorizes that exact action—not a vague intention. Permissions are checked again immediately before execution.

See `MANGO-EXECUTION-SPEC.md` and `docs/APPROVAL-EXECUTION.md`.

## MANGO Tool Protocol

MANGO Tool Protocol standardizes how Employees act on systems while keeping permissions independent from the model.

**Registered Tool ∩ Capability ∩ Employee Permission ∩ Gate = Allowed Action**

Capabilities: `read`, `draft`, `write`, `send`, `delete`, `spend`, `admin`.

The reference build includes a contained local filesystem adapter. Email, Calendar, CRM and Finance are declared as external adapters but are not falsely simulated.

See `MANGO-TOOL-PROTOCOL.md` and `docs/TOOLS.md`.

## MANGO State / Control Plane

MANGO State makes execution persistent. Every bounded execution can have a Run ID, lifecycle, checkpoints, Approval Cards, retries and an event history.

**Memory answers “what does the Employee know?” State answers “what is the Employee doing now?”**

Run lifecycle:

`queued → running → waiting_approval → running → completed`

with controlled `blocked`, `failed`, `cancelled` and linked retry paths.

Commands include `mango start`, `status`, `checkpoint`, `request-approval`, `approvals`, `approve`, `reject`, `retry`, `cancel`, and `history`.

See `MANGO-STATE-SPEC.md` and `docs/STATE-CONTROL-PLANE.md`.

## MANGO Memory

MANGO Memory is the portable operational-memory layer. It stores governed memory with provenance, authority, confidence, scope and lifecycle rather than dumping chat history into prompts.

> **Data cannot become Authority.**

`mango run` now retrieves a bounded **Memory Pack** containing only relevant verified/promoted non-sensitive memories.

Commands: `mango memory add`, `search`, `verify`, `approve`, `reject`, `supersede`, `forget`, `explain`, `audit`, and `consolidate`.

See `MANGO-MEMORY-SPEC.md` and `docs/MEMORY.md`.

## Reference Employee

`reference-employees/mango-chief-of-staff/` is the canonical working example. It includes six core Skills, Company File, Operating Policy, memory, safe fictional fixtures and a 30-case Golden Set.

## Learning loop

MANGO does not silently turn every correction into permanent policy:

**Correction → classify → propose change → human approval → update rule/Skill → regression test → version**

This is designed to make learning cumulative without silently expanding authority.

## Status

**v0.12 RC1 — MANGO Release Candidate hardening.** The package has offline compatibility adapters for Codex, Claude Code, Gemini CLI, Hermes Agent and OpenClaw. Live end-to-end model execution requires those CLIs and their credentials; `mango doctor` reports what is available on the host.

## Credits

**Método MANGO and MANGO Employee were created by Amílcar Zozaya.**

Concept, methodology, MANGO framework, AI Employee architecture and product direction: **Amílcar Zozaya**.

This repository includes implementation code and documentation developed to operationalize that methodology as a portable specification, Skill library, safety layer, test harness and multi-runtime CLI.

## License

MIT. See `LICENSE`.

## Citation

If you use MANGO Employee in research, teaching, products or derivative frameworks, please credit:

**Zozaya, Amílcar. “MANGO Employee Specification and Método MANGO.” 2026.**
