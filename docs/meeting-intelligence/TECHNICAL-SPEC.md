# MANGO Meeting Intelligence v2 — Technical Specification

## Reuse and compatibility

Upgrades the existing `post-meeting-capture` Skill to `2.0.0`.
Existing Skills and reference Employees retain the same Skill ID. The new
validated report keeps legacy aliases `risks`, `undefined_fields`,
`state_updates` and `followup_draft=null` without claiming side effects.

## CLI

`mango meeting EMPLOYEE --input SOURCE [--meeting-date YYYY-MM-DD]`
`[--timezone IANA] [--title TITLE] [--runtime prepare|codex|claude|gemini|hermes|openclaw]`
`[--model MODEL] [--extraction extraction.json] [--formats json,md,docx,pdf]`
`[--out-dir DIRECTORY] [--prompt-out FILE]`.

A user may invoke `mango run ... --skill post-meeting-capture` generically,
but **only `mango meeting` runs the dedicated deterministic evidence/date
validator and document renderers**.

## Trusted/untrusted boundary

1. Employee configuration and canonical Skill enter via
   `runtime.build_package`, which enforces Skill assignment/autonomy/Gates.
2. User-supplied transcript is appended to the extraction prompt as explicitly
   untrusted data.
3. A live runtime returns one JSON object inside the
   `BEGIN_MANGO_MEETING_JSON` / `END_MANGO_MEETING_JSON` envelope.
4. All record-level `source_excerpt` values must match a contiguous span
   of the supplied transcript after whitespace/case normalization.
5. `source_timestamp`, if supplied, must also appear in the transcript.
6. The motor validates types and metadata before exporting.

The schema is `skills/post-meeting-capture/extraction.schema.json`.
Runtime checks additionally enforce source matching, timezone validity,
date computation, participant-name presence and report invariants.

## Extraction arrays

`decisions`, `tasks`, `commitments`, `pending`, `critical_points`.
They may be empty. Each object includes `source_excerpt`.

Tasks and commitments include `owner|null`, `due_text|null` and
`status=committed|proposed|pending`. The motor ignores any model-authored
`due_date` and computes a trusted one from `due_text`.
Conservative proposal language in a purported commitment is downgraded to
proposed and marked for human review.

## Date grammar

Supported:
- explicit `YYYY-MM-DD`, `dd/mm/YYYY`,
  `d de mes de YYYY` in Spanish;
- `mañana`, `pasado mañana`;
- `en N días`, `dentro de N días`;
- `el próximo/siguiente/este <día de la semana>`.

Bare weekday expressions remain ambiguous; anything requiring a missing
`meeting_date` returns `needs_meeting_date`.
The zone is validated using Python ZoneInfo and recorded as metadata.
Date computations use `meeting_date` only: no current-clock guessing.

## Critical points

The extraction proposes criterion scores 0–3 for urgency, impact, dependency,
risk. The motor validates each criterion and deterministically recomputes
`priority_score=sum(criteria)`. Up to three records are retained in order.
The criteria reflect the model's evidence-bound assessments; they are not
independent ground-truth measurements.

## Output

`report_id` is unique per generation attempt. Output files have the stem
`meeting-<random>.json|md|docx|pdf`. Existing files are never overwritten.
Export dependency checks occur before writing to avoid partial export.

Machine-readable output includes:
`meeting`, `executive_summary`, `decisions`, `tasks`,
`commitments`, `pending`, `critical_points`, `review_required`,
`memory_candidates`, `source_integrity` plus legacy aliases.

Only `candidate` Memory proposals are created in JSON. No automatic
write to Memory DB, State, CRM or calendar; no external send.

## Format adapters

Inputs: TXT, MD, JSON; optionally DOCX via python-docx or searchable PDF
via pypdf. No OCR/transcription.

Outputs: JSON and Markdown without extra dependencies; optionally DOCX via
python-docx and PDF via ReportLab. Installation:
`pip install -e ".[meeting]"`.

Word/PDF/Markdown are rendered from one validated report object. Word/PDF
document layout and Unicode handling are covered by optional-dependency
regression tests.

## Retention and privacy

Source files stay at the user-supplied location. A `--prompt-out` file
contains the whole transcript; limit access. Report JSON repeats excerpts
and personal names. Live runtimes may transmit input to external providers:
users are responsible for obtaining applicable authorization and following
their organization's retention policies.

## Tests

`cli-tests/test_meeting.py` covers extraction, evidence rejection,
timestamps, status, deterministic dates, missing metadata, critical points,
JSON/Markdown/Word/PDF, prepare mode and the CLI.

## Versioning

This release introduces Meeting Intelligence as the first v0.13 feature.
Future additions may include persistent State integration, OCR/audio, output
templates, date locale packs, follow-up drafting, and controlled external
synchronization; none are implied by this v2 contract.
