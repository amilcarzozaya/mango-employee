# MANGO Employee Threat Model — RC1

> **Advanced / normative reference.** If you are new to MANGO Employee, start with `docs/START-HERE.md`, then `docs/CONCEPTS.md` and `docs/SECURITY.md`. This file assumes the basic trust boundaries are already understood.


## Protected assets
Employee policy, Company/Client context, Memory, Tool configuration, Approval decisions, Run state, audit evidence, Team handoffs and recovery media.

## Trust boundaries
Human ↔ Employee; Sources ↔ Context; Runtime/model ↔ Control Plane; Employee ↔ Tools; Employee ↔ Employee; persistent state ↔ backups.

## Primary threats
Prompt injection is constrained by untrusted-context boundaries. Permission escalation is constrained by Employee permissions, Tool Protocol and Gates. Approval replay/tampering is constrained by exact Action hashes. Memory poisoning is constrained by authority levels and approval before promotion. Hidden work is constrained by persistent Run state. Cross-Employee escalation is constrained by Team roles, scoped memory and Handoff Contracts. Circular delegation is rejected. Database corruption is checked with SQLite integrity checks. Restore media is verified by SHA-256 before use. Unknown newer schemas fail closed. Secret-bearing `.env` files are excluded from operational backups.

## Residual risks
Compromised host OS, stolen credentials, malicious administrators, provider-side model changes, non-atomic external systems and incomplete business-policy configuration remain outside the guarantees of the reference implementation.
