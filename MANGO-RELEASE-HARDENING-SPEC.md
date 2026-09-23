# MANGO Release Hardening Specification (MRHS) v0.1

> **Advanced / normative reference.** If you are new to MANGO Employee, start with `docs/START-HERE.md`, then `docs/CONCEPTS.md` and `docs/COMMAND-REFERENCE.md`. This file assumes the basic terms Employee, Skill, Runtime, Run, Gate, Tool, Memory, and Handoff are already understood.


Created by **Amílcar Zozaya**, creator of Método MANGO.

Target: **MANGO Employee v0.13 RC1**

The purpose of this release is to freeze feature growth and prove the control plane can be installed, migrated, audited, recovered and regression-tested before v1.0.

## Release laws

1. No schema change ships without an idempotent migration path.
2. A newer unknown schema fails closed.
3. Backups use SQLite online backup plus SHA-256 manifests.
4. Restore verifies all checksums before changing operational state.
5. Restore refuses destructive overwrite unless explicitly forced.
6. Invalid Run/Handoff states and orphaned records fail integrity audit.
7. Security, integrity and migrations must all pass release readiness.
8. Hardening cannot grant new business authority.
9. Release manifests hash source/spec artifacts for provenance.
10. Recovery must be testable offline.

**Migrations ∩ Integrity ∩ Security ∩ Tests ∩ Clean Install ∩ Recovery = RC Ready**
