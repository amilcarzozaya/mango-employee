# MANGO Approval & Execution Engine

```bash
mango action prepare EMPLOYEE RUN_ID workspace write --args '{"path":"draft.md","content":"..."}'
mango action list EMPLOYEE --run-id RUN_ID
mango action approve EMPLOYEE ACTION_ID --actor Founder
mango action approve EMPLOYEE ACTION_ID --actor Founder --execute
mango action reject EMPLOYEE ACTION_ID --actor Founder
mango action execute EMPLOYEE ACTION_ID
```

High-impact actions generate an Approval Card automatically. Approval is cryptographically bound to the exact Run + Tool + Capability + arguments. Permissions are rechecked before execution.
