# MANGO State Specification (MSS) v0.1

> **Advanced / normative reference.** If you are new to MANGO Employee, start with `docs/START-HERE.md`, then `docs/CONCEPTS.md` and `docs/COMMAND-REFERENCE.md`. This file assumes the basic terms Employee, Skill, Runtime, Run, Gate, Tool, Memory, and Handoff are already understood.


Created by **Amílcar Zozaya**, creator of Método MANGO.

MANGO State is the persistent control plane for MANGO Employees. Memory answers **what the employee knows**. State answers **what the employee is doing now**.

## Run lifecycle
`queued → running → waiting_approval → running → completed`

Alternative controlled paths include `blocked`, `failed`, `cancelled`, and retry into a new linked run.

## Core objects
- **Run** — one bounded execution of Employee + Skill + Task.
- **Checkpoint** — resumable state recorded during a run.
- **Approval Card** — explicit human decision required by a Gate.
- **Run Event** — append-only operational audit event.
- **Attempt** — a retry linked to its parent run.
- **Chain Step** — an ordered parent/child Skill execution stored inside one root Run.

## Principles
1. No invisible work: every persistent execution has a Run ID.
2. No silent approval: Gates pause state.
3. No destructive retry: retry creates a linked attempt.
4. No lost history: state transitions and approvals are event-logged.
5. Runtime independence: State survives a change of model/runtime.
6. Memory and State remain separate: durable knowledge is Memory; execution progress is State.

## Canonical storage
SQLite in `state/state.db` for v0.1.


## Chain Runs

A chain Run uses one root Run ID with synthetic Skill identity:

`chain:<parent_skill>-><child_skill>`

Ordered `chain_steps` record:
- role (parent/child);
- Skill ID;
- runtime;
- package ID;
- span ID;
- status;
- output path;
- completion time.

A blocked handoff remains resumable within the same Run using `mango handoff`.
