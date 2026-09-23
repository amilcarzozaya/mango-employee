# Changelog

## 0.13.0rc3 — Operational Workflows (Stage 4)

- Connects Meeting Intelligence and Quote Builder to existing persistent State, Approval Cards and Observability without duplicating the Skill implementations.
- Adds mango workflow meeting / meeting-resume with source-hash-bound sensitive_data approvals for external runtimes when configured.
- Adds mango workflow quote-draft / quote-issue with SHA256-bound pricing/scope/deadline/legal approvals and same-Run issuance.
- Blocks direct gated Quote issue without formal approvals; human name alone is insufficient when commercial Gates exist.
- Keeps multi-approval Runs waiting until all pending cards are resolved; rejection blocks issuance.
- Adds crash recovery and same-folio idempotence, per-Employee output confinement, and validation of source/draft integrity.
- Adds release backup/restore coverage for validated Meeting reports (not original transcripts or prompts).
- Adds end-to-end offline and simulated-runtime regression tests, from-zero documentation and RC3 release manifest.


## 0.13.0rc2 — MANGO Quote Builder v1

- Adds independent commercial-quotation Skill and explicit reference Employee assignment.
- Adds one-time issuer profiles with tax rules configured by the issuer.
- Adds pure Decimal calculator with discount, additive tax, withholding, inclusive tax and transparent per-line rounding.
- Adds draft snapshots, atomic/idempotent SQLite folios, manual human attestation and JSON/Markdown/Word/PDF output.
- Adds fictional fixtures, JSON schemas, user manual, technical specification and regression tests.
- Explicitly excludes CFDI, tax-law inference, automatic sending and authenticated approver identity.


## 0.13.0rc1 — MANGO Meeting Intelligence v2
- Upgrades the existing post-meeting-capture Skill to v2, preserving its ID and legacy output aliases.
- Adds mango meeting with prepare, live extraction, and validated offline JSON import.
- Adds evidence-bound decisions, actions, commitments, pending items and up to three critical points.
- Adds deterministic due-date parsing and ambiguity flags without invented deadlines.
- Adds optional TXT/Markdown/JSON/DOCX/PDF input and JSON/Markdown/DOCX/PDF output.
- Adds fictional fixtures, user guide, technical spec, schemas and regression tests.


## 0.12.0rc2 — Documentation onboarding refresh
- Added a zero-assumption documentation path from prerequisites through first Run.
- Added detailed prerequisite installation/verification for Python, pip, Git, virtual environments, Node, and optional runtimes.
- Added complete Skill assignment, command, troubleshooting, upgrade/recovery, and Category Search onboarding guides.
- Rewrote runtime setup with current upstream install/authentication references and explicit verification levels.
- Expanded State, Memory, Tools, Approval, Observability, Teams, Security, Architecture, and Reference Employee guides.
- Marked technical specifications as advanced references and historical benchmarks as historical artifacts.
- Added documentation regression checks to keep onboarding/version/tag references current.

## 0.12.0rc2 — Chain Runtime
- Added `mango chain` for one-Run parent→child Skill orchestration.
- Added `mango handoff` to resume blocked chain Runs with validated handoff JSON.
- Added `mango chain-status` and chain lineage in State/Trace.
- Added Trusted Runtime Handoff envelope to runtime packages.
- Added strict handoff/receipt validation and provenance.
- Added Category Search → LinkedIn child auto-chain support.
- Added MANGO Chain Runtime Specification and regression tests.

## 0.12.0rc1 — Hardening / Release Candidate
- Feature freeze before v1.0.
- Idempotent schema metadata/migrations.
- Fail-closed newer-schema handling.
- SQLite integrity and orphan-record audit.
- Verified backup and checksum-checked restore.
- Explicit force required for destructive restore.
- Release readiness gate.
- SHA-256 release provenance manifest.
- Threat model and operations runbook.
- Restored v0.11 Team CLI surface as a compatibility requirement.

## 0.11.0 — MANGO Teams & Handoffs
- Teams and explicit member roles.
- Controlled delegation and Handoff Contracts.
- Scoped shared-memory enforcement.
- Linked child Runs and provenance.
- Circular/self-delegation prevention.

## 0.10.0 — MANGO Evals & Benchmark
- Golden Set benchmark runner.
- Weighted deterministic operational scoring.
- Offline and live-runtime modes.
- JSON results, Markdown reports and descriptive comparisons.
- Security audit embedded in benchmark results.
- MANGO Evals & Benchmark Specification v0.1.


## 0.9.0 — MANGO Observability & Audit
- Per-Run trace IDs and execution spans.
- Provenance for Employee, Skill, Sources, Memory and Tools.
- Human approval decisions included in trace reports.
- Operational metrics and trace integrity audit.
- Human-readable `mango trace explain` without chain-of-thought disclosure.
- MANGO Observability & Audit Specification v0.1.


## 0.8.0 — Approval & Execution Engine
- Prepared Action objects with immutable action hashes.
- Automatic Approval Cards for gated tool actions.
- Exact approval-to-action binding.
- Re-authorization immediately before execution.
- Rejection blocks runs; approval resumes them.
- Tool results recorded into Run event history.
- MANGO Approval & Execution Specification v0.1.


## 0.7.0 — MANGO Tool Protocol
- Portable tool registry and capability vocabulary.
- Permission intersection and Gate-aware authorization.
- Safe filesystem adapter with path containment.
- Prepared tool invocation envelopes with IDs/hashes.
- Reference declarations for Email, Calendar, CRM, Finance and Workspace.
- MANGO Tool Protocol v0.1.


## 0.6.0 — MANGO State / Control Plane
- Persistent Run lifecycle and SQLite state store.
- Checkpoints, Approval Cards and append-only run events.
- Human approve/reject workflow.
- Linked retries, cancellation, history and inspection.
- `mango start` persistent execution command.
- MANGO State Specification v0.1.


## 0.5.0 — MANGO Memory
- SQLite operational memory and audit trail.
- Governed memory lifecycle and scopes.
- Bounded runtime Memory Packs.
- Memory CLI and regression tests.
- Data-cannot-become-Authority safety rule.


## 0.4.0 — GitHub-ready multi-runtime security release
- Added Gemini CLI, Hermes Agent and OpenClaw adapters.
- Hardened Codex and Claude defaults.
- Added `mango security` and `mango doctor`.
- Added context size bounds and secret redaction.
- Added explicit untrusted-context boundary.
- Added GitHub Actions CI.
- Added security, runtime and architecture documentation.
- Added MIT license, contribution guide, release checklist and creator attribution.

## 0.3.0
- Added `mango run` runtime packaging and Codex/Claude adapters.

## 0.2.0
- Added `mango init`.

## 0.1.0
- Added validate, test and eval export commands.
