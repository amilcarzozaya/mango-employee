# MANGO Operational Workflows Specification v1

> Advanced reference. Start with [the full Spanish user guide](docs/OPERATIONAL-WORKFLOWS.md)
> and [MANGO concepts](docs/CONCEPTS.md).

## Scope and version

MANGO Employee CLI **0.13.0rc3** integrates these existing Skills without
duplicating their business logic:

- post-meeting-capture 2.0.0 (Meeting Intelligence)
- commercial-quotation 1.0.0 (Quote Builder)

\`mango_cli/operational_workflows.py\` is the orchestration layer.
It reuses \`runtime.build_package\`, \`state\`, \`observability\`,
\`meeting.process_meeting\` and \`quote.make_quote/issue_quote\`.

## Meeting lifecycle

~~~text
Employee preflight → Run running → source digest/provenance →
   ├─ local extraction / prepare: process → report → completed
   └─ live model with sensitive_data Gate:
        Approval Card(source SHA, runtime/model) → waiting_approval
           ├─ rejected: blocked, no model call
           └─ approved + source unchanged: meeting-resume SAME Run
                → process → report → completed
~~~

The source is read and checked before creating the Run. All outputs
default to \`EMPLOYEE/meetings/output\`. An explicit external output path
is rejected in tracked workflows. Original transcripts are not copied
into State; SHA256 source digests appear in provenance.

Prepare mode does not manufacture an extraction; a precomputed JSON
can be imported and validated without calling a model. The existing
Meeting validator still rejects ungrounded citations, owners and dates.

## Quote lifecycle

~~~text
Employee/Skill preflight → Run running → exact Decimal quote →
  immutable local draft (no folio) → checksum/provenance →
  Approval Cards for all configured pricing/scope/deadline/legal Gates →
  waiting_approval →
  all approved → running → revalidate exact cards/checksum →
  issue_quote transaction BEGIN IMMEDIATE → issued documents →
  root Run completed
~~~

The content-binding payload is:
\`kind=mango_quote_issue_v1\`, \`run_id\`, \`draft_id\`,
\`draft_sha256\`, \`profile_id\`, \`currency\`, \`total\`,
\`client_name\`, \`quote_date\`, \`valid_until\`.

Before allocating a folio, the quote service independently revalidates
all required Approval Cards, exact payload fields, Employee ID, Skill,
Run status and the current immutable draft SHA256. Passing an
\`approved_by\` string alone is rejected for any Employee with
active commercial Gates.

The actor who approved pricing becomes the issued document's
\`approved_by\` field. \`resolve_approval\` keeps the Run in
\`waiting_approval\` until every pending card is resolved.

## Execution and error behavior

- 0: operation completed or prepared without further approvals.
- 2: waiting on Approval Cards; Run ID and card IDs are returned.
- 1: validation/security/runtime error.

A rejected Approval Card blocks the Run. Partial approval batches
that encounter an exception are blocked rather than left apparently
authorized. If rendering fails after SQLite commits a folio, retry
\`workflow quote-issue RUN_ID\`; the existing quote service reuses
the committed folio idempotently.

For completed Runs, \`workflow quote-issue\` returns the recorded result
rather than generating another document or consuming another number.

## Persistence and backup

- \`state/state.db\`: Run lifecycle, checkpoints, Approval Cards, events.
- \`observability/trace.db\`: spans, source hashes, package provenance,
  resulting artifacts and audit metrics.
- \`quotes/drafts\`, \`quotes/issued\`, \`quotes/folios.sqlite\`: commercial
  records and idempotent folio ledger.
- \`meetings/output\`: generated reports.

Release backup covers State/Trace, operational quote stores and
validated meeting artifacts. By default it does NOT package
original transcripts or full prompts.

## Security boundaries

1. Employee/Skill assignment and autonomy checked at start and mutation.
2. Sensitive external-model Meeting invocation is gated when
   \`sensitive_data\` exists and remains human-approved for exact source hash.
3. Quote issuance cannot bypass existing enabled pricing/scope/deadline/legal
   Gates through direct \`mango quote issue\`.
4. All Approval Cards are content-bound to the immutable quote draft,
   and revalidated immediately before SQLite issuance.
5. No external send, CFDI, client messaging, CRM mutation or automatic
   Memory promotion.
6. \`--approved-by\` and the normal CLI actor are recorded statements.
   They do not authenticate a physical or corporate identity.

The user's organization must still provide secure local filesystem
permissions, encryption/backups, model-provider authorization and real
operator identity/role management.

## Tests

\`cli-tests/test_operational_workflows.py\` covers:
- offline tracked meeting and prepare mode;
- sensitive-data approval with no premature model invocation;
- source hash mutation and approval rejection;
- independent gated quote workflow with four required approval categories;
- no early transition on partial approval;
- direct gated-issue bypass prevention;
- tampering, crash recovery and idempotent folios;
- per-Employee isolation and output confinement;
- CLI end-to-end and trace audit;
- meeting report backup/restore regression.
