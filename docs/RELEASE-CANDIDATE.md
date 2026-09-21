# MANGO Employee v0.12 RC1

v0.12 is a hardening release, not a feature release.

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
