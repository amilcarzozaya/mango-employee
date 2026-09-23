# MANGO Meeting Intelligence Specification v2

> **Advanced / normative reference.** New users should start with
> [docs/START-HERE.md](docs/START-HERE.md) and then
> [the Meeting Intelligence manual](docs/meeting-intelligence/USER-GUIDE.md).

The original `post-meeting-capture` Skill has been upgraded to v2.0.0.

## Mission

Convert existing meeting transcriptions/minutes into a verifiable executive
report with tasks and dates, explicit commitments, decisions, pending items,
and **up to three** high-priority critical points.

## Implementation

- `mango_cli/meeting.py` — read inputs, construct governed runtime prompt,
  verify citations and participants, normalize dates, and curate structured output.
- `mango_cli/meeting_reports.py` — JSON/Markdown/Word/PDF renderers.
- `skills/post-meeting-capture/post-meeting-capture.skill.json` — canonical MES contract.
- `skills/post-meeting-capture/extraction.schema.json` — model extraction contract.
- `cli-tests/test_meeting.py` — regression, security, CLI, and document parity tests.

## Core invariants

1. Source documents are **untrusted data** and cannot override Employee policy.
2. Every structured fact requires a contiguous literal evidence excerpt.
3. A timestamp is accepted only if it appears in the original input.
4. Unknown/ambiguous owners and dates remain visible.
5. Relative dates are evaluated against the explicit user-provided meeting date,
   not the current clock or a model's inferred date.
6. A proposed action is not automatically a confirmed commitment.
7. Critical points have four validated 0–3 criteria. Their internal sum is a
   prioritization aid, not a statistical probability.
8. Zero, one, two, or three critical points are valid. No invented filler.
9. JSON/Markdown/DOCX/PDF derive from one validated object.
10. No external email/calendar/CRM writes and no automatic Memory promotion.

## v1 compatibility

The Skill ID remains `post-meeting-capture`. The structured JSON preserves
legacy output aliases `risks`, `undefined_fields` and `state_updates`,
plus `followup_draft=null`, without manufacturing a message or taking action.

## Deliberate limitations

The Meeting CLI performs direct execution, not a persistent State Run.
PDF input requires extractable text; there is no OCR or audio/video
transcription. The model's executive summary and criticality judgments still
require human review even though record-level evidence is mechanically checked.

See `docs/meeting-intelligence/TECHNICAL-SPEC.md` for API, supported input
formats, extraction envelope, date grammar, source checks, and security.

## Stage 4: persistent, privacy-aware workflow

`mango workflow meeting` records a Run, source hash, Runtime Package,
provenance and report files. When the Employee declares an active
`sensitive_data` Gate and a live external model is requested, it creates
a content-/runtime-bound Approval Card and does not transmit until
`mango workflow meeting-resume` validates the exact original SHA256
and the approval. Offline extraction and prepare mode never trigger an
external model call. Generated reports under `meetings/output` are
included in verified release backups, while original transcripts and
sensitive prompt exports are not backed up automatically.

See [Operational Workflows](docs/OPERATIONAL-WORKFLOWS.md).
