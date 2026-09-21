# MANGO Memory

## Quick start

```bash
mango memory init reference-employees/mango-chief-of-staff
mango memory add reference-employees/mango-chief-of-staff --type decision --subject acme.erp.phase1 --value "ERP excluded from phase 1" --scope client --scope-id acme --source-type meeting --source-id meeting-2026-09-20 --authority client --confidence 1
mango memory verify reference-employees/mango-chief-of-staff MEM_ID --actor Founder
mango memory approve reference-employees/mango-chief-of-staff MEM_ID --actor Founder
mango memory search reference-employees/mango-chief-of-staff "Acme ERP"
mango memory explain reference-employees/mango-chief-of-staff MEM_ID
mango memory audit reference-employees/mango-chief-of-staff
mango memory consolidate reference-employees/mango-chief-of-staff
```

`mango run` automatically retrieves a bounded MANGO Memory Pack for the task and active Skill. Candidate and sensitive memories are excluded from normal runtime retrieval.
