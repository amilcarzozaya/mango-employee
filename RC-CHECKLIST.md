# MANGO Employee v0.12 RC1 — Validation Checklist

- Automated regression suite: **56 passed, 1 warning in 0.60s**
- Isolated clean install: **PASS**
- Installed CLI without build environment: **PASS**
- Relative-path CLI portability: **PASS**
- GitHub Actions Python 3.10: **PASS**
- GitHub Actions Python 3.11: **PASS**
- GitHub Actions Python 3.12: **PASS**
- GitHub Actions Python 3.13: **PASS**
- v0.11 Team CLI compatibility: **PASS**
- Schema migration + idempotence: **PASS**
- Newer-schema fail-closed behavior: **PASS**
- Data integrity audit: **PASS**
- Security audit: **PASS**
- Release readiness: **PASS**
- Backup checksum verification: **PASS**
- Restore round-trip: **PASS**
- Post-restore readiness: **PASS**
- Release provenance manifest: **PASS**

Release hash: `06ce5df0f125bb4ca0357ba4eae5be554672d8b88dd53b94a35de48ddca896b3`

RC1 is technically hardened. Promotion to v1.0 still requires real-world pilot evidence plus final licensing/IP/public-API decisions.