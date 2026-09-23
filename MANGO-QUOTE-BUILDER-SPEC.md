# MANGO Quote Builder Specification v1

> **Advanced / normative reference.** If you are new to MANGO Employee, start with `docs/START-HERE.md`, then `docs/CONCEPTS.md` and the [Quote Builder user guide](docs/quote-builder/USER-GUIDE.md).

## Author and purpose

Amílcar Zozaya, creator of Método MANGO and MANGO Employee.

`commercial-quotation@1.0.0` is an independent Skill complementing `proposal-builder`. It configures an issuer once and produces exact, inspectable commercial quotations without letting an LLM perform arithmetic.

## Implementation

- `mango_cli/quote.py` — profile validation, exact Decimal calculator, immutable draft snapshots, SQLite folio issuance.
- `mango_cli/quote_render.py` — Markdown, JSON, optional Word and PDF.
- `skills/commercial-quotation/` — Skill, input schemas and README.
- `docs/quote-builder/` — from-zero manual and technical spec.
- `cli-tests/test_quote.py` — golden math, tax, concurrency, idempotency and document export tests.

## Core invariants

1. Issuer must configure identity, company, legal name, email, phone, address, currency, taxes, conditions and folio prefix explicitly.
2. Prices and tax codes originate in user-supplied JSON, never inferred from AI output.
3. The tax catalogue is per issuer and has optional effective dates.
4. Quantity, price, discount and rates are calculated with Decimal, not binary float; line rounding is ROUND_HALF_UP.
5. Tax-inclusive pricing is reverse-calculated and any residual reconciled on the last additional tax.
6. The draft stores issuer/tax snapshots and an integrity hash; no commercial folio assigned.
7. Issuance requires manual approval attestation and allocates a unique, sequential prefix/year folio under BEGIN IMMEDIATE SQLite transaction.
8. The same draft cannot consume a second folio under retries.
9. Generated DOCX/PDF/Markdown are rendered from the same validated JSON payload.
10. Nothing sends emails, debits accounts, changes CRM or issues CFDI automatically.

## Stage 4: formal commercial approval

The independent Skill now has a tracked workflow using
`mango workflow quote-draft` and `mango workflow quote-issue`. Each
configured pricing, scope, deadline and legal Gate creates its own
Approval Card, bound to the Run ID and exact immutable draft SHA256.
The quote service revalidates all cards, category scope, Employee ID,
draft hash, total, currency and commercial dates **at mutation time**.

The direct `mango quote issue` command is deliberately rejected for
Employees with commercial Gates unless `--approval-run RUN_ID` supplies
the formally authorized Run; using the workflow command is preferred so
the same Run is completed and its Trace is preserved. `--approved-by`
alone remains possible only for legitimately ungated Employees and
does not authenticate identity.

The quote workflow retains the same folio across rendering failure/retry
and never sends commercial documents externally. For setup and exact CLI
syntax see [Operational Workflows](docs/OPERATIONAL-WORKFLOWS.md).

## Limitations and controls

An `approved_by` string is a manual operator statement, not authenticated identity, a digital signature or a replacement for formal organizational approval. Tax rules are configurable data, not a tax-law inference engine. The example withholding is simulated arithmetic only. No CFDI/PAC implementation exists.

The current CLI issues local documents; planned future versions may integrate authenticated Gate approvals, approved offer catalogues, CRM and invoices as separately governed components.

For operation, use [the full user guide](docs/quote-builder/USER-GUIDE.md) and [technical spec](docs/quote-builder/TECHNICAL-SPEC.md).
