# Architecture — Beginner to Advanced

If this is your first MANGO installation, read docs/START-HERE.md and docs/CONCEPTS.md first.

## The shortest architecture view

~~~text
Employee + Skill + Task
        ↓
Context / Sources / Memory
        ↓
Runtime Package
        ↓
Safety Contract + Gates + Tool Policy
        ↓
Runtime Adapter
        ↓
Model / prepare
        ↓
Result
~~~

For persistent execution:

~~~text
Run State
  ├── checkpoints
  ├── approvals
  ├── events
  └── trace/provenance
~~~

For parent→child Skill execution:

~~~text
Root Run
  ├── Parent Skill
  │     ↓ typed handoff
  └── Child Skill
        ↓ receipt
~~~

## Employee contract

employee.json is the explicit operating contract.

It covers:

- identity/mission/owner;
- MANGO framing;
- context;
- sources;
- Memory policy;
- assigned Skills;
- Tools/permissions;
- autonomy;
- Gates;
- routines;
- evaluation;
- learning;
- governance.

## Skill layer

A Skill is one bounded procedure.

The canonical registry is skills/registry.json.

Runtime security requires explicit Employee assignment in addition to registry presence.

## Context resolver

mango_cli/runtime.py resolves Employee-relative context.

Controls include:

- path confinement;
- file/type limits;
- source filtering;
- context size caps;
- secret-pattern redaction;
- UNTRUSTED DATA labeling.

## Runtime Package

The Runtime Package is the portability boundary.

Adapters should remain thin. They translate the same package into the invocation expected by the selected runtime instead of redefining Employee policy.

## Runtime adapters

Supported runtime names:

- prepare;
- codex;
- claude;
- gemini;
- hermes;
- openclaw.

See docs/RUNTIMES.md for installation and verification.

## State vs Memory

State:
- execution lifecycle;
- what is happening now;
- Run ID;
- approvals/checkpoints/results.

Memory:
- durable operational knowledge;
- provenance/authority/confidence;
- lifecycle status.

They use separate SQLite stores deliberately.

## Tool and Action layers

Tool Protocol decides whether a capability exists and is authorized.

Approval & Execution binds an exact Run + Tool + capability + arguments to a prepared action.

## Observability

Persistent Runs produce spans/provenance/metrics.

Trace explain is operational provenance, not hidden reasoning.

## Chain Runtime

mango chain validates:

- parent/child assignment;
- dependency version;
- handoff contract;
- handoff JSON;
- child receipt lineage.

Both steps remain inside one root Run.

## Normative specifications

For implementation details, use the root MANGO-*-SPEC.md files.

For user setup, use docs/README.md.
