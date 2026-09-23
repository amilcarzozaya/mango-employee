# Core Concepts — Plain-Language Guide

This page defines the terms used by the CLI and documentation.

## Employee

An **Employee** is the complete operating contract for an AI worker.

The main file is employee.json.

It defines:

- identity;
- role and mission;
- human owner;
- MANGO framing;
- responsibilities;
- assigned Skills;
- tool permissions;
- autonomy ceiling;
- Gates;
- governance;
- evaluation and learning policy.

A runtime may know about a Skill globally, but the Employee cannot use it unless the Skill is assigned to that Employee.

## Skill

A **Skill** is one repeatable job.

Examples:

- pre-meeting-brief;
- weekly-ceo-review;
- category-search-system;
- linkedin-search-visibility.

A Skill defines:

- objective;
- trigger;
- procedure;
- rules;
- output;
- Definition of Done;
- QA;
- autonomy level;
- Gates;
- missing-information policy;
- tests.

A Skill is not a model and not a Tool.

## Skill registry

skills/registry.json is the canonical library of registered Skills.

Important:

**Registered does not mean assigned.**

The runtime intentionally checks both:

1. the Skill exists in the registry or Employee;
2. the Skill appears in employee.json.

This prevents an Employee from silently acquiring every Skill in the repository.

## Runtime

A **Runtime** is the execution surface that receives the prepared MANGO package.

Supported runtime names:

- prepare;
- codex;
- claude;
- gemini;
- hermes;
- openclaw.

prepare is built in and performs no model call.

The others require third-party CLIs and authentication.

## Task

A **Task** is the specific instruction for one invocation.

Example:

“Prepare me for tomorrow’s Acme meeting.”

The Skill remains reusable; the Task changes per run.

## Runtime Package

The **Runtime Package** is the structured object MANGO builds from:

- Employee;
- active Skill;
- Task;
- bounded context;
- Memory Pack;
- Gates;
- Tool policy;
- autonomy;
- governance;
- optional trusted Handoff.

It receives a package_id.

## Context

**Context** is local material the Runtime Package is allowed to read for the task.

MANGO labels loaded context as untrusted data so a document cannot silently override policy.

Extra context paths must stay inside the Employee directory.

## Source

A **Source** is a declared information source with authority, permissions, freshness, and governed subjects.

Examples:

- contract directory;
- CRM;
- project system;
- finance;
- local documents.

A source declaration does not magically connect the external system. The runtime or a Tool adapter must actually implement access.

## Memory

**Memory** is durable operational knowledge with provenance and lifecycle.

Memory is separate from chat history.

Statuses include:

- candidate;
- verified;
- promoted;
- superseded;
- rejected;
- forgotten.

Normal Runtime Packages inject only bounded relevant verified/promoted memory.

## State and Run

**State** answers: “what is the Employee doing now?”

A **Run** is one persistent execution record with:

- run_id;
- status;
- Skill;
- Task;
- runtime;
- checkpoints;
- result/error;
- approvals;
- events;
- trace.

Use mango start when you need persistence for a single Skill.

mango run is simpler and does not create the same persistent State record.

mango chain creates a persistent root Run for a parent→child Skill chain.

## Checkpoint

A **Checkpoint** is an append-only snapshot of progress attached to a Run.

Example:

~~~json
{"stage":"draft_ready","document":"proposal-v2"}
~~~

## Gate

A **Gate** is a policy boundary that requires human approval before a restricted category of action.

Examples:

- external_send;
- publish;
- spend;
- pricing;
- scope;
- deadline;
- legal;
- delete;
- permissions;
- sensitive_data.

A Gate is not the same thing as a Runtime prompt asking politely. It is an explicit policy object.

## Approval Card

An **Approval Card** records a specific decision a human must approve or reject.

Approval is explicit. Silence is not approval.

## Tool

A **Tool** is an action surface.

Examples could include:

- local workspace filesystem;
- email adapter;
- calendar adapter;
- CRM adapter.

Tool capabilities are explicit:

- read;
- draft;
- write;
- send;
- delete;
- spend;
- admin.

A Skill tells the Employee what job to do. A Tool gives it a controlled way to act.

## Action

An **Action** is a prepared Tool invocation bound to exact arguments. High-impact actions can require a Gate and human approval before execution.

## Handoff

A **Handoff** is structured data passed from one controlled worker/Skill to another.

MANGO has two related uses:

- Teams/Handoffs: delegation between Employees.
- Chain Runtime: parent Skill → child Skill inside one root Run.

## Chain

A **Chain** is a governed two-step Skill execution.

Example:

category-search-system → linkedin-search-visibility

mango chain:

1. executes the parent;
2. extracts a typed handoff;
3. validates lineage/contract;
4. executes the child;
5. validates a receipt;
6. stores both steps under one Run.

## Trace

A **Trace** is operational provenance.

It answers questions such as:

- what Skill ran?
- what package was used?
- what Tool was invoked?
- what did a human approve?
- what handoff was emitted?
- which child consumed it?

Trace explain is not hidden chain-of-thought. It is an operational audit explanation.

## Golden Set

A **Golden Set** is a collection of test cases describing expected behavior.

Typical classes:

- normal;
- missing information;
- conflicting sources;
- gate required;
- prompt injection.

## Autonomy level

MANGO uses numeric autonomy levels 0–4.

The exact business meaning should be defined by the organization, but the runtime enforces one critical relationship:

**Skill autonomy cannot exceed Employee max autonomy.**

A higher number is not “better”. Use the lowest level that can safely complete the work.

## Definition of Done

A Skill’s Definition of Done says what must be true before the Skill is considered complete.

It is part of the operational contract, not optional prose.

## Next page

Continue with [FIRST-EMPLOYEE.md](FIRST-EMPLOYEE.md).
