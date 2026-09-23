# MANGO Approval & Execution Specification (MAES) v0.1

> **Advanced / normative reference.** If you are new to MANGO Employee, start with `docs/START-HERE.md`, then `docs/CONCEPTS.md` and `docs/COMMAND-REFERENCE.md`. This file assumes the basic terms Employee, Skill, Runtime, Run, Gate, Tool, Memory, and Handoff are already understood.


Created by **Amílcar Zozaya**, creator of Método MANGO.

MAES closes the controlled-action loop:

**THINK → PREPARE → AUTHORIZE → ASK → APPROVE → RE-AUTHORIZE → ACT → RECORD**

## Action object
A prepared action binds Run ID, Tool, Capability and exact arguments into an immutable SHA-256 action hash.

## Approval binding
An Approval Card is bound to the exact `action_id` and `action_hash`. Approval of one payload cannot authorize a modified payload.

## Execution rules
1. Employee permission is checked when the action is prepared.
2. High-impact capabilities create an Approval Card and pause the Run.
3. Silence is not approval.
4. Approval must match the exact action hash.
5. Permission is checked again immediately before execution.
6. An action executes at most once.
7. Result is recorded as a Run Event.
8. Rejection blocks the Run.
9. Runtime/model cannot bypass this engine.

## Security property
**Approval authorizes an exact action, not a general intention.**
