# MANGO Employee v0.12 RC2 — Validation Checklist

- Automated regression suite: **PASS in CI**
- Isolated editable install: **PASS**
- GitHub Actions Python 3.10: **PASS**
- GitHub Actions Python 3.11: **PASS**
- GitHub Actions Python 3.12: **PASS**
- GitHub Actions Python 3.13: **PASS**
- MANGO Chain Runtime regression tests: **PASS**
- Category Search → LinkedIn handoff lineage: **PASS**
- v0.11 Team CLI compatibility: **PASS**
- Schema migration + idempotence: **PASS**
- Newer-schema fail-closed behavior: **PASS**
- Data integrity audit: **PASS**
- Security audit: **PASS**
- Release readiness: **PASS**
- Backup checksum verification: **PASS**
- Restore round-trip: **PASS**
- Release provenance manifest: **PASS**
- Manifest/package version consistency guard: **PASS**
- Documentation onboarding/link regression tests: **PASS**

Release manifest:
- Format: `mango-release-manifest-v1`
- Version: `0.12.0rc2`
- Canonical files: **29**
- Release hash: `d95019d2c01fb636d33c4c0b062bca4824c35528b60cd65d0017d33321a43dd3`

RC2 includes Chain Runtime and the refreshed release provenance snapshot. Promotion beyond RC2 still requires the project’s normal release/pilot criteria.
