---
name: mango-employee
description: Design, create, audit, improve, or operate MANGO Employee Specification (MES) employees and their reusable skills. Use when the user asks to build an AI employee, convert a repeated workflow into a skill, create or update a MANGO employee JSON/Markdown spec, define autonomy/gates/memory/tools, audit an employee, or turn corrections into versioned operational rules. Do not use for generic one-off prompts that do not need an operational employee or reusable workflow.
---

# MANGO Employee Skill

Use the MANGO Employee Specification as the contract for building AI employees.

## Required references

Before creating or materially changing an employee:
1. Read `references/MANGO-EMPLOYEE-SPEC.md`.
2. Read `references/mango-employee.schema.json` when producing or validating JSON.
3. If an existing employee spec exists in the repository, treat it as the current state and modify it rather than inventing a replacement.

## Operating doctrine

- Design systems, not only prompts.
- Source before inference.
- Least privilege.
- Draft before send.
- Autonomy is per skill.
- Human authority must be explicit.
- Never interpret silence as approval.
- Never turn an unverified model inference into company state.
- Missing critical information is a valid stop condition.
- Every recurring correction should improve a rule, skill, test, or source mapping.

## Workflow

### 1. Frame with MANGO

Establish:
- **M — Meta:** business result.
- **A — Audiencia:** who consumes the work.
- **N — Nivel:** depth, cadence and autonomy.
- **G — Guía:** sources, policies, examples and restrictions.
- **O — Opciones y formato:** exact outputs and formats.

If a critical field is missing, mark it `TBD` and continue only where safe. Do not fabricate company policy.

### 2. Define the employee

Specify:
- role and mission;
- owner;
- responsibilities;
- non-responsibilities;
- sources of truth;
- allowed tools;
- memory policy;
- skills;
- gates;
- metrics.

### 3. Build skills

For every repeated workflow define:
`trigger -> inputs -> sources -> procedure -> rules -> output -> QA -> gates -> autonomy -> memory update -> tests`

A skill is incomplete without a Definition of Done.

### 4. Assign autonomy

Use:
- 0 Observer
- 1 Analyst
- 2 Preparer
- 3 Controlled Executor
- 4 Bounded Operator

Default to the lowest level that achieves the goal. Level 3+ requires explicit permissions, logging, bounded scope and rollback.

### 5. Apply gates

Stop for human approval when policy requires it, especially for:
- external sends;
- spending;
- pricing;
- scope;
- external deadlines;
- legal terms;
- publishing;
- destructive actions;
- permission changes;
- sensitive data.

When blocked, return an Approval Card:
- action;
- reason;
- target;
- exact change;
- sources;
- cost;
- risk;
- reversibility;
- rollback;
- alternatives;
- decision required.

### 6. Validate

Check:
- required schema fields;
- source traceability;
- permission/tool mismatch;
- undefined authority;
- conflicting sources;
- missing gates;
- autonomy too high;
- irreversible actions without rollback;
- memory without retention rule;
- outputs without Definition of Done;
- no regression tests.

### 7. Learn

When the user corrects behavior:
1. classify the correction;
2. identify whether it belongs in Company File, Client File, source map, skill, gate or test;
3. propose the smallest durable change;
4. require human approval for policy/authority changes;
5. add a regression case;
6. increment the appropriate version.

## Output modes

### CREATE
Produce:
1. `employee.json`
2. concise human-readable summary
3. unresolved `TBD`s
4. activation checklist

### SKILL
Produce a reusable skill with all MES skill fields and tests.

### AUDIT
Produce:
- PASS;
- RISKS;
- REQUIRED CHANGES;
- TESTS BEFORE ACTIVATION.

Do not silently modify files unless the user asked you to edit them.

### OPERATE
When an employee spec is active:
1. identify applicable skill;
2. load only necessary context;
3. verify sources and permissions;
4. detect gates;
5. execute within autonomy;
6. return result + sources + state changes + pending human decisions.

## Final checks

Before completion:
- facts have provenance;
- no undeclared permissions are assumed;
- gates are respected;
- missing information is visible;
- no destructive action was inferred;
- JSON validates conceptually against the MES schema;
- changes are versionable and reviewable.
