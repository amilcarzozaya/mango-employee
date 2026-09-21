# MANGO Tool Protocol

```bash
mango tools list EMPLOYEE
mango tools audit EMPLOYEE
mango tools authorize EMPLOYEE email send
mango tools invoke EMPLOYEE workspace read --args '{"path":"notes.md"}'
mango tools register EMPLOYEE my-tool --adapter external --capability read --risk low
```

`invoke` prepares an invocation by default. `--execute` executes only implemented local adapters. External adapters are intentionally not simulated.

A high-impact invocation with a Gate returns `approval_required` rather than executing.
