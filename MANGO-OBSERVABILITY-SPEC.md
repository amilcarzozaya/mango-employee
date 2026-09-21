# MANGO Observability & Audit Specification (MOAS) v0.1

Created by **Amílcar Zozaya**, creator of Método MANGO.

MOAS answers a business-critical question:

> **What exactly did this AI Employee do, and why?**

## Trace model
Every persistent Run has a deterministic Trace ID. A trace contains:
- spans: runtime and tool execution timing/status;
- provenance edges: Employee, Skill, Memory, Source and Tool usage;
- human decisions: Approval Cards and actors;
- run events: checkpoints, transitions and execution events;
- metrics: context count, memory retrieval count, tool calls and runtime exit status.

## Provenance graph
`Run → Employee → Skill → Sources + Memory → Tools → Human Decisions → Result`

## Privacy
Observability stores hashes for span inputs/outputs by default rather than raw model payloads. Existing source/memory IDs are referenced, not duplicated.

## Audit laws
1. A completed run should identify its Employee and Skill.
2. Human approvals must identify the actor.
3. Terminal runs must not contain orphan running spans.
4. Tool calls are linked to Action IDs and Runs.
5. Observability must not grant permissions or alter execution.
6. Trace data is evidence, not authority.

## Explainability
`mango trace explain` produces a human-readable operational explanation without exposing hidden chain-of-thought.
