# MANGO Observability & Audit

```bash
mango trace show EMPLOYEE RUN_ID
mango trace explain EMPLOYEE RUN_ID
mango trace explain EMPLOYEE RUN_ID --out explanation.md
mango trace audit EMPLOYEE RUN_ID
```

`mango start` now creates runtime spans and provenance automatically. Tool execution adds tool spans. The trace references Employee, Skill, Sources, Memory, approvals and events.

The explanation is operational provenance—not hidden model reasoning.
