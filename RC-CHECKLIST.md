# MANGO Employee v0.13 RC3 — Stage 4 Integration Release Checklist

## Scope

- Meeting Intelligence v2 and Quote Builder v1 run independently on the
  existing MANGO Employee control plane.
- `mango workflow meeting` creates persistent State and provenance;
  `meeting-resume` permits exact source-hash-authorized external execution
  when the Employee declares a sensitive_data Gate.
- `mango workflow quote-draft` creates an immutable snapshot and one Approval
  Card for every configured commercial Gate (pricing/scope/deadline/legal).
- `mango workflow quote-issue` checks every card, source Run and immutable
  draft hash before allocating an atomic, idempotent commercial folio.
- A direct `mango quote issue` cannot bypass a configured commercial Gate.
- Release backup now includes verified Meeting reports, quote operational
  stores, State and Observability — not original transcripts or full prompts.

## Automated acceptance tests

- [x] New CLI and shared State/Gate/Trace integration implemented.
- [x] Meeting/Quote standalone APIs retained; direct quote issuance hardened.
- [x] Formal approvals are bound to immutable source/draft content.
- [x] Multi-card state transition changed to wait for all pending approvals.
- [x] Per-Employee file output confinement and documented retention boundaries.
- [x] Regression tests for rejection, hash tampering, concurrent folios and
      rendering failure/retry.
- [x] Beginner manual, normative specification and command reference updated.
- [x] Release manifest rebuilt from canonical source content.
- [ ] Verify CI Python 3.10–3.13 across full suite before merging.
- [ ] Verify main CI following merge before tagging release.

## Release provenance

- Manifest format: mango-release-manifest-v1
- Package: 0.13.0rc3
- Canonical files: 37
- Release hash: 68b8c23c7ca531d3072d659aa5b5d9024f4da2db53d8e4cfba0b3ff97b7e1b56

## Explicit limitations

Operator names in `mango approve` are CLI assertions, not corporate
identity verification. These workflows do not send communications,
auto-promote Memory, issue CFDI or infer tax treatment from business
descriptions. A real enterprise deployment requires authenticated actor
roles, storage encryption, retention rules and approved provider access.
