# MANGO Quote Builder — commercial-quotation 1.0.0

An independent MANGO Employee Skill for exact, reviewable commercial quotations.

## New user

Read [the from-zero manual](../../docs/quote-builder/USER-GUIDE.md). Install the
optional document dependencies with `pip install -e ".[quote]"`.

The Skill exists in `skills/registry.json` but is **not automatically available
to every Employee**. Assign it to employee.json or use the updated Chief of Staff
reference Employee, then validate with `mango info` and `mango validate`.

## Workflow

```bash
mango quote profile init reference-employees/mango-chief-of-staff \
  --from-file examples/quote-builder/issuer-profile.json

mango quote calculate reference-employees/mango-chief-of-staff \
  --profile demo --request examples/quote-builder/request.json

mango quote draft reference-employees/mango-chief-of-staff \
  --profile demo --request examples/quote-builder/request.json \
  --formats json,md,docx,pdf

mango quote issue reference-employees/mango-chief-of-staff \
  --draft DRAFT_ID --approved-by "Aprobador humano" \
  --formats json,md,docx,pdf
```

All example names, contacts, client data and transactions are fictitious.

No AI model is needed for exact financial calculations, tax application or
document generation. The issuer alone selects applicable tax codes, rates,
dates and treatment. This Skill does not issue CFDI, send emails or authenticate
the human approver.
