# MANGO State / Control Plane

## Commands

```bash
mango start EMPLOYEE --skill pre-meeting-brief --task "Prep Acme" --runtime prepare
mango status EMPLOYEE
mango status EMPLOYEE RUN_ID
mango checkpoint EMPLOYEE RUN_ID --data '{"stage":"draft_ready"}'
mango request-approval EMPLOYEE RUN_ID --category external_send --action "Send follow-up" --reason "Client-facing communication"
mango approvals EMPLOYEE
mango approve EMPLOYEE APPROVAL_ID --actor Founder
mango reject EMPLOYEE APPROVAL_ID --actor Founder
mango retry EMPLOYEE RUN_ID
mango cancel EMPLOYEE RUN_ID
mango history EMPLOYEE
```

`mango start` creates a persistent Run before preparing/executing the Runtime Package. The Control Plane records status, package checkpoint, result/error, attempts, Approval Cards and an append-only event history.

State and Memory deliberately use separate SQLite stores.
