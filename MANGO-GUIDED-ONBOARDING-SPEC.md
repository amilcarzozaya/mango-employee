# MANGO Guided Onboarding Specification v1

MANGO Employee 0.13 RC4 · Amílcar Zozaya

> Advanced reference. New users should start with
> [docs/START-HERE.md](docs/START-HERE.md) and then
> [the guided user manual](docs/GUIDED-SETUP.md).

## Goal

Provide a Spanish interactive terminal onboarding for Meeting Intelligence
and Quote Builder without requiring users to hand-edit JSON. Reuse canonical
validators, Decimal arithmetic, State/Approval Cards and Trace.

## Surfaces

- mango guided — main menu.
- mango guided check — read-only local prerequisites and optional runtimes.
- mango guided setup DIR — create/validate a new Employee, assign both
  Skills and enable commercial plus sensitive_data Gates.
- mango guided profile EMPLOYEE — ask issuer/tax questions, validate
  and save directly through quote.init_profile_data without temporary
  user-supplied JSON files.
- mango guided quote EMPLOYEE — prompt for client, lines, explicit
  tax codes, discounts, dates, terms, exact preview and confirmation;
  save a private request and invoke quote_draft_workflow.
- mango guided meeting EMPLOYEE — validate existing text and date;
  prepare a private prompt or optionally select an installed model
  with explicit consent plus source-hash-bound sensitive approval.
- mango guided approvals EMPLOYEE — review source/borrador SHA256,
  ask separately for each Gate, default to NO; optionally issue
  or resume only after all approvals.

## Authority

The guided layer never performs financial arithmetic with an LLM,
never allocates a folio directly, never bypasses configured Gates,
never sends a communication or creates a CFDI. Every underlying
workflow revalidates the same original immutable input data at
the mutation boundary. The CLI approver name is self-attestation,
not enterprise identity verification.

## Local persistence

Employee spec from initializer.create_project, validated and explicitly
assigned Skills. Directly configured profile in quotes/profiles.
Generated request in quotes/requests using exclusive private
file creation. Prompt in meetings/prompts with restrictive permissions;
not included in release backups. Business artifacts, SQLite
State and Observability continue to use existing services.

## Installation

install.sh and install.ps1 create an isolated local Python .venv,
install the optional Word/PDF dependencies, run guided diagnostics
and offer the guided menu. Neither requires administrator privileges
or authenticates any external AI service.

## Acceptance

- Works in Spanish on Python 3.10–3.13.
- No manual JSON required for setup, quote or issuer profile.
- Setup creates both assigned Skills and includes sensitive_data Gate.
- Every tax code is selected explicitly, never inferred.
- No quote draft without preview/confirmation and no folio before
  all mandatory Approval Cards are resolved.
- Empty approval answer means NO; each Gate reviewed separately.
- No external transcript use without affirmative consent and
  existing sensitive_data authorization.
- Prepare mode creates a usable private prompt, never a fictitious report.
- Cancellation, invalid input and duplicate profile paths fail closed.
- Docs and release manifest match the canonical code and CI passes.

Tests: cli-tests/test_guided.py plus existing state, workflow, quote,
meeting, security and release regression suites.
