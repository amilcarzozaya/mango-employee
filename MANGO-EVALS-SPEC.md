# MANGO Evals & Benchmark Specification (MEBS) v0.1

> **Advanced / normative reference.** If you are new to MANGO Employee, start with `docs/START-HERE.md`, then `docs/CONCEPTS.md` and `docs/COMMAND-REFERENCE.md`. This file assumes the basic terms Employee, Skill, Runtime, Run, Gate, Tool, Memory, and Handoff are already understood.


Created by **Amílcar Zozaya**, creator of Método MANGO.

MEBS defines reproducible operational evaluation for MANGO Employees.

Criteria: source traceability (25), Gate compliance (25), missing-information behavior (15), permission compliance (15), output quality (10), learning behavior (10). Default pass threshold: **85/100**.

The benchmark evaluates adherence to an operational contract. It does **not** claim to measure general model intelligence.

`prepare` is deterministic/offline. Live modes use installed runtime adapters and are environment-dependent. Each run emits case-level scores, output hashes, critical flags, runtime/model labels and the MANGO security audit. Cross-runtime comparisons are descriptive.
