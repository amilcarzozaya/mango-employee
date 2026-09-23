# MANGO Employee v0.13 RC4 — Release Candidate Guide

This page is for maintainers/operators preparing the RC4 repository state.

New users should start at docs/START-HERE.md.

## RC4 scope

RC4 adds the Spanish Guided menu and local installers. A new user
can create an Employee, capture issuer/tax information, create quotations,
review formal Approval Cards, and prepare meeting workflows without
editing JSON. Existing deterministic calculations and formal safety
controls remain authoritative.

[Guided manual](GUIDED-SETUP.md).

## Previous RC scope

RC4 implements Stage 4: tracked `mango workflow meeting` and
`mango workflow quote-draft/quote-issue` using the existing State,
Approval Cards and Observability services. A configured sensitive_data
Gate prevents external meeting transmission before consent; commercial
Gates each require approval bound to the exact quote draft hash.
Direct quote issuance cannot bypass active commercial Gates.
The release backup now includes validated Meeting reports along with
quote operational stores, while original transcripts and prompts are
excluded by default.

See [the full Stage 4 guide](OPERATIONAL-WORKFLOWS.md).

## Prior releases

RC4 adds independent MANGO Quote Builder v1.0.0: issuer profiles,
exact Decimal commercial quote engine, explicitly configured tax codes,
immutable drafts, SQLite-issued folios with manual approval statement,
Word/PDF export and release backup of operational quotation stores.

RC1 previously added Meeting Intelligence v2; its functionality remains.
Quote Builder deliberately excludes CFDI, external send, live tax-law inference
and verified corporate approver identity.

## Existing platform scope

MANGO Meeting Intelligence v2 adds verified meeting reports, deterministic date parsing and optional Word/PDF. It does not transcribe audio, perform OCR or send external messages.


The existing platform combines:

- release hardening;
- governed State/Memory/Observability;
- Tool/Approval layers;
- Teams/Handoffs;
- MANGO Chain Runtime;
- Category Search parent→LinkedIn child Skill support.

## Employee release checks

~~~bash
mango release migrate EMPLOYEE
mango release audit EMPLOYEE
mango release readiness EMPLOYEE
mango release backup EMPLOYEE --out ./backups
~~~

Verify the printed backup directory:

~~~bash
mango release verify-backup EMPLOYEE BACKUP_DIRECTORY
~~~

Restore test only when intentionally validating recovery:

~~~bash
mango release restore EMPLOYEE BACKUP_DIRECTORY --force
~~~

## Repository validation

~~~bash
python -m pip install -e .
pytest -q
mango validate reference-employees/mango-chief-of-staff
mango test reference-employees/mango-chief-of-staff
mango security reference-employees/mango-chief-of-staff
~~~

CI should pass the supported Python matrix.

## Release manifest

The repository manifest uses format:

~~~text
mango-release-manifest-v1
~~~

The generator fails closed if hardening RC_VERSION and pyproject.toml version diverge.

RELEASE-MANIFEST.json records:

- release label;
- package version;
- schema version;
- generated timestamp;
- canonical file count;
- file paths/hashes/sizes;
- release hash.

Because README.md and MANGO-*-SPEC.md files are part of the canonical manifest set, changing them requires manifest regeneration before calling the release snapshot clean.

## RC4 provenance

The exact release hash can change when tracked release documentation/runtime/spec files are updated.

Therefore, treat RELEASE-MANIFEST.json in the current branch/main as the source of truth rather than copying an older hash from this prose.

## Promotion criteria

Promotion beyond RC4 should require:

- automated suite green;
- clean install;
- release readiness;
- backup/restore round-trip;
- security pass;
- no unresolved critical Gate/permission issues;
- real Employee pilot evidence;
- final licensing/IP/public-API decisions appropriate to the release.

## Upgrade guide

See UPGRADE.md.
