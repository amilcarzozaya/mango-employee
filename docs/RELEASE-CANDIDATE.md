# MANGO Employee v0.12 RC2

v0.12 RC2 combines release hardening with the governed Chain Runtime added after RC1.

```bash
mango release migrate EMPLOYEE
mango release audit EMPLOYEE
mango release readiness EMPLOYEE
mango release backup EMPLOYEE --out ./backups
mango release verify-backup EMPLOYEE ./backups/mango-backup-...
mango release restore EMPLOYEE ./backups/mango-backup-... --force
mango release manifest EMPLOYEE --out release-manifest.json
```

Promotion to v1.0 should require the complete automated suite, clean installation, release readiness, backup/restore round-trip and real Employee pilots without unresolved critical violations.


## Manifest hygiene

`mango release manifest` now fails closed if the hardening release version and `pyproject.toml` version diverge.

Current RC2 provenance:
- manifest format: `mango-release-manifest-v1`;
- package version: `0.12.0rc2`;
- canonical file count: 29;
- release hash: `0adca72dbc9c10a955cb3bbad0824c53cd0a25459cca59d8e37ba1e30ec128a8`.

The manifest includes the runtime Python modules and MANGO `*-SPEC.md` documents, including Chain Runtime.
